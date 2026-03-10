// Feel Sync Web Application - Frontend JavaScript
class FeelSyncApp {
    constructor() {
        this.currentUser = null;
        this.moodData = [];
        this.chart = null;
        this.audio = null;
        this.breathInterval = null;
        this.gameInterval = null;
        this.score = 0;
        this.recentNuggets = []; // To avoid repeats
        this.lastNuggetType = null; // To mix up types
        this.chatHistory = []; // Session chat history for context
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeMoodChart();
        this.loadUserData();
        this.setupRouting();
        this.updateThemeByTime();
        this.loadResources();
        this.createHeroParticles();
        this.updateHomeWhisper();
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('login-btn').addEventListener('click', () => this.showModal('login-modal'));
        document.getElementById('get-started-btn').addEventListener('click', () => this.showModal('register-modal'));

        // Modal controls
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.hideModal('login-modal');
            this.showModal('register-modal');
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.hideModal('register-modal');
            this.showModal('login-modal');
        });

        // Forms
        document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form').addEventListener('submit', (e) => this.handleRegister(e));

        // Mood tracking
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectMood(btn));
        });
        document.getElementById('save-mood').addEventListener('click', () => this.saveMoodEntry());

        // Home interaction
        const homeWhisper = document.getElementById('home-whisper-card');
        if (homeWhisper) {
            homeWhisper.addEventListener('click', () => this.updateHomeWhisper());
        }

        // Chat
        const aiSendBtn = document.getElementById('ai-send-btn');
        const aiChatInput = document.getElementById('ai-chat-input');
        if (aiSendBtn) aiSendBtn.addEventListener('click', () => this.handleAiChat());
        if (aiChatInput) aiChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleAiChat();
        });

        // Mobile Menu
        const mobileMenu = document.getElementById('mobile-menu');
        const navMenu = document.querySelector('.nav-menu');
        if (mobileMenu) {
            mobileMenu.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        // Wellness Hub Navigation
        document.querySelectorAll('.hub-nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.target;
                document.querySelectorAll('.hub-nav-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.hub-section').forEach(s => s.classList.remove('active'));
                btn.classList.add('active');
                if (document.getElementById(target)) {
                    document.getElementById(target).classList.add('active');
                }

                // Switch logic
                if (target === 'game-app') {
                    this.startZenGame();
                } else {
                    this.stopZenGame();
                }

                if (target === 'sounds-app') {
                    this.stopAmbientSound(); // Reset when entering sound tab
                }

                // Always stop breathing when switching away or back
                if (target !== 'breathing-app') {
                    this.stopBreathingExercise();
                }
            });
        });

        const startBreathBtn = document.getElementById('start-breathing');
        if (startBreathBtn) startBreathBtn.addEventListener('click', () => this.toggleBreathingExercise());

        document.querySelectorAll('.audio-btn').forEach(btn => {
            btn.addEventListener('click', () => this.toggleAmbientSound(btn.dataset.sound, btn));
        });

        const stopAudioHub = document.getElementById('stop-audio-hub');
        if (stopAudioHub) {
            stopAudioHub.addEventListener('click', () => this.stopAmbientSound());
        }

        // Close listeners for separate modals
        const closeGame = document.getElementById('close-game-modal');
        if (closeGame) closeGame.onclick = () => {
            this.hideModal('game-modal');
            this.stopZenGame();
        };

        const closeEmpower = document.getElementById('close-empower-modal');
        if (closeEmpower) closeEmpower.onclick = () => {
            this.hideModal('empower-modal');
        };

        const nextNugget = document.getElementById('next-nugget');
        if (nextNugget) nextNugget.onclick = () => this.generateNewNugget();

        // Creative Journal
        const newPromptBtn = document.getElementById('new-prompt');
        if (newPromptBtn) newPromptBtn.addEventListener('click', () => this.generateNewPrompt());

        const saveCreativeBtn = document.getElementById('save-creative');
        if (saveCreativeBtn) saveCreativeBtn.addEventListener('click', () => this.saveCreativeEntry());
        document.querySelectorAll('.btn-tag').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.classList.toggle('selected');
            });
        });

        // New Routing logic for section-based nav
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const targetId = link.getAttribute('href').substring(1);
                if (document.getElementById(targetId)) {
                    e.preventDefault();
                    this.navigateTo(targetId);
                }
            });
        });

        // Handle page reload with hash
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash) this.navigateTo(hash, false);
        });

        // Edit Journal Form
        const editJournalForm = document.getElementById('edit-journal-form');
        if (editJournalForm) editJournalForm.addEventListener('submit', (e) => this.handleUpdateJournal(e));
        document.querySelectorAll('.edit-mood-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.edit-mood-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.editSelectedMood = btn.dataset.mood;
            });
        });
    }

    navigateTo(sectionId, updateHash = true) {
        // Protected sections: everything except 'home'
        const protectedSections = ['mood-tracker', 'journal', 'dashboard', 'chatbot', 'daily-reflection', 'resources'];
        if (protectedSections.includes(sectionId) && !this.currentUser) {
            this.showNotification('Please login to access this feature', 'info');
            this.showModal('login-modal');
            return;
        }

        const targetSection = document.getElementById(sectionId);
        if (!targetSection) return;

        // Update Nav Active State
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add('active');
            }
        });

        // Update Section Visibility with Transition
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });

        targetSection.style.display = 'flex'; // Ensure it's ready to show
        setTimeout(() => {
            targetSection.classList.add('active');
        }, 50);

        if (updateHash) {
            window.history.pushState(null, null, `#${sectionId}`);
        }

        // Initialize Section Logic
        if (sectionId === 'dashboard') this.initDashboard();
        if (sectionId === 'chatbot') this.initChatbot();
        if (sectionId === 'daily-reflection') this.initReflections();

        // Particle Container Visibility (Only Home)
        const particleContainer = document.getElementById('particle-container');
        if (particleContainer) {
            particleContainer.style.display = (sectionId === 'home') ? 'block' : 'none';
        }

        // Close mobile menu if open
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) navMenu.classList.remove('active');
    }

    setupRouting() {
        const hash = window.location.hash.substring(1) || 'home';
        this.navigateTo(hash, false);
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'block';
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'none';
    }

    async handleLogin(e) {
        e.preventDefault();
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        if (!emailInput || !passwordInput) return;

        const email = emailInput.value;
        const password = passwordInput.value;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                // Save to localStorage
                localStorage.setItem('feelsync_user', JSON.stringify(this.currentUser));
                localStorage.setItem('feelsync_token', data.token);
                this.hideModal('login-modal');
                this.updateUIForLoggedInUser();
                this.loadUserMoodData();
                this.showNotification(`Welcome back, ${data.user.username}! ✨`, 'success');
                // Let them stay on home to see the new dashboard
                if (window.location.hash !== '#home' && window.location.hash) {
                    this.navigateTo('mood-tracker');
                }
            } else {
                this.showNotification(data.message || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showNotification('Connection error. Please try again.', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('register-modal');
                this.showNotification('Account created successfully! Please login.', 'success');
                this.showModal('login-modal');
            } else {
                this.showNotification(data.message || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showNotification('Connection error. Please try again.', 'error');
        }
    }

    selectMood(selectedBtn) {
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        selectedBtn.classList.add('selected');
        this.selectedMood = selectedBtn.dataset.mood;
    }

    async saveMoodEntry() {
        if (!this.selectedMood) {
            this.showNotification('Please select a mood first', 'error');
            return;
        }

        const notes = document.getElementById('mood-notes').value;

        try {
            const response = await fetch('/api/mood', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mood_score: parseInt(this.selectedMood),
                    notes: notes,
                    user_id: this.currentUser?.id || 1 // Default user for demo
                }),
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Mood entry saved!', 'success');
                document.getElementById('mood-notes').value = '';
                document.querySelectorAll('.mood-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });
                this.selectedMood = null;
                this.loadUserMoodData();
                this.provideRecommendation(parseInt(this.selectedMood));
            } else {
                this.showNotification(data.message || 'Failed to save mood', 'error');
            }
        } catch (error) {
            console.error('Mood save error:', error);
            this.showNotification('Connection error. Please try again.', 'error');
        }
    }

    // --- AI Chatbot Integration ---
    async initChatbot() {
        const sendBtn = document.getElementById('ai-send-btn');
        const inputField = document.getElementById('ai-chat-input');

        // Remove existing listener if any to prevent duplicates
        const newSendBtn = sendBtn.cloneNode(true);
        sendBtn.parentNode.replaceChild(newSendBtn, sendBtn);

        newSendBtn.addEventListener('click', () => this.handleAiChat());
        inputField.onkeypress = (e) => {
            if (e.key === 'Enter') this.handleAiChat();
        };
    }

    async handleAiChat() {
        const chatInput = document.getElementById('ai-chat-input');
        const chatMessages = document.getElementById('ai-chat-messages');
        const message = chatInput.value.trim();

        if (!message) return;

        // User message
        this.appendChatMessage(message, 'user');
        chatInput.value = '';

        // Typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message ai-typing';
        typingDiv.innerHTML = `<div class="message-content">Thinking...</div>`;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Update local history
        this.chatHistory.push({ role: 'user', content: message });

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}`
                },
                body: JSON.stringify({
                    message,
                    history: this.chatHistory.slice(-10) // Send context
                })
            });
            const data = await response.json();

            typingDiv.remove();
            const botMessage = data.response;
            this.chatHistory.push({ role: 'assistant', content: botMessage });
            this.appendChatMessage(botMessage.replace(/\n/g, '<br>'), 'bot');
        } catch (error) {
            typingDiv.remove();
            console.error('Chat error:', error);
            this.showNotification('AI service unavailable', 'error');
        }
    }

    appendChatMessage(message, sender) {
        const chatMessages = document.getElementById('ai-chat-messages');
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;
        div.innerHTML = `<div class="message-content">${message}</div>`;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- Dashboard Integration ---
    async initDashboard() {
        try {
            const analyticsRes = await fetch('/api/mood-analytics', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}` }
            });
            const insightsRes = await fetch('/api/pattern-insights', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}` }
            });

            const analytics = await analyticsRes.json();
            const insights = await insightsRes.json();

            this.renderDashboardCharts(analytics, insights);
            this.updateDashboardInsights(insights);
        } catch (error) {
            console.error('Dashboard error:', error);
        }
    }

    renderDashboardCharts(analytics, insights) {
        // Line Chart
        const trendCtx = document.getElementById('weeklyTrendChart').getContext('2d');
        if (this.trendChart) this.trendChart.destroy();
        this.trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: analytics.weekly_trend.map(d => d.date),
                datasets: [{
                    label: 'Mood',
                    data: analytics.weekly_trend.map(d => d.avg_score),
                    borderColor: '#5aa773',
                    fill: false,
                    tension: 0.4
                }]
            }
        });

        // Emotion Pie
        const distCtx = document.getElementById('emotionDistChart').getContext('2d');
        const moodLabels = { 1: 'Sad', 2: 'Down', 3: 'Neutral', 4: 'Good', 5: 'Happy' };
        if (this.distChart) this.distChart.destroy();
        this.distChart = new Chart(distCtx, {
            type: 'pie',
            data: {
                labels: analytics.emotion_distribution.map(d => moodLabels[d.mood_score]),
                datasets: [{
                    data: analytics.emotion_distribution.map(d => d.count),
                    backgroundColor: ['#ff6b6b', '#ffd93d', '#6bcbff', '#4ecdc4', '#5aa773']
                }]
            }
        });

        // Ratio Doughnut
        const ratioCtx = document.getElementById('moodRatioChart').getContext('2d');
        if (this.ratioChart) this.ratioChart.destroy();
        this.ratioChart = new Chart(ratioCtx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [analytics.ratio.positive, analytics.ratio.negative, analytics.ratio.neutral],
                    backgroundColor: ['#5aa773', '#ff6b6b', '#6bcbff']
                }]
            }
        });

        // Day Bar
        const dayCtx = document.getElementById('dayTrendsChart').getContext('2d');
        if (this.dayChart) this.dayChart.destroy();
        this.dayChart = new Chart(dayCtx, {
            type: 'bar',
            data: {
                labels: insights.day_trends.map(d => d.day),
                datasets: [{
                    label: 'Avg Mood',
                    data: insights.day_trends.map(d => d.avg_score),
                    backgroundColor: '#667eea'
                }]
            }
        });
    }

    updateDashboardInsights(insights) {
        document.getElementById('common-emotion').textContent = insights.common_emotion;
        document.getElementById('pos-percentage').textContent = insights.pos_percentage + '%';
        document.getElementById('neg-percentage').textContent = insights.neg_percentage + '%';
        const stability = insights.pos_percentage > 70 ? 'High' : insights.pos_percentage > 40 ? 'Moderate' : 'Volatile';
        document.getElementById('mood-stability').textContent = stability;
    }

    // --- Reflections Integration ---
    initReflections() {
        const submitBtn = document.getElementById('submit-reflection');
        submitBtn.onclick = () => this.handleReflectionSubmit();
    }

    async handleReflectionSubmit() {
        const smile = document.getElementById('smile').value;
        const challenge = document.getElementById('challenge').value;
        const grateful = document.getElementById('grateful').value;
        const submitBtn = document.getElementById('submit-reflection');

        if (!smile || !challenge || !grateful) {
            this.showNotification('Please fill all fields', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';

        try {
            const response = await fetch('/api/daily-reflection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}`
                },
                body: JSON.stringify({ smile, challenge, grateful })
            });
            const data = await response.json();
            if (response.ok) {
                document.getElementById('reflection-summary').textContent = data.summary;
                document.getElementById('summary-section').style.display = 'block';
                submitBtn.textContent = 'Reflect Again';
                submitBtn.disabled = false;
            }
        } catch (error) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate Smart Summary';
        }
    }

    initializeMoodChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        const ctx = document.getElementById('moodChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Mood Score',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            stepSize: 1,
                            callback: function (value) {
                                const moods = ['', '😢', '😕', '😐', '🙂', '😊'];
                                return moods[value] || value;
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    async loadUserMoodData() {
        try {
            const response = await fetch(`/api/mood/${this.currentUser?.id || 1}`);
            const data = await response.json();

            if (response.ok) {
                this.updateMoodChart(data.mood_entries);
                this.renderJournal(data.mood_entries); // Show journal entries
            }
        } catch (error) {
            console.error('Error loading mood data:', error);
        }
    }

    updateMoodChart(moodEntries) {
        if (!this.chart || !moodEntries) return;
        // Sort briefly for chart (chronological)
        const sortedEntries = [...moodEntries].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        const labels = sortedEntries.map(entry => {
            const date = new Date(entry.timestamp);
            return `${date.getDate()}/${date.getMonth() + 1}`;
        });

        const data = sortedEntries.map(entry => entry.mood_score);

        if (this.chart.data) {
            this.chart.data.labels = labels;
            this.chart.data.datasets[0].data = data;
            this.chart.update();
        }
    }

    renderJournal(moodEntries) {
        const journalContainer = document.getElementById('journal-container');
        if (!journalContainer) return;

        // Sort by newest first for the journal
        const sortedEntries = [...moodEntries].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        if (sortedEntries.length === 0) {
            journalContainer.innerHTML = '<p class="no-data">No journal entries yet. Start by logging your mood above!</p>';
            return;
        }

        const moodEmojis = {
            1: '😢',
            2: '😕',
            3: '😐',
            4: '🙂',
            5: '😊'
        };

        const stickers = ['🍓', '🌸', '✨', '🐾', '🎀', '🎈', '🍀', '🦋'];

        journalContainer.innerHTML = sortedEntries.map((entry, index) => {
            const date = new Date(entry.timestamp);
            const dateStr = date.toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });

            // Pick 2 random stickers
            const s1 = stickers[Math.floor(Math.random() * stickers.length)];
            const s2 = stickers[Math.floor(Math.random() * stickers.length)];
            const cat = Math.random() > 0.5 ? '🐱' : '🐈';

            return `
                <div class="scrapbook-card" data-id="${entry.id}">
                    <div class="sticker sticker-1">${s1}</div>
                    <div class="sticker sticker-2">${s2}</div>
                    <div class="sticker sticker-cat">${cat}</div>
                    
                    <div class="scrapbook-actions">
                        <button title="Edit" onclick="feelSyncApp.openEditModal(${entry.id}, ${entry.mood_score}, \`${entry.notes ? entry.notes.replace(/`/g, '\\`').replace(/\n/g, '\\n') : ''}\`)"><i class="fas fa-edit"></i></button>
                        <button title="Delete" onclick="feelSyncApp.deleteJournalEntry(${entry.id})"><i class="fas fa-trash"></i></button>
                    </div>

                    <div class="scrapbook-date">${dateStr}</div>
                    <div class="scrapbook-mood">
                        <span class="scrapbook-emoji">${moodEmojis[entry.mood_score] || '😐'}</span>
                        <div class="scrapbook-label">${this.getMoodLabel(entry.mood_score)}</div>
                    </div>
                    
                    <div class="scrapbook-content">
                        ${entry.notes ? entry.notes : 'No words today, just vibes...'}
                    </div>
                </div>
            `;
        }).join('');
    }

    async deleteJournalEntry(id) {
        if (!confirm('Are you sure you want to delete this memory? 🌸')) return;

        try {
            const response = await fetch(`/api/mood/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Memory deleted from your journal', 'info');
                this.loadUserMoodData();
            } else {
                this.showNotification('Failed to delete entry', 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showNotification('Connection error', 'error');
        }
    }

    openEditModal(id, mood, notes) {
        const modal = document.getElementById('edit-journal-modal');
        document.getElementById('edit-entry-id').value = id;
        document.getElementById('edit-mood-notes').value = notes;

        // Select the current mood button
        document.querySelectorAll('.edit-mood-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.mood == mood) {
                btn.classList.add('selected');
                this.editSelectedMood = mood;
            }
        });

        modal.style.display = 'block';
    }

    async handleUpdateJournal(e) {
        e.preventDefault();
        const id = document.getElementById('edit-entry-id').value;
        const notes = document.getElementById('edit-mood-notes').value;
        const mood = this.editSelectedMood;

        if (!mood) {
            this.showNotification('Please select a mood', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/mood/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mood_score: parseInt(mood),
                    notes: notes
                })
            });

            if (response.ok) {
                this.showNotification('Journal entry updated! ✨', 'success');
                this.hideModal('edit-journal-modal');
                this.loadUserMoodData();
            } else {
                const data = await response.json();
                this.showNotification(data.message || 'Update failed', 'error');
            }
        } catch (error) {
            console.error('Update error:', error);
            this.showNotification('Connection error', 'error');
        }
    }

    getMoodLabel(score) {
        const labels = {
            1: 'Very Low',
            2: 'Low',
            3: 'Neutral',
            4: 'Good',
            5: 'Great'
        };
        return labels[score] || 'Neutral';
    }

    updateUIForLoggedInUser() {
        if (!this.currentUser) return;
        document.body.classList.add('logged-in');
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.innerHTML = `<i class="fas fa-user-circle"></i> ${this.currentUser.username}`;
        }

        // Add logout listener if needed
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.onclick = () => this.logout();
        }

        this.updateHomePersonalization();
    }

    async loadResources() {
        try {
            const response = await fetch('/api/resources');
            const data = await response.json();

            if (response.ok && data.resources) {
                this.renderResources(data.resources);
            }
        } catch (error) {
            console.error('Error loading resources:', error);
        }
    }

    renderResources(resources) {
        const grid = document.querySelector('.resources-grid');
        if (!grid) return;

        // Group resources by category - mapped to current database categories
        const categories = {
            'meditation': { icon: 'fa-wind', label: 'Breathing' },
            'game': { icon: 'fa-leaf', label: 'Zen Garden' },
            'journal': { icon: 'fa-magic', label: 'Journal' },
            'sounds': { icon: 'fa-music', label: 'Sounds' }
        };

        grid.innerHTML = '';

        resources.forEach(resource => {
            const catInfo = categories[resource.category] || { icon: 'fa-info-circle', label: 'Wellness' };
            const card = document.createElement('div');
            card.className = 'resource-card';
            card.innerHTML = `
                ${this.recommendedId === this.getInternalTab(resource.category, resource.content_url) ? '<div class="recommendation-badge">Recommended</div>' : ''}
                <div class="resource-icon-wrapper">
                    <i class="fas ${catInfo.icon}"></i>
                </div>
                <h3>${resource.title}</h3>
                <p>${resource.description}</p>
                <button class="btn-explore" onclick="window.feelSyncApp.openWellnessHub('${this.getInternalTab(resource.category, resource.content_url)}')">
                    Explore Now <i class="fas fa-arrow-right" style="font-size: 0.9rem; -webkit-text-fill-color: initial; background: none;"></i>
                </button>
            `;
            grid.appendChild(card);
        });
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('feelsync_user');
        document.body.classList.remove('logged-in');

        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.textContent = 'Login';
        }

        this.navigateTo('home');
        this.showNotification('Logged out successfully', 'success');
    }

    loadUserData() {
        // Load user data from localStorage for demo purposes
        const savedUser = localStorage.getItem('feelsync_user');
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.updateUIForLoggedInUser();
            this.loadUserMoodData();
        }
    }

    updateThemeByTime() {
        const hour = new Date().getHours();
        document.body.classList.remove('theme-morning', 'theme-afternoon', 'theme-evening', 'theme-night');

        if (hour >= 5 && hour < 12) document.body.classList.add('theme-morning');
        else if (hour >= 12 && hour < 17) document.body.classList.add('theme-afternoon');
        else if (hour >= 17 && hour < 21) document.body.classList.add('theme-evening');
        else document.body.classList.add('theme-night');
    }

    provideRecommendation(moodScore) {
        let recId = 'breathing-app';
        let message = '';

        if (moodScore <= 2) {
            recId = 'game-app';
            message = "Feeling a bit low? Try popping some bubbles in the Zen Garden!";
        } else if (moodScore === 3) {
            recId = 'sounds-app';
            message = "Neutral vibes? Relax with some beach sounds.";
        } else {
            recId = 'breathing-app';
            message = "Great mood! Keep the peace with a quick breathing session.";
        }

        this.recommendedId = recId;
        this.showNotification(message, 'info');
        this.loadResources(); // Re-render to show badge
    }

    showNotification(message, type = 'success', isCenter = false) {
        const notification = document.createElement('div');
        notification.className = `notification ${type} ${isCenter ? 'center' : ''}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 100);
        const duration = isCenter ? 4000 : 3000;
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    // Wellness Hub Logic - Now separated into modals
    openWellnessHub(tab = 'breathing-app') {
        const modalIdMap = {
            'breathing-app': 'breathing-modal',
            'game-app': 'game-modal',
            'creative-journal': 'journal-modal',
            'empower-app': 'empower-modal'
        };

        const modalId = modalIdMap[tab] || 'breathing-modal';
        this.showModal(modalId);

        // Start specific logic if needed
        if (tab === 'game-app') this.startZenGame();
        if (tab === 'empower-app') this.generateNewNugget();
    }

    // Breathing Logic
    toggleBreathingExercise() {
        const startBtn = document.getElementById('start-breathing');
        if (this.breathInterval) {
            this.stopBreathingExercise();
            startBtn.textContent = 'Start Exercise';
        } else {
            this.startBreathingExercise();
            startBtn.textContent = 'Stop Exercise';
        }
    }

    startBreathingExercise() {
        const circle = document.getElementById('breath-circle');
        const text = document.getElementById('breath-text');
        let phase = 0; // 0: Inhale, 1: Hold, 2: Exhale

        const runPhase = () => {
            if (phase === 0) {
                circle.className = 'breathing-circle inhale';
                text.textContent = 'Inhale...';
                this.breathTimeout = setTimeout(() => { phase = 1; runPhase(); }, 4000);
            } else if (phase === 1) {
                circle.className = 'breathing-circle hold';
                text.textContent = 'Hold...';
                this.breathTimeout = setTimeout(() => { phase = 2; runPhase(); }, 7000);
            } else {
                circle.className = 'breathing-circle exhale';
                text.textContent = 'Exhale...';
                this.breathTimeout = setTimeout(() => { phase = 0; runPhase(); }, 8000);
            }
        };

        runPhase();
        this.breathInterval = true;
    }

    stopBreathingExercise() {
        clearTimeout(this.breathTimeout);
        this.breathInterval = null;
        const circle = document.getElementById('breath-circle');
        const text = document.getElementById('breath-text');
        if (circle) circle.className = 'breathing-circle';
        if (text) text.textContent = 'Get Ready';
        return;
    }

    // Mindful Nuggets Logic
    generateNewNugget() {
        const nuggets = [
            // Consoling Lyrics (Hidden Artist, Song Name Only)
            { type: 'Consoling Lyric 🎵', content: '"I\'m the one I should love in this world. Shining me, precious soul of mine."', meaning: '— Song: Epiphany. Self-love is the ultimate healing.' },
            { type: 'Consoling Lyric 🎵', content: '"Loving myself doesn’t require anyone else’s permission."', meaning: '— Song: Answer: Love Myself. You are enough exactly as you are.' },
            { type: 'Consoling Lyric 🎵', content: '"The morning will come again. No darkness, no season can last forever."', meaning: '— Song: Spring Day. Hard times are always temporary.' },
            { type: 'Consoling Lyric 🎵', content: '"It\'s okay to stop. You don\'t have to run without knowing the reason."', meaning: '— Song: Paradise. Your pace is your own, don\'t rush.' },
            { type: 'Consoling Lyric 🎵', content: '"You worked hard today. You did so well. I\'m proud of you."', meaning: '— Song: Magic Shop. You gave your best today, and that is enough.' },
            { type: 'Consoling Lyric 🎵', content: '"Everything is going to be alright. Look up, we are all under the same sky."', meaning: '— Song: Mikrokosmos. You are connected and never truly alone.' },
            { type: 'Consoling Lyric 🎵', content: '"When you\'re tired, let\'s walk on the flowery path together."', meaning: '— Song: 2! 3!. Better days are blooming for you.' },
            { type: 'Consoling Lyric 🎵', content: '"Who says you’re not perfect? Who says you’re not worth it?"', meaning: '— Song: Who Says. Never let anyone define your value.' },
            { type: 'Consoling Lyric 🎵', content: '"I wish you could love yourself as much as I love you."', meaning: '— Song: Magic Shop. You are precious beyond measure.' },
            { type: 'Consoling Lyric 🎵', content: '"Maybe I can never fly... but I want to stretch out my hand."', meaning: '— Song: Awake. The effort to try is beautiful in itself.' },
            { type: 'Consoling Lyric 🎵', content: '"Yesterday’s me, today’s me, tomorrow’s me... I’m learning how to love myself."', meaning: '— Song: Answer: Love Myself. Healing is a journey, stay patient.' },
            { type: 'Consoling Lyric 🎵', content: '"Life goes on. Like an echo in the forest, the day will return."', meaning: '— Song: Life Goes On. Keep moving forward, one breath at a time.' },
            { type: 'Consoling Lyric 🎵', content: '"It’s alright even if you don’t have a name that everyone knows."', meaning: '— Song: Paradise. You are special just by being you.' },
            { type: 'Consoling Lyric 🎵', content: '"Stop runnin\' for nothin\' my friend. It\'s okay to not have a dream."', meaning: '— Song: Paradise. Peace is found in the present, not just goals.' },
            { type: 'Consoling Lyric 🎵', content: '"The stars are bright because of the darkness."', meaning: '— Song: Mikrokosmos. Your struggles are what make your light shine.' },
            { type: 'Consoling Lyric 🎵', content: '"Don’t be trapped in someone else’s dream."', meaning: '— Song: N.O. Your happiness belongs to you alone.' },
            { type: 'Consoling Lyric 🎵', content: '"If you can\'t fly, then run. If you can\'t run, then walk. Today we will survive."', meaning: '— Song: Not Today. Any progress, no matter how small, is a victory.' },
            { type: 'Consoling Lyric 🎵', content: '"Breathe... it\'s okay to make mistakes."', meaning: '— Song: Breathe. Exhale the pressure, inhale the peace.' },
            { type: 'Consoling Lyric 🎵', content: '"Someone says, "I’m sick of all this." But I hope you don’t let go of yourself."', meaning: '— Song: Zero O’Clock. Hang in there, a new day starts at midnight.' },
            { type: 'Consoling Lyric 🎵', content: '"You can\'t stop me lovin\' myself."', meaning: '— Song: IDOL. Your self-love is an unstoppable force.' },
            { type: 'Consoling Lyric 🎵', content: '"Believe in yourself, even if you’re not perfect. You’re worth it."', meaning: '— Song: 21st Century Girl. You are unique and amazing.' },
            { type: 'Consoling Lyric 🎵', content: '"Where there is hope, there is always hardship. But keep going."', meaning: '— Song: Sea. Persistence is the key to finding your ocean.' },
            { type: 'Consoling Lyric 🎵', content: '"Don\'t be afraid, the future is only a continuation of now."', meaning: '— Song: Tomorrow. Focus on this moment, the rest will follow.' },
            { type: 'Consoling Lyric 🎵', content: '"The dawn before the sun rises is the darkest."', meaning: '— Song: Tomorrow. Light is just around the corner.' },
            { type: 'Consoling Lyric 🎵', content: '"Follow your dream like a breaker. Even if it breaks, don\'t run backward."', meaning: '— Song: Tomorrow. Your efforts are never wasted.' },
            { type: 'Consoling Lyric 🎵', content: '"I believe in myself; my back hurts in order to let my wings sprout."', meaning: '— Song: Interlude: Wings. Your struggles are your wings growing.' },
            { type: 'Consoling Lyric 🎵', content: '"Smile at me, help me, it\'s okay to be shaky sometimes."', meaning: '— Song: Interlude: Wings. It\'s okay to ask for support.' },
            { type: 'Consoling Lyric 🎵', content: '"Everything will be okay. It will pass, it always does."', meaning: '— Song: everythinggoes. Time is a healer.' },
            { type: 'Consoling Lyric 🎵', content: '"A brand new day will come eventually. Just wait for the sun."', meaning: '— Song: A Brand New Day. Morning always returns.' },
            { type: 'Consoling Lyric 🎵', content: '"You are the sunlight that rose again in my life."', meaning: '— Song: Euphoria. You are someone\'s reason to smile.' },
            { type: 'Consoling Lyric 🎵', content: '"It\'s okay to shed a few tears. Just don\'t give up on yourself."', meaning: '— Song: Sea. Crying is a part of healing.' },
            { type: 'Consoling Lyric 🎵', content: '"We were too young to give up. We are still blooming."', meaning: '— Song: Path. Your life is still a beautiful unfolding story.' },

            // Mindful Thoughts & Reflections
            { type: 'Gentle Thought 🌿', content: 'You are enough just as you are. Your value is not tied to your productivity.', meaning: 'Simply being here is an achievement.' },
            { type: 'Mindful Reminder 🌊', content: 'The waves of emotion will come and go. You are the ocean, not the wave.', meaning: 'Stay grounded in your inner vastness.' },
            { type: 'Self-Belief 🌟', content: 'Confidence isn\'t "they will like me." Confidence is "I\'ll be fine if they don\'t."', meaning: 'Your peace depends only on you.' },
            { type: 'Soft Reflection ✨', content: 'Be gentle with yourself. You are doing something you\'ve never done before: living today.', meaning: 'New experiences require patience and kindness.' },
            { type: 'Mindful Reminder 🍃', content: 'Flowers don\'t compete with the flower next to them. They just bloom.', meaning: 'Comparison is the thief of joy. Focus on your own growth.' },

            // More Song Lyrics (Song Name Only)
            { type: 'Consoling Lyric 🎵', content: '"You\'re my best friend for the rest of my life."', meaning: '— Song: Best of Me. You are your own best companion.' },
            { type: 'Consoling Lyric 🎵', content: '"Small things that aren\'t small... you\'re the one that makes me fly."', meaning: '— Song: Boy With Luv. Notice the small joys.' },
            { type: 'Consoling Lyric 🎵', content: '"I\'m becoming a moon that stays by your side throughout the night."', meaning: '— Song: Moon. There is always light in the darkness.' },
            { type: 'Consoling Lyric 🎵', content: '"The world is a little bit blurry, but I can see you clearly."', meaning: '— Song: Inner Child. Listen to the child inside of you.' },
            { type: 'Consoling Lyric 🎵', content: '"We are together, even if we are apart."', meaning: '— Song: For Youth. Connection transcends distance.' },
            { type: 'Consoling Lyric 🎵', content: '"I\'m still here, I\'m still same."', meaning: '— Song: Still With You. Your core remains beautiful and constant.' },
            { type: 'Consoling Lyric 🎵', content: '"Don\'t be afraid to dream again."', meaning: '— Song: Dream. It is never too late to start anew.' },
            { type: 'Consoling Lyric 🎵', content: '"The stars in the sky are not just far away. They are reflected in your eyes."', meaning: '— Song: Mikrokosmos. You carry the universe within you.' },
            { type: 'Consoling Lyric 🎵', content: '"It\'s okay, I\'m here. Just breathe and let it go."', meaning: '— Song: 00:00. Every midnight is a fresh start.' },
            { type: 'Consoling Lyric 🎵', content: '"You are the most beautiful moment in life."', meaning: '— Song: HYYH. Appreciate the beauty of your existence right now.' },
            { type: 'Consoling Lyric 🎵', content: '"Keep walking, don\'t look back. You are doing great."', meaning: '— Song: 2! 3!. Look forward to more good days.' },
            { type: 'Mindful Reflection 🕯️', content: 'Even a small candle can light up the entire room. Your small acts of kindness matter.', meaning: 'You influence the world more than you know.' },
            { type: 'Empowering Thought 💪', content: 'Your strength is not measured by how much you can carry, but by how you choose to carry it.', meaning: 'Mindset is your greatest tool.' },
            { type: 'Soft Reminder 🕊️', content: 'Silence is not empty. It is full of answers if you listen closely.', meaning: 'Take a moment to just be silent today.' },

            // Daily Motivation (Member Quotes essence)
            { type: 'Daily Motivation ☀️', content: '"No matter who you are, where you’re from, your skin color, your gender identity: just speak yourself."', meaning: '— Your voice is unique and deserves to be heard.' },
            { type: 'Daily Motivation ☀️', content: '"If you can\'t fly, then run. Today we will survive."', meaning: '— Survival is the first step to thriving. Keep going.' },
            { type: 'Daily Motivation ☀️', content: '"Your presence can give happiness. I hope you remember that."', meaning: '— You are a gift to the people around you.' },
            { type: 'Daily Motivation ☀️', content: '"Life is a sculpture that you cast as you make mistakes and learn from them."', meaning: '— Mistakes are just the chisel that shapes your character.' },
            { type: 'Daily Motivation ☀️', content: '"I have come to love myself for who I am, for who I was, and for who I hope to become."', meaning: '— Love every version of yourself: past, present, and future.' },
            { type: 'Daily Motivation ☀️', content: '"Don’t be trapped in someone else’s dream."', meaning: '— Your path belongs to you. Define your own success.' },
            { type: 'Daily Motivation ☀️', content: '"Effort makes you. You will regret someday if you don’t do your best now."', meaning: '— Give your heart to what matters. Your future self will thank you.' },
            { type: 'Daily Motivation ☀️', content: '"Go on your path, even if you live for a day."', meaning: '— Live with intention and passion, no matter the time.' },
            { type: 'Daily Motivation ☀️', content: '"Purple is the last color of the rainbow. It means I will trust and love you for a long time."', meaning: '— Real connection is built on lasting trust.' },
            { type: 'Daily Motivation ☀️', content: '"Love myself, love yourself, peace."', meaning: '— The simplest but most powerful mantra for a happy life.' },
            { type: 'Daily Motivation ☀️', content: '"Living without passion is like being dead."', meaning: '— Find what makes your heart beat faster and follow it.' },
            { type: 'Daily Motivation ☀️', content: '"Smooth like butter!"', meaning: '— May your day be easy and your confidence be high.' },
            { type: 'Daily Motivation ☀️', content: '"Even if it\'s a road of thorns, we still run."', meaning: '— Strength is continuing even when the path is difficult.' },
            { type: 'Daily Motivation ☀️', content: '"Teamwork makes the dream work."', meaning: '— You don\'t have to do everything alone. Lean on those who care.' },
            { type: 'Daily Motivation ☀️', content: '"The only time you should ever look back is to see how far you\'ve come."', meaning: '— Progress is the only direction that matters.' },

            // Empowering Wisdom (Keeping a few good ones)
            { type: 'Empowering Word', content: 'Kintsugi (Japanese)', meaning: 'The art of repairing broken pottery with gold. Your scars make you beautiful.' },
            { type: 'Empowering Word', content: 'Sisu (Finnish)', meaning: 'Extraordinary determination. The guts to keep going when it\'s hard.' },
            { type: 'Psychology Fact', content: 'Neuroplasticity means your brain is constantly changing. You can rewire yourself for confidence.', meaning: 'Your past doesn\'t define your potential.' },
            { type: 'Empowering Word', content: 'Ikigai (Japanese)', meaning: 'A "reason for being" – finding what you love and what the world needs.' },
            { type: 'Soft Reminder 🕊️', content: 'You are your own home. Take care of the space you live in.', meaning: 'Self-care is a necessity, not a luxury.' },
            { type: 'Mindful Thought 🌊', content: 'Don\'t let the world make you hard. Don\'t let pain make you hate. Don\'t let the bitterness steal your sweetness.', meaning: 'Protect your inner light.' },
            { type: 'Consoling Lyric 🎵', content: '"If you can\'t fly, then run. If you can\'t run, then walk. If you can\'t walk, then crawl."', meaning: '— Song: Not Today. Just never stop moving toward your healing.' },
            { type: 'Daily Motivation ☀️', content: '"Life is short, but we should live it for a long time."', meaning: '— Quality of life comes from the moments you choose to cherish.' },
            { type: 'Gentle Thought 🌿', content: 'It\'s okay to be a beginner. It\'s okay to not know everything.', meaning: 'Learning is a lifelong and beautiful process.' },
            { type: 'Consoling Lyric 🎵', content: '"The world is a sea. One person gets lost, another person finds the shore."', meaning: '— Song: Sea. You will find your shore eventually.' },
            { type: 'Mindful Reminder 🍃', content: 'You don\'t have to be perfect to be amazing.', meaning: 'Your flaws are part of your unique story.' },
            { type: 'Consoling Lyric 🎵', content: '"Wait a little more, just a few more nights. I’ll go to see you."', meaning: '— Song: Spring Day. The reunion with your happy self is coming.' },
            { type: 'Daily Motivation ☀️', content: '"Always do your best, but don\'t kill yourself trying."', meaning: '— Balance is everything. Be kind to your body and mind.' },
            { type: 'Consoling Lyric 🎵', content: '"Even if you live for a day... go on your path."', meaning: '— Song: No More Dream. Authenticity is everything.' },
            { type: 'Soft Reflection ✨', content: 'Your shadows only exist because there is a light nearby.', meaning: 'Focus on the light, even when the shadow feels large.' },
            { type: 'Consoling Lyric 🎵', content: '"I\'m the one I should love in this world."', meaning: '— Song: Epiphany. Start with yourself, the rest will follow.' }
        ];

        // Shuffled and Type-Mixed Logic
        let availableNuggets = nuggets.filter(n =>
            !this.recentNuggets.includes(n.content) &&
            n.type !== this.lastNuggetType
        );

        // Fallback if we have too few options with different types
        if (availableNuggets.length < 5) {
            availableNuggets = nuggets.filter(n => !this.recentNuggets.includes(n.content));
        }

        if (availableNuggets.length === 0) {
            this.recentNuggets = [];
            availableNuggets = nuggets;
        }

        const nugget = availableNuggets[Math.floor(Math.random() * availableNuggets.length)];

        // Track for mix-up
        this.recentNuggets.push(nugget.content);
        if (this.recentNuggets.length > 30) this.recentNuggets.shift();
        this.lastNuggetType = nugget.type;

        const typeEl = document.getElementById('nugget-type');
        const contentEl = document.getElementById('nugget-content');
        const footerEl = document.getElementById('nugget-footer');

        if (typeEl) typeEl.textContent = nugget.type;
        if (contentEl) {
            contentEl.style.opacity = 0;
            setTimeout(() => {
                contentEl.textContent = nugget.content;
                contentEl.style.opacity = 1;
            }, 200);
        }
        if (footerEl) footerEl.textContent = nugget.meaning;
    }

    // Zen Game Logic
    startZenGame() {
        if (this.gameInterval) return;
        const canvas = document.getElementById('game-canvas');
        this.score = 0;
        document.getElementById('score-val').textContent = '0';

        const affirmations = [
            "It's okay to take a breath—I'm here with you.",
            "You're doing your absolute best, and that is more than enough.",
            "Everything is going to be alright, just take it one bubble at a time.",
            "I'm so proud of how far you've come today.",
            "You deserve this moment of peace and quiet.",
            "Whatever you're feeling right now is valid and it will pass.",
            "You are stronger than you know, and braver than you feel.",
            "Take a moment to be kind to yourself—you deserve it.",
            "Small steps are still progress. You're doing great.",
            "You don't have to carry it all today. Let it go for a moment.",
            "You are not alone in this journey.",
            "I believe in you, and I'm here to support you."
        ];

        this.gameInterval = setInterval(() => {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.left = Math.random() * 80 + 10 + '%';
            bubble.innerHTML = '✨';

            bubble.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                if (bubble.classList.contains('popping')) return;

                bubble.classList.add('popping');
                const text = affirmations[Math.floor(Math.random() * affirmations.length)];

                this.showNotification(text, 'success', true); // Only show Center message

                this.score++;
                document.getElementById('score-val').textContent = this.score;

                setTimeout(() => bubble.remove(), 300);
            });

            canvas.appendChild(bubble);
            setTimeout(() => {
                if (bubble.parentElement) bubble.remove();
            }, 4000);
        }, 1200);
    }

    stopZenGame() {
        clearInterval(this.gameInterval);
        this.gameInterval = null;
        const canvas = document.getElementById('game-canvas');
        if (canvas) canvas.innerHTML = '';
    }

    // Creative Journal Logic
    generateNewPrompt() {
        const prompts = [
            "What's one thing you're proud of yourself for today?",
            "Write about a place where you feel most at peace.",
            "If your current emotion was a color, what would it be and why?",
            "What are three things you're grateful for right now?",
            "Describe a small win you had this week."
        ];
        document.getElementById('daily-prompt').textContent = prompts[Math.floor(Math.random() * prompts.length)];
    }

    async saveCreativeEntry() {
        const notes = document.getElementById('creative-notes').value.trim();
        const tags = Array.from(document.querySelectorAll('.btn-tag.selected')).map(b => b.dataset.emoji).join(' ');

        if (!notes) {
            this.showNotification('Please write something first!', 'error');
            return;
        }

        const fullNotes = `${tags} ${notes}`;
        document.getElementById('mood-notes').value = fullNotes;
        this.selectMood(document.querySelector('.mood-btn[data-mood="3"]'));
        await this.saveMoodEntry();

        document.getElementById('creative-notes').value = '';
        document.querySelectorAll('.btn-tag').forEach(b => b.classList.remove('selected'));
        this.hideModal('journal-modal');

        // Navigate to journal to see the result
        setTimeout(() => {
            this.navigateTo('journal');
            this.showNotification('Entry added to your journal! ✨', 'success');
        }, 500);
    }

    getInternalTab(category, url) {
        if (url && url.startsWith('internal:')) {
            return url.replace('internal:', '');
        }

        const cat = category ? category.toLowerCase().trim() : '';
        const mapping = {
            meditation: 'breathing-app',
            game: 'game-app',
            journal: 'creative-journal',
            sounds: 'sounds-app'
        };
        return mapping[cat] || 'breathing-app';
    }
    // Home Page Personalization
    updateHomePersonalization() {
        const welcomeTitle = document.getElementById('welcome-title');
        const heroSubtitle = document.getElementById('hero-subtitle');

        if (this.currentUser && welcomeTitle) {
            welcomeTitle.textContent = `Hello, ${this.currentUser.username}`;
            heroSubtitle.textContent = "How is your heart feeling today? Let's take a small step together.";
            this.updateHomeWhisper();
        }
    }

    updateHomeWhisper() {
        const whisperText = document.getElementById('home-whisper-text');
        const whisperMeaning = document.getElementById('home-whisper-meaning');

        if (!whisperText) return;

        const whispers = [
            { content: '"I\'m the one I should love in this world."', meaning: '— Song: Epiphany' },
            { content: '"The morning will come again."', meaning: '— Song: Spring Day' },
            { content: '"You worked hard today. You did so well."', meaning: '— Song: Magic Shop' },
            { content: '"It\'s okay to stop. You don\'t have to run."', meaning: '— Song: Paradise' },
            { content: '"Everything is going to be alright."', meaning: '— Song: Mikrokosmos' }
        ];

        const random = whispers[Math.floor(Math.random() * whispers.length)];
        whisperText.textContent = random.content;
        whisperMeaning.textContent = random.meaning;
    }

    createHeroParticles() {
        const container = document.getElementById('particle-container');
        if (!container) return;

        container.innerHTML = ''; // Clear existing - no more floating emojis
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.feelSyncApp = new FeelSyncApp();
});

// Demo data for testing without backend
const demoMoodData = [
    { mood_score: 3, timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 4, timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 2, timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 5, timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 4, timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 3, timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
    { mood_score: 4, timestamp: new Date().toISOString() }
];

// Fallback for demo mode when backend is not available
window.addEventListener('load', () => {
    setTimeout(() => {
        const app = window.feelSyncApp;
        if (app && app.chart && app.chart.data.labels.length === 0) {
            app.updateMoodChart(demoMoodData);
        }
    }, 1000);
});