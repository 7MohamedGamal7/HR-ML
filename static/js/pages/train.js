// Training Page - صفحة التدريب

async function loadTrainPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.train_title}</h2>
                <p class="text-muted">${t.train_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-cog"></i> ${lang === 'ar' ? 'إعدادات التدريب' : 'Training Settings'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">${t.train_model_type}</label>
                                <select class="form-select" id="modelType">
                                    <option value="random_forest">Random Forest</option>
                                    <option value="gradient_boosting">Gradient Boosting</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="useCrossValidation" checked>
                                    <label class="form-check-label" for="useCrossValidation">
                                        ${t.train_cross_validation}
                                    </label>
                                </div>
                            </div>
                            
                            <div class="d-grid">
                                <button class="btn btn-gradient-primary btn-lg" onclick="startTraining()">
                                    <i class="fas fa-brain"></i> ${t.train_start}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm" id="trainingResultCard" style="display: none;">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-bar"></i> ${lang === 'ar' ? 'نتائج التدريب' : 'Training Results'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="progress mb-3" id="trainingProgressContainer" style="display: none;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: 0%" id="trainingProgressBar"></div>
                            </div>
                            <div id="trainingResult"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-history"></i> ${t.train_history}</h5>
                            <button class="btn btn-sm btn-outline-primary" onclick="loadTrainPage()">
                                <i class="fas fa-sync"></i> ${i18n[lang].refresh}
                            </button>
                        </div>
                        <div class="card-body" id="trainingHistoryContent">
                            <!-- Training history will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load training history
    await loadTrainingHistory();
}

async function startTraining() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const modelType = document.getElementById('modelType').value;
    const useCrossValidation = document.getElementById('useCrossValidation').checked;
    
    const resultCard = document.getElementById('trainingResultCard');
    const progressContainer = document.getElementById('trainingProgressContainer');
    const progressBar = document.getElementById('trainingProgressBar');
    const resultDiv = document.getElementById('trainingResult');
    
    resultCard.style.display = 'block';
    progressContainer.style.display = 'block';
    progressBar.style.width = '10%';
    resultDiv.innerHTML = `<p class="text-center"><i class="fas fa-spinner fa-spin"></i> ${t.train_progress}</p>`;
    
    try {
        progressBar.style.width = '30%';
        
        const config = {
            model_type: modelType,
            use_cross_validation: useCrossValidation
        };
        
        const result = await API.trainModel(config, lang);
        
        progressBar.style.width = '100%';
        
        if (result.status === 'success' && result.metrics) {
            const metrics = result.metrics;
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-check-circle"></i> ${t.train_success}</h5>
                </div>
                <div class="row">
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-primary">${(metrics.accuracy * 100).toFixed(2)}%</h4>
                                <p class="mb-0">${lang === 'ar' ? 'الدقة' : 'Accuracy'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-success">${(metrics.precision * 100).toFixed(2)}%</h4>
                                <p class="mb-0">${lang === 'ar' ? 'الدقة الدقيقة' : 'Precision'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-info">${(metrics.recall * 100).toFixed(2)}%</h4>
                                <p class="mb-0">${lang === 'ar' ? 'الاستدعاء' : 'Recall'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-warning">${(metrics.f1_score * 100).toFixed(2)}%</h4>
                                <p class="mb-0">F1 Score</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            window.dashboard.showAlert(t.train_success + ' ✅', 'success');
            
            // Reload training history
            setTimeout(() => loadTrainingHistory(), 1000);
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> ${result.detail || t.train_error}
                </div>
            `;
        }
        
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 2000);
        
    } catch (error) {
        progressBar.style.width = '100%';
        progressBar.classList.add('bg-danger');
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> ${t.train_error}: ${error.message}
            </div>
        `;
    }
}

async function loadTrainingHistory() {
    const lang = window.dashboard.getCurrentLang();
    
    try {
        const history = await API.getTrainingHistory();
        
        if (history && history.length > 0) {
            const headers = [
                lang === 'ar' ? 'التاريخ' : 'Date',
                lang === 'ar' ? 'نوع النموذج' : 'Model Type',
                lang === 'ar' ? 'الدقة' : 'Accuracy',
                lang === 'ar' ? 'الدقة الدقيقة' : 'Precision',
                lang === 'ar' ? 'الاستدعاء' : 'Recall',
                'F1 Score',
                lang === 'ar' ? 'وقت التدريب' : 'Training Time',
                lang === 'ar' ? 'حجم البيانات' : 'Data Size'
            ];
            
            const rows = history.map(h => [
                window.dashboard.formatDate(h.date),
                h.model_type,
                `<span class="badge bg-success">${(h.accuracy * 100).toFixed(1)}%</span>`,
                `${(h.precision * 100).toFixed(1)}%`,
                `${(h.recall * 100).toFixed(1)}%`,
                `${(h.f1_score * 100).toFixed(1)}%`,
                `${h.training_time.toFixed(1)}s`,
                window.dashboard.formatNumber(h.data_size)
            ]);
            
            document.getElementById('trainingHistoryContent').innerHTML = window.dashboard.createTable(headers, rows);
        } else {
            document.getElementById('trainingHistoryContent').innerHTML = `
                <p class="text-center text-muted">${lang === 'ar' ? 'لا يوجد سجل تدريب' : 'No training history'}</p>
            `;
        }
    } catch (error) {
        console.error('Error loading training history:', error);
    }
}

