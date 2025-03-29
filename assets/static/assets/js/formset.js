document.addEventListener("DOMContentLoaded", function () {
    const formContainer = document.getElementById("form-container");
    const addButton = document.getElementById("add-form");
    let totalForms = document.querySelector("#id_form-TOTAL_FORMS");

    function updateFormIndices() {
        let forms = formContainer.querySelectorAll(".form-row");
        forms.forEach((row, index) => {
            row.querySelectorAll("input, select").forEach(input => {
                if (input.name) {
                    input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
                    input.id = input.id.replace(/form-\d+-/, `form-${index}-`);
                }
            });
        });
        totalForms.value = forms.length;
    }

    addButton.addEventListener("click", function () {
        let formNum = parseInt(totalForms.value);
        let newForm = formContainer.children[0].cloneNode(true);

        // Remove existing values in input fields
        newForm.querySelectorAll("input, select").forEach(input => {
            input.value = "";
        });

        // Ensure remove button works
        let removeBtn = newForm.querySelector(".remove-form");
        if (!removeBtn) {
            removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.classList.add("remove-form", "btn", "btn-danger", "btn-sm");
            removeBtn.innerText = "Remove";
            newForm.appendChild(removeBtn);
        }
        removeBtn.addEventListener("click", function () {
            removeFormRow(this);
        });

        formContainer.appendChild(newForm);
        updateFormIndices();
    });

    function removeFormRow(button) {
        let row = button.closest("tr");
        if (row) {
            row.remove();
            updateFormIndices();
        }
    }

    // Attach remove handlers to existing remove buttons
    document.querySelectorAll(".remove-form").forEach(button => {
        button.addEventListener("click", function () {
            removeFormRow(this);
        });
    });
});
