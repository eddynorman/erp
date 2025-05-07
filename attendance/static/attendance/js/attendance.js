// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
}

// Attendance Management
class AttendanceManager {
    constructor() {
        this.initializeEventListeners();
        this.startClock();
    }

    initializeEventListeners() {
        // Initialize fingerprint scanner if present
        const fingerprintScanner = document.getElementById('fingerprint-scanner');
        if (fingerprintScanner) {
            fingerprintScanner.addEventListener('click', () => this.handleFingerprintScan());
        }

        // Initialize date pickers if present
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.addEventListener('change', () => this.handleDateChange(input));
        });

        // Initialize export buttons if present
        const exportButtons = document.querySelectorAll('[data-export]');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleExport(e));
        });
    }

    startClock() {
        const clockElement = document.getElementById('current-time');
        if (clockElement) {
            setInterval(() => {
                clockElement.textContent = formatTime(new Date());
            }, 1000);
        }
    }

    async handleFingerprintScan() {
        const statusElement = document.getElementById('fingerprint-status');
        const scannerElement = document.getElementById('fingerprint-scanner');
        const progressBar = document.querySelector('.progress');
        const progressBarInner = document.querySelector('.progress-bar');

        if (!statusElement || !scannerElement) return;

        try {
            // Update UI for scanning
            statusElement.className = 'alert alert-warning';
            statusElement.textContent = 'Scanning...';
            if (progressBar) progressBar.style.display = 'block';
            if (progressBarInner) progressBarInner.style.width = '0%';

            // Simulate scanning progress
            await this.simulateScanningProgress(progressBarInner);

            // Determine the endpoint based on the current page
            const endpoint = this.getCurrentEndpoint();
            const data = this.prepareScanData();

            // Send scan data to server
            const response = await this.sendScanData(endpoint, data);

            // Handle response
            if (response.status === 'success') {
                statusElement.className = 'alert alert-success';
                statusElement.textContent = 'Successfully recorded!';
                setTimeout(() => location.reload(), 1500);
            } else {
                throw new Error(response.message || 'Failed to record attendance');
            }
        } catch (error) {
            statusElement.className = 'alert alert-danger';
            statusElement.textContent = `Error: ${error.message}`;
        } finally {
            if (progressBar) progressBar.style.display = 'none';
        }
    }

    async simulateScanningProgress(progressBar) {
        return new Promise(resolve => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                if (progressBar) progressBar.style.width = `${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(interval);
                    resolve();
                }
            }, 50);
        });
    }

    getCurrentEndpoint() {
        const path = window.location.pathname;
        if (path.includes('check-in-out')) {
            return '/attendance/check-in-out/';
        } else if (path.includes('break')) {
            return '/attendance/break/';
        } else if (path.includes('register-fingerprint')) {
            return '/attendance/register-fingerprint/';
        }
        return null;
    }

    prepareScanData() {
        const data = {
            fingerprint_verified: true,
            location: 'Main Office'
        };

        // Add break type if on break management page
        if (window.location.pathname.includes('break')) {
            data.break_type = document.querySelector('.badge-warning') ? 'end' : 'start';
        }

        return data;
    }

    async sendScanData(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    }

    handleDateChange(input) {
        const form = input.closest('form');
        if (form) {
            form.submit();
        }
    }

    async handleExport(event) {
        const button = event.currentTarget;
        const recordId = button.dataset.export;
        
        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            const response = await fetch(`/attendance/summary/${recordId}/export/`);
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `attendance_record_${recordId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export record. Please try again.');
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-download"></i>';
        }
    }
}

// Report Management
class ReportManager {
    constructor() {
        this.initializeReportFilters();
    }

    initializeReportFilters() {
        const filterForm = document.querySelector('form[method="get"]');
        if (filterForm) {
            const inputs = filterForm.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('change', () => filterForm.submit());
            });
        }
    }

    async showDetails(summaryId) {
        try {
            const response = await fetch(`/attendance/summary/${summaryId}/details/`);
            const data = await response.json();
            
            const modalContent = document.getElementById('detailsContent');
            if (modalContent) {
                modalContent.innerHTML = data.html;
                $('#detailsModal').modal('show');
            }
        } catch (error) {
            console.error('Failed to load details:', error);
            alert('Failed to load attendance details. Please try again.');
        }
    }
}

// Initialize managers when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.attendanceManager = new AttendanceManager();
    window.reportManager = new ReportManager();
}); 