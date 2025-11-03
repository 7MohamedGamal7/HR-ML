// Home Page - الصفحة الرئيسية

async function loadHomePage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="mb-1">${t.home_title}</h2>
                    <p class="text-muted">${t.home_welcome}</p>
                </div>
                <button class="btn btn-gradient-primary" onclick="window.dashboard.loadPage('train')">
                    <i class="fas fa-brain"></i> ${t.train_start}
                </button>
            </div>
            
            <!-- Statistics Cards -->
            <div class="row" id="statsCards">
                <!-- Cards will be loaded here -->
            </div>
            
            <!-- Charts Row -->
            <div class="row mt-4">
                <div class="col-lg-8">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-line"></i> ${t.model_performance}</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="performanceChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-clock"></i> ${t.recent_training}</h5>
                        </div>
                        <div class="card-body" id="recentTraining">
                            <!-- Recent training will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity Table -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-history"></i> ${t.train_history}</h5>
                            <button class="btn btn-sm btn-outline-primary" onclick="loadHomeData()">
                                <i class="fas fa-sync"></i> ${t.refresh}
                            </button>
                        </div>
                        <div class="card-body" id="trainingHistory">
                            <!-- Training history will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load data
    await loadHomeData();
}

async function loadHomeData() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    try {
        // Load statistics
        const stats = await API.getStatistics();
        
        // Create stat cards
        const statsHTML = `
            ${window.dashboard.createStatCard('fas fa-cubes', t.stat_models, stats.total_models, 'primary', 12)}
            ${window.dashboard.createStatCard('fas fa-magic', t.stat_predictions, window.dashboard.formatNumber(stats.total_predictions), 'success', 8)}
            ${window.dashboard.createStatCard('fas fa-chart-line', t.stat_accuracy, (stats.average_accuracy * 100).toFixed(1) + '%', 'info', 5)}
            ${window.dashboard.createStatCard('fas fa-users', t.stat_employees, window.dashboard.formatNumber(stats.total_employees), 'warning', -2)}
        `;
        
        document.getElementById('statsCards').innerHTML = statsHTML;
        
        // Load recent training
        if (stats.recent_training && stats.recent_training.length > 0) {
            let recentHTML = '<div class="list-group list-group-flush">';
            stats.recent_training.forEach(training => {
                const statusColor = training.status === 'completed' ? 'success' : 'warning';
                recentHTML += `
                    <div class="list-group-item border-0 px-0">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${training.model_type}</h6>
                                <small class="text-muted">${window.dashboard.formatDate(training.date)}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-${statusColor}">${(training.accuracy * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            recentHTML += '</div>';
            document.getElementById('recentTraining').innerHTML = recentHTML;
        }
        
        // Load training history
        const history = await API.getTrainingHistory();
        if (history && history.length > 0) {
            const headers = [
                lang === 'ar' ? 'التاريخ' : 'Date',
                lang === 'ar' ? 'نوع النموذج' : 'Model Type',
                lang === 'ar' ? 'الدقة' : 'Accuracy',
                lang === 'ar' ? 'الدقة الدقيقة' : 'Precision',
                lang === 'ar' ? 'الاستدعاء' : 'Recall',
                lang === 'ar' ? 'F1 Score' : 'F1 Score',
                lang === 'ar' ? 'وقت التدريب' : 'Training Time'
            ];
            
            const rows = history.map(h => [
                window.dashboard.formatDate(h.date),
                h.model_type,
                `<span class="badge bg-success">${(h.accuracy * 100).toFixed(1)}%</span>`,
                `${(h.precision * 100).toFixed(1)}%`,
                `${(h.recall * 100).toFixed(1)}%`,
                `${(h.f1_score * 100).toFixed(1)}%`,
                `${h.training_time.toFixed(1)}s`
            ]);
            
            document.getElementById('trainingHistory').innerHTML = window.dashboard.createTable(headers, rows);
        }
        
        // Create performance chart
        createPerformanceChart(history);
        
    } catch (error) {
        console.error('Error loading home data:', error);
        window.dashboard.showAlert(t.error + ': ' + error.message, 'danger');
    }
}

function createPerformanceChart(history) {
    if (!history || history.length === 0) return;
    
    const lang = window.dashboard.getCurrentLang();
    
    const labels = history.map(h => {
        const date = new Date(h.date);
        return date.toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US', { month: 'short', day: 'numeric' });
    }).reverse();
    
    const accuracyData = history.map(h => (h.accuracy * 100).toFixed(1)).reverse();
    const precisionData = history.map(h => (h.precision * 100).toFixed(1)).reverse();
    const recallData = history.map(h => (h.recall * 100).toFixed(1)).reverse();
    
    const data = {
        labels: labels,
        datasets: [
            {
                label: lang === 'ar' ? 'الدقة' : 'Accuracy',
                data: accuracyData,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: lang === 'ar' ? 'الدقة الدقيقة' : 'Precision',
                data: precisionData,
                borderColor: 'rgb(56, 239, 125)',
                backgroundColor: 'rgba(56, 239, 125, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: lang === 'ar' ? 'الاستدعاء' : 'Recall',
                data: recallData,
                borderColor: 'rgb(79, 172, 254)',
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    };
    
    const options = {
        scales: {
            y: {
                beginAtZero: true,
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
                        return context.dataset.label + ': ' + context.parsed.y + '%';
                    }
                }
            }
        }
    };
    
    window.dashboard.createChart('performanceChart', 'line', data, options);
}

