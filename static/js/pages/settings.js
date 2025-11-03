// Settings Page - صفحة الإعدادات

async function loadSettingsPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.settings_title}</h2>
                <p class="text-muted">${t.settings_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-language"></i> ${lang === 'ar' ? 'إعدادات اللغة' : 'Language Settings'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">${t.settings_language}</label>
                                <select class="form-select" id="languageSelect" onchange="changeLanguage()">
                                    <option value="ar" ${lang === 'ar' ? 'selected' : ''}>العربية</option>
                                    <option value="en" ${lang === 'en' ? 'selected' : ''}>English</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card shadow-sm mt-3">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-palette"></i> ${lang === 'ar' ? 'إعدادات المظهر' : 'Appearance Settings'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">${t.settings_theme}</label>
                                <select class="form-select" id="themeSelect">
                                    <option value="light">${lang === 'ar' ? 'فاتح' : 'Light'}</option>
                                    <option value="dark">${lang === 'ar' ? 'داكن' : 'Dark'}</option>
                                    <option value="auto">${lang === 'ar' ? 'تلقائي' : 'Auto'}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-bell"></i> ${lang === 'ar' ? 'إعدادات الإشعارات' : 'Notification Settings'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="form-check form-switch mb-3">
                                <input class="form-check-input" type="checkbox" id="emailNotifications" checked>
                                <label class="form-check-label" for="emailNotifications">
                                    ${lang === 'ar' ? 'إشعارات البريد الإلكتروني' : 'Email Notifications'}
                                </label>
                            </div>
                            <div class="form-check form-switch mb-3">
                                <input class="form-check-input" type="checkbox" id="trainingNotifications" checked>
                                <label class="form-check-label" for="trainingNotifications">
                                    ${lang === 'ar' ? 'إشعارات التدريب' : 'Training Notifications'}
                                </label>
                            </div>
                            <div class="form-check form-switch mb-3">
                                <input class="form-check-input" type="checkbox" id="predictionNotifications">
                                <label class="form-check-label" for="predictionNotifications">
                                    ${lang === 'ar' ? 'إشعارات التنبؤ' : 'Prediction Notifications'}
                                </label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card shadow-sm mt-3">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-cog"></i> ${lang === 'ar' ? 'إعدادات النموذج' : 'Model Settings'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">${lang === 'ar' ? 'نوع النموذج الافتراضي' : 'Default Model Type'}</label>
                                <select class="form-select" id="defaultModelType">
                                    <option value="random_forest">Random Forest</option>
                                    <option value="gradient_boosting">Gradient Boosting</option>
                                </select>
                            </div>
                            <div class="form-check form-switch mb-3">
                                <input class="form-check-input" type="checkbox" id="autoCrossValidation" checked>
                                <label class="form-check-label" for="autoCrossValidation">
                                    ${lang === 'ar' ? 'استخدام التحقق المتقاطع تلقائياً' : 'Auto Cross Validation'}
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> ${lang === 'ar' ? 'معلومات النظام' : 'System Information'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>${lang === 'ar' ? 'اسم النظام:' : 'System Name:'}</strong> HR-ML System</p>
                                    <p><strong>${lang === 'ar' ? 'الإصدار:' : 'Version:'}</strong> 1.0.0</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>${lang === 'ar' ? 'آخر تحديث:' : 'Last Update:'}</strong> ${new Date().toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US')}</p>
                                    <p><strong>${lang === 'ar' ? 'الحالة:' : 'Status:'}</strong> <span class="badge bg-success">${lang === 'ar' ? 'نشط' : 'Active'}</span></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="d-flex gap-2 justify-content-end">
                        <button class="btn btn-outline-secondary" onclick="resetSettings()">
                            <i class="fas fa-undo"></i> ${t.settings_reset}
                        </button>
                        <button class="btn btn-gradient-primary" onclick="saveSettings()">
                            <i class="fas fa-save"></i> ${t.settings_save}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load saved settings
    loadSavedSettings();
}

function changeLanguage() {
    const newLang = document.getElementById('languageSelect').value;
    if (newLang !== window.dashboard.getCurrentLang()) {
        window.dashboard.toggleLanguage();
    }
}

function loadSavedSettings() {
    // Load settings from localStorage
    const settings = JSON.parse(localStorage.getItem('hrml_settings') || '{}');
    
    if (settings.theme) {
        document.getElementById('themeSelect').value = settings.theme;
    }
    
    if (settings.defaultModelType) {
        document.getElementById('defaultModelType').value = settings.defaultModelType;
    }
    
    if (settings.notifications) {
        document.getElementById('emailNotifications').checked = settings.notifications.email !== false;
        document.getElementById('trainingNotifications').checked = settings.notifications.training !== false;
        document.getElementById('predictionNotifications').checked = settings.notifications.prediction === true;
    }
    
    if (settings.autoCrossValidation !== undefined) {
        document.getElementById('autoCrossValidation').checked = settings.autoCrossValidation;
    }
}

function saveSettings() {
    const lang = window.dashboard.getCurrentLang();
    
    const settings = {
        language: document.getElementById('languageSelect').value,
        theme: document.getElementById('themeSelect').value,
        defaultModelType: document.getElementById('defaultModelType').value,
        autoCrossValidation: document.getElementById('autoCrossValidation').checked,
        notifications: {
            email: document.getElementById('emailNotifications').checked,
            training: document.getElementById('trainingNotifications').checked,
            prediction: document.getElementById('predictionNotifications').checked
        }
    };
    
    // Save to localStorage
    localStorage.setItem('hrml_settings', JSON.stringify(settings));
    
    window.dashboard.showAlert(
        lang === 'ar' ? 'تم حفظ الإعدادات بنجاح ✅' : 'Settings saved successfully ✅',
        'success'
    );
}

function resetSettings() {
    const lang = window.dashboard.getCurrentLang();
    
    if (confirm(lang === 'ar' ? 'هل أنت متأكد من إعادة تعيين الإعدادات؟' : 'Are you sure you want to reset settings?')) {
        localStorage.removeItem('hrml_settings');
        loadSettingsPage();
        
        window.dashboard.showAlert(
            lang === 'ar' ? 'تم إعادة تعيين الإعدادات' : 'Settings reset',
            'info'
        );
    }
}

