// Prediction Page - صفحة التنبؤ

async function loadPredictPage() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const content = `
        <div class="fade-in">
            <div class="mb-4">
                <h2 class="mb-1">${t.predict_title}</h2>
                <p class="text-muted">${t.predict_subtitle}</p>
            </div>
            
            <div class="row">
                <div class="col-lg-8">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-user"></i> ${lang === 'ar' ? 'بيانات الموظف' : 'Employee Data'}</h5>
                        </div>
                        <div class="card-body">
                            <form id="predictForm">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Age</label>
                                        <input type="number" class="form-control" id="age" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Years Since Contract Start</label>
                                        <input type="number" class="form-control" id="years_since_contract" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Salary Total</label>
                                        <input type="number" class="form-control" id="salary_total" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Basic Salary</label>
                                        <input type="number" class="form-control" id="basic_salary" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Training Hours</label>
                                        <input type="number" class="form-control" id="training_hours" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Performance Score</label>
                                        <input type="number" class="form-control" id="performance_score" min="0" max="100" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Department</label>
                                        <select class="form-select" id="dept_name" required>
                                            <option value="">Select...</option>
                                            <option value="IT">IT</option>
                                            <option value="HR">HR</option>
                                            <option value="Finance">Finance</option>
                                            <option value="Sales">Sales</option>
                                            <option value="Marketing">Marketing</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Gender</label>
                                        <select class="form-select" id="gender" required>
                                            <option value="">Select...</option>
                                            <option value="Male">Male</option>
                                            <option value="Female">Female</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="d-grid">
                                    <button type="button" class="btn btn-gradient-primary btn-lg" onclick="makePrediction()">
                                        <i class="fas fa-magic"></i> ${t.predict_button}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card shadow-sm" id="predictionResultCard" style="display: none;">
                        <div class="card-header bg-white">
                            <h5 class="mb-0"><i class="fas fa-chart-pie"></i> ${t.predict_result}</h5>
                        </div>
                        <div class="card-body text-center" id="predictionResult">
                            <!-- Prediction result will be shown here -->
                        </div>
                    </div>
                    
                    <div class="card shadow-sm mt-3 bg-light">
                        <div class="card-body">
                            <h6 class="mb-3"><i class="fas fa-info-circle"></i> ${lang === 'ar' ? 'معلومات' : 'Information'}</h6>
                            <p class="small mb-0">
                                ${lang === 'ar' ? 
                                    'سيقوم النظام بتحليل البيانات المدخلة والتنبؤ بأهلية الموظف للترقية بناءً على النموذج المدرب.' :
                                    'The system will analyze the entered data and predict employee eligibility for promotion based on the trained model.'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('pageContent').innerHTML = content;
}

async function makePrediction() {
    const lang = window.dashboard.getCurrentLang();
    const t = i18n[lang];
    
    const employeeData = {
        Age: parseInt(document.getElementById('age').value),
        Years_Since_Contract_Start: parseInt(document.getElementById('years_since_contract').value),
        Salary_Total: parseFloat(document.getElementById('salary_total').value),
        Basic_Salary: parseFloat(document.getElementById('basic_salary').value),
        Training_Hours: parseInt(document.getElementById('training_hours').value),
        Performance_Score: parseInt(document.getElementById('performance_score').value),
        Dept_Name: document.getElementById('dept_name').value,
        gender: document.getElementById('gender').value,
        // Add default values for other required fields
        Allowances: 0,
        Insurance_Salary: 0,
        Remaining_Contract_Renewal: 0,
        Car_Ride_Time: 0,
        Skill_level_measurement_certificate: 0,
        Awards: 0,
        Emp_Type: 'Full-time',
        Working_Condition: 'Normal',
        Emp_Marital_Status: 'Single',
        Governorate: 'Cairo',
        Shift_Type: 'Day',
        Jop_Name: 'Employee'
    };
    
    window.dashboard.showLoading();
    
    try {
        const result = await API.predict(employeeData, lang);
        
        const resultCard = document.getElementById('predictionResultCard');
        const resultDiv = document.getElementById('predictionResult');
        
        if (result.prediction !== undefined) {
            const isEligible = result.prediction === 1 || result.prediction === true;
            const confidence = result.confidence || result.probability || 0.5;
            
            resultDiv.innerHTML = `
                <div class="mb-3">
                    <i class="fas fa-${isEligible ? 'check-circle' : 'times-circle'} fa-4x text-${isEligible ? 'success' : 'danger'}"></i>
                </div>
                <h4 class="mb-3">${isEligible ? t.predict_eligible : t.predict_not_eligible}</h4>
                <div class="progress mb-2" style="height: 25px;">
                    <div class="progress-bar bg-${isEligible ? 'success' : 'danger'}" 
                         role="progressbar" 
                         style="width: ${(confidence * 100).toFixed(0)}%">
                        ${(confidence * 100).toFixed(1)}%
                    </div>
                </div>
                <p class="text-muted mb-0">${t.predict_confidence}</p>
            `;
            
            resultCard.style.display = 'block';
            
            window.dashboard.showAlert(
                lang === 'ar' ? 'تم التنبؤ بنجاح ✅' : 'Prediction completed successfully ✅',
                'success'
            );
        } else {
            window.dashboard.showAlert(result.detail || t.error, 'danger');
        }
    } catch (error) {
        window.dashboard.showAlert(t.error + ': ' + error.message, 'danger');
    } finally {
        window.dashboard.hideLoading();
    }
}

