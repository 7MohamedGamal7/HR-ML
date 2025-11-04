// API Helper Functions

const API_BASE = window.location.origin;

const API = {
    // Health Check
    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE}/health/liveness`);
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            return null;
        }
    },
    
    // Upload
    async uploadFile(file, lang = 'ar') {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE}/upload/dataset?lang=${lang}`, {
                method: 'POST',
                body: formData
            });

            // التحقق من نوع المحتوى - Check content type
            const contentType = response.headers.get('content-type');

            if (!response.ok) {
                // محاولة قراءة رسالة الخطأ
                let errorMessage = `HTTP ${response.status}`;

                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } else {
                    // إذا كانت الاستجابة HTML (خطأ داخلي)
                    const errorText = await response.text();
                    if (errorText.includes('Internal Server Error')) {
                        errorMessage = lang === 'ar'
                            ? 'خطأ داخلي في الخادم. يرجى التحقق من صيغة الملف والمحاولة مرة أخرى.'
                            : 'Internal server error. Please check the file format and try again.';
                    } else {
                        errorMessage = errorText.substring(0, 200);
                    }
                }

                throw new Error(errorMessage);
            }

            // التحقق من أن الاستجابة JSON صالحة
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                throw new Error(lang === 'ar'
                    ? 'استجابة غير صالحة من الخادم'
                    : 'Invalid response from server');
            }

        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    },
    
    // Training
    async trainModel(config = {}, lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/?lang=${lang}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            return await response.json();
        } catch (error) {
            console.error('Training error:', error);
            throw error;
        }
    },
    
    async trainFromDatabase(tableName = null, query = null, limit = null, lang = 'ar') {
        let url = `${API_BASE}/train/from-database?lang=${lang}`;
        if (tableName) url += `&table_name=${tableName}`;
        if (query) url += `&query=${encodeURIComponent(query)}`;
        if (limit) url += `&limit=${limit}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('Database training error:', error);
            throw error;
        }
    },
    
    // Database
    async testDatabaseConnection(lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/database/test-connection?lang=${lang}`);
            return await response.json();
        } catch (error) {
            console.error('Database connection test error:', error);
            throw error;
        }
    },
    
    async getDatabaseTables(lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/database/tables?lang=${lang}`);
            return await response.json();
        } catch (error) {
            console.error('Get tables error:', error);
            throw error;
        }
    },
    
    async getTableInfo(tableName, lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/database/table-info?table_name=${tableName}&lang=${lang}`);
            return await response.json();
        } catch (error) {
            console.error('Get table info error:', error);
            throw error;
        }
    },
    
    async saveDatabaseConfig(config, lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/database/save-config?lang=${lang}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            return await response.json();
        } catch (error) {
            console.error('Save database config error:', error);
            throw error;
        }
    },
    
    async loadDatabaseConfig(lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/train/database/load-config?lang=${lang}`);
            return await response.json();
        } catch (error) {
            console.error('Load database config error:', error);
            throw error;
        }
    },
    
    // Prediction
    async predict(employeeData, lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/predict/?lang=${lang}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(employeeData)
            });
            return await response.json();
        } catch (error) {
            console.error('Prediction error:', error);
            throw error;
        }
    },
    
    async batchPredict(file, lang = 'ar') {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`${API_BASE}/predict/batch?lang=${lang}`, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Batch prediction error:', error);
            throw error;
        }
    },
    
    // Models
    async getModelInfo(lang = 'ar') {
        try {
            const response = await fetch(`${API_BASE}/predict/model-info?lang=${lang}`);
            return await response.json();
        } catch (error) {
            console.error('Get model info error:', error);
            return null;
        }
    },
    
    // Statistics (mock data for now - can be implemented as real endpoints later)
    async getStatistics() {
        // This would be a real API endpoint in production
        return {
            total_models: 5,
            total_predictions: 1234,
            average_accuracy: 0.92,
            total_employees: 450,
            recent_training: [
                {
                    id: 1,
                    date: new Date().toISOString(),
                    model_type: 'Random Forest',
                    accuracy: 0.94,
                    status: 'completed'
                },
                {
                    id: 2,
                    date: new Date(Date.now() - 86400000).toISOString(),
                    model_type: 'Gradient Boosting',
                    accuracy: 0.91,
                    status: 'completed'
                }
            ]
        };
    },
    
    async getTrainingHistory() {
        // Mock data - implement real endpoint later
        return [
            {
                id: 1,
                date: new Date().toISOString(),
                model_type: 'Random Forest',
                accuracy: 0.94,
                precision: 0.93,
                recall: 0.92,
                f1_score: 0.925,
                training_time: 45.2,
                data_size: 1000
            },
            {
                id: 2,
                date: new Date(Date.now() - 86400000).toISOString(),
                model_type: 'Gradient Boosting',
                accuracy: 0.91,
                precision: 0.90,
                recall: 0.89,
                f1_score: 0.895,
                training_time: 62.5,
                data_size: 1000
            },
            {
                id: 3,
                date: new Date(Date.now() - 172800000).toISOString(),
                model_type: 'Random Forest',
                accuracy: 0.89,
                precision: 0.88,
                recall: 0.87,
                f1_score: 0.875,
                training_time: 38.7,
                data_size: 800
            }
        ];
    },
    
    async getModelComparison() {
        // Mock data - implement real endpoint later
        return {
            models: ['Random Forest', 'Gradient Boosting', 'Logistic Regression'],
            metrics: {
                accuracy: [0.94, 0.91, 0.85],
                precision: [0.93, 0.90, 0.84],
                recall: [0.92, 0.89, 0.83],
                f1_score: [0.925, 0.895, 0.835]
            }
        };
    }
};

// Export API object
window.API = API;

