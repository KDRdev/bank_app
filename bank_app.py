import datetime
import csv

from sql_lib import SqlHelper
from exceptions import CreditLimitExceeded, TransactionDataMissing


DEFAULT_DATE = datetime.date.today()


class BankAccount:
    """Bank account class. Allows creating debit/credit account and importing transactions from CSV file."""
    
    def __init__(self, db_name, test=False):
        self.db_name = db_name
        self.account_type = ""
        self.credit_limit = 0.0
        self.sql = SqlHelper(db_name)
        if not test:
            self.setup_account()
        else:
            # Account setup process for test
            self.sql.execute("CREATE TABLE IF NOT EXISTS account(type TEXT, credit_limit REAL)")
            self.sql.execute(
                "CREATE TABLE IF NOT EXISTS account_transaction(date TEXT NOT NULL, description TEXT , amount REAL NOT NULL)"
            )
            self.sql.insert("INSERT INTO account VALUES (?, ?)", ('debit', 0.0))
            self.sql.conn.commit()
            
    def setup_account(self):
        """Method used for manual account setup (e.g. from CLI by the user)."""
        
        self.sql.execute("CREATE TABLE IF NOT EXISTS account(type TEXT, credit_limit REAL)")
        account_data = self.sql.fetch_one("SELECT * FROM account")
        # Setting up the account data
        if not account_data:
            account_type = ""
            print("No account found, let's create a new one.")
            while account_type.lower() not in ["debit", "credit"]:
                account_type = input("What type of account do you want to create? (Debit/Credit) ")
            
            if account_type.lower() == "credit":
                credit_limit = 0
                while not credit_limit < 0:
                    credit_limit = float(input("What credit limit should we set for your credit account (e.g. -1500.00)? "))
                self.credit_limit = credit_limit
            else:
                self.credit_limit = 0.0
                
            self.sql.insert("INSERT INTO account VALUES (?, ?)", (self.account_type, self.credit_limit))
            print("Account created successfully!")
        else:
            self.account_type = account_data[0]
            self.credit_limit = account_data[1]

        # Setting up transaction table
        self.sql.execute(
            "CREATE TABLE IF NOT EXISTS account_transaction(date TEXT NOT NULL, description TEXT , amount REAL NOT NULL)"
        )
    
    def get_transactions(self, date_start=DEFAULT_DATE, date_end=DEFAULT_DATE):
        """Queries the database for transactions created between date_start and date_end inclusively.

        Args:
            date_start (datetime.date, optional): Search for transactions created on or after this date. Defaults to DEFAULT_DATE.
            date_end (datetime.date, optional): Search for transactions created on or before this date. Defaults to DEFAULT_DATE.

        Returns:
            list: list of tuples containing transaction data.
        """
        return self.sql.fetch_all("SELECT * FROM account_transaction WHERE date BETWEEN ? AND ?", (date_start, date_end))

    def get_balance(self, date=DEFAULT_DATE):
        """Calculates the balance of the account on a given date.

        Args:
            date (datetime, optional): Date, for which we want to get the balance. Defaults to DEFAULT_DATE.

        Returns:
            float: account balance as a float.
        """
        res = self.sql.fetch_one("SELECT SUM(amount) FROM account_transaction WHERE date <= ?", (date,))
        return float(f"{res[0]:.2f}") if res[0] else 0.0
            
        
    def import_transactions(self, file_path):
        """Main method for importing transactions from a CSV file.

        Args:
            file_path (str): String with a relative path to the CSV file.

        Returns:
            float: account balance after importing transactions or prints an informational message.
        """        """"""
        transactions_data = self.get_transactions_data_from_file(file_path)
        if transactions_data:
            if len(transactions_data) == 1:
                transactions_data = tuple(transactions_data[0])
            self.create_bank_transactions(transactions_data)
            print(f"Transactions imported successfully! Current balance is {self.get_balance()}.")
            return 
        else:
            print("No transactions were imported.")

    def create_bank_transactions(self, transactions_data):
        """Method for creating bank transaction records in the database.

        Args:
            transactions_data (list(tuple)): List of tuples containing transaction values for bank transaction.
        """
        self.sql.insert(
            "INSERT INTO account_transaction VALUES(?, ?, ?)", transactions_data
        )
            
    def get_transactions_data_from_file(self, file_path):
        """Method processes the CSV file and returns transactions data for further processing.

        Args:
            file_path (str): String with a relative path to the CSV file.

        Returns:
            list(tuple): list of transactions data or prints an error message.
        """
        try:
            with open(file_path) as file:
                reader = csv.DictReader(file, delimiter=";")
                transactions_to_create = []
                import_balance = self.get_balance()
                for row in reader:
                    if self.transaction_is_valid(row) and not self.credit_limit_exceeded(import_balance, row["amount"]):
                        transactions_to_create.append((row["date"], row["description"], row["amount"]))
                        import_balance += float(row["amount"])
                return transactions_to_create
        except OSError:
            print(f"Could not open/read file. Make sure file exists within path: {file_path}")
        except (TransactionDataMissing, CreditLimitExceeded) as error:
            print(error)
            
    def transaction_is_valid(self, transaction_data):
        """Validates if all components needed for creating a bank transaction record.

        Args:
            transaction_data (dict): a dict containing transaction data.

        Raises:
            TransactionDataMissing: if one of the required fields is missing.

        Returns:
            bool: returns True if all required fields are present.
        """
        if not transaction_data.get("date") or not transaction_data.get("amount") or not transaction_data.get("description"):
            raise TransactionDataMissing(
                "One of the transactions is missing required data. Please check your file and try again."
            )
        return True

    def credit_limit_exceeded(self, current_balance, transaction_amount):
        """Checks if transaction amount exceeds the credit limit during import. For this we're using "temporary balance",
        calculated based on the current balance and each transaction amount.

        Args:
            current_balance (float): current bank account balance.
            transaction_amount (str): transaction amount from the import file.

        Raises:
            CreditLimitExceeded: if importing this transaction would cause the balance to go below the credit limit.

        Returns:
            bool: if the transaction amount does not exceed the credit limit.
        """
        if current_balance + float(transaction_amount) < self.credit_limit:
            if self.account_type == "debit":
                error_msg = f"Your account balance cannot be less than {self.credit_limit}"
            else:
                error_msg = f"You've reached your credit limit. Your account balance cannot be less than {self.credit_limit}"
            raise CreditLimitExceeded(error_msg)
        return False
            

bank_account = BankAccount("bank_account.db")
print("Account loaded. Current account balance:", bank_account.get_balance())
print("-----------------")
print("Get list of bank transactions using command bank_account.get_transactions()")
print("Get current bank account balance using command bank_account.get_balance()")
print("To import transactions from a CSV file, use command bank_account.import_transactions('file_path')")
