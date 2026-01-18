"""
Chemistry Lab API with Authentication and Subscription Management
Connects to OpenRouter for paid LLM access
"""

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import httpx
from loguru import logger
import json

from chemistry_engine import ChemistryEngine, Molecule, ChemicalState

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
security = HTTPBearer()

# OpenRouter API
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    subscription_tier: str = "free"
    created_at: datetime
    subscription_expires: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class SubscriptionUpdate(BaseModel):
    tier: str  # free, basic, pro, enterprise
    payment_method: str
    amount: float


class ChemistryQuery(BaseModel):
    message: str
    reactants: List[str] = Field(default_factory=list)
    temperature: float = 298.15
    pressure: float = 101325.0
    use_advanced_model: bool = False


class ReactionSimulation(BaseModel):
    reactant_ids: List[str]
    temperature: float = 298.15
    pressure: float = 101325.0
    simulation_steps: int = 100


class MoleculeCreate(BaseModel):
    name: str
    formula: str
    atoms: List[Dict[str, Any]]
    bonds: List[Dict[str, Any]]
    state: str = "solid"
    temperature: float = 298.15


# Database (In-memory for demo - use PostgreSQL in production)
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}


class ChemistryLabAPI:
    def __init__(self):
        self.app = FastAPI(
            title="Interactive Chemistry Lab API",
            description="AI-powered chemistry simulation with real-time reactions",
            version="1.0.0"
        )
        
        # Enable CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.chemistry_engine = ChemistryEngine()
        self.active_connections: List[WebSocket] = []
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes."""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "Interactive Chemistry Lab",
                "version": "1.0.0",
                "features": [
                    "Real-time reaction simulation",
                    "3D molecular visualization",
                    "AI chemistry chat",
                    "Subscription-based LLM access"
                ]
            }
        
        # ============ AUTHENTICATION ============
        
        @self.app.post("/auth/register", response_model=Token)
        async def register(user: UserCreate):
            """Register a new user."""
            if user.email in users_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = bcrypt.hashpw(
                user.password.encode('utf-8'),
                bcrypt.gensalt()
            )
            
            # Create user
            user_id = f"user_{len(users_db)}"
            user_data = {
                "id": user_id,
                "email": user.email,
                "username": user.username,
                "password": hashed_password,
                "subscription_tier": "free",
                "created_at": datetime.utcnow(),
                "subscription_expires": None
            }
            users_db[user.email] = user_data
            
            # Generate token
            token = self._create_access_token({"sub": user.email})
            
            return Token(
                access_token=token,
                user=User(**{k: v for k, v in user_data.items() if k != 'password'})
            )
        
        @self.app.post("/auth/login", response_model=Token)
        async def login(credentials: UserLogin):
            """Login and get access token."""
            user_data = users_db.get(credentials.email)
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Verify password
            if not bcrypt.checkpw(
                credentials.password.encode('utf-8'),
                user_data['password']
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Generate token
            token = self._create_access_token({"sub": credentials.email})
            
            return Token(
                access_token=token,
                user=User(**{k: v for k, v in user_data.items() if k != 'password'})
            )
        
        @self.app.get("/auth/me", response_model=User)
        async def get_current_user(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get current user info."""
            user = await self._get_current_user(credentials.credentials)
            return User(**{k: v for k, v in user.items() if k != 'password'})
        
        # ============ SUBSCRIPTION ============
        
        @self.app.post("/subscription/upgrade")
        async def upgrade_subscription(
            subscription: SubscriptionUpdate,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Upgrade user subscription."""
            user = await self._get_current_user(credentials.credentials)
            
            # Validate tier
            valid_tiers = ["free", "basic", "pro", "enterprise"]
            if subscription.tier not in valid_tiers:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tier. Choose from: {valid_tiers}"
                )
            
            # Update subscription
            user['subscription_tier'] = subscription.tier
            user['subscription_expires'] = datetime.utcnow() + timedelta(days=30)
            
            return {
                "success": True,
                "tier": subscription.tier,
                "expires": user['subscription_expires'],
                "features": self._get_tier_features(subscription.tier)
            }
        
        @self.app.get("/subscription/features")
        async def get_subscription_features(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get features available in current subscription."""
            user = await self._get_current_user(credentials.credentials)
            return self._get_tier_features(user['subscription_tier'])
        
        # ============ CHEMISTRY SIMULATION ============
        
        @self.app.post("/chemistry/simulate")
        async def simulate_reaction(
            simulation: ReactionSimulation,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Simulate a chemical reaction."""
            user = await self._get_current_user(credentials.credentials)
            
            result = self.chemistry_engine.simulate_reaction(
                simulation.reactant_ids,
                simulation.temperature
            )
            
            return {
                "success": True,
                "simulation": result,
                "user_tier": user['subscription_tier']
            }
        
        @self.app.post("/chemistry/molecule/create")
        async def create_molecule(
            molecule: MoleculeCreate,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Create a custom molecule."""
            # Create molecule from specification
            from chemistry_engine import Atom, Bond, BondType
            
            atoms = [
                Atom(
                    symbol=a['symbol'],
                    atomic_number=a['atomic_number'],
                    mass=a['mass'],
                    position=tuple(a.get('position', [0, 0, 0]))
                )
                for a in molecule.atoms
            ]
            
            bonds = [
                Bond(
                    atom1_id=b['atom1'],
                    atom2_id=b['atom2'],
                    bond_type=BondType(b['type']),
                    bond_order=b.get('order', 1)
                )
                for b in molecule.bonds
            ]
            
            mol = Molecule(
                name=molecule.name,
                formula=molecule.formula,
                atoms=atoms,
                bonds=bonds,
                state=ChemicalState(molecule.state),
                temperature=molecule.temperature
            )
            
            mol_id = self.chemistry_engine.add_molecule(mol)
            
            return {
                "success": True,
                "molecule_id": mol_id,
                "structure": mol.get_3d_structure()
            }
        
        @self.app.get("/chemistry/molecule/{molecule_id}")
        async def get_molecule(
            molecule_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get molecule details and 3D structure."""
            if molecule_id not in self.chemistry_engine.molecules:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Molecule not found"
                )
            
            mol = self.chemistry_engine.molecules[molecule_id]
            
            return {
                "id": molecule_id,
                "name": mol.name,
                "formula": mol.formula,
                "state": mol.state.value,
                "temperature": mol.temperature,
                "structure": mol.get_3d_structure(),
                "properties": {
                    "molecular_weight": mol.molecular_weight,
                    "num_atoms": len(mol.atoms),
                    "num_bonds": len(mol.bonds),
                    "color": mol.color,
                    "pH": mol.pH
                }
            }
        
        # ============ AI CHEMISTRY CHAT ============
        
        @self.app.post("/chemistry/chat")
        async def chemistry_chat(
            query: ChemistryQuery,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """
            Chat with AI about chemistry, reactions, and compounds.
            Uses OpenRouter for advanced models (subscription required).
            """
            user = await self._get_current_user(credentials.credentials)
            
            # Check subscription for advanced models
            if query.use_advanced_model:
                if user['subscription_tier'] == 'free':
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Advanced models require paid subscription"
                    )
            
            # Build chemistry context
            context = self._build_chemistry_context(query.reactants)
            
            # Get AI response
            if query.use_advanced_model:
                response = await self._call_openrouter(
                    query.message,
                    context,
                    user['subscription_tier']
                )
            else:
                response = await self._call_basic_model(query.message, context)
            
            return {
                "response": response,
                "context": context,
                "model_used": "advanced" if query.use_advanced_model else "basic",
                "user_tier": user['subscription_tier']
            }
        
        @self.app.get("/chemistry/explain/{reaction_type}")
        async def explain_reaction(
            reaction_type: str,
            reactants: str = "",
            products: str = "",
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get detailed explanation of a reaction type."""
            reactant_list = [r.strip() for r in reactants.split(",")] if reactants else []
            product_list = [p.strip() for p in products.split(",")] if products else []
            
            explanation = self.chemistry_engine.explain_reaction(
                reactant_list,
                product_list
            )
            
            return {
                "reaction_type": reaction_type,
                "explanation": explanation,
                "reactants": reactant_list,
                "products": product_list
            }
        
        # ============ WEBSOCKET FOR REAL-TIME UPDATES ============
        
        @self.app.websocket("/ws/chemistry")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time chemistry updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message['type'] == 'simulate':
                        result = self.chemistry_engine.simulate_reaction(
                            message['reactants'],
                            message.get('temperature', 298.15)
                        )
                        await websocket.send_json(result)
                    
                    elif message['type'] == 'chat':
                        response = await self._call_basic_model(
                            message['message'],
                            {}
                        )
                        await websocket.send_json({
                            "type": "chat_response",
                            "message": response
                        })
            
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    # ============ HELPER METHODS ============
    
    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def _get_current_user(self, token: str) -> Dict:
        """Decode token and get user."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None or email not in users_db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return users_db[email]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def _get_tier_features(self, tier: str) -> Dict[str, Any]:
        """Get features for subscription tier."""
        features = {
            "free": {
                "simulations_per_day": 10,
                "molecules_stored": 5,
                "ai_messages_per_day": 20,
                "models": ["basic"],
                "3d_visualization": True,
                "reaction_explanations": True,
                "advanced_parameters": False,
                "api_access": False
            },
            "basic": {
                "simulations_per_day": 100,
                "molecules_stored": 50,
                "ai_messages_per_day": 200,
                "models": ["basic", "claude-3-haiku"],
                "3d_visualization": True,
                "reaction_explanations": True,
                "advanced_parameters": True,
                "api_access": True
            },
            "pro": {
                "simulations_per_day": 1000,
                "molecules_stored": 500,
                "ai_messages_per_day": 2000,
                "models": ["basic", "claude-3-haiku", "claude-3-sonnet", "gpt-4"],
                "3d_visualization": True,
                "reaction_explanations": True,
                "advanced_parameters": True,
                "api_access": True,
                "custom_molecules": True,
                "export_data": True
            },
            "enterprise": {
                "simulations_per_day": "unlimited",
                "molecules_stored": "unlimited",
                "ai_messages_per_day": "unlimited",
                "models": ["all"],
                "3d_visualization": True,
                "reaction_explanations": True,
                "advanced_parameters": True,
                "api_access": True,
                "custom_molecules": True,
                "export_data": True,
                "white_label": True,
                "dedicated_support": True
            }
        }
        return features.get(tier, features["free"])
    
    def _build_chemistry_context(self, reactants: List[str]) -> Dict[str, Any]:
        """Build context for AI chat."""
        context = {
            "reactants": reactants,
            "molecules_in_engine": len(self.chemistry_engine.molecules),
            "available_molecules": list(self.chemistry_engine.molecules.keys())
        }
        return context
    
    async def _call_openrouter(
        self, 
        message: str, 
        context: Dict[str, Any],
        tier: str
    ) -> str:
        """Call OpenRouter API for advanced AI models."""
        
        # Select model based on tier
        model_map = {
            "basic": "openai/gpt-3.5-turbo",
            "pro": "anthropic/claude-3-sonnet",
            "enterprise": "anthropic/claude-3-opus"
        }
        model = model_map.get(tier, "openai/gpt-3.5-turbo")
        
        system_prompt = """You are an expert chemistry AI assistant specializing in:
- Chemical reactions and mechanisms
- Atomic and molecular structures
- Thermodynamics and kinetics
- Organic, inorganic, and physical chemistry
- Laboratory techniques and safety

Explain reactions in detail, including WHY they occur (thermodynamics), 
HOW they proceed (mechanism), and WHAT happens at the atomic level.
"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Context: {context}\n\nQuestion: {message}"}
                        ]
                    },
                    headers={
                        "Authorization": f"Bearer YOUR_OPENROUTER_API_KEY",
                        "HTTP-Referer": "https://chemistry-lab.ai",
                        "X-Title": "Interactive Chemistry Lab"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                else:
                    return await self._call_basic_model(message, context)
        
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return await self._call_basic_model(message, context)
    
    async def _call_basic_model(self, message: str, context: Dict[str, Any]) -> str:
        """Basic rule-based response for free tier."""
        
        message_lower = message.lower()
        
        # Pattern matching for common chemistry questions
        if "why" in message_lower and any(word in message_lower for word in ["react", "reaction"]):
            return """
Reactions occur due to thermodynamic driving forces:

1. **Energy Minimization**: Systems naturally move toward lower energy states
2. **Entropy**: Reactions increase disorder in the universe
3. **Gibbs Free Energy**: ΔG = ΔH - TΔS must be negative for spontaneity
4. **Electron Configuration**: Atoms seek stable octet configurations
5. **Bond Strength**: Stronger product bonds drive reactions forward

The reaction proceeds when molecules have sufficient activation energy to overcome the energy barrier.
            """.strip()
        
        elif "how" in message_lower and any(word in message_lower for word in ["work", "proceed", "occur"]):
            return """
Chemical reactions proceed through these steps:

1. **Collision**: Reactant molecules must collide with proper orientation
2. **Activation**: Thermal energy helps overcome activation barrier
3. **Transition State**: Temporary high-energy intermediate forms
4. **Bond Breaking**: Old bonds break (requires energy)
5. **Bond Forming**: New bonds form (releases energy)
6. **Product Formation**: Stable products separate

The reaction mechanism shows the step-by-step molecular changes.
            """.strip()
        
        elif "what" in message_lower:
            return """
In a chemical reaction:

1. **Reactants** are converted to **Products**
2. **Atoms** are conserved (not created or destroyed)
3. **Bonds** break and form
4. **Energy** is absorbed or released
5. **Electron distribution** changes
6. **Physical properties** may change (color, state, temperature)

The balanced equation shows the stoichiometry of the reaction.
            """.strip()
        
        else:
            return """
I'm here to help explain chemistry! Ask me about:
- Why reactions occur (thermodynamics)
- How reactions proceed (mechanisms)
- What happens in reactions (observations)
- Atomic structures and bonding
- Reaction conditions and parameters

Upgrade to Pro for access to advanced AI models like Claude 3 and GPT-4!
            """.strip()


def create_chemistry_api() -> FastAPI:
    """Create and return FastAPI chemistry lab application."""
    api = ChemistryLabAPI()
    return api.app


if __name__ == "__main__":
    import uvicorn
    app = create_chemistry_api()
    uvicorn.run(app, host="0.0.0.0", port=8001)
