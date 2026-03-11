document.addEventListener('DOMContentLoaded', function () {
    const user = JSON.parse(localStorage.getItem('feelsync_user'));
    if (!user) {
        window.location.href = '/';
        return;
    }

    // Logout functionality
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('feelsync_user');
        localStorage.removeItem('feelsync_token');
        window.location.href = '/';
    });

    // Fetch and render data
    initDashboard();

    // Theme preview on change
    document.getElementById('pref-theme').addEventListener('change', (e) => {
        applyTheme(e.target.value);
    });
});

function applyTheme(theme) {
    document.body.classList.remove('theme-morning', 'theme-afternoon', 'theme-evening', 'theme-night', 'theme-dark', 'theme-pastel', 'theme-light');
    if (theme === 'dark' || theme === 'pastel' || theme === 'light') {
        document.body.classList.add(`theme-${theme}`);
    } else {
        // Fallback for dashboard
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 12) document.body.classList.add('theme-morning');
        else if (hour >= 12 && hour < 17) document.body.classList.add('theme-afternoon');
        else if (hour >= 17 && hour < 21) document.body.classList.add('theme-evening');
        else document.body.classList.add('theme-night');
    }
}

const translations = {
    en: {
        title: "Mood Insights & Analytics",
        subtitle: "Understand your emotional patterns and journey.",
        weekly_trend: "Weekly Mood Trend",
        emotion_dist: "Emotion Distribution",
        mood_ratio: "Mood Ratio (Pos vs Neg)",
        day_trends: "Mood by Day of Week",
        deep_insights: "Deep Intelligence Insights",
        dominant_emotion: "Dominant Emotion",
        positive_days: "Positive Days",
        negative_days: "Negative Days",
        mood_stability: "Mood Stability",
        recent_activity: "Recent Activity",
        acc_prefs: "Account Preferences",
        theme_pref: "Theme Preference",
        lang_pref: "Preferred Language",
        reminder: "Daily Reminder Time",
        enable_notif: "Enable Notifications",
        save: "Save Preferences",
        home: "Home",
        dashboard: "Dashboard",
        ai_support: "AI Support",
        reflections: "Reflections",
        logout: "Logout"
    },
    hi: {
        title: "मनोदशा अंतर्दृष्टि और विश्लेषण",
        subtitle: "अपने भावनात्मक पैटर्न और यात्रा को समझें।",
        weekly_trend: "साप्ताहिक मनोदशा प्रवृत्ति",
        emotion_dist: "भावना वितरण",
        mood_ratio: "मनोदशा अनुपात (सकारात्मक बनाम नकारात्मक)",
        day_trends: "सप्ताह के दिन के अनुसार मनोदशा",
        deep_insights: "गहन खुफिया अंतर्दृष्टि",
        dominant_emotion: "प्रमुख भावना",
        positive_days: "सकारात्मक दिन",
        negative_days: "नकारात्मक दिन",
        mood_stability: "मनोदशा स्थिरता",
        recent_activity: "हाल की गतिविधि",
        acc_prefs: "खाता प्राथमिकताएं",
        theme_pref: "थीम प्राथमिकता",
        lang_pref: "पसंदीदा भाषा",
        reminder: "दैनिक अनुस्मारक समय",
        enable_notif: "सूचनाएं सक्षम करें",
        save: "प्राथमिकताएं सहेजें",
        home: "होम",
        dashboard: "डैशबोर्ड",
        ai_support: "एआई सहायता",
        reflections: "प्रतिबिंब",
        logout: "लॉगआउट"
    },
    es: {
        title: "Análisis de Ánimo",
        subtitle: "Comprende tus patrones emocionales.",
        weekly_trend: "Tendencia Semanal",
        emotion_dist: "Distribución de Emociones",
        mood_ratio: "Ratio de Ánimo",
        day_trends: "Ánimo por Día",
        deep_insights: "Perspectivas Profundas",
        dominant_emotion: "Emoción Dominante",
        positive_days: "Días Positivos",
        negative_days: "Días Negativos",
        mood_stability: "Estabilidad de Ánimo",
        recent_activity: "Actividad Reciente",
        acc_prefs: "Preferencias de Cuenta",
        theme_pref: "Preferencia de Tema",
        lang_pref: "Idioma Preferido",
        reminder: "Hora de Recordatorio",
        enable_notif: "Activar Notificaciones",
        save: "Guardar",
        home: "Inicio",
        dashboard: "Panel",
        ai_support: "Soporte AI",
        reflections: "Reflexiones",
        logout: "Cerrar sesión"
    }
};

function translateApp(lang) {
    const t = translations[lang] || translations.en;
    
    // Header
    const h1 = document.querySelector('header h1');
    if (h1) h1.textContent = t.title;
    const subtitle = document.querySelector('header p');
    if (subtitle) subtitle.textContent = t.subtitle;

    // Charts
    document.querySelectorAll('.chart-container h3').forEach(h3 => {
        if (h3.textContent.includes("Weekly")) h3.textContent = t.weekly_trend;
        if (h3.textContent.includes("Emotion")) h3.textContent = t.emotion_dist;
        if (h3.textContent.includes("Ratio")) h3.textContent = t.mood_ratio;
        if (h3.textContent.includes("Day of Week")) h3.textContent = t.day_trends;
    });

    // Insights & Sections
    const insightsH3 = document.querySelector('.insights-card h3');
    if (insightsH3) insightsH3.textContent = t.deep_insights;
    const activityH3 = document.querySelector('#activity-list').parentElement.querySelector('h3');
    if (activityH3) activityH3.textContent = t.recent_activity;
    const prefsH3 = document.querySelector('#preferences-section h3');
    if (prefsH3) prefsH3.textContent = t.acc_prefs;

    // Labels
    const labels = document.querySelectorAll('.insight-label');
    if (labels[0]) labels[0].textContent = t.dominant_emotion;
    if (labels[1]) labels[1].textContent = t.positive_days;
    if (labels[2]) labels[2].textContent = t.negative_days;
    if (labels[3]) labels[3].textContent = t.mood_stability;

    // Form labels
    const formLabels = document.querySelectorAll('#preferences-form label');
    if (formLabels[0]) formLabels[0].textContent = t.theme_pref;
    if (formLabels[1]) formLabels[1].textContent = t.lang_pref;
    if (formLabels[2]) formLabels[2].textContent = t.reminder;
    if (formLabels[3]) formLabels[3].textContent = t.enable_notif;
    const saveBtn = document.querySelector('#preferences-form button');
    if (saveBtn) saveBtn.textContent = t.save;

    // Nav
    const navLinks = document.querySelectorAll('.nav-link');
    if (navLinks[0]) navLinks[0].textContent = t.home;
    if (navLinks[1]) navLinks[1].textContent = t.dashboard;
    if (navLinks[2]) navLinks[2].textContent = t.ai_support;
    if (navLinks[3]) navLinks[3].textContent = t.reflections;
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.textContent = t.logout;
}

async function initDashboard() {
    try {
        // Fetch Mood Analytics
        const analyticsRes = await fetch('/api/mood-analytics', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}` // Fallback if used
            }
        });
        const analytics = await analyticsRes.json();
        console.log("Analytics data:", analytics);

        // Fetch Pattern Insights
        const insightsRes = await fetch('/api/pattern-insights', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}`
            }
        });
        const insights = await insightsRes.json();
        console.log("Insights data:", insights);

        renderCharts(analytics, insights);
        updateInsights(insights);
        
        // Fetch and display Activity
        fetchActivity();
        
        // Fetch and display Preferences
        fetchPreferences();

    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

async function fetchActivity() {
    try {
        const res = await fetch('/api/activity', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}` }
        });
        const data = await res.json();
        const activityList = document.getElementById('activity-list');
        
        if (data.activities && data.activities.length > 0) {
            activityList.innerHTML = data.activities.map(act => {
                let icon = 'fa-info-circle';
                let text = act.activity_type.replace('_', ' ');
                
                if (act.activity_type === 'login') icon = 'fa-sign-in-alt';
                if (act.activity_type === 'mood_logged') icon = 'fa-smile';
                if (act.activity_type === 'ai_chat') icon = 'fa-robot';
                if (act.activity_type === 'reflection_logged') icon = 'fa-journal-whills';
                
                return `
                    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <i class="fas ${icon}" style="color: #5aa773; width: 20px;"></i>
                        <div style="flex: 1;">
                            <span style="text-transform: capitalize; font-weight: 600;">${text}</span>
                            <div style="font-size: 0.8rem; opacity: 0.6;">${act.timestamp}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (err) {
        console.error("Activity fetch error:", err);
    }
}

async function fetchPreferences() {
    try {
        const res = await fetch('/api/preferences', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}` }
        });
        const data = await res.json();
        
        if (data) {
            document.getElementById('pref-theme').value = data.theme || 'light';
            document.getElementById('pref-lang').value = data.language || 'en';
            document.getElementById('pref-notif').checked = data.notification_enabled;
            if (data.reminder_time) {
                // Remove seconds for time input compatibility
                document.getElementById('pref-reminder').value = data.reminder_time.substring(0, 5);
            }
            if (data.theme) applyTheme(data.theme);
            if (data.language) translateApp(data.language);
        }
    } catch (err) {
        console.error("Preferences fetch error:", err);
    }
}

document.getElementById('preferences-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.textContent = 'Saving...';
    
    const prefs = {
        theme: document.getElementById('pref-theme').value,
        language: document.getElementById('pref-lang').value,
        notification_enabled: document.getElementById('pref-notif').checked,
        reminder_time: document.getElementById('pref-reminder').value
    };
    
    try {
        const res = await fetch('/api/preferences', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('feelsync_token')}`
            },
            body: JSON.stringify(prefs)
        });
        
        if (res.ok) {
            alert('Preferences saved successfully! ✨');
            translateApp(prefs.language);
            applyTheme(prefs.theme);
        } else {
            alert('Failed to save preferences.');
        }
    } catch (err) {
        console.error("Save preferences error:", err);
    } finally {
        btn.textContent = 'Save Preferences';
    }
});

function renderCharts(analytics, insights) {
    // 1. Weekly Trend Chart
    const trendCtx = document.getElementById('weeklyTrendChart').getContext('2d');
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: analytics.weekly_trend.map(d => d.date),
            datasets: [{
                label: 'Average Mood',
                data: analytics.weekly_trend.map(d => d.avg_score),
                borderColor: '#5aa773',
                backgroundColor: 'rgba(90, 167, 115, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { min: 1, max: 5 } }
        }
    });

    // 2. Emotion Distribution Chart
    const distCtx = document.getElementById('emotionDistChart').getContext('2d');
    const moodLabels = { 1: 'Sad', 2: 'Down', 3: 'Neutral', 4: 'Good', 5: 'Happy' };
    new Chart(distCtx, {
        type: 'pie',
        data: {
            labels: analytics.emotion_distribution.map(d => moodLabels[d.mood_score]),
            datasets: [{
                data: analytics.emotion_distribution.map(d => d.count),
                backgroundColor: ['#ff6b6b', '#ffd93d', '#6bcbff', '#4ecdc4', '#5aa773']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // 3. Mood Ratio Chart
    const ratioCtx = document.getElementById('moodRatioChart').getContext('2d');
    new Chart(ratioCtx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [analytics.ratio.positive, analytics.ratio.negative, analytics.ratio.neutral],
                backgroundColor: ['#5aa773', '#ff6b6b', '#6bcbff']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // 4. Day of Week Trends Chart
    const dayCtx = document.getElementById('dayTrendsChart').getContext('2d');
    new Chart(dayCtx, {
        type: 'bar',
        data: {
            labels: insights.day_trends.map(d => d.day),
            datasets: [{
                label: 'Avg Mood by Day',
                data: insights.day_trends.map(d => d.avg_score),
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { min: 1, max: 5 } }
        }
    });
}

function updateInsights(insights) {
    document.getElementById('common-emotion').textContent = insights.common_emotion;
    document.getElementById('pos-percentage').textContent = insights.pos_percentage + '%';
    document.getElementById('neg-percentage').textContent = insights.neg_percentage + '%';

    const stability = insights.pos_percentage > 70 ? 'High' : insights.pos_percentage > 40 ? 'Moderate' : 'Volatile';
    document.getElementById('mood-stability').textContent = stability;
}
