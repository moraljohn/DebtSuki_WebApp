function fetchItem() {
    const tableName = document.getElementById('specific_table').value;
    fetch(`/get_debtors/${tableName}`)
        .then(response => response.json())
        .then(data => {
            const nameSelect = document.getElementById('names_list');
            nameSelect.innerHTML = '<option disabled selected value="">Select a debtor</option>';
            data.names.forEach(name => {
                const option = document.createElement("option");
                option.value = name;
                option.name = name;
                option.text = name;
                nameSelect.appendChild(option);
            })
        })
}