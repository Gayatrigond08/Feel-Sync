document.addEventListener('DOMContentLoaded', function () {
    const user = JSON.parse(localStorage.getItem('feelsync_user'));
    if (!user) {
        window.location.href = '/';
        return;
    }

    // Logout functionality
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('feelsync_user');
        window.location.href = '/';
    });

    // Fetch and render data
    initDashboard();
});

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

    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

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
