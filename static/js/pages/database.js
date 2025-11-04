// Database Page - صفحة قاعدة البيانات

async function loadDatabasePage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.db_title}</h2>
                <p class="text-muted">${t.db_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-plug"></i> ${lang === 'ar' ? 'معلومات الاتصال' : 'Connection Information'}</h5>
                        </div>
                        <div class="card-body">
                            <form id="dbForm">
                                <div class="mb-3">
                                    <label class="form-label">${t.db_host}</label>
                                    <input type="text" class="form-control" id="dbHost" placeholder="localhost" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">${t.db_port}</label>
                                    <input type="number" class="form-control" id="dbPort" value="1433" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">${t.db_name}</label>
                                    <input type="text" class="form-control" id="dbName" placeholder="HR_Database" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">${t.db_username}</label>
                                    <input type="text" class="form-control" id="dbUsername" placeholder="sa" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">${t.db_password}</label>
                                    <input type="password" class="form-control" id="dbPassword" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">${lang === 'ar' ? 'الجدول الافتراضي' : 'Default Table'}</label>
                                    <input type="text" class="form-control" id="dbDefaultTable" value="Employees">
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button type="button" class="btn btn-gradient-primary" onclick="testDatabaseConnection()">
                                        <i class="fas fa-plug"></i> ${t.db_test}
                                    </button>
                                    <button type="button" class="btn btn-gradient-warning" onclick="diagnoseDatabaseConnection()">
                                        <i class="fas fa-stethoscope"></i> ${lang === 'ar' ? 'تشخيص المشكلة' : 'Diagnose Issue'}
                                    </button>
                                    <button type="button" class="btn btn-gradient-success" onclick="saveDatabaseConfig()">
                                        <i class="fas fa-save"></i> ${t.db_save}
                                    </button>
                                </div>

                                <!-- Help Section -->
                                <div class="alert alert-info mt-3" role="alert">
                                    <h6 class="alert-heading">
                                        <i class="fas fa-info-circle"></i> ${lang === 'ar' ? 'نصائح مهمة' : 'Important Tips'}
                                    </h6>
                                    <small>
                                        ${lang === 'ar' ?
                                            '• إذا كان SQL Server على نفس الجهاز، استخدم: <code>host.docker.internal</code><br>' +
                                            '• لا تستخدم <code>localhost</code> أو <code>127.0.0.1</code><br>' +
                                            '• إذا كان SQL Server على جهاز آخر، استخدم عنوان IP (مثال: <code>192.168.1.50</code>)<br>' +
                                            '• تأكد من تفعيل TCP/IP في SQL Server Configuration Manager<br>' +
                                            '• تأكد من فتح المنفذ 1433 في Firewall'
                                            :
                                            '• If SQL Server is on the same machine, use: <code>host.docker.internal</code><br>' +
                                            '• Don\'t use <code>localhost</code> or <code>127.0.0.1</code><br>' +
                                            '• If SQL Server is on another machine, use IP address (e.g., <code>192.168.1.50</code>)<br>' +
                                            '• Make sure TCP/IP is enabled in SQL Server Configuration Manager<br>' +
                                            '• Make sure port 1433 is open in Firewall'
                                        }
                                    </small>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card shadow-sm" id="tablesCard" style="display: none;">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-table"></i> ${t.db_tables}</h5>
                        </div>
                        <div class="card-body">
                            <div id="tablesList"></div>
                        </div>
                    </div>
                    
                    <div class="card shadow-sm mt-3" id="tableInfoCard" style="display: none;">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> ${lang === 'ar' ? 'معلومات الجدول' : 'Table Information'}</h5>
                        </div>
                        <div class="card-body" id="tableInfoContent">
                            <!-- Table info will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4" id="trainingCard" style="display: none;">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-brain"></i> ${lang === 'ar' ? 'التدريب من قاعدة البيانات' : 'Training from Database'}</h5>
                        </div>
                        <div class="card-body">
                            <div class="progress mb-3">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: 0%" id="dbTrainingProgress"></div>
                            </div>
                            <div id="dbTrainingStatus"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
    
    // Load saved configuration
    await loadSavedConfig();
}

async function loadSavedConfig() {
    try {
        const lang = window.dashboard.getCurrentLang();
        const config = await API.loadDatabaseConfig(lang);
        
        if (config && config.config) {
            document.getElementById('dbHost').value = config.config.host || '';
            document.getElementById('dbPort').value = config.config.port || 1433;
            document.getElementById('dbName').value = config.config.database || '';
            document.getElementById('dbUsername').value = config.config.username || '';
            document.getElementById('dbDefaultTable').value = config.config.default_table || 'Employees';
        }
    } catch (error) {
        console.log('No saved configuration found');
    }
}

async function testDatabaseConnection() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];

    window.dashboard.showLoading();

    try {
        const result = await API.testDatabaseConnection(lang);

        if (result.status === 'success') {
            window.dashboard.showAlert(t.db_success + ' ✅', 'success');
            await loadDatabaseTables();
        } else {
            window.dashboard.showAlert(t.db_error + ': ' + (result.detail || result.message), 'danger');
        }
    } catch (error) {
        window.dashboard.showAlert(t.db_error + ': ' + error.message, 'danger');
    } finally {
        window.dashboard.hideLoading();
    }
}

async function diagnoseDatabaseConnection() {
    const lang = window.dashboard.getCurrentLang();

    window.dashboard.showLoading();

    try {
        const response = await fetch(`/train/database/diagnose?lang=${lang}`);
        const result = await response.json();

        if (result.diagnosis) {
            const diagnosis = result.diagnosis;

            // إنشاء HTML للتقرير التشخيصي
            let diagnosticHTML = `
                <div class="modal fade" id="diagnosticModal" tabindex="-1">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-gradient-warning text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-stethoscope"></i>
                                    ${lang === 'ar' ? 'تقرير التشخيص الشامل' : 'Comprehensive Diagnostic Report'}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
            `;

            // حالة عامة
            const statusBadge = diagnosis.overall_status === 'success' ?
                '<span class="badge bg-success">✅ ناجح - Success</span>' :
                '<span class="badge bg-danger">❌ فشل - Failed</span>';

            diagnosticHTML += `
                <div class="alert alert-${diagnosis.overall_status === 'success' ? 'success' : 'danger'}">
                    <h6>${lang === 'ar' ? 'الحالة العامة' : 'Overall Status'}: ${statusBadge}</h6>
                </div>
            `;

            // الإعدادات
            diagnosticHTML += `
                <h6><i class="fas fa-cog"></i> ${lang === 'ar' ? 'الإعدادات الحالية' : 'Current Configuration'}</h6>
                <table class="table table-sm table-bordered">
                    <tr><th>Host</th><td><code>${diagnosis.configuration.host}</code></td></tr>
                    <tr><th>Port</th><td><code>${diagnosis.configuration.port}</code></td></tr>
                    <tr><th>Database</th><td><code>${diagnosis.configuration.database}</code></td></tr>
                    <tr><th>Username</th><td><code>${diagnosis.configuration.username}</code></td></tr>
                    <tr><th>Driver</th><td><code>${diagnosis.configuration.driver}</code></td></tr>
                    <tr><th>Timeout</th><td><code>${diagnosis.configuration.timeout}s</code></td></tr>
                </table>
                <hr>
            `;

            // نتائج الفحوصات
            diagnosticHTML += `<h6><i class="fas fa-check-circle"></i> ${lang === 'ar' ? 'نتائج الفحوصات' : 'Check Results'}</h6>`;

            for (const [checkName, checkResult] of Object.entries(diagnosis.checks)) {
                const statusIcon = checkResult.status === 'ok' || checkResult.status === 'success' ? '✅' :
                                 checkResult.status === 'warning' ? '⚠️' : '❌';

                diagnosticHTML += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h6>${statusIcon} ${checkName.replace(/_/g, ' ').toUpperCase()}</h6>
                            <p class="mb-0"><small>${checkResult.message || JSON.stringify(checkResult)}</small></p>
                        </div>
                    </div>
                `;
            }

            // التوصيات
            if (diagnosis.recommendations && diagnosis.recommendations.length > 0) {
                diagnosticHTML += `
                    <hr>
                    <h6><i class="fas fa-lightbulb"></i> ${lang === 'ar' ? 'التوصيات المقترحة' : 'Recommendations'}</h6>
                    <div class="list-group">
                `;

                diagnosis.recommendations.forEach((rec, index) => {
                    const priorityBadge = rec.priority === 'critical' ? 'danger' :
                                        rec.priority === 'high' ? 'warning' : 'info';

                    diagnosticHTML += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <span class="badge bg-${priorityBadge} me-2">${rec.priority || 'info'}</span>
                                    <strong>${index + 1}.</strong> ${rec.message}
                                </div>
                            </div>
                            ${rec.fix ? `<div class="mt-2"><code>${rec.fix}</code></div>` : ''}
                            ${rec.command ? `<div class="mt-2"><code>${rec.command}</code></div>` : ''}
                        </div>
                    `;
                });

                diagnosticHTML += '</div>';
            }

            // تحليل الخطأ (إذا وجد)
            if (diagnosis.error_analysis) {
                const analysis = diagnosis.error_analysis;
                diagnosticHTML += `
                    <hr>
                    <h6><i class="fas fa-exclamation-triangle"></i> ${lang === 'ar' ? 'تحليل الخطأ' : 'Error Analysis'}</h6>
                    <div class="alert alert-warning">
                        <strong>${lang === 'ar' ? 'نوع الخطأ' : 'Error Type'}:</strong> ${analysis.error_type}<br>
                        <strong>${lang === 'ar' ? 'الأسباب المحتملة' : 'Possible Causes'}:</strong>
                        <ul class="mb-0 mt-2">
                            ${analysis.possible_causes.map(cause => `<li>${cause}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            diagnosticHTML += `
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    ${lang === 'ar' ? 'إغلاق' : 'Close'}
                                </button>
                                <button type="button" class="btn btn-primary" onclick="copyDiagnosticReport()">
                                    <i class="fas fa-copy"></i> ${lang === 'ar' ? 'نسخ التقرير' : 'Copy Report'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // إضافة Modal إلى الصفحة
            const existingModal = document.getElementById('diagnosticModal');
            if (existingModal) {
                existingModal.remove();
            }

            document.body.insertAdjacentHTML('beforeend', diagnosticHTML);

            // عرض Modal
            const modal = new bootstrap.Modal(document.getElementById('diagnosticModal'));
            modal.show();

            // حفظ التقرير للنسخ
            window.lastDiagnosticReport = diagnosis;

        } else {
            window.dashboard.showAlert(lang === 'ar' ? 'فشل التشخيص' : 'Diagnosis failed', 'danger');
        }
    } catch (error) {
        window.dashboard.showAlert(
            (lang === 'ar' ? 'خطأ في التشخيص: ' : 'Diagnosis error: ') + error.message,
            'danger'
        );
    } finally {
        window.dashboard.hideLoading();
    }
}

function copyDiagnosticReport() {
    if (window.lastDiagnosticReport) {
        const reportText = JSON.stringify(window.lastDiagnosticReport, null, 2);
        navigator.clipboard.writeText(reportText).then(() => {
            const lang = window.dashboard.getCurrentLang();
            window.dashboard.showAlert(
                lang === 'ar' ? 'تم نسخ التقرير ✅' : 'Report copied ✅',
                'success'
            );
        });
    }
}

async function saveDatabaseConfig() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const config = {
        host: document.getElementById('dbHost').value,
        port: parseInt(document.getElementById('dbPort').value),
        database: document.getElementById('dbName').value,
        username: document.getElementById('dbUsername').value,
        password: document.getElementById('dbPassword').value,
        driver: 'ODBC Driver 17 for SQL Server',
        timeout: 30,
        default_table: document.getElementById('dbDefaultTable').value
    };
    
    window.dashboard.showLoading();
    
    try {
        const result = await API.saveDatabaseConfig(config, lang);
        
        if (result.status === 'success') {
            window.dashboard.showAlert(lang === 'ar' ? 'تم حفظ الإعدادات بنجاح ✅' : 'Configuration saved successfully ✅', 'success');
        } else {
            window.dashboard.showAlert(lang === 'ar' ? 'فشل حفظ الإعدادات' : 'Failed to save configuration', 'danger');
        }
    } catch (error) {
        window.dashboard.showAlert(lang === 'ar' ? 'خطأ في الحفظ: ' : 'Save error: ' + error.message, 'danger');
    } finally {
        window.dashboard.hideLoading();
    }
}

async function loadDatabaseTables() {
    const lang = window.dashboard.getCurrentLang();
    
    try {
        const result = await API.getDatabaseTables(lang);
        
        if (result.tables && result.tables.length > 0) {
            let tablesHTML = '<div class="list-group">';
            
            result.tables.forEach(table => {
                tablesHTML += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <i class="fas fa-table text-primary me-2"></i>
                                <strong>${table}</strong>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-info me-1" onclick="showTableInfo('${table}')">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                                <button class="btn btn-sm btn-success" onclick="trainFromTable('${table}')">
                                    <i class="fas fa-brain"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            tablesHTML += '</div>';
            document.getElementById('tablesList').innerHTML = tablesHTML;
            document.getElementById('tablesCard').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading tables:', error);
    }
}

async function showTableInfo(tableName) {
    const lang = window.dashboard.getCurrentLang();
    
    window.dashboard.showLoading();
    
    try {
        const result = await API.getTableInfo(tableName, lang);
        
        if (result.table_info) {
            const info = result.table_info;
            let infoHTML = `
                <h5><i class="fas fa-table text-primary"></i> ${tableName}</h5>
                <div class="row mt-3">
                    <div class="col-6">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-primary">${window.dashboard.formatNumber(info.row_count || 0)}</h3>
                                <p class="mb-0">${lang === 'ar' ? 'عدد الصفوف' : 'Rows'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h3 class="text-success">${info.column_count || 0}</h3>
                                <p class="mb-0">${lang === 'ar' ? 'عدد الأعمدة' : 'Columns'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (info.columns && info.columns.length > 0) {
                infoHTML += `
                    <div class="mt-3">
                        <h6>${lang === 'ar' ? 'الأعمدة:' : 'Columns:'}</h6>
                        <div class="d-flex flex-wrap gap-1">
                            ${info.columns.map(col => `<span class="badge bg-primary">${col}</span>`).join('')}
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('tableInfoContent').innerHTML = infoHTML;
            document.getElementById('tableInfoCard').style.display = 'block';
        }
    } catch (error) {
        window.dashboard.showAlert(lang === 'ar' ? 'خطأ في تحميل معلومات الجدول' : 'Error loading table info', 'danger');
    } finally {
        window.dashboard.hideLoading();
    }
}

async function trainFromTable(tableName) {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const trainingCard = document.getElementById('trainingCard');
    const progressBar = document.getElementById('dbTrainingProgress');
    const statusDiv = document.getElementById('dbTrainingStatus');
    
    trainingCard.style.display = 'block';
    progressBar.style.width = '10%';
    statusDiv.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${t.train_progress}`;
    
    try {
        progressBar.style.width = '30%';
        
        const result = await API.trainFromDatabase(tableName, null, null, lang);
        
        progressBar.style.width = '100%';
        
        if (result.status === 'success' && result.metrics) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-check-circle"></i> ${t.train_success}</h5>
                    <p class="mb-0">${lang === 'ar' ? 'الدقة:' : 'Accuracy:'} <strong>${(result.metrics.accuracy * 100).toFixed(2)}%</strong></p>
                </div>
            `;
            window.dashboard.showAlert(t.train_success + ' ✅', 'success');
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> ${result.detail || t.train_error}
                </div>
            `;
        }
    } catch (error) {
        progressBar.style.width = '100%';
        progressBar.classList.add('bg-danger');
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> ${t.train_error}: ${error.message}
            </div>
        `;
    }
}

