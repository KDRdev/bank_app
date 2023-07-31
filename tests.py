import datetime
import csv
import os
import unittest

from bank_app import BankAccount

class TestBankAccount(unittest.TestCase):
    
    def setUp(self):
        self.bank_account = BankAccount('bank_account_test.db', test=True)
        self.conn = self.bank_account.sql.conn
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS account(type TEXT, credit_limit REAL)")
        c.execute(
            "CREATE TABLE IF NOT EXISTS account_transaction(date TEXT NOT NULL, description TEXT , amount REAL NOT NULL)"
        )
        c.execute("INSERT INTO account VALUES (?, ?)", ('debit', 0.0))
        self.conn.commit()
        c.close()
        
        self.header = ['date', 'description', 'amount']
        with open('test_transactions.csv', 'w', encoding='UTF8') as file:
            test_transaction_1 = ['2023-05-01', 'Test transaction 1', 70.00]
            test_transaction_2 = ['2023-05-02', 'Test transaction 2', -25.50]
            test_transaction_3 = ['2023-05-03', 'Test transaction 3', 10.00]
            writer = csv.writer(file, delimiter=';')
            writer.writerow(self.header)
            writer.writerow(test_transaction_1)
            writer.writerow(test_transaction_2)
            writer.writerow(test_transaction_3)
        
        with open('test_transactions_1.csv', 'w', encoding='UTF8') as file:
            new_test_transaction = ['2023-05-04', 'Test transaction 4', -100.00]
            writer = csv.writer(file, delimiter=';')
            writer.writerow(self.header)
            writer.writerow(new_test_transaction)
            
        with open('test_transactions_2.csv', 'w', encoding='UTF8') as file:
            new_test_transaction = ['2023-05-05', 'Test transaction 5', -60.00]
            writer = csv.writer(file, delimiter=';')
            writer.writerow(self.header)
            writer.writerow(new_test_transaction)

    def test_01_update_balance_on_transactions_import(self):
        self.assertEqual(0.0, self.bank_account.get_balance(), "Balance should be 0.0")
        self.bank_account.import_transactions('test_transactions.csv')
        self.assertEqual(54.5, self.bank_account.get_balance(), "Account balance should be 54.5 after importing transactions")

    def test_02_get_balance_on_specific_date(self):
        self.bank_account.import_transactions('test_transactions.csv')
        self.assertEqual(44.50, self.bank_account.get_balance(datetime.date(2023, 5, 2)), "Balance should be 44.50 on 2023-05-02")
        self.assertEqual(0.00, self.bank_account.get_balance(datetime.date(2023, 4, 30)), "Balance should be 0.00 on 2023-04-30")

    def test_03_debit_account_balance_negative_no_import(self):
        self.bank_account.import_transactions("test_transactions_1.csv")
        bank_transactions = self.bank_account.get_transactions(datetime.date(2023, 5, 4), datetime.date(2023, 5, 4))
        self.assertEqual(0, len(bank_transactions), "No transactions should be imported")
            
    def test_04_credit_account_balance_negative(self):
        self.bank_account.import_transactions('test_transactions.csv')
        self.bank_account.account_type = 'credit'
        self.bank_account.credit_limit = -100.00
        self.bank_account.import_transactions('test_transactions_1.csv')
        self.assertEqual(-45.50, self.bank_account.get_balance(), "Account balance should be -45.50 after importing transactions")
        self.bank_account.import_transactions('test_transaction_2.csv')
        self.assertEqual(-45.50, self.bank_account.get_balance(), "Account balance should be -45.50 after importing transactions")
    
    def tearDown(self):
        if self.conn:
            self.conn.close()
        os.remove("bank_account_test.db")
        os.remove("test_transactions.csv")
        os.remove("test_transactions_1.csv")
        os.remove("test_transactions_2.csv")
