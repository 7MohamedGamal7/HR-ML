// Upload Page - صفحة رفع البيانات

async function loadUploadPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.upload_title}</h2>
                <p class="text-muted">${t.upload_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-8">
                    <div class="card shadow-sm">
                        <div class="card-body p-5">
                            <div class="text-center mb-4">
                                <div class="upload-icon mb-3">
                                    <i class="fas fa-cloud-upload-alt fa-5x text-primary"></i>
                                </div>
                                <h4>${t.upload_select_file}</h4>
                                <p class="text-muted">${t.upload_supported_formats}</p>
                            </div>
                            
                            <div class="mb-3">
                                <input type="file" class="form-control form-control-lg" id="fileInput" 
                                       accept=".csv,.xlsx,.xls,.xlsb,.xlsm,.tsv,.json,.parquet,.feather,.txt">
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button class="btn btn-gradient-primary btn-lg" onclick="uploadFile()">
                                    <i class="fas fa-upload"></i> ${t.upload_button}
                                </button>
                            </div>
                            
                            <div id="uploadProgress" class="mt-3" style="display: none;">
                                <div class="progress">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                         role="progressbar" style="width: 0%" id="progressBar"></div>
                                </div>
                                <p class="text-center mt-2 mb-0" id="progressText">0%</p>
                            </div>
                            
                            <div id="uploadResult" class="mt-3"></div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card shadow-sm bg-light">
                        <div class="card-body">
                            <h5 class="mb-3"><i class="fas fa-info-circle"></i> ${t.info}</h5>
                            <ul class="list-unstyled">
                                <li class="mb-2">
                                    <i class="fas fa-check text-success"></i>
                                    ${lang === 'ar' ? 'الحد الأقصى لحجم الملف: 100 ميجابايت' : 'Maximum file size: 100 MB'}
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-check text-success"></i>
                                    ${lang === 'ar' ? 'الصيغ المدعومة: CSV, Excel, JSON, Parquet' : 'Supported formats: CSV, Excel, JSON, Parquet'}
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-check text-success"></i>
                                    ${lang === 'ar' ? 'يجب أن يحتوي الملف على الأعمدة المطلوبة' : 'File must contain required columns'}
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-check text-success"></i>
                                    ${lang === 'ar' ? 'سيتم التحقق من البيانات تلقائياً' : 'Data will be validated automatically'}
                                </li>
                            </ul>
                            
                            <hr>
                            
                            <h6 class="mb-2">${lang === 'ar' ? 'الأعمدة المطلوبة:' : 'Required Columns:'}</h6>
                            <div class="d-flex flex-wrap gap-1">
                                <span class="badge bg-primary">Age</span>
                                <span class="badge bg-primary">Dept_Name</span>
                                <span class="badge bg-primary">Jop_Name</span>
                                <span class="badge bg-primary">Salary_Total</span>
                                <span class="badge bg-primary">Basic_Salary</span>
                                <span class="badge bg-primary">Training_Hours</span>
                                <span class="badge bg-primary">Performance_Score</span>
                                <span class="badge bg-primary">gender</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card shadow-sm mt-3">
                        <div class="card-body">
                            <h5 class="mb-3"><i class="fas fa-download"></i> ${lang === 'ar' ? 'ملفات نموذجية' : 'Sample Files'}</h5>
                            <div class="d-grid gap-2">
                                <a href="/test_data/sample_employees.csv" class="btn btn-outline-primary btn-sm" download>
                                    <i class="fas fa-file-csv"></i> CSV Sample
                                </a>
                                <a href="/test_data/sample_employees.xlsx" class="btn btn-outline-success btn-sm" download>
                                    <i class="fas fa-file-excel"></i> Excel Sample
                                </a>
                                <a href="/test_data/sample_employees.json" class="btn btn-outline-info btn-sm" download>
                                    <i class="fas fa-file-code"></i> JSON Sample
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Data Preview Section -->
            <div class="row mt-4" id="dataPreviewSection" style="display: none;">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-table"></i> ${lang === 'ar' ? 'معاينة البيانات' : 'Data Preview'}</h5>
                            <button class="btn btn-sm btn-outline-danger" onclick="clearPreview()">
                                <i class="fas fa-times"></i> ${t.close}
                            </button>
                        </div>
                        <div class="card-body" id="dataPreview">
                            <!-- Data preview will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
}

async function uploadFile() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        window.dashboard.showAlert(lang === 'ar' ? 'الرجاء اختيار ملف' : 'Please select a file', 'warning');
        return;
    }
    
    // Show progress
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const resultDiv = document.getElementById('uploadResult');
    
    progressDiv.style.display = 'block';
    resultDiv.innerHTML = '';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
            progressText.textContent = progress + '%';
        }
    }, 200);
    
    try {
        const result = await API.uploadFile(file, lang);
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        setTimeout(() => {
            progressDiv.style.display = 'none';
            
            if (result.status === 'success') {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <h5><i class="fas fa-check-circle"></i> ${t.upload_success}</h5>
                        <p class="mb-2">${lang === 'ar' ? 'اسم الملف:' : 'File name:'} <strong>${result.filename}</strong></p>
                        <p class="mb-2">${lang === 'ar' ? 'عدد الصفوف:' : 'Rows:'} <strong>${window.dashboard.formatNumber(result.rows)}</strong></p>
                        <p class="mb-0">${lang === 'ar' ? 'عدد الأعمدة:' : 'Columns:'} <strong>${result.columns}</strong></p>
                        <hr>
                        <div class="d-flex gap-2">
                            <button class="btn btn-primary" onclick="window.dashboard.loadPage('train')">
                                <i class="fas fa-brain"></i> ${lang === 'ar' ? 'بدء التدريب' : 'Start Training'}
                            </button>
                            <button class="btn btn-outline-primary" onclick="showDataPreview()">
                                <i class="fas fa-eye"></i> ${lang === 'ar' ? 'معاينة البيانات' : 'Preview Data'}
                            </button>
                        </div>
                    </div>
                `;
                
                // Store upload result for preview
                window.uploadedData = result;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <h5><i class="fas fa-exclamation-circle"></i> ${t.upload_error}</h5>
                        <p class="mb-0">${result.message || result.detail}</p>
                    </div>
                `;
            }
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        progressDiv.style.display = 'none';
        
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-circle"></i> ${t.upload_error}</h5>
                <p class="mb-0">${error.message}</p>
            </div>
        `;
    }
}

function showDataPreview() {
    const lang = window.dashboard.getCurrentLang();
    const previewSection = document.getElementById('dataPreviewSection');
    const previewDiv = document.getElementById('dataPreview');
    
    if (window.uploadedData && window.uploadedData.preview) {
        const preview = window.uploadedData.preview;
        
        // Create table from preview data
        let tableHTML = '<div class="table-responsive"><table class="table table-sm table-hover"><thead><tr>';
        
        // Headers
        if (preview.length > 0) {
            Object.keys(preview[0]).forEach(key => {
                tableHTML += `<th>${key}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';
            
            // Rows
            preview.forEach(row => {
                tableHTML += '<tr>';
                Object.values(row).forEach(value => {
                    tableHTML += `<td>${value !== null && value !== undefined ? value : '-'}</td>`;
                });
                tableHTML += '</tr>';
            });
        }
        
        tableHTML += '</tbody></table></div>';
        previewDiv.innerHTML = tableHTML;
        previewSection.style.display = 'block';
        
        // Scroll to preview
        previewSection.scrollIntoView({ behavior: 'smooth' });
    } else {
        window.dashboard.showAlert(lang === 'ar' ? 'لا توجد بيانات للمعاينة' : 'No data to preview', 'warning');
    }
}

function clearPreview() {
    document.getElementById('dataPreviewSection').style.display = 'none';
}

