$(document).ready(function () {
    let formCount = $("#items-tbody tr").length;

    $("#add-item").click(function (){
        let newForm = $("#empty-form tr").clone()

        // Update form index
        newForm.html(function(i, html) {
            return html.replace(/__prefix__/g, formCount);
        });
        
        // Add the new form to the table
        $('#items-tbody').append(newForm);
        
        // Update form count in management form
        $('#id_requisitionitem_set-TOTAL_FORMS').val(++formCount);
        
        // Initialize the new form's event handlers
        initializeFormEvents(newForm);

        // After adding the new form, make sure it has a remove button that actually removes the row
        newForm.find('.remove-form').click(function() {
            $(this).closest('tr').remove();
            
            // Update form count in management form
            $('#id_receiveditem_set-TOTAL_FORMS').val(--formCount);
        });
    })
    // Remove item form
    $(document).on('click', '.remove-form', function() {
        $(this).closest('tr').remove();
        
        // Update form count in management form
        $('#id_receiveditem_set-TOTAL_FORMS').val(--formCount);
    });
    
    // Initialize existing forms
    $('.item-form').each(function() {
        initializeFormEvents($(this));
    });

    function initializeFormEvents(formRow) {
        const itemSelect = formRow.find('.item-select');
        const unitSelect = formRow.find('.unit-select');
        const quantityInput = formRow.find('.quantity-input');
        const unitCostInput = formRow.find('.unit-price');
        const totalCostInput = formRow.find('.total-cost');
        
        // When item changes, fetch available stock and units
        itemSelect.change(function() {
            const itemId = $(this).val();
            if (itemId) {
                $.ajax({
                    url: `/inventory/ajax/get-item-details`,
                    data: {
                        'item_id': itemId
                    },
                    dataType: 'json',
                    success: function(data) {
                        
                        // Update units dropdown
                        unitSelect.empty();
                        unitSelect.append('<option value="">---------</option>');
                        $.each(data.units, function(index, unit) {
                            unitSelect.append(`<option value="${unit.id}">${unit.unit}</option>`);
                        });
                        
                        // Reset other fields
                        unitCostInput.val('');
                        quantityInput.val('');
                        totalCostInput.val('');
                    }
                });
            } else {
                // Reset all fields if no item selected
                unitSelect.empty();
                unitSelect.append('<option value="">---------</option>');
                unitCostInput.val('');
                quantityInput.val('');
                totalCostInput.val('');
            }
        });
        
        // When unit changes, fetch unit price
        unitSelect.change(function() {
            const unitId = $(this).val();
            if (unitId) {
                $.ajax({
                    url: `/inventory/ajax/get-unit-price`,
                    data: {
                        'unit_id': unitId
                    },
                    dataType: 'json',
                    success: function(data) {
                        // Update unit cost
                        unitCostInput.val(data.buying_price);
                        
                        // Recalculate total if quantity exists
                        calculateTotal(quantityInput, unitCostInput, totalCostInput);
                    }
                });
            } else {
                unitCostInput.val('');
                totalCostInput.val('');
            }
        });
        
        // When quantity changes, calculate total cost
        quantityInput.on('input', function() {
            calculateTotal(quantityInput, unitCostInput, totalCostInput);
        });
        
        // When unit cost changes, calculate total cost
        unitCostInput.on('input', function() {
            calculateTotal(quantityInput, unitCostInput, totalCostInput);
        });
    }

    // Function to calculate total cost
    function calculateTotal(quantityInput, unitCostInput, totalCostInput) {
        const quantity = parseFloat(quantityInput.val()) || 0;
        const unitCost = parseFloat(unitCostInput.val()) || 0;
        const total = quantity * unitCost;
        
        totalCostInput.val(total.toFixed(2));
    }

    $("#receiving-form").submit(function (e) {
        let isValid = true

        // Check if there are any items
        if ($('#items-tbody tr').length === 0) {
            alert('Please add at least one item to the Receiving.');
            isValid = false;
        }
        
        // Check if all required fields are filled
        $('#items-tbody tr').each(function() {
            const item = $(this).find('.item-select').val();
            const unit = $(this).find('.unit-select').val();
            const quantity = $(this).find('.quantity-input').val();
            
            if (!item || !unit || !quantity) {
                alert('Please fill in all required fields for each item.');
                isValid = false;
                return false; // Break the loop
            }
        });
        
        // Check if units are loaded for each item
        $('#items-tbody tr').each(function() {
            const itemSelect = $(this).find('.item-select');
            const unitSelect = $(this).find('.unit-select');
            
            if (itemSelect.val() && unitSelect.find('option').length <= 1) {
                // Only the empty option exists, units weren't loaded
                alert('Please wait for units to load for all items or try selecting the item again.');
                isValid = false;
                return false;
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
    })

     // Handle delete checkboxes for existing items
     $('.item-form').each(function() {
        const row = $(this);
        const deleteCheckbox = row.find('input[id$="-DELETE"]');
        
        // If this is an existing item (has an ID)
        if (row.find('input[id$="-id"]').val()) {

            // Add a delete button instead
            const deleteButton = row.find('.delete-item-form');
            deleteCheckbox.parent().append(deleteButton);
            
            // When delete button is clicked
            deleteButton.click(function() {
                // Check the hidden checkbox
                deleteCheckbox.prop('checked', true);
                // Hide the row
                row.hide();
                // Optional: Show a message that the item will be removed when saved
                const alertMsg = $('<div class="alert alert-warning mt-2">This item will be removed when you save the requisition.</div>');
                $('#items-tbody').append(alertMsg);
            });
        }
    });
})