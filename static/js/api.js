// API Service for University Attendance System
class AttendanceAPI {
    constructor() {
        this.baseURL = '/api';
        this.csrfToken = this.getCSRFToken();
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            credentials: 'include',
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Dashboard methods
    async getDashboard() {
        return await this.request('/dashboard/');
    }

    // Attendance methods
    async getAttendance(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/attendance/?${queryString}`);
    }

    async markAttendance(attendanceData) {
        return await this.request('/attendance/', {
            method: 'POST',
            body: JSON.stringify(attendanceData)
        });
    }

    async bulkMarkAttendance(attendances) {
        return await this.request('/attendance/bulk_create/', {
            method: 'POST',
            body: JSON.stringify({ attendances })
        });
    }

    async getAttendanceSummary() {
        return await this.request('/attendance/summary/');
    }

    async getCourseReport(courseId) {
        return await this.request(`/attendance/course_report/?course_id=${courseId}`);
    }

    // Student methods
    async getStudents(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/students/?${queryString}`);
    }

    async getStudentAttendance(studentId, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/students/${studentId}/attendance/?${queryString}`);
    }

    // Course methods
    async getCourses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/courses/?${queryString}`);
    }

    // Class Schedule methods
    async getTodayClasses() {
        return await this.request('/class-schedules/today_classes/');
    }

    async getClassSchedules(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/class-schedules/?${queryString}`);
    }
}

// Initialize API service
window.attendanceAPI = new AttendanceAPI();