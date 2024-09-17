# DebtSuki: Debt Management and Financial Tracking System
#### Video Demo:  <https://www.youtube.com/watch?v=WJ0u_QXgadI>

#### Description:
DebtSuki is your go-to web app for managing and tracking debts with ease. It is designed to help manage of debtors efficiently, keeping track of your debtors, their payments, interest rate, and the overall history of transaction and changes for each debtor. It is implemented with a mix of HTML, CSS, Bootstrap, JavaScript, SQLite, and Flask.

Upon logging in, users are greeted with a welcome message and an overview of their debt tables. If no tables are created yet, users can easily get started with a single click. The home page provides a summary of all debt tables, including the number of debtors, creation dates, and payment statuses. Users can click on any table name to view detailed summaries, including debtor names, remaining amounts, interest rates, payment methods, and due dates. They can also perform actions like editing entries, adding interest, making partial payments, adding new debts, marking debts as paid, or deleting entries.

The history page displays of all transactions and changes for each debtor that allows users to filter by table and debtor for easy navigation. Designed to be responsive, DebtSuki looks great on any device, ensuring a seamless experience whether you’re on a desktop, tablet, or smartphone. In short, DebtSuki simplifies debt management, providing all the tools needed to keep track of financial records and make informed decisions, whether for personal or business use.

My project consists of the following files:
- **app.py**: This is the controller file that uses Flask to route different HTML files as pages. It also handles creating, editing, inserting, updating, and deleting data from the SQL database. The file uses Flask and SQL functions from the CS50 library.

- **helpers.py**: Similar to the problem set 9 finance, this file provides additional functions for app.py, including login_required and php for converting money into Philippine pesos format.

- **debt.db**: This is my SQLite database file that stores all the data related to users, debt tables, debtors, and transactions.

- **static/**: It contains my CSS and JavaScript files.

- **templates/**: The folder that contains all the HTML files or templates used in the website.

**TEMPLATES FOLDER**
- **layout.html**: This is the main HTML file where the default design codes of the website are placed.

- **index.html**: The page that consists of the project title and can be displayed to either logged-in or not logged-in users.

- **login.html**: The login page for users to enter their credentials and access their accounts.

- **register.html**: The register page for users to create their accounts on the website.

- **homepage.html**: The home page display for users after logging in that consist of the overview of all tables created if a table is already created or there is already an existing table like having a record.

- **summary.html**: The summary page where the summary of a specific table can be viewed.

- **summaryHome.html**: An HTML file with the same content as summary.html. It directs the user from the home page to a specific table directly without having to choose in summary.html by just clicking the name of the table listed in the home page overview of tables. I made this because I had hard time adding logic to the summary.html file and /summary route

- **history.html**: The history page where the history of each debtor in a table can be viewed. It’s like viewing the transactions you had with that particular person or debtor, keeping track of what happened.

- **historyView.html**: An HTML file with the same content as history.html. It directs the user from the summary page to a specific debtor of the selected table without having to select in the history page by just clicking the name of that debtor shown in the table you selected in the summary page. I made this because I had hard time adding logic to the history.html file and /history route
