// Models Page - صفحة النماذج

async function loadModelsPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.models_title}</h2>
                <p class="text-muted">${t.models_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-cube"></i> ${t.models_current}</h5>
                        </div>
                        <div class="card-body" id="currentModelInfo">
                            <!-- Current model info will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-cubes"></i> ${lang === 'ar' ? 'إجراءات النماذج' : 'Model Actions'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" onclick="exportModel()">
                                    <i class="fas fa-download"></i> ${t.models_export}
                                </button>
                                <button class="btn btn-outline-success" onclick="document.getElementById('importModelInput').click()">
                                    <i class="fas fa-upload"></i> ${t.models_import}
                                </button>
                                <input type="file" id="importModelInput" style="display: none;" accept=".pkl,.joblib" onchange="importModel(this)">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-history"></i> ${t.models_saved}</h5>
                            <button class="btn btn-sm btn-outline-primary" onclick="loadModelsPage()">
                                <i class="fas fa-sync"></i> ${i18n[lang].refresh}
                            </button>
                        </div>
                        <div class="card-body" id="savedModelsList">
                            <!-- Saved models list will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load current model info
    await loadCurrentModelInfo();
}

async function loadCurrentModelInfo() {
    const lang = window.dashboard.getCurrentLang();
    
    try {
        const modelInfo = await API.getModelInfo(lang);
        
        if (modelInfo && modelInfo.model_info) {
            const info = modelInfo.model_info;
            const infoHTML = `
                <div class="row">
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-primary">${info.model_type || 'N/A'}</h4>
                                <p class="mb-0 small">${lang === 'ar' ? 'نوع النموذج' : 'Model Type'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h4 class="text-success">${info.accuracy ? (info.accuracy * 100).toFixed(1) + '%' : 'N/A'}</h4>
                                <p class="mb-0 small">${lang === 'ar' ? 'الدقة' : 'Accuracy'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-12">
                        <p class="mb-1"><strong>${lang === 'ar' ? 'تاريخ التدريب:' : 'Training Date:'}</strong> ${info.training_date ? window.dashboard.formatDate(info.training_date) : 'N/A'}</p>
                        <p class="mb-0"><strong>${lang === 'ar' ? 'عدد الميزات:' : 'Features Count:'}</strong> ${info.features_count || 'N/A'}</p>
                    </div>
                </div>
            `;
            document.getElementById('currentModelInfo').innerHTML = infoHTML;
        } else {
            document.getElementById('currentModelInfo').innerHTML = `
                <p class="text-center text-muted">${lang === 'ar' ? 'لا يوجد نموذج مدرب حالياً' : 'No trained model available'}</p>
            `;
        }
    } catch (error) {
        console.error('Error loading model info:', error);
        document.getElementById('currentModelInfo').innerHTML = `
            <p class="text-center text-muted">${lang === 'ar' ? 'خطأ في تحميل معلومات النموذج' : 'Error loading model info'}</p>
        `;
    }
}

function exportModel() {
    const lang = window.dashboard.getCurrentLang();
    
    // Create a download link for the model file
    const link = document.createElement('a');
    link.href = `${API_BASE}/models/export`;
    link.download = `hr_model_${new Date().toISOString().split('T')[0]}.pkl`;
    link.click();
    
    window.dashboard.showAlert(
        lang === 'ar' ? 'جاري تصدير النموذج...' : 'Exporting model...',
        'info'
    );
}

function importModel(input) {
    const lang = window.dashboard.getCurrentLang();
    const file = input.files[0];
    
    if (!file) return;
    
    window.dashboard.showAlert(
        lang === 'ar' ? 'ميزة الاستيراد قيد التطوير' : 'Import feature is under development',
        'info'
    );
    
    // This would be implemented with a real API endpoint
    // const formData = new FormData();
    // formData.append('model_file', file);
    // await fetch(`${API_BASE}/models/import`, { method: 'POST', body: formData });
}

