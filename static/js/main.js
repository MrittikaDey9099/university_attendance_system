// Main JavaScript for University Attendance System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // Real-time clock
    function updateClock() {
        const now = new Date();
        const clockElement = document.getElementById('real-time-clock');
        if (clockElement) {
            clockElement.textContent = now.toLocaleString();
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Attendance chart initialization
    initializeAttendanceCharts();

    // Auto-refresh attendance data every 30 seconds
    setInterval(refreshAttendanceData, 30000);
});

// Initialize attendance charts
function initializeAttendanceCharts() {
    const ctx = document.getElementById('attendanceChart');
    if (ctx) {
        // This would be populated with actual data from the backend
        const attendanceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Late'],
                datasets: [{
                    data: [75, 15, 10],
                    backgroundColor: [
                        '#27ae60',
                        '#e74c3c',
                        '#f39c12'
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
                    }
                }
            }
        });
    }

    // Monthly attendance trend chart
    const trendCtx = document.getElementById('attendanceTrendChart');
    if (trendCtx) {
        const trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Attendance %',
                    data: [85, 78, 92, 88, 95, 90],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 50,
                        max: 100
                    }
                }
            }
        });
    }
}

// Refresh attendance data
function refreshAttendanceData() {
    // This would make an AJAX call to refresh data
    console.log('Refreshing attendance data...');
}

// QR Code Scanner functionality
function initializeQRScanner() {
    const scannerSection = document.getElementById('qr-scanner');
    if (scannerSection) {
        // This would integrate with a QR scanner library
        console.log('QR Scanner initialized');
    }
}

// Export attendance data
function exportAttendanceData(format = 'csv') {
    // This would handle data export functionality
    console.log(`Exporting data in ${format} format`);
    
    // Show success message
    showNotification('Data exported successfully!', 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container.mt-4').prepend(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Search functionality
function filterTable(tableId, searchId) {
    const search = document.getElementById(searchId);
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName('tr');
    
    search.addEventListener('keyup', function() {
        const filter = search.value.toLowerCase();
        for (let i = 1; i < tr.length; i++) {
            const td = tr[i].getElementsByTagName('td');
            let found = false;
            for (let j = 0; j < td.length; j++) {
                if (td[j].textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            tr[i].style.display = found ? '' : 'none';
        }
    });
}

// Initialize when document is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAttendanceCharts);
} else {
    initializeAttendanceCharts();
}