# Bank App
## Description
A bank account application built with Python. It allows creating Debit/Credit account, setting credit limit for credit account and importing bank transactions.

For importing the transactions, a CSV file is required, formatted as following:

* Column titles: data, description, amount
* Delimiter: semicolon (;)

Sample CSV file contents:

```
date;description;amount
2023-07-25;"First transaction";-49.99
2023-07-25;"Second transaction";14.23
2023-07-26;"Third transaction";25.99
2023-07-27;"Fourth transaction";-4.99
2023-07-28;"Fifth transaction";-5.99
2023-07-31;"Sixth transaction";-8.99
2023-07-31;"Seventh transaction";10.99
```

By default, the app will try opening a DB file with account configuration and transactions history named "bank_account.db", located in the root directory of the app. If the file is missing, a new DB will be created and you will be prompted to enter account details.

## Usage
Install Python version 3.10+. In the app root folder, run the command using Terminal: 

```python -i bank_app.py```

To import transactions, use command:

```bank_acount.import_transactions(PATH_TO_FILE)```

To get account balanca on a particular date, use command below (if date parameter is omitted, today will be used by default):

```bank_acount.get_balance(DATE)```

To get list of transacitons in the particular date range, use this command (if date parameters are omitted, today will be used by default):

```bank_acount.get_transactions(DATE_FROM, DATE_TO)```