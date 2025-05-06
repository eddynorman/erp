// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle dynamic form fields
    function setupDynamicFormFields() {
        // Department-Category relationship
        var departmentSelect = document.querySelector('#id_department');
        var categorySelect = document.querySelector('#id_category');
        
        if (departmentSelect && categorySelect) {
            departmentSelect.addEventListener('change', function() {
                var departmentId = this.value;
                if (departmentId) {
                    fetch(`/inventory/api/departments/${departmentId}/categories/`)
                        .then(response => response.json())
                        .then(data => {
                            categorySelect.innerHTML = '<option value="">---------</option>';
                            data.forEach(category => {
                                categorySelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                            });
                        });
                } else {
                    categorySelect.innerHTML = '<option value="">---------</option>';
                }
            });
        }

        // Item-Unit relationship
        var itemSelect = document.querySelector('#id_item');
        var unitSelect = document.querySelector('#id_unit');
        
        if (itemSelect && unitSelect) {
            itemSelect.addEventListener('change', function() {
                var itemId = this.value;
                if (itemId) {
                    fetch(`/inventory/api/items/${itemId}/units/`)
                        .then(response => response.json())
                        .then(data => {
                            unitSelect.innerHTML = '<option value="">---------</option>';
                            data.forEach(unit => {
                                unitSelect.innerHTML += `<option value="${unit.id}">${unit.unit}</option>`;
                            });
                        });
                } else {
                    unitSelect.innerHTML = '<option value="">---------</option>';
                }
            });
        }
    }

    // Handle stock calculations
    function setupStockCalculations() {
        var quantityInput = document.querySelector('#id_quantity');
        var unitPriceInput = document.querySelector('#id_unit_price');
        var totalCostInput = document.querySelector('#id_total_cost');
        
        if (quantityInput && unitPriceInput && totalCostInput) {
            function calculateTotal() {
                var quantity = parseFloat(quantityInput.value) || 0;
                var unitPrice = parseFloat(unitPriceInput.value) || 0;
                totalCostInput.value = (quantity * unitPrice).toFixed(2);
            }
            
            quantityInput.addEventListener('input', calculateTotal);
            unitPriceInput.addEventListener('input', calculateTotal);
        }
    }

    // Handle search functionality
    function setupSearch() {
        var searchInput = document.querySelector('.search-box input');
        var searchTimeout;
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    var currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('search', searchInput.value);
                    window.location.href = currentUrl.toString();
                }, 500);
            });
        }
    }

    // Handle filters
    function setupFilters() {
        var filterSelects = document.querySelectorAll('.filter-select');
        
        filterSelects.forEach(function(select) {
            select.addEventListener('change', function() {
                var currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set(this.name, this.value);
                window.location.href = currentUrl.toString();
            });
        });
    }

    // Handle stock level indicators
    function updateStockLevelIndicators() {
        var stockLevels = document.querySelectorAll('.stock-level');
        
        stockLevels.forEach(function(element) {
            var currentStock = parseFloat(element.dataset.current);
            var minimumStock = parseFloat(element.dataset.minimum);
            var optimumStock = parseFloat(element.dataset.optimum);
            
            element.classList.remove('low', 'medium', 'good');
            
            if (currentStock <= minimumStock) {
                element.classList.add('low');
            } else if (currentStock <= optimumStock) {
                element.classList.add('medium');
            } else {
                element.classList.add('good');
            }
        });
    }

    // Handle print functionality
    function setupPrint() {
        var printButtons = document.querySelectorAll('.print-button');
        
        printButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                window.print();
            });
        });
    }

    // Initialize all functionality
    setupDynamicFormFields();
    setupStockCalculations();
    setupSearch();
    setupFilters();
    updateStockLevelIndicators();
    setupPrint();
}); 