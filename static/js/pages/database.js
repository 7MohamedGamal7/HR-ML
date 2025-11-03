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
                                    <button type="button" class="btn btn-gradient-success" onclick="saveDatabaseConfig()">
                                        <i class="fas fa-save"></i> ${t.db_save}
                                    </button>
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

