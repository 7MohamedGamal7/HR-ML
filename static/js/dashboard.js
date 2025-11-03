// لوحة التحكم الرئيسية - Main Dashboard Script

let currentPage = 'home';
let currentLang = 'ar';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadPage('home');
});

function initializeDashboard() {
    // Sidebar collapse functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebarCollapseTop = document.getElementById('sidebarCollapseTop');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
        });
    }
    
    if (sidebarCollapseTop) {
        sidebarCollapseTop.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
        });
    }
    
    // Navigation click handlers
    const navLinks = document.querySelectorAll('[data-page]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            loadPage(page);
            
            // Update active state
            document.querySelectorAll('.sidebar li').forEach(li => li.classList.remove('active'));
            this.parentElement.classList.add('active');
        });
    });
    
    // Mobile sidebar toggle
    if (window.innerWidth <= 768) {
        sidebar.classList.add('collapsed');
        content.classList.add('expanded');
    }
}

function loadPage(pageName) {
    currentPage = pageName;
    const pageContent = document.getElementById('pageContent');
    
    // Show loading spinner
    showLoading();
    
    // Load page content based on page name
    setTimeout(() => {
        switch(pageName) {
            case 'home':
                loadHomePage();
                break;
            case 'upload':
                loadUploadPage();
                break;
            case 'database':
                loadDatabasePage();
                break;
            case 'train':
                loadTrainPage();
                break;
            case 'predict':
                loadPredictPage();
                break;
            case 'models':
                loadModelsPage();
                break;
            case 'reports':
                loadReportsPage();
                break;
            case 'settings':
                loadSettingsPage();
                break;
            default:
                loadHomePage();
        }
        hideLoading();
    }, 300);
}

function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

function showAlert(message, type = 'info', container = 'pageContent') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const containerElement = document.getElementById(container);
    if (containerElement) {
        containerElement.insertBefore(alertDiv, containerElement.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('ar-EG').format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat(currentLang === 'ar' ? 'ar-EG' : 'en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function createStatCard(icon, title, value, color = 'primary', trend = null) {
    return `
        <div class="col-md-6 col-lg-3">
            <div class="stat-card ${color} fade-in">
                <div class="icon">
                    <i class="${icon}"></i>
                </div>
                <h3>${value}</h3>
                <p>${title}</p>
                ${trend ? `<small class="text-${trend > 0 ? 'success' : 'danger'}">
                    <i class="fas fa-arrow-${trend > 0 ? 'up' : 'down'}"></i> ${Math.abs(trend)}%
                </small>` : ''}
            </div>
        </div>
    `;
}

function createChart(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'Segoe UI',
                            size: 12
                        },
                        padding: 15
                    }
                }
            },
            ...options
        }
    });
}

function toggleLanguage() {
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    
    // Update all i18n elements
    updateI18n();
    
    // Reload current page with new language
    loadPage(currentPage);
}

function updateI18n() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (i18n[currentLang] && i18n[currentLang][key]) {
            element.textContent = i18n[currentLang][key];
        }
    });
}

// Utility function to create table
function createTable(headers, rows, actions = null) {
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        ${headers.map(h => `<th>${h}</th>`).join('')}
                        ${actions ? '<th>' + (currentLang === 'ar' ? 'الإجراءات' : 'Actions') + '</th>' : ''}
                    </tr>
                </thead>
                <tbody>
    `;
    
    rows.forEach(row => {
        tableHTML += '<tr>';
        row.forEach(cell => {
            tableHTML += `<td>${cell}</td>`;
        });
        if (actions) {
            tableHTML += `<td>${actions(row)}</td>`;
        }
        tableHTML += '</tr>';
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    return tableHTML;
}

// Export functions for use in other scripts
window.dashboard = {
    loadPage,
    showLoading,
    hideLoading,
    showAlert,
    formatNumber,
    formatDate,
    createStatCard,
    createChart,
    createTable,
    toggleLanguage,
    getCurrentLang: () => currentLang
};

