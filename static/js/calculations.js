/**
 * JavaScript for Civil Engineering Calculations System
 * Developed by João Layon
 */

// Global application object
const EngineeringApp = {
    // Configuration
    config: {
        animationDuration: 300,
        toastDuration: 4000,
        chartColors: {
            primary: '#0d6efd',
            success: '#198754',
            info: '#0dcaf0',
            warning: '#ffc107',
            danger: '#dc3545'
        }
    },

    // Utility functions
    utils: {
        // Format numbers for engineering display
        formatNumber: function(num, decimals = 2) {
            if (typeof num !== 'number') return '0.00';
            return num.toLocaleString('pt-BR', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        },

        // Convert units
        convertUnit: function(value, fromUnit, toUnit) {
            const conversions = {
                // Length
                'm_to_cm': 100,
                'cm_to_m': 0.01,
                'm_to_mm': 1000,
                'mm_to_m': 0.001,
                
                // Area
                'm2_to_cm2': 10000,
                'cm2_to_m2': 0.0001,
                'm2_to_ha': 0.0001,
                'ha_to_m2': 10000,
                
                // Force
                'kN_to_N': 1000,
                'N_to_kN': 0.001,
                
                // Pressure
                'MPa_to_kPa': 1000,
                'kPa_to_MPa': 0.001,
                'Pa_to_kPa': 0.001,
                'kPa_to_Pa': 1000
            };

            const key = `${fromUnit}_to_${toUnit}`;
            return conversions[key] ? value * conversions[key] : value;
        },

        // Debounce function for input events
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Validate engineering input
        validateInput: function(value, min = null, max = null) {
            const num = parseFloat(value);
            if (isNaN(num)) return { valid: false, message: 'Valor deve ser numérico' };
            if (min !== null && num < min) return { valid: false, message: `Valor deve ser maior que ${min}` };
            if (max !== null && num > max) return { valid: false, message: `Valor deve ser menor que ${max}` };
            return { valid: true, value: num };
        }
    },

    // Toast notification system
    toast: {
        show: function(message, type = 'info', duration = null) {
            const toastDuration = duration || EngineeringApp.config.toastDuration;
            
            const toastHtml = `
                <div class="toast align-items-center text-bg-${type}" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${this.getIcon(type)} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
                    </div>
                </div>
            `;
            
            let toastContainer = document.getElementById('toastContainer');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toastContainer';
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                toastContainer.style.zIndex = '9999';
                document.body.appendChild(toastContainer);
            }
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement, { delay: toastDuration });
            
            toast.show();
            
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
            
            return toast;
        },

        getIcon: function(type) {
            const icons = {
                success: 'check-circle',
                info: 'info-circle',
                warning: 'exclamation-triangle',
                danger: 'times-circle'
            };
            return icons[type] || 'info-circle';
        },

        success: function(message, duration = null) {
            return this.show(message, 'success', duration);
        },

        error: function(message, duration = null) {
            return this.show(message, 'danger', duration);
        },

        warning: function(message, duration = null) {
            return this.show(message, 'warning', duration);
        },

        info: function(message, duration = null) {
            return this.show(message, 'info', duration);
        }
    },

    // Form validation and enhancement
    forms: {
        init: function() {
            // Add real-time validation to all forms
            document.querySelectorAll('form').forEach(form => {
                this.enhanceForm(form);
            });
        },

        enhanceForm: function(form) {
            // Add loading state on submit
            form.addEventListener('submit', function(e) {
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    EngineeringApp.forms.setLoadingState(submitButton, true);
                }
            });

            // Add real-time validation
            form.querySelectorAll('input[type="number"]').forEach(input => {
                input.addEventListener('input', EngineeringApp.utils.debounce((e) => {
                    EngineeringApp.forms.validateNumericInput(e.target);
                }, 300));
            });
        },

        setLoadingState: function(button, loading) {
            if (loading) {
                button.disabled = true;
                const originalText = button.textContent;
                button.dataset.originalText = originalText;
                button.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Calculando...
                `;
            } else {
                button.disabled = false;
                button.textContent = button.dataset.originalText || 'Calcular';
            }
        },

        validateNumericInput: function(input) {
            const value = input.value;
            const min = input.getAttribute('min');
            const max = input.getAttribute('max');
            
            const validation = EngineeringApp.utils.validateInput(value, 
                min ? parseFloat(min) : null, 
                max ? parseFloat(max) : null
            );

            if (!validation.valid && value !== '') {
                input.classList.add('is-invalid');
                let feedback = input.parentNode.querySelector('.invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    input.parentNode.appendChild(feedback);
                }
                feedback.textContent = validation.message;
            } else {
                input.classList.remove('is-invalid');
                const feedback = input.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.remove();
                }
            }
        }
    },

    // Chart functionality
    charts: {
        createMomentDiagram: function(canvasId, length, loadType, loadValue) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            
            // Generate moment diagram data
            const points = 50;
            const labels = [];
            const momentData = [];
            
            for (let i = 0; i <= points; i++) {
                const x = (i / points) * length;
                labels.push(x.toFixed(1));
                
                let moment;
                if (loadType === 'uniform') {
                    moment = (loadValue * x * (length - x)) / 2;
                } else { // point load at center
                    if (x <= length / 2) {
                        moment = (loadValue * x) / 2;
                    } else {
                        moment = (loadValue * (length - x)) / 2;
                    }
                }
                momentData.push(moment);
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Momento Fletor (kN.m)',
                        data: momentData,
                        borderColor: EngineeringApp.config.chartColors.primary,
                        backgroundColor: EngineeringApp.config.chartColors.primary + '20',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Diagrama de Momento Fletor'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Posição (m)'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Momento (kN.m)'
                            }
                        }
                    }
                }
            });
        },

        createShearDiagram: function(canvasId, length, loadType, loadValue) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            
            // Generate shear diagram data
            const labels = [];
            const shearData = [];
            
            if (loadType === 'uniform') {
                labels.push('0', length.toString());
                shearData.push(loadValue * length / 2, -loadValue * length / 2);
            } else { // point load
                labels.push('0', (length/2 - 0.01).toString(), (length/2 + 0.01).toString(), length.toString());
                shearData.push(loadValue / 2, loadValue / 2, -loadValue / 2, -loadValue / 2);
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Esforço Cortante (kN)',
                        data: shearData,
                        borderColor: EngineeringApp.config.chartColors.danger,
                        backgroundColor: EngineeringApp.config.chartColors.danger + '20',
                        fill: true,
                        stepped: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Diagrama de Esforço Cortante'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Posição (m)'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Cortante (kN)'
                            }
                        }
                    }
                }
            });
        }
    },

    // Local storage management
    storage: {
        save: function(key, data) {
            try {
                localStorage.setItem(`engineering_${key}`, JSON.stringify(data));
                return true;
            } catch (e) {
                console.error('Error saving to localStorage:', e);
                return false;
            }
        },

        load: function(key) {
            try {
                const data = localStorage.getItem(`engineering_${key}`);
                return data ? JSON.parse(data) : null;
            } catch (e) {
                console.error('Error loading from localStorage:', e);
                return null;
            }
        },

        remove: function(key) {
            try {
                localStorage.removeItem(`engineering_${key}`);
                return true;
            } catch (e) {
                console.error('Error removing from localStorage:', e);
                return false;
            }
        },

        // Save form data for recovery
        saveFormData: function(formId, data) {
            return this.save(`form_${formId}`, data);
        },

        // Load saved form data
        loadFormData: function(formId) {
            return this.load(`form_${formId}`);
        }
    },

    // Page-specific functionality
    pages: {
        structural: {
            init: function() {
                // Auto-save form data
                const form = document.querySelector('#structuralForm');
                if (form) {
                    form.addEventListener('input', EngineeringApp.utils.debounce(() => {
                        const formData = new FormData(form);
                        const data = Object.fromEntries(formData);
                        EngineeringApp.storage.saveFormData('structural', data);
                    }, 1000));
                }
            }
        },

        hydraulics: {
            init: function() {
                // Add unit conversion helpers
                const diameterInput = document.querySelector('input[name="pipe_diameter"]');
                if (diameterInput) {
                    diameterInput.addEventListener('change', function() {
                        const value = parseFloat(this.value);
                        if (value && value > 0) {
                            const area = Math.PI * Math.pow(value / 2000, 2); // Convert mm to m
                            const areaDisplay = document.getElementById('pipe-area-display');
                            if (areaDisplay) {
                                areaDisplay.textContent = `Área: ${EngineeringApp.utils.formatNumber(area * 10000, 2)} cm²`;
                            }
                        }
                    });
                }
            }
        },

        topography: {
            init: function() {
                // Add coordinate validation and preview
                const coordInput = document.querySelector('textarea[name="coordinates"]');
                if (coordInput) {
                    coordInput.addEventListener('input', EngineeringApp.utils.debounce(() => {
                        this.validateCoordinates(coordInput.value);
                    }, 500));
                }
            },

            validateCoordinates: function(coordinatesText) {
                const lines = coordinatesText.trim().split('\n');
                let validCount = 0;
                let errors = [];

                lines.forEach((line, index) => {
                    const trimmed = line.trim();
                    if (trimmed) {
                        const coords = trimmed.split(',');
                        if (coords.length === 2) {
                            const x = parseFloat(coords[0]);
                            const y = parseFloat(coords[1]);
                            if (!isNaN(x) && !isNaN(y)) {
                                validCount++;
                            } else {
                                errors.push(`Linha ${index + 1}: coordenadas inválidas`);
                            }
                        } else {
                            errors.push(`Linha ${index + 1}: formato incorreto (use x,y)`);
                        }
                    }
                });

                // Display validation feedback
                const feedback = document.getElementById('coord-feedback');
                if (feedback) {
                    if (errors.length > 0) {
                        feedback.innerHTML = `<div class="text-danger small">${errors.slice(0, 3).join('<br>')}</div>`;
                    } else if (validCount >= 3) {
                        feedback.innerHTML = `<div class="text-success small">${validCount} pontos válidos</div>`;
                    } else {
                        feedback.innerHTML = `<div class="text-warning small">Mínimo 3 pontos necessários</div>`;
                    }
                }
            }
        }
    },

    // Print functionality
    print: {
        generateReport: function(calculationType, data) {
            const printWindow = window.open('', '_blank');
            const reportHtml = this.buildReportHtml(calculationType, data);
            
            printWindow.document.write(reportHtml);
            printWindow.document.close();
            
            printWindow.onload = function() {
                printWindow.print();
            };
        },

        buildReportHtml: function(calculationType, data) {
            const currentDate = new Date().toLocaleDateString('pt-BR');
            
            return `
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Cálculo - ${calculationType}</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
                        .section { margin: 20px 0; }
                        .result { background: #f5f5f5; padding: 10px; border-left: 4px solid #007bff; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Sistema de Cálculos de Engenharia Civil</h1>
                        <h2>João Layon - Engenheiro Civil</h2>
                        <p>Data: ${currentDate}</p>
                    </div>
                    
                    <div class="section">
                        <h3>Tipo de Cálculo: ${calculationType}</h3>
                        <!-- Report content would be dynamically generated here -->
                    </div>
                    
                    <div class="section">
                        <p><strong>Nota:</strong> Este relatório foi gerado automaticamente pelo 
                           Sistema de Cálculos de Engenharia Civil desenvolvido por João Layon.</p>
                    </div>
                </body>
                </html>
            `;
        }
    },

    // Application initialization
    init: function() {
        console.log('Inicializando Sistema de Engenharia Civil - João Layon');
        
        // Initialize forms
        this.forms.init();
        
        // Initialize tooltips and popovers
        this.initBootstrapComponents();
        
        // Initialize page-specific functionality
        this.initPageSpecific();
        
        // Set up global event listeners
        this.setupGlobalListeners();
        
        // Show welcome message for new users
        this.showWelcomeMessage();
        
        console.log('Sistema inicializado com sucesso');
    },

    initBootstrapComponents: function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    initPageSpecific: function() {
        const path = window.location.pathname;
        
        if (path.includes('/structural')) {
            this.pages.structural.init();
        } else if (path.includes('/hydraulics')) {
            this.pages.hydraulics.init();
        } else if (path.includes('/topography')) {
            this.pages.topography.init();
        }
    },

    setupGlobalListeners: function() {
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                const submitButton = e.target.querySelector('button[type="submit"]');
                if (submitButton) {
                    setTimeout(() => {
                        this.forms.setLoadingState(submitButton, false);
                    }, 5000); // Reset after 5 seconds
                }
            }
        });

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.toast.info('Ctrl+S detectado - dados salvos automaticamente');
            }
        });
    },

    showWelcomeMessage: function() {
        const isFirstVisit = !this.storage.load('user_visited');
        
        if (isFirstVisit) {
            setTimeout(() => {
                this.toast.success('Bem-vindo ao Sistema de Engenharia Civil - João Layon!', 6000);
                this.storage.save('user_visited', true);
            }, 1000);
        }
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    EngineeringApp.init();
});

// Export for global use
window.EngineeringApp = EngineeringApp;
