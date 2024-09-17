function addTable() {
    var row = document.querySelector('#addTableInput')
    if (row.style.visibility === "hidden" || row.style.visibility === "") {
        row.style.visibility = "visible";
    } else {
        row.style.visibility = "hidden";
    }
}

function addRow() {
    var row = document.querySelector('#addRowInput')
    if (row.style.visibility === "hidden" || row.style.visibility === "") {
        row.style.visibility = "visible";
    } else {
        row.style.visibility = "hidden"
    }
}

function howBtn() {
    var row = document.querySelector('.howToAdd-container')
    if (row.style.display === "none" || row.style.display === "") {
        row.style.display = "block";
    } else {
        row.style.display = "none";
    }
}


document.getElementById('createTableBtn').addEventListener('click', function() {
    let tableName = prompt("Enter table name: ").trim();
    if (tableName) {
        fetch(`/check_table_name/${tableName}`)
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                alert("Table name already exists. Please choose a different name.");
            } else {
                createTable(tableName);
            }
        })
    } else {
        alert("Table name cannot be empty or whitespace.");
    }
});

function createTable(tableName) {
    const PAYMENT_METHOD = ["CASH", "GCASH", "PAYMAYA", "CREDIT/DEBIT CARD"];
    let tableContainer = document.getElementById('tableContainer');
    tableContainer.innerHTML = `
        <h2>Table Name: <span class="badge text-bg-secondary">${tableName}</span></h2>
        <form action="/create" method="post">
            <input type="hidden" name="table_name" value="${tableName}">
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Gross</th>
                            <th scope="col">Interest</th>
                            <th scope="col">Payment</th>
                            <th scope="col">Due Date</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <tr>
                            <td><input autocomplete="off" autofocus class="form-control" name="name" placeholder="Name" required type="text"></td>
                            <td><input autocomplete="off" class="form-control" name="gross" placeholder="Gross" required type="number"></td>
                            <td><input autocomplete="off" class="form-control" name="interest" placeholder="Interest" required type="number"></td>
                            <td>
                                <select name="payment" class="form-select">
                                    <option disabled selected value="">Payment Method</option>
                                </select>
                            </td>
                            <td><input autocomplete="off" class="form-control text-center" name="due-date" required type="date"></td>
                            <td><button class="btn btn-success" onclick="addRow()" type="button">Add Row</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <button class="btn btn-primary" type="submit">Submit</button>
        </form>
    `;
    let paymentSelect = tableContainer.querySelector('select[name="payment"]');
    for (let i = 0; i < PAYMENT_METHOD.length; i++) {
        let option = document.createElement('option');
        option.value = PAYMENT_METHOD[i];
        option.text = PAYMENT_METHOD[i];
        paymentSelect.appendChild(option);
    }
}

function addRow() {
    const PAYMENT_METHOD = ["CASH", "GCASH", "PAYMAYA", "CREDIT/DEBIT CARD"];
    let tableBody = document.getElementById('tableBody');
    let newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input autocomplete="off" autofocus class="form-control" name="name" placeholder="Name" required type="text"></td>
        <td><input autocomplete="off" class="form-control" name="gross" placeholder="Gross" required type="number"></td>
        <td><input autocomplete="off" class="form-control" name="interest" placeholder="Interest" required type="number"></td>
        <td>
            <select name="payment" class="form-select">
                <option disabled selected value="">Payment Method</option>
            </select>
        </td>
        <td><input autocomplete="off" class="form-control text-center" name="due-date" required type="date"></td>
        <td><button class="btn btn-danger" onclick="removeRow(this)" type="button">Remove</button></td>
    `;
    tableBody.appendChild(newRow);
    let paymentSelect = newRow.querySelector('select[name="payment"]');
    for (let i = 0; i < PAYMENT_METHOD.length; i++) {
        let option = document.createElement('option');
        option.value = PAYMENT_METHOD[i];
        option.text = PAYMENT_METHOD[i];
        paymentSelect.appendChild(option);
    }
}

function removeRow(button) {
    button.parentElement.parentElement.remove();
}



function tableNewRow() {
    const PAYMENT_METHOD = ["CASH", "GCASH", "PAYMAYA", "CREDIT/DEBIT CARD"];
    let tableNewRow = document.getElementById('tableAddRow');
    let tableName = tableNewRow.getAttribute('data-table-name');
    let addRow = document.createElement('tr');
    addRow.classList.add('dynamic-row');
    addRow.innerHTML = `
        <input name="tableName" type="hidden" value="${tableName}" form="debtForm">
        <th scope="row">Name<input autocomplete="off" class="form-control text-center" name="name" placeholder="Name" type="text" required form="debtForm"></th>
        <th scope="row" colspan="2">Gross<input autocomplete="off" class="form-control text-center" name="gross" placeholder="Gross" type="number" required form="debtForm"></th>
        <th scope="row" colspan="2">Interest<input autocomplete="off" class="form-control text-center" name="interest" placeholder="Interest" type="number" required form="debtForm"></th>
        <th scope="row" colspan="2">Payment
            <select name="payment" class="form-select text-center" required form="debtForm">
                <option disabled selected value="">Payment Method</option>
            </select>
        </th>
        <th scope="row" colspan="2">Due Date<input autocomplete="off" class="form-control text-center" name="due-date" placeholder="Due Date" required type="date" form="debtForm"></th>
        <td colspan="2"><button class="btn btn-danger" onclick="tableRemoveRow(this)" type="button">Remove</button></td>
    `;
    tableNewRow.appendChild(addRow);

    document.getElementById('saveNewRowBtn').style.display = 'block';

    let paymentSelect = addRow.querySelector('select[name="payment"]');
    for (let i = 0; i < PAYMENT_METHOD.length; i++) {
        let option = document.createElement('option');
        option.value = PAYMENT_METHOD[i];
        option.text = PAYMENT_METHOD[i];
        paymentSelect.appendChild(option);
    }
}

function tableRemoveRow(button) {
    button.parentElement.parentElement.remove();

    // let tableNewRow = document.getElementById('tableAddRow');
    let dynamicRows = document.querySelectorAll('#tableAddRow .dynamic-row')
    if (dynamicRows.length === 0) {
        document.getElementById('saveNewRowBtn').style.display = 'none';
    }
}