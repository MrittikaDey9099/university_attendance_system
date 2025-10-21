// Attendance-specific JavaScript functionality

class AttendanceManager {
    constructor() {
        this.currentDate = new Date().toISOString().split('T')[0];
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Mark attendance buttons
        document.querySelectorAll('.mark-attendance').forEach(button => {
            button.addEventListener('click', (e) => this.markAttendance(e));
        });

        // Bulk attendance actions
        const bulkAction = document.getElementById('bulk-action');
        if (bulkAction) {
            bulkAction.addEventListener('change', (e) => this.handleBulkAction(e));
        }

        // Date picker
        const datePicker = document.getElementById('attendance-date');
        if (datePicker) {
            datePicker.value = this.currentDate;
            datePicker.addEventListener('change', (e) => this.filterByDate(e));
        }
    }

    markAttendance(event) {
        const button = event.target;
        const studentId = button.dataset.studentId;
        const courseId = button.dataset.courseId;
        const status = button.dataset.status;

        // Show loading state
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading"></span>';
        button.disabled = true;

        // Simulate API call
        setTimeout(() => {
            // This would be an actual AJAX call to your Django backend
            this.submitAttendance(studentId, courseId, status)
                .then(response => {
                    button.innerHTML = '✓';
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-success');
                    this.showNotification('Attendance marked successfully!', 'success');
                })
                .catch(error => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    this.showNotification('Error marking attendance!', 'danger');
                });
        }, 1000);
    }

    async submitAttendance(studentId, courseId, status) {
        // This would be your actual API endpoint
        const response = await fetch('/api/mark-attendance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                student_id: studentId,
                course_id: courseId,
                status: status,
                date: this.currentDate
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response.json();
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    filterByDate(event) {
        this.currentDate = event.target.value;
        // Reload or filter attendance records
        window.location.href = `?date=${this.currentDate}`;
    }

    showNotification(message, type) {
        // Use the existing notification function
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        }
    }

    handleBulkAction(event) {
        const action = event.target.value;
        const selectedStudents = document.querySelectorAll('.student-checkbox:checked');
        
        if (selectedStudents.length === 0) {
            this.showNotification('Please select at least one student', 'warning');
            return;
        }

        if (action === 'mark-present') {
            this.bulkMarkAttendance(selectedStudents, 'P');
        } else if (action === 'mark-absent') {
            this.bulkMarkAttendance(selectedStudents, 'A');
        }
    }

    bulkMarkAttendance(students, status) {
        students.forEach(checkbox => {
            const studentId = checkbox.value;
            // Mark attendance for each student
            console.log(`Marking ${studentId} as ${status}`);
        });
        
        this.showNotification(`Attendance marked for ${students.length} students`, 'success');
    }
}

// Initialize attendance manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.attendanceManager = new AttendanceManager();
    
    // Initialize table search if needed
    const attendanceTable = document.getElementById('attendanceTable');
    if (attendanceTable) {
        filterTable('attendanceTable', 'searchAttendance');
    }
});