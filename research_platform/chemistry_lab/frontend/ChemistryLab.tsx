/**
 * Interactive Chemistry Lab - React Frontend
 * 
 * Features:
 * - 3D molecular visualization
 * - Real-time reaction simulation
 * - AI chemistry chat
 * - Interactive equipment
 * - Glowing effects and animations
 */

import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import axios from 'axios';
import './ChemistryLab.css';

const API_BASE_URL = 'http://localhost:8001';

interface Atom {
  symbol: string;
  position: [number, number, number];
  charge: number;
  color: string;
}

interface Molecule {
  id: string;
  name: string;
  formula: string;
  structure: {
    atoms: Atom[];
    bonds: any[];
  };
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const ChemistryLab: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('chemistry_token'));
  const [molecules, setMolecules] = useState<Molecule[]>([]);
  const [selectedMolecules, setSelectedMolecules] = useState<string[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentView, setCurrentView] = useState<'lab' | 'chat' | 'settings'>('lab');
  const [temperature, setTemperature] = useState(298.15);
  const [pressure, setPressure] = useState(101325);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const moleculeObjectsRef = useRef<THREE.Group[]>([]);

  // ============ AUTHENTICATION ============

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      });
      
      setToken(response.data.access_token);
      setUser(response.data.user);
      localStorage.setItem('chemistry_token', response.data.access_token);
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please check your credentials.');
    }
  };

  const handleRegister = async (email: string, password: string, username: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        password,
        username
      });
      
      setToken(response.data.access_token);
      setUser(response.data.user);
      localStorage.setItem('chemistry_token', response.data.access_token);
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed.');
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('chemistry_token');
  };

  // ============ 3D VISUALIZATION ============

  useEffect(() => {
    if (!canvasRef.current || !token) return;

    // Initialize Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 10;
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    rendererRef.current = renderer;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controlsRef.current = controls;

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      
      // Rotate molecules
      moleculeObjectsRef.current.forEach((mol, index) => {
        mol.rotation.y += 0.01 * (index + 1);
      });
      
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, [token]);

  const visualizeMolecule = (molecule: Molecule) => {
    if (!sceneRef.current) return;

    const group = new THREE.Group();

    // Create atoms
    molecule.structure.atoms.forEach((atom) => {
      const geometry = new THREE.SphereGeometry(0.5, 32, 32);
      const material = new THREE.MeshPhongMaterial({
        color: atom.color,
        emissive: atom.color,
        emissiveIntensity: 0.3,
        shininess: 100
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(...atom.position);
      
      // Add glow effect
      const glowGeometry = new THREE.SphereGeometry(0.6, 32, 32);
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: atom.color,
        transparent: true,
        opacity: 0.3
      });
      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      glow.position.set(...atom.position);
      
      group.add(sphere);
      group.add(glow);
    });

    // Create bonds
    molecule.structure.bonds.forEach((bond: any) => {
      const start = molecule.structure.atoms.find(a => a.symbol === bond.atom1)?.position;
      const end = molecule.structure.atoms.find(a => a.symbol === bond.atom2)?.position;
      
      if (start && end) {
        const direction = new THREE.Vector3(...end).sub(new THREE.Vector3(...start));
        const length = direction.length();
        const geometry = new THREE.CylinderGeometry(0.1, 0.1, length, 8);
        const material = new THREE.MeshPhongMaterial({ color: 0xcccccc });
        const cylinder = new THREE.Mesh(geometry, material);
        
        cylinder.position.set(
          (start[0] + end[0]) / 2,
          (start[1] + end[1]) / 2,
          (start[2] + end[2]) / 2
        );
        
        const axis = new THREE.Vector3(0, 1, 0);
        cylinder.quaternion.setFromUnitVectors(axis, direction.normalize());
        
        group.add(cylinder);
      }
    });

    sceneRef.current.add(group);
    moleculeObjectsRef.current.push(group);
  };

  // ============ CHEMISTRY OPERATIONS ============

  const loadPredefinedMolecules = async () => {
    try {
      // Create water molecule
      const waterResponse = await axios.post(
        `${API_BASE_URL}/chemistry/molecule/create`,
        {
          name: "Water",
          formula: "H₂O",
          atoms: [
            { symbol: "H", atomic_number: 1, mass: 1.008, position: [-0.757, 0.586, 0] },
            { symbol: "O", atomic_number: 8, mass: 15.999, position: [0, 0, 0] },
            { symbol: "H", atomic_number: 1, mass: 1.008, position: [0.757, 0.586, 0] }
          ],
          bonds: [
            { atom1: "H", atom2: "O", type: "covalent", order: 1 },
            { atom1: "H", atom2: "O", type: "covalent", order: 1 }
          ],
          state: "liquid"
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const waterMolecule = await axios.get(
        `${API_BASE_URL}/chemistry/molecule/${waterResponse.data.molecule_id}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setMolecules([waterMolecule.data]);
      visualizeMolecule(waterMolecule.data);
    } catch (error) {
      console.error('Error loading molecules:', error);
    }
  };

  const simulateReaction = async () => {
    if (selectedMolecules.length === 0) {
      alert('Please select molecules to react');
      return;
    }

    setIsSimulating(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/chemistry/simulate`,
        {
          reactant_ids: selectedMolecules,
          temperature,
          pressure,
          simulation_steps: 100
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      console.log('Simulation result:', response.data);
      
      // Display results
      const analysis = response.data.simulation.analysis;
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `
🧪 REACTION SIMULATION COMPLETE

WHAT HAPPENS:
${JSON.stringify(analysis.what_happens, null, 2)}

WHY IT HAPPENS:
${analysis.why_it_happens.join('\n')}

HOW IT HAPPENS:
${analysis.how_it_happens.join('\n')}

🔬 ATOMIC INTERACTIONS:
${analysis.atomic_interactions.map((a: any) => 
  `${a.atom}: ${a.electrons} (${a.valence} valence electrons)`
).join('\n')}
        `,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setIsSimulating(false);
    }
  };

  // ============ AI CHAT ============

  const sendChatMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await axios.post(
        `${API_BASE_URL}/chemistry/chat`,
        {
          message: inputMessage,
          reactants: selectedMolecules,
          temperature,
          pressure,
          use_advanced_model: user?.subscription_tier !== 'free'
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message.',
        timestamp: new Date()
      }]);
    }
  };

  // ============ RENDER ============

  if (!token) {
    return <LoginScreen onLogin={handleLogin} onRegister={handleRegister} />;
  }

  return (
    <div className="chemistry-lab">
      {/* Navigation */}
      <nav className="lab-nav">
        <div className="logo">🧪 Chemistry Lab</div>
        <div className="nav-buttons">
          <button 
            className={currentView === 'lab' ? 'active' : ''}
            onClick={() => setCurrentView('lab')}
          >
            🔬 Lab
          </button>
          <button 
            className={currentView === 'chat' ? 'active' : ''}
            onClick={() => setCurrentView('chat')}
          >
            💬 AI Chat
          </button>
          <button 
            className={currentView === 'settings' ? 'active' : ''}
            onClick={() => setCurrentView('settings')}
          >
            ⚙️ Settings
          </button>
        </div>
        <div className="user-info">
          <span className="tier-badge">{user?.subscription_tier}</span>
          <span>{user?.username}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="lab-content">
        {currentView === 'lab' && (
          <>
            {/* 3D Visualization */}
            <div className="visualization-container">
              <canvas ref={canvasRef} className="molecule-canvas" />
              
              {/* Controls Overlay */}
              <div className="controls-overlay">
                <div className="control-group">
                  <label>Temperature (K)</label>
                  <input 
                    type="range" 
                    min="200" 
                    max="500" 
                    value={temperature}
                    onChange={(e) => setTemperature(Number(e.target.value))}
                    className="glowing-slider"
                  />
                  <span>{temperature.toFixed(2)} K</span>
                </div>
                
                <div className="control-group">
                  <label>Pressure (Pa)</label>
                  <input 
                    type="range" 
                    min="50000" 
                    max="200000" 
                    value={pressure}
                    onChange={(e) => setPressure(Number(e.target.value))}
                    className="glowing-slider"
                  />
                  <span>{pressure.toFixed(0)} Pa</span>
                </div>
                
                <button 
                  className="simulate-button glowing-button"
                  onClick={simulateReaction}
                  disabled={isSimulating}
                >
                  {isSimulating ? '⚡ Simulating...' : '🚀 Simulate Reaction'}
                </button>
              </div>
            </div>

            {/* Chemistry Equipment */}
            <div className="equipment-panel">
              <h3>🔬 Laboratory Equipment</h3>
              <div className="equipment-grid">
                <EquipmentItem name="Beaker" icon="🧪" />
                <EquipmentItem name="Flask" icon="🏺" />
                <EquipmentItem name="Burner" icon="🔥" />
                <EquipmentItem name="Thermometer" icon="🌡️" />
                <EquipmentItem name="pH Meter" icon="📊" />
                <EquipmentItem name="Stirrer" icon="🔄" />
              </div>
            </div>

            {/* Molecule Library */}
            <div className="molecule-library">
              <h3>📚 Molecule Library</h3>
              <button onClick={loadPredefinedMolecules} className="load-button">
                Load Common Molecules
              </button>
              <div className="molecule-list">
                {molecules.map((mol) => (
                  <div 
                    key={mol.id} 
                    className={`molecule-card ${selectedMolecules.includes(mol.id) ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedMolecules(prev =>
                        prev.includes(mol.id)
                          ? prev.filter(id => id !== mol.id)
                          : [...prev, mol.id]
                      );
                    }}
                  >
                    <div className="molecule-formula">{mol.formula}</div>
                    <div className="molecule-name">{mol.name}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {currentView === 'chat' && (
          <div className="chat-container">
            <div className="chat-messages">
              {chatMessages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Ask about chemistry reactions, mechanisms, compounds..."
                className="glowing-input"
              />
              <button onClick={sendChatMessage} className="send-button">
                Send ✉️
              </button>
            </div>
          </div>
        )}

        {currentView === 'settings' && (
          <SettingsPanel user={user} token={token} />
        )}
      </div>
    </div>
  );
};

// ============ SUB-COMPONENTS ============

const LoginScreen: React.FC<{
  onLogin: (email: string, password: string) => void;
  onRegister: (email: string, password: string, username: string) => void;
}> = ({ onLogin, onRegister }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');

  return (
    <div className="login-screen">
      <div className="login-card glowing-card">
        <h1>🧪 Interactive Chemistry Lab</h1>
        <p>Explore chemical reactions with AI-powered simulations</p>
        
        <div className="login-form">
          {isRegister && (
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="glowing-input"
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="glowing-input"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="glowing-input"
          />
          
          <button
            onClick={() => isRegister 
              ? onRegister(email, password, username)
              : onLogin(email, password)
            }
            className="glowing-button"
          >
            {isRegister ? 'Register' : 'Login'}
          </button>
          
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="toggle-button"
          >
            {isRegister ? 'Have an account? Login' : 'Need an account? Register'}
          </button>
        </div>
      </div>
    </div>
  );
};

const EquipmentItem: React.FC<{ name: string; icon: string }> = ({ name, icon }) => (
  <div className="equipment-item glowing-card">
    <div className="equipment-icon">{icon}</div>
    <div className="equipment-name">{name}</div>
  </div>
);

const SettingsPanel: React.FC<{ user: any; token: string }> = ({ user, token }) => {
  const [subscription, setSubscription] = useState(user?.subscription_tier);

  const upgradeSubscription = async (tier: string) => {
    try {
      await axios.post(
        `${API_BASE_URL}/subscription/upgrade`,
        {
          tier,
          payment_method: 'card',
          amount: tier === 'basic' ? 9.99 : tier === 'pro' ? 29.99 : 99.99
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setSubscription(tier);
      alert(`Upgraded to ${tier} plan!`);
    } catch (error) {
      console.error('Upgrade error:', error);
    }
  };

  return (
    <div className="settings-panel">
      <h2>⚙️ Settings</h2>
      
      <div className="subscription-section">
        <h3>💎 Subscription Plans</h3>
        <div className="plans-grid">
          <SubscriptionPlan
            name="Free"
            price="$0/month"
            features={[
              '10 simulations/day',
              'Basic AI model',
              '5 molecules stored',
              '3D visualization'
            ]}
            current={subscription === 'free'}
            onUpgrade={() => upgradeSubscription('free')}
          />
          <SubscriptionPlan
            name="Basic"
            price="$9.99/month"
            features={[
              '100 simulations/day',
              'Claude 3 Haiku',
              '50 molecules stored',
              'Advanced parameters',
              'API access'
            ]}
            current={subscription === 'basic'}
            onUpgrade={() => upgradeSubscription('basic')}
          />
          <SubscriptionPlan
            name="Pro"
            price="$29.99/month"
            features={[
              'Unlimited simulations',
              'Claude 3 Sonnet & GPT-4',
              '500 molecules',
              'Custom molecules',
              'Export data',
              'Priority support'
            ]}
            current={subscription === 'pro'}
            onUpgrade={() => upgradeSubscription('pro')}
            featured
          />
          <SubscriptionPlan
            name="Enterprise"
            price="$99.99/month"
            features={[
              'Everything in Pro',
              'All AI models',
              'Unlimited storage',
              'White label',
              'Dedicated support',
              'Custom integrations'
            ]}
            current={subscription === 'enterprise'}
            onUpgrade={() => upgradeSubscription('enterprise')}
          />
        </div>
      </div>
    </div>
  );
};

const SubscriptionPlan: React.FC<{
  name: string;
  price: string;
  features: string[];
  current: boolean;
  onUpgrade: () => void;
  featured?: boolean;
}> = ({ name, price, features, current, onUpgrade, featured }) => (
  <div className={`plan-card ${featured ? 'featured' : ''} ${current ? 'current' : ''}`}>
    {featured && <div className="featured-badge">⭐ Most Popular</div>}
    <h4>{name}</h4>
    <div className="price">{price}</div>
    <ul className="features-list">
      {features.map((feature, index) => (
        <li key={index}>✓ {feature}</li>
      ))}
    </ul>
    <button
      onClick={onUpgrade}
      disabled={current}
      className={current ? 'current-plan-button' : 'upgrade-button'}
    >
      {current ? 'Current Plan' : 'Upgrade'}
    </button>
  </div>
);

export default ChemistryLab;
