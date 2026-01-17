"""
Unified Research & Chemistry Platform API
Combines research analysis and chemistry simulation with integrated subscription and OpenRouter
"""

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import httpx
from loguru import logger
import json
import asyncio
from pathlib import Path

# Import existing modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from chemistry_lab.backend.chemistry_engine import ChemistryEngine, Molecule
from agents import AgentFactory, AgentOrchestrator, ConsensusEngine
from extractors import ExtractionOrchestrator, PaperSource

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
security = HTTPBearer()

# OpenRouter Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS = {
    "free": "openai/gpt-3.5-turbo",
    "basic": "anthropic/claude-3-haiku",
    "pro": "anthropic/claude-3-sonnet",
    "enterprise": "anthropic/claude-3-opus"
}

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    field_of_study: str = "General Science"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    field_of_study: str
    subscription_tier: str = "free"
    credits_remaining: float = 0.0
    created_at: datetime
    subscription_expires: Optional[datetime] = None


class CreditUsage(BaseModel):
    user_id: str
    action: str
    credits_used: float
    model_used: str
    timestamp: datetime


class ResearchQuery(BaseModel):
    query: str
    research_question: str
    max_papers: int = 10
    analysis_types: List[str] = ["what", "how", "why"]


class ChemistryQuery(BaseModel):
    message: str
    reactants: List[str] = Field(default_factory=list)
    temperature: float = 298.15
    pressure: float = 101325.0


class SubscriptionUpgrade(BaseModel):
    tier: str
    payment_token: str


# In-memory database (use PostgreSQL in production)
users_db: Dict[str, Dict] = {}
credit_usage_db: List[Dict] = []
openrouter_keys: Dict[str, str] = {}  # user_id -> api_key


class UnifiedPlatform:
    def __init__(self):
        self.app = FastAPI(
            title="Unified Research & Chemistry Platform",
            description="Advanced platform combining multi-agent research analysis with interactive chemistry simulation",
            version="2.0.0"
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize engines
        self.chemistry_engine = ChemistryEngine()
        self.paper_orchestrator = None
        self.agent_pool = {}
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes."""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "Unified Research & Chemistry Platform",
                "version": "2.0.0",
                "features": [
                    "Multi-agent research analysis",
                    "Interactive chemistry simulation",
                    "Integrated OpenRouter API",
                    "Credit-based subscription",
                    "Advanced UI/UX"
                ]
            }
        
        # ============ AUTHENTICATION ============
        
        @self.app.post("/auth/register")
        async def register(user: UserCreate):
            """Register new user with initial credits."""
            if user.email in users_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            hashed_password = bcrypt.hashpw(
                user.password.encode('utf-8'),
                bcrypt.gensalt()
            )
            
            user_id = f"user_{len(users_db)}"
            user_data = {
                "id": user_id,
                "email": user.email,
                "username": user.username,
                "field_of_study": user.field_of_study,
                "password": hashed_password,
                "subscription_tier": "free",
                "credits_remaining": 100.0,  # Free starting credits
                "created_at": datetime.utcnow(),
                "subscription_expires": None,
                "total_research_queries": 0,
                "total_chemistry_simulations": 0,
                "total_ai_messages": 0
            }
            users_db[user.email] = user_data
            
            token = self._create_access_token({"sub": user.email})
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {k: v for k, v in user_data.items() if k != 'password'}
            }
        
        @self.app.post("/auth/login")
        async def login(credentials: UserLogin):
            """Login user."""
            user_data = users_db.get(credentials.email)
            
            if not user_data or not bcrypt.checkpw(
                credentials.password.encode('utf-8'),
                user_data['password']
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            token = self._create_access_token({"sub": credentials.email})
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {k: v for k, v in user_data.items() if k != 'password'}
            }
        
        @self.app.get("/auth/me")
        async def get_current_user(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get current user with credit info."""
            user = await self._get_current_user(credentials.credentials)
            return {k: v for k, v in user.items() if k != 'password'}
        
        # ============ SUBSCRIPTION & CREDITS ============
        
        @self.app.post("/subscription/upgrade")
        async def upgrade_subscription(
            subscription: SubscriptionUpgrade,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Upgrade subscription and add credits."""
            user = await self._get_current_user(credentials.credentials)
            
            credit_packages = {
                "free": {"credits": 100, "price": 0},
                "basic": {"credits": 1000, "price": 9.99},
                "pro": {"credits": 5000, "price": 29.99},
                "enterprise": {"credits": 50000, "price": 99.99}
            }
            
            if subscription.tier not in credit_packages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tier"
                )
            
            package = credit_packages[subscription.tier]
            user['subscription_tier'] = subscription.tier
            user['credits_remaining'] += package['credits']
            user['subscription_expires'] = datetime.utcnow() + timedelta(days=30)
            
            return {
                "success": True,
                "tier": subscription.tier,
                "credits_added": package['credits'],
                "new_balance": user['credits_remaining'],
                "expires": user['subscription_expires']
            }
        
        @self.app.post("/credits/purchase")
        async def purchase_credits(
            amount: int,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Purchase additional credits."""
            user = await self._get_current_user(credentials.credentials)
            
            # $1 = 100 credits
            credits_to_add = amount * 100
            user['credits_remaining'] += credits_to_add
            
            return {
                "success": True,
                "credits_added": credits_to_add,
                "new_balance": user['credits_remaining']
            }
        
        @self.app.get("/credits/usage")
        async def get_credit_usage(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get detailed credit usage history."""
            user = await self._get_current_user(credentials.credentials)
            
            user_usage = [
                usage for usage in credit_usage_db 
                if usage['user_id'] == user['id']
            ]
            
            return {
                "current_balance": user['credits_remaining'],
                "total_used": sum(u['credits_used'] for u in user_usage),
                "usage_history": user_usage[-50:],  # Last 50 transactions
                "breakdown": self._calculate_usage_breakdown(user_usage)
            }
        
        # ============ OPENROUTER INTEGRATION ============
        
        @self.app.post("/openrouter/configure")
        async def configure_openrouter(
            api_key: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Configure user's OpenRouter API key."""
            user = await self._get_current_user(credentials.credentials)
            openrouter_keys[user['id']] = api_key
            
            # Test the key
            valid = await self._test_openrouter_key(api_key)
            
            return {
                "success": valid,
                "message": "API key configured successfully" if valid else "Invalid API key"
            }
        
        @self.app.get("/openrouter/balance")
        async def get_openrouter_balance(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get OpenRouter credit balance."""
            user = await self._get_current_user(credentials.credentials)
            api_key = openrouter_keys.get(user['id'])
            
            if not api_key:
                return {"balance": 0, "configured": False}
            
            balance = await self._get_openrouter_balance(api_key)
            return {"balance": balance, "configured": True}
        
        # ============ RESEARCH ANALYSIS ============
        
        @self.app.post("/research/analyze")
        async def analyze_research(
            query: ResearchQuery,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Perform multi-agent research analysis."""
            user = await self._get_current_user(credentials.credentials)
            
            # Check credits
            estimated_cost = self._estimate_research_cost(query)
            if user['credits_remaining'] < estimated_cost:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Insufficient credits. Need {estimated_cost}, have {user['credits_remaining']}"
                )
            
            # Initialize if needed
            if not self.paper_orchestrator:
                from config import get_settings
                settings = get_settings()
                self.paper_orchestrator = ExtractionOrchestrator(
                    storage_path=settings.paper_storage_path
                )
            
            # Search papers
            papers = await self.paper_orchestrator.search_and_process(
                query=query.query,
                max_results=query.max_papers,
                download_pdfs=False
            )
            
            # Get or create agents
            agents = await self._get_or_create_agents(user)
            
            # Analyze
            consensus_engine = ConsensusEngine()
            orchestrator = AgentOrchestrator(agents, consensus_engine)
            
            results = await orchestrator.analyze_papers_with_query(
                papers=papers,
                query=query.research_question,
                run_all_analysis_types=len(query.analysis_types) > 1
            )
            
            # Deduct credits
            actual_cost = len(papers) * len(agents) * 2  # 2 credits per paper per agent
            await self._deduct_credits(user, actual_cost, "research_analysis", "multi-agent")
            user['total_research_queries'] += 1
            
            return {
                "success": True,
                "papers_analyzed": len(papers),
                "agents_used": len(agents),
                "results": results,
                "credits_used": actual_cost,
                "credits_remaining": user['credits_remaining']
            }
        
        # ============ CHEMISTRY SIMULATION ============
        
        @self.app.post("/chemistry/simulate")
        async def simulate_chemistry(
            query: ChemistryQuery,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Simulate chemical reactions."""
            user = await self._get_current_user(credentials.credentials)
            
            # Check credits (5 credits per simulation)
            if user['credits_remaining'] < 5:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Insufficient credits for simulation"
                )
            
            # Create molecules if needed
            if not query.reactants:
                water = self.chemistry_engine.create_water_molecule()
                mol_id = self.chemistry_engine.add_molecule(water)
                query.reactants = [mol_id]
            
            # Run simulation
            result = self.chemistry_engine.simulate_reaction(
                query.reactants,
                query.temperature
            )
            
            # Deduct credits
            await self._deduct_credits(user, 5, "chemistry_simulation", "molecular_dynamics")
            user['total_chemistry_simulations'] += 1
            
            return {
                "success": True,
                "simulation": result,
                "credits_used": 5,
                "credits_remaining": user['credits_remaining']
            }
        
        @self.app.post("/chemistry/chat")
        async def chemistry_chat(
            message: str,
            use_openrouter: bool = True,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Chat with AI about chemistry using OpenRouter."""
            user = await self._get_current_user(credentials.credentials)
            
            if use_openrouter:
                api_key = openrouter_keys.get(user['id'])
                if not api_key:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OpenRouter API key not configured"
                    )
                
                response = await self._call_openrouter(
                    api_key,
                    message,
                    user['subscription_tier']
                )
                
                # Credits deducted by OpenRouter, track usage
                await self._log_credit_usage(
                    user['id'],
                    10,  # Estimated
                    "chemistry_chat",
                    OPENROUTER_MODELS[user['subscription_tier']]
                )
            else:
                # Use basic response (1 credit)
                if user['credits_remaining'] < 1:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="Insufficient credits"
                    )
                
                response = self._basic_chemistry_response(message)
                await self._deduct_credits(user, 1, "chemistry_chat", "basic")
            
            user['total_ai_messages'] += 1
            
            return {
                "response": response,
                "model_used": OPENROUTER_MODELS[user['subscription_tier']] if use_openrouter else "basic",
                "credits_remaining": user['credits_remaining']
            }
        
        # ============ UNIFIED DASHBOARD ============
        
        @self.app.get("/dashboard/stats")
        async def get_dashboard_stats(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get user dashboard statistics."""
            user = await self._get_current_user(credentials.credentials)
            
            user_usage = [u for u in credit_usage_db if u['user_id'] == user['id']]
            
            return {
                "user": {
                    "username": user['username'],
                    "field_of_study": user['field_of_study'],
                    "tier": user['subscription_tier'],
                    "member_since": user['created_at']
                },
                "credits": {
                    "remaining": user['credits_remaining'],
                    "used_total": sum(u['credits_used'] for u in user_usage),
                    "usage_trend": self._calculate_usage_trend(user_usage)
                },
                "activity": {
                    "research_queries": user['total_research_queries'],
                    "chemistry_simulations": user['total_chemistry_simulations'],
                    "ai_messages": user['total_ai_messages']
                },
                "recent_activity": user_usage[-10:]
            }
        
        # ============ WEBSOCKET ============
        
        @self.app.websocket("/ws/live")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates."""
            await websocket.accept()
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message['type'] == 'ping':
                        await websocket.send_json({"type": "pong"})
                    
                    elif message['type'] == 'simulate':
                        # Real-time chemistry simulation
                        result = self.chemistry_engine.simulate_reaction(
                            message.get('reactants', []),
                            message.get('temperature', 298.15)
                        )
                        await websocket.send_json({
                            "type": "simulation_result",
                            "data": result
                        })
            
            except WebSocketDisconnect:
                pass
    
    # ============ HELPER METHODS ============
    
    def _create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def _get_current_user(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None or email not in users_db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return users_db[email]
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def _deduct_credits(self, user: Dict, amount: float, action: str, model: str):
        """Deduct credits and log usage."""
        user['credits_remaining'] -= amount
        await self._log_credit_usage(user['id'], amount, action, model)
    
    async def _log_credit_usage(self, user_id: str, amount: float, action: str, model: str):
        """Log credit usage."""
        credit_usage_db.append({
            "user_id": user_id,
            "action": action,
            "credits_used": amount,
            "model_used": model,
            "timestamp": datetime.utcnow()
        })
    
    def _estimate_research_cost(self, query: ResearchQuery) -> float:
        """Estimate research query cost."""
        return query.max_papers * 10  # 10 credits per paper
    
    async def _get_or_create_agents(self, user: Dict):
        """Get or create agent pool for user."""
        user_id = user['id']
        if user_id not in self.agent_pool:
            # Create minimal agent pool based on tier
            from config import get_settings
            settings = get_settings()
            
            num_agents = {"free": 2, "basic": 5, "pro": 10, "enterprise": 15}[user['subscription_tier']]
            
            agents = AgentFactory.create_agent_pool(
                openai_keys=settings.openai_api_keys[:1],
                anthropic_keys=settings.anthropic_api_keys[:1],
                google_keys=[],
                max_agents=num_agents
            )
            self.agent_pool[user_id] = agents
        
        return self.agent_pool[user_id]
    
    async def _call_openrouter(self, api_key: str, message: str, tier: str) -> str:
        """Call OpenRouter API."""
        model = OPENROUTER_MODELS[tier]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are an expert chemistry AI assistant."},
                            {"role": "user", "content": message}
                        ]
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://unified-platform.ai",
                        "X-Title": "Unified Research Platform"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                else:
                    return f"Error calling OpenRouter: {response.status_code}"
        
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return f"Error: {str(e)}"
    
    def _basic_chemistry_response(self, message: str) -> str:
        """Basic chemistry response without AI."""
        return f"Basic response to: {message}\n\nUpgrade to use advanced AI models via OpenRouter!"
    
    async def _test_openrouter_key(self, api_key: str) -> bool:
        """Test if OpenRouter API key is valid."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{OPENROUTER_BASE_URL}/auth/key",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                return response.status_code == 200
        except:
            return False
    
    async def _get_openrouter_balance(self, api_key: str) -> float:
        """Get OpenRouter credit balance."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{OPENROUTER_BASE_URL}/auth/key",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('data', {}).get('limit_remaining', 0)
        except:
            pass
        return 0.0
    
    def _calculate_usage_breakdown(self, usage_history: List[Dict]) -> Dict:
        """Calculate usage breakdown by action type."""
        breakdown = {}
        for usage in usage_history:
            action = usage['action']
            breakdown[action] = breakdown.get(action, 0) + usage['credits_used']
        return breakdown
    
    def _calculate_usage_trend(self, usage_history: List[Dict]) -> List[Dict]:
        """Calculate usage trend over time."""
        # Group by date
        daily_usage = {}
        for usage in usage_history:
            date = usage['timestamp'].date()
            daily_usage[date] = daily_usage.get(date, 0) + usage['credits_used']
        
        return [
            {"date": str(date), "credits": credits}
            for date, credits in sorted(daily_usage.items())
        ]


def create_unified_app() -> FastAPI:
    """Create unified application."""
    platform = UnifiedPlatform()
    return platform.app


if __name__ == "__main__":
    import uvicorn
    app = create_unified_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)
