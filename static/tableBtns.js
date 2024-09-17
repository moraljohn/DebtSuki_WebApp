function editRow(id) {
    const row = document.querySelector(`#editRow${id}`)
    row.style.display = row.style.display === "none" ? "table-row" : "none"


    const rowBtn = document.getElementById('row');
    rowBtn.style.display = row.style.display === "none" ? "none" : "block"

    rowBtn.setAttribute('form', 'editRowForm' + id);

    document.getElementById(`addInterestRow${id}`).style.display = 'none';
    document.getElementById(`addPartial${id}`).style.display = 'none';
    document.getElementById(`addDebt${id}`).style.display = 'none';

    document.getElementById('interest').style.display = 'none';
    document.getElementById('partial').style.display = 'none';
    document.getElementById('debt').style.display = 'none';
}

function addInterestRow(id) {
    const row = document.querySelector(`#addInterestRow${id}`);
    row.style.display = row.style.display === "none" ? "table-row" : "none"
    
    const rowBtn = document.getElementById('interest');
    rowBtn.style.display = row.style.display === "none" ? "none" : "block"

    rowBtn.setAttribute('form', 'addInterestForm' + id);

    document.getElementById(`editRow${id}`).style.display = 'none';
    document.getElementById(`addPartial${id}`).style.display = 'none';
    document.getElementById(`addDebt${id}`).style.display = 'none';

    document.getElementById('row').style.display = 'none';
    document.getElementById('partial').style.display = 'none';
    document.getElementById('debt').style.display = 'none';
}

function addPartial(id) {
    const row = document.querySelector(`#addPartial${id}`);
    row.style.display = row.style.display === "none" ? "table-row" : "none"

    const rowBtn = document.getElementById('partial');
    rowBtn.style.display = row.style.display === "none" ? "none" : "block"

    rowBtn.setAttribute('form', 'addPartialForm' + id);

    document.getElementById(`addInterestRow${id}`).style.display = 'none';
    document.getElementById(`editRow${id}`).style.display = 'none';
    document.getElementById(`addDebt${id}`).style.display = 'none';

    document.getElementById('interest').style.display = 'none';
    document.getElementById('row').style.display = 'none';
    document.getElementById('debt').style.display = 'none';
}

function addDebt(id) {
    const row = document.querySelector(`#addDebt${id}`);
    row.style.display = row.style.display === "none" ? "table-row" : "none"

    const rowBtn = document.getElementById('debt');
    rowBtn.style.display = row.style.display === "none" ? "none" : "block"

    rowBtn.setAttribute('form', 'addDebtForm' + id);

    document.getElementById(`addInterestRow${id}`).style.display = 'none';
    document.getElementById(`addPartial${id}`).style.display = 'none';
    document.getElementById(`editRow${id}`).style.display = 'none';

    document.getElementById('interest').style.display = 'none';
    document.getElementById('partial').style.display = 'none';
    document.getElementById('row').style.display = 'none';
}



function showBtnRow(id) {
    const row = document.querySelector(`#showBtnRow${id}`);
    // row.style.display = row.style.display === "none" ? "table-row" : "none"
    if (row.style.display === 'table-row') {
        row.style.display = 'none';
    } else {
        const allRows = document.querySelectorAll('[id^="showBtnRow"]');
        allRows.forEach(row => {
            row.style.display = 'none';
        });

        const allEditRow = document.querySelectorAll('[id^="editRow"]');
        allEditRow.forEach(row => {
            row.style.display = 'none';
        });

        const allInterestRow = document.querySelectorAll('[id^="addInterestRow"]');
        allInterestRow.forEach(row => {
            row.style.display = 'none';
        });

        const allPartialRow = document.querySelectorAll('[id^="addPartial"]');
        allPartialRow.forEach(row => {
            row.style.display = 'none';
        });

        const allDebtRow = document.querySelectorAll('[id^="addDebt"]');
        allDebtRow.forEach(row => {
            row.style.display = 'none';
        });

        document.getElementById('row').style.display = 'none';
        document.getElementById('interest').style.display = 'none';
        document.getElementById('partial').style.display = 'none';
        document.getElementById('row').style.display = 'none';

        row.style.display = 'table-row';
    }

    if (row.style.display === "none") {
        document.getElementById('row').style.display = 'none';
        document.getElementById('interest').style.display = 'none';
        document.getElementById('partial').style.display = 'none';
        document.getElementById('debt').style.display = 'none';

        const row = document.querySelector(`#editRow${id}`)
        const interest = document.querySelector(`#addInterestRow${id}`);
        const partial = document.querySelector(`#addPartial${id}`);
        const debt = document.querySelector(`#addDebt${id}`);

        row.style.display = 'none';
        interest.style.display = 'none';
        partial.style.display = 'none';
        debt.style.display = 'none';
    }
}

// function hoverBtnRow(id) {
//     const row = document.querySelector(`#showBtnRow${id}`);
//     row.style.display = row.style.display === "none" ? "table-row" : "none"
// }

// function unhoverBtnRow(id) {
//     const row = document.querySelector(`#showBtnRow${id}`);
//     row.style.display = "none";
// }



function paidRow(id, name, tableName) {
    if (confirm(`Mark ${name} as paid?`)) {
        window.location.href = `/paidRow/${id}/${name}/${tableName}`
    }
}


function deleteRow(id, name, tableName) {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
        window.location.href = `/deleteRow/${id}/${name}/${tableName}`;
    }
}

function deleteTable(table_name) {
    if (confirm(`Are you sure you want to delete ${table_name}?`)) {
        window.location.href = `/deleteTable/${table_name}`
    }
}