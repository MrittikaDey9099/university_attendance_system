// Real-time Dashboard functionality
class DashboardManager {
    constructor() {
        this.api = window.attendanceAPI;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupRealTimeUpdates();
        this.initializeCharts();
    }

    async loadDashboardData() {
        try {
            const data = await this.api.getDashboard();
            this.updateDashboardUI(data);
            this.updateCharts(data);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateDashboardUI(data) {
        // Update stats cards
        if (data.stats) {
            this.updateStatsCards(data.stats);
        }

        // Update recent activity
        if (data.recent_attendance) {
            this.updateRecentActivity(data.recent_attendance);
        }

        if (data.recent_activity) {
            this.updateRecentActivity(data.recent_activity);
        }

        // Update today's classes
        if (data.today_classes) {
            this.updateTodayClasses(data.today_classes);
        }
    }

    updateStatsCards(stats) {
        const statsContainer = document.getElementById('statsContainer');
        if (!statsContainer) return;

        statsContainer.innerHTML = `
            <div class="col-md-3">
                <div class="card dashboard-card card-primary">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title">Total Classes</h6>
                                <h3 class="text-primary">${stats.total_classes || 0}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-calendar-alt fa-2x text-primary"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card card-success">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title">Present</h6>
                                <h3 class="text-success">${stats.present_classes || stats.today_attendance || 0}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-check-circle fa-2x text-success"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card card-warning">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title">Attendance %</h6>
                                <h3 class="text-warning">${stats.attendance_percentage || 0}%</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-chart-line fa-2x text-warning"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card card-info">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title">Today's Classes</h6>
                                <h3 class="text-info">${stats.today_classes_count || stats.total_courses || 0}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-book fa-2x text-info"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateRecentActivity(activities) {
        const activityContainer = document.getElementById('recentActivity');
        if (!activityContainer) return;

        if (activities.length === 0) {
            activityContainer.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        No recent activity found
                    </td>
                </tr>
            `;
            return;
        }

        activityContainer.innerHTML = activities.map(activity => `
            <tr>
                <td>${activity.date}</td>
                <td>${activity.student_name || 'N/A'}</td>
                <td>${activity.course_name || 'N/A'}</td>
                <td>
                    <span class="badge bg-${this.getStatusColor(activity.status)}">
                        ${this.getStatusText(activity.status)}
                    </span>
                </td>
                <td>${new Date(activity.timestamp).toLocaleTimeString()}</td>
            </tr>
        `).join('');
    }

    updateTodayClasses(classes) {
        const classesContainer = document.getElementById('todayClasses');
        if (!classesContainer) return;

        if (classes.length === 0) {
            classesContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        No classes scheduled for today
                    </div>
                </div>
            `;
            return;
        }

        classesContainer.innerHTML = classes.map(cls => `
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">${cls.course_name}</h6>
                        <p class="card-text mb-1">
                            <i class="fas fa-clock me-2"></i>
                            ${cls.start_time} - ${cls.end_time}
                        </p>
                        <p class="card-text mb-1">
                            <i class="fas fa-user me-2"></i>
                            ${cls.teacher_name}
                        </p>
                        <p class="card-text">
                            <i class="fas fa-door-open me-2"></i>
                            ${cls.room || 'Room TBA'}
                        </p>
                    </div>
                </div>
            </div>
        `).join('');
    }

    getStatusColor(status) {
        const colors = {
            'P': 'success',
            'A': 'danger',
            'L': 'warning',
            'E': 'info'
        };
        return colors[status] || 'secondary';
    }

    getStatusText(status) {
        const texts = {
            'P': 'Present',
            'A': 'Absent',
            'L': 'Late',
            'E': 'Excused'
        };
        return texts[status] || 'Unknown';
    }

    initializeCharts() {
        this.createAttendanceChart();
        this.createTrendChart();
    }

    createAttendanceChart() {
        const ctx = document.getElementById('attendanceChart');
        if (!ctx) return;

        this.charts.attendance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Late', 'Excused'],
                datasets: [{
                    data: [75, 15, 8, 2],
                    backgroundColor: [
                        '#27ae60',
                        '#e74c3c',
                        '#f39c12',
                        '#3498db'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createTrendChart() {
        const ctx = document.getElementById('attendanceTrendChart');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Attendance %',
                    data: [85, 78, 92, 88, 95, 90],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 50,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Attendance: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateCharts(data) {
        // Update charts with real data when available
        // This would be called with actual data from the API
    }

    setupRealTimeUpdates() {
        // Refresh dashboard every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);

        // Listen for custom events (e.g., new attendance marked)
        document.addEventListener('attendanceUpdated', () => {
            this.loadDashboardData();
        });
    }

    showError(message) {
        // Show error notification
        if (typeof showNotification === 'function') {
            showNotification(message, 'danger');
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('statsContainer')) {
        window.dashboardManager = new DashboardManager();
    }
});