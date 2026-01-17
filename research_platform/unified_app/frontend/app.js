/**
 * Unified Research & Chemistry Platform - Frontend Application
 */

const API_BASE = 'http://localhost:8080';
let authToken = localStorage.getItem('auth_token');
let currentUser = null;
let scene, camera, renderer, moleculeGroup;

// ============ INITIALIZATION ============

window.addEventListener('DOMContentLoaded', async () => {
    showLoading();
    
    if (authToken) {
        try {
            await loadUserData();
            showApp();
            await loadDashboard();
            init3DScene();
        } catch (error) {
            console.error('Auth error:', error);
            showLogin();
        }
    } else {
        showLogin();
    }
    
    hideLoading();
    
    // Setup form handlers
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Estimate cost on input
    document.getElementById('maxPapers')?.addEventListener('input', estimateResearchCost);
});

function showLoading() {
    document.getElementById('loadingScreen').style.display = 'flex';
}

function hideLoading() {
    setTimeout(() => {
        document.getElementById('loadingScreen').style.display = 'none';
    }, 1000);
}

function showLogin() {
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
}

function showApp() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('app').style.display = 'block';
}

// ============ AUTHENTICATION ============

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await axios.post(`${API_BASE}/auth/login`, {
            email,
            password
        });
        
        authToken = response.data.access_token;
        localStorage.setItem('auth_token', authToken);
        currentUser = response.data.user;
        
        showApp();
        await loadDashboard();
        init3DScene();
    } catch (error) {
        alert('Login failed: ' + (error.response?.data?.detail || error.message));
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const field_of_study = document.getElementById('fieldOfStudy').value;
    
    try {
        const response = await axios.post(`${API_BASE}/auth/register`, {
            username,
            email,
            password,
            field_of_study
        });
        
        authToken = response.data.access_token;
        localStorage.setItem('auth_token', authToken);
        currentUser = response.data.user;
        
        showApp();
        await loadDashboard();
        init3DScene();
    } catch (error) {
        alert('Registration failed: ' + (error.response?.data?.detail || error.message));
    }
}

function showLoginTab(tab) {
    if (tab === 'login') {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('registerForm').style.display = 'none';
    } else {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'block';
    }
    
    document.querySelectorAll('.login-tab').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

function logout() {
    localStorage.removeItem('auth_token');
    authToken = null;
    currentUser = null;
    showLogin();
}

async function loadUserData() {
    const response = await axios.get(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
    });
    currentUser = response.data;
    updateUserDisplay();
}

function updateUserDisplay() {
    document.getElementById('username').textContent = currentUser.username;
    document.getElementById('tierBadge').textContent = currentUser.subscription_tier.toUpperCase();
    document.getElementById('creditBalance').textContent = Math.floor(currentUser.credits_remaining);
}

// ============ NAVIGATION ============

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load tab data
    if (tabName === 'dashboard') loadDashboard();
    else if (tabName === 'credits') loadCreditsTab();
}

// ============ DASHBOARD ============

async function loadDashboard() {
    try {
        const response = await axios.get(`${API_BASE}/dashboard/stats`, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const stats = response.data;
        
        // Update user info
        document.getElementById('welcomeUser').textContent = stats.user.username;
        document.getElementById('fieldOfStudy').textContent = stats.user.field_of_study;
        
        // Update activity stats
        document.getElementById('researchCount').textContent = stats.activity.research_queries;
        document.getElementById('chemSimCount').textContent = stats.activity.chemistry_simulations;
        document.getElementById('aiMsgCount').textContent = stats.activity.ai_messages;
        
        // Update credits
        document.getElementById('dashCredits').textContent = Math.floor(stats.credits.remaining);
        
        // Update recent activity
        const activityHtml = stats.recent_activity.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">${getActivityIcon(activity.action)}</div>
                <div class="activity-details">
                    <div class="activity-name">${formatActivityName(activity.action)}</div>
                    <div class="activity-time">${formatTime(activity.timestamp)}</div>
                </div>
                <div class="activity-credits">-${activity.credits_used}</div>
            </div>
        `).join('');
        document.getElementById('recentActivity').innerHTML = activityHtml || '<p>No recent activity</p>';
        
        // Check OpenRouter status
        await checkOpenRouterStatus();
        
    } catch (error) {
        console.error('Dashboard error:', error);
    }
}

function getActivityIcon(action) {
    const icons = {
        'research_analysis': '🔍',
        'chemistry_simulation': '⚗️',
        'chemistry_chat': '💬'
    };
    return icons[action] || '📊';
}

function formatActivityName(action) {
    return action.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return date.toLocaleDateString();
}

// ============ OPENROUTER ============

async function checkOpenRouterStatus() {
    try {
        const response = await axios.get(`${API_BASE}/openrouter/balance`, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        if (response.data.configured) {
            document.getElementById('orStatusDot').className = 'status-dot status-active';
            document.getElementById('orStatusText').textContent = 'Connected';
            document.getElementById('orBalance').textContent = `Balance: $${response.data.balance.toFixed(2)}`;
        } else {
            document.getElementById('orStatusDot').className = 'status-dot status-inactive';
            document.getElementById('orStatusText').textContent = 'Not Configured';
            document.getElementById('orBalance').textContent = '';
        }
    } catch (error) {
        console.error('OpenRouter check error:', error);
    }
}

function configureOpenRouter() {
    const apiKey = prompt('Enter your OpenRouter API key:');
    if (apiKey) {
        axios.post(`${API_BASE}/openrouter/configure`, apiKey, {
            headers: { 
                Authorization: `Bearer ${authToken}`,
                'Content-Type': 'text/plain'
            }
        }).then(response => {
            if (response.data.success) {
                alert('OpenRouter configured successfully!');
                checkOpenRouterStatus();
            } else {
                alert('Invalid API key');
            }
        }).catch(error => {
            alert('Error: ' + error.message);
        });
    }
}

// ============ RESEARCH ============

function estimateResearchCost() {
    const maxPapers = parseInt(document.getElementById('maxPapers').value) || 0;
    const cost = maxPapers * 10;
    document.getElementById('researchCost').textContent = `${cost} credits`;
}

async function startResearchAnalysis() {
    const topic = document.getElementById('researchTopic').value;
    const question = document.getElementById('researchQuestion').value;
    const maxPapers = parseInt(document.getElementById('maxPapers').value);
    
    if (!topic || !question) {
        alert('Please fill in both topic and question');
        return;
    }
    
    const btn = document.getElementById('researchBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Analyzing...';
    
    const resultsDiv = document.getElementById('researchResults');
    resultsDiv.innerHTML = '<div class="loading-results">Analyzing papers with AI agents...</div>';
    
    try {
        const analysisTypes = [];
        document.querySelectorAll('.checkbox-group input:checked').forEach(cb => {
            analysisTypes.push(cb.value);
        });
        
        const response = await axios.post(`${API_BASE}/research/analyze`, {
            query: topic,
            research_question: question,
            max_papers: maxPapers,
            analysis_types: analysisTypes
        }, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        displayResearchResults(response.data);
        
        // Update credits
        currentUser.credits_remaining = response.data.credits_remaining;
        updateUserDisplay();
        
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${error.response?.data?.detail || error.message}</p>
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.textContent = '🚀 Start Analysis';
    }
}

function displayResearchResults(data) {
    const resultsDiv = document.getElementById('researchResults');
    
    let html = `
        <div class="results-header">
            <h3>Analysis Complete</h3>
            <div class="results-meta">
                <span>📄 ${data.papers_analyzed} papers</span>
                <span>🤖 ${data.agents_used} AI agents</span>
                <span>💰 ${data.credits_used} credits used</span>
            </div>
        </div>
    `;
    
    // Display results for each analysis type
    for (const [type, analysis] of Object.entries(data.results.analysis_results)) {
        const consensus = analysis.consensus;
        
        html += `
            <div class="analysis-section">
                <h4>${type.toUpperCase()} Analysis</h4>
                <div class="consensus-score">
                    <span>Confidence: ${(consensus.confidence_score * 100).toFixed(0)}%</span>
                    <span>Agreement: ${(consensus.agreement_level * 100).toFixed(0)}%</span>
                </div>
                
                <div class="findings">
                    <h5>Key Findings</h5>
                    <ul>
                        ${consensus.key_findings.slice(0, 5).map(f => `<li>${f}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="recommendations">
                    <h5>Recommendations</h5>
                    <ul>
                        ${consensus.recommendations.slice(0, 3).map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    resultsDiv.innerHTML = html;
}

// ============ CHEMISTRY ============

function init3DScene() {
    const canvas = document.getElementById('moleculeCanvas');
    if (!canvas) return;
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    
    camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 0.1, 1000);
    camera.position.z = 10;
    
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    // Create water molecule as default
    moleculeGroup = new THREE.Group();
    createWaterMolecule();
    scene.add(moleculeGroup);
    
    animate3D();
}

function createWaterMolecule() {
    // Oxygen (red)
    const oGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const oMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xff0000,
        emissive: 0xff0000,
        emissiveIntensity: 0.3
    });
    const oxygen = new THREE.Mesh(oGeometry, oMaterial);
    moleculeGroup.add(oxygen);
    
    // Hydrogen atoms (white)
    const hGeometry = new THREE.SphereGeometry(0.3, 32, 32);
    const hMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xffffff,
        emissive: 0xffffff,
        emissiveIntensity: 0.3
    });
    
    const h1 = new THREE.Mesh(hGeometry, hMaterial);
    h1.position.set(-1.5, 1, 0);
    moleculeGroup.add(h1);
    
    const h2 = new THREE.Mesh(hGeometry, hMaterial);
    h2.position.set(1.5, 1, 0);
    moleculeGroup.add(h2);
    
    // Bonds
    const bondGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1.8, 8);
    const bondMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc });
    
    const bond1 = new THREE.Mesh(bondGeometry, bondMaterial);
    bond1.position.set(-0.75, 0.5, 0);
    bond1.rotation.z = Math.PI / 4;
    moleculeGroup.add(bond1);
    
    const bond2 = new THREE.Mesh(bondGeometry, bondMaterial);
    bond2.position.set(0.75, 0.5, 0);
    bond2.rotation.z = -Math.PI / 4;
    moleculeGroup.add(bond2);
}

function animate3D() {
    requestAnimationFrame(animate3D);
    moleculeGroup.rotation.y += 0.01;
    renderer.render(scene, camera);
}

function updateTemperature(value) {
    document.getElementById('tempDisplay').textContent = parseFloat(value).toFixed(2);
}

function updatePressure(value) {
    document.getElementById('pressDisplay').textContent = parseInt(value);
}

async function runChemistrySimulation() {
    const temperature = parseFloat(document.getElementById('temperature').value);
    const pressure = parseInt(document.getElementById('pressure').value);
    
    try {
        const response = await axios.post(`${API_BASE}/chemistry/simulate`, {
            message: "Simulate water molecule",
            reactants: [],
            temperature,
            pressure
        }, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const result = response.data.simulation;
        
        // Display results in chat
        addChatMessage('assistant', `
            ⚡ Simulation Complete!\n\n
            WHAT: ${JSON.stringify(result.analysis.what_happens, null, 2)}\n\n
            WHY: ${result.analysis.why_it_happens.join('\n')}\n\n
            HOW: ${result.analysis.how_it_happens.join('\n')}
        `);
        
        // Update credits
        currentUser.credits_remaining = response.data.credits_remaining;
        updateUserDisplay();
        
    } catch (error) {
        alert('Simulation error: ' + (error.response?.data?.detail || error.message));
    }
}

// ============ CHEMISTRY CHAT ============

async function sendChemistryMessage() {
    const input = document.getElementById('chemChatInput');
    const message = input.value.trim();
    if (!message) return;
    
    addChatMessage('user', message);
    input.value = '';
    
    const useOpenRouter = document.getElementById('useOpenRouter').checked;
    
    try {
        const response = await axios.post(`${API_BASE}/chemistry/chat`, null, {
            params: {
                message,
                use_openrouter: useOpenRouter
            },
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        addChatMessage('assistant', response.data.response);
        
        // Update credits
        currentUser.credits_remaining = response.data.credits_remaining;
        updateUserDisplay();
        
    } catch (error) {
        addChatMessage('assistant', 'Error: ' + (error.response?.data?.detail || error.message));
    }
}

function addChatMessage(role, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${content.replace(/\n/g, '<br>')}</p>
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ============ CREDITS ============

async function loadCreditsTab() {
    try {
        const response = await axios.get(`${API_BASE}/credits/usage`, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const usage = response.data;
        
        // Display usage history
        const historyHtml = usage.usage_history.map(item => `
            <tr>
                <td>${formatTime(item.timestamp)}</td>
                <td>${formatActivityName(item.action)}</td>
                <td>${item.model_used}</td>
                <td class="credit-amount">-${item.credits_used}</td>
            </tr>
        `).join('');
        
        document.getElementById('usageHistory').innerHTML = `
            <table class="usage-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Action</th>
                        <th>Model</th>
                        <th>Credits</th>
                    </tr>
                </thead>
                <tbody>
                    ${historyHtml || '<tr><td colspan="4">No usage history</td></tr>'}
                </tbody>
            </table>
        `;
        
    } catch (error) {
        console.error('Credits tab error:', error);
    }
}

async function upgradePlan(tier) {
    const confirmed = confirm(`Upgrade to ${tier.toUpperCase()} plan?`);
    if (!confirmed) return;
    
    try {
        const response = await axios.post(`${API_BASE}/subscription/upgrade`, {
            tier,
            payment_token: 'demo_token'
        }, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        alert(`Successfully upgraded to ${tier}!\nCredits added: ${response.data.credits_added}`);
        await loadUserData();
        await loadDashboard();
        
    } catch (error) {
        alert('Upgrade error: ' + (error.response?.data?.detail || error.message));
    }
}

async function purchaseCredits(amount) {
    const confirmed = confirm(`Purchase ${amount * 100} credits for $${amount}?`);
    if (!confirmed) return;
    
    try {
        const response = await axios.post(`${API_BASE}/credits/purchase`, amount, {
            headers: { 
                Authorization: `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        alert(`Successfully purchased ${response.data.credits_added} credits!`);
        await loadUserData();
        
    } catch (error) {
        alert('Purchase error: ' + (error.response?.data?.detail || error.message));
    }
}
