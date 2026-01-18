# 🧪 Interactive Chemistry Lab

A stunning, interactive web application for chemistry simulation with AI-powered explanations, 3D molecular visualization, and real-time reaction analysis.

## ✨ Features

### 🔬 Core Chemistry Features
- **3D Molecular Visualization** - Real-time rendering of atomic structures with WebGL
- **Reaction Simulation** - Detailed molecular dynamics and energy profiles
- **Parameter Control** - Adjust temperature, pressure, and other reaction conditions
- **Atomic-Level Explanations** - Understand WHAT, WHY, and HOW reactions occur

### 🤖 AI-Powered Analysis
- **Chemistry Chat** - Ask questions and get detailed explanations
- **Multiple AI Models** - Access to Claude 3, GPT-4, and more (subscription-based)
- **OpenRouter Integration** - Direct connection to state-of-the-art reasoning models
- **Real-time Responses** - WebSocket support for instant updates

### 🎨 Interactive Design
- **Glowing Effects** - Beautiful neon aesthetics throughout
- **Smooth Animations** - Floating, pulsing, and shimmering effects
- **Cursor Interactions** - Responsive hover states and transitions
- **Equipment Simulation** - Interactive lab equipment (beakers, flasks, burners)

### 💎 Subscription Tiers
- **Free** - Basic simulations and AI responses
- **Basic ($9.99/mo)** - Claude 3 Haiku, 100 simulations/day
- **Pro ($29.99/mo)** - Claude 3 Sonnet, GPT-4, unlimited simulations
- **Enterprise ($99.99/mo)** - All models, white-label, dedicated support

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd chemistry_lab/backend

# Install dependencies
pip install fastapi uvicorn pydantic python-jose bcrypt httpx numpy loguru

# Run the API
python chemistry_api.py
```

The API will be available at `http://localhost:8001`

### Frontend Setup

```bash
cd chemistry_lab/frontend

# Install dependencies
npm install react react-dom three axios

# Start development server
npm run dev
```

The web app will be available at `http://localhost:3000`

## 📖 API Documentation

### Authentication

#### Register
```bash
POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
  "username": "ChemistryNerd"
}
```

#### Login
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Chemistry Operations

#### Create Molecule
```bash
POST /chemistry/molecule/create
Authorization: Bearer <token>
{
  "name": "Water",
  "formula": "H₂O",
  "atoms": [
    {"symbol": "H", "atomic_number": 1, "mass": 1.008, "position": [-0.757, 0.586, 0]},
    {"symbol": "O", "atomic_number": 8, "mass": 15.999, "position": [0, 0, 0]},
    {"symbol": "H", "atomic_number": 1, "mass": 1.008, "position": [0.757, 0.586, 0]}
  ],
  "bonds": [
    {"atom1": "H", "atom2": "O", "type": "covalent", "order": 1},
    {"atom1": "H", "atom2": "O", "type": "covalent", "order": 1}
  ]
}
```

#### Simulate Reaction
```bash
POST /chemistry/simulate
Authorization: Bearer <token>
{
  "reactant_ids": ["water_0"],
  "temperature": 298.15,
  "pressure": 101325,
  "simulation_steps": 100
}
```

Response includes:
- Detailed WHAT/WHY/HOW analysis
- Atomic-level interactions
- Energy profile
- 3D visualization data

#### Chat with AI
```bash
POST /chemistry/chat
Authorization: Bearer <token>
{
  "message": "Why does water boil at 100°C?",
  "reactants": [],
  "temperature": 298.15,
  "use_advanced_model": true
}
```

### Subscription Management

#### Upgrade Subscription
```bash
POST /subscription/upgrade
Authorization: Bearer <token>
{
  "tier": "pro",
  "payment_method": "card",
  "amount": 29.99
}
```

## 🎯 Usage Examples

### Example 1: Water Molecule Simulation

```python
import requests

# Login
response = requests.post('http://localhost:8001/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Create water molecule
water = requests.post(
    'http://localhost:8001/chemistry/molecule/create',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'name': 'Water',
        'formula': 'H₂O',
        'atoms': [
            {'symbol': 'H', 'atomic_number': 1, 'mass': 1.008, 'position': [-0.757, 0.586, 0]},
            {'symbol': 'O', 'atomic_number': 8, 'mass': 15.999, 'position': [0, 0, 0]},
            {'symbol': 'H', 'atomic_number': 1, 'mass': 1.008, 'position': [0.757, 0.586, 0]}
        ],
        'bonds': [
            {'atom1': 'H', 'atom2': 'O', 'type': 'covalent', 'order': 1},
            {'atom1': 'H', 'atom2': 'O', 'type': 'covalent', 'order': 1}
        ]
    }
)

molecule_id = water.json()['molecule_id']

# Simulate
simulation = requests.post(
    'http://localhost:8001/chemistry/simulate',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'reactant_ids': [molecule_id],
        'temperature': 373.15,  # 100°C
        'pressure': 101325
    }
)

print(simulation.json()['simulation']['analysis'])
```

### Example 2: AI Chemistry Chat

```javascript
const response = await fetch('http://localhost:8001/chemistry/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Explain why sodium reacts violently with water',
    use_advanced_model: true
  })
});

const data = await response.json();
console.log(data.response);
```

## 🏗️ Architecture

```
Chemistry Lab
│
├── Backend (FastAPI)
│   ├── chemistry_engine.py     - Core simulation engine
│   ├── chemistry_api.py        - REST API with auth
│   └── OpenRouter integration  - AI model access
│
├── Frontend (React + Three.js)
│   ├── ChemistryLab.tsx        - Main component
│   ├── ChemistryLab.css        - Glowing styles
│   └── 3D visualization        - WebGL rendering
│
└── Features
    ├── Molecular dynamics
    ├── Energy calculations
    ├── AI explanations
    └── Real-time updates (WebSocket)
```

## 🎨 UI Components

### Navigation Bar
- Service logo with pulsing animation
- View switcher (Lab / Chat / Settings)
- User info with subscription tier badge

### Chemistry Lab View
- **3D Canvas** - Interactive molecular visualization
- **Control Panel** - Temperature, pressure sliders
- **Equipment** - Beakers, flasks, burners with hover effects
- **Molecule Library** - Selectable molecules with glow on selection

### Chat View
- **Message History** - User and AI messages
- **Input Field** - Glowing border on focus
- **Model Indicator** - Shows which AI model is used

### Settings View
- **Subscription Plans** - Grid of tier cards
- **Features List** - What's included in each plan
- **Upgrade Button** - Animated call-to-action

## 🎓 Chemistry Explanations

The system provides three levels of explanation:

### WHAT Happens
- Molecular changes
- State transitions
- Observable phenomena

### WHY It Happens
- Thermodynamic driving forces
- Gibbs free energy
- Entropy changes
- Electronic factors

### HOW It Proceeds
- Collision theory
- Activation energy
- Transition states
- Mechanism steps

## 🔐 Security

- JWT-based authentication
- Bcrypt password hashing
- CORS protection
- Rate limiting
- Subscription verification

## 📊 Performance

- 3D rendering at 60 FPS
- Real-time molecular dynamics
- WebSocket for instant updates
- Optimized API responses

## 🌐 Deployment

### Docker Deployment

```bash
# Build images
docker build -t chemistry-backend ./backend
docker build -t chemistry-frontend ./frontend

# Run containers
docker run -p 8001:8001 chemistry-backend
docker run -p 3000:3000 chemistry-frontend
```

### Environment Variables

Create `.env` file:

```env
# Backend
SECRET_KEY=your-secret-key-change-in-production
OPENROUTER_API_KEY=your-openrouter-key
DATABASE_URL=postgresql://user:pass@localhost/chemistry

# Frontend
REACT_APP_API_URL=http://localhost:8001
```

## 🔮 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] VR chemistry lab
- [ ] Collaborative experiments
- [ ] Export to laboratory notebook
- [ ] Integration with lab equipment APIs
- [ ] Machine learning for property prediction
- [ ] Quantum chemistry calculations
- [ ] Chemical safety database

## 📝 License

MIT License - Open source and free to use

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

## 📧 Support

- Documentation: This README
- API Docs: `http://localhost:8001/docs`
- Issues: GitHub Issues
- Email: support@chemistrylab.ai

## 🎉 Credits

Built with:
- FastAPI - Modern Python web framework
- React - UI library
- Three.js - 3D graphics
- OpenRouter - AI model access
- NumPy - Scientific computing

---

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: 2025-01-17

🧪 **Start exploring chemistry today!** 🧪
