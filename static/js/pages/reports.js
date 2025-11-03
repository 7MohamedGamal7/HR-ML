// Reports Page - صفحة التقارير

async function loadReportsPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="mb-1">${t.reports_title}</h2>
                    <p class="text-muted">${t.reports_subtitle}</p>
                </div>
                <button class="btn btn-gradient-primary" onclick="exportReport()">
                    <i class="fas fa-download"></i> ${t.reports_export}
                </button>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-line"></i> ${t.reports_accuracy_trend}</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="accuracyTrendChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-bar"></i> ${t.reports_model_comparison}</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="modelComparisonChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-pie"></i> ${t.reports_predictions_count}</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="predictionsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> ${lang === 'ar' ? 'ملخص الإحصائيات' : 'Statistics Summary'}</h5>
                        </div>
                        <div class="card-body" id="statsSummary">
                            <!-- Stats summary will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load reports data
    await loadReportsData();
}

async function loadReportsData() {
    const lang = window.dashboard.getCurrentLang();
    
    try {
        // Load training history for accuracy trend
        const history = await API.getTrainingHistory();
        
        if (history && history.length > 0) {
            createAccuracyTrendChart(history);
        }
        
        // Load model comparison data
        const comparison = await API.getModelComparison();
        if (comparison) {
            createModelComparisonChart(comparison);
        }
        
        // Create predictions chart (mock data)
        createPredictionsChart();
        
        // Load statistics summary
        const stats = await API.getStatistics();
        if (stats) {
            const summaryHTML = `
                <div class="row">
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-primary">${stats.total_models}</h3>
                                <p class="mb-0 small">${lang === 'ar' ? 'النماذج المدربة' : 'Trained Models'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-success">${window.dashboard.formatNumber(stats.total_predictions)}</h3>
                                <p class="mb-0 small">${lang === 'ar' ? 'التنبؤات' : 'Predictions'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-info">${(stats.average_accuracy * 100).toFixed(1)}%</h3>
                                <p class="mb-0 small">${lang === 'ar' ? 'متوسط الدقة' : 'Avg Accuracy'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-warning">${window.dashboard.formatNumber(stats.total_employees)}</h3>
                                <p class="mb-0 small">${lang === 'ar' ? 'الموظفون' : 'Employees'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('statsSummary').innerHTML = summaryHTML;
        }
        
    } catch (error) {
        console.error('Error loading reports data:', error);
    }
}

function createAccuracyTrendChart(history) {
    const lang = window.dashboard.getCurrentLang();
    
    const labels = history.map(h => {
        const date = new Date(h.date);
        return date.toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US', { month: 'short', day: 'numeric' });
    }).reverse();
    
    const data = {
        labels: labels,
        datasets: [{
            label: lang === 'ar' ? 'الدقة' : 'Accuracy',
            data: history.map(h => (h.accuracy * 100).toFixed(1)).reverse(),
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true
        }]
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
        }
    };
    
    window.dashboard.createChart('accuracyTrendChart', 'line', data, options);
}

function createModelComparisonChart(comparison) {
    const lang = window.dashboard.getCurrentLang();
    
    const data = {
        labels: comparison.models,
        datasets: [
            {
                label: lang === 'ar' ? 'الدقة' : 'Accuracy',
                data: comparison.metrics.accuracy.map(v => (v * 100).toFixed(1)),
                backgroundColor: 'rgba(102, 126, 234, 0.8)'
            },
            {
                label: lang === 'ar' ? 'الدقة الدقيقة' : 'Precision',
                data: comparison.metrics.precision.map(v => (v * 100).toFixed(1)),
                backgroundColor: 'rgba(56, 239, 125, 0.8)'
            },
            {
                label: lang === 'ar' ? 'الاستدعاء' : 'Recall',
                data: comparison.metrics.recall.map(v => (v * 100).toFixed(1)),
                backgroundColor: 'rgba(79, 172, 254, 0.8)'
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
        }
    };
    
    window.dashboard.createChart('modelComparisonChart', 'bar', data, options);
}

function createPredictionsChart() {
    const lang = window.dashboard.getCurrentLang();
    
    const data = {
        labels: [
            lang === 'ar' ? 'مؤهل للترقية' : 'Eligible',
            lang === 'ar' ? 'غير مؤهل' : 'Not Eligible'
        ],
        datasets: [{
            data: [734, 500],
            backgroundColor: [
                'rgba(56, 239, 125, 0.8)',
                'rgba(240, 147, 251, 0.8)'
            ]
        }]
    };
    
    window.dashboard.createChart('predictionsChart', 'doughnut', data);
}

function exportReport() {
    const lang = window.dashboard.getCurrentLang();
    
    window.dashboard.showAlert(
        lang === 'ar' ? 'جاري تصدير التقرير...' : 'Exporting report...',
        'info'
    );
    
    // This would generate a PDF or Excel report
    setTimeout(() => {
        window.dashboard.showAlert(
            lang === 'ar' ? 'ميزة التصدير قيد التطوير' : 'Export feature is under development',
            'warning'
        );
    }, 1000);
}

