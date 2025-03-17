import boto3
import uuid
from decimal import Decimal

class ExpenseManagerLib:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.s3 = boto3.client("s3")
        self.sns = boto3.client("sns")
        self.table_name = "ExpensesTable"
        self.s3_bucket = "your-s3-bucket-name"
        self.sns_topic_arn = "arn:aws:sns:your-region:your-account-id:ExpenseAlertTopic"

    def categorize_expense(self, description):
        categories = {
            "food": ["restaurant", "groceries", "dinner"],
            "transport": ["uber", "bus", "taxi"],
            "shopping": ["amazon", "electronics"],
            "others": []
        }
        desc = description.lower()
        for cat, keywords in categories.items():
            if any(word in desc for word in keywords):
                return cat
        return "others"

    def split_expense(self, total, users):
        split = round(total / len(users), 2)
        return {u: split for u in users}

    def save_transaction(self, transaction):
        table = self.dynamodb.Table(self.table_name)

        # Ensure required fields
        if 'transaction_id' not in transaction:
            transaction['transaction_id'] = str(uuid.uuid4())

        if 'description' in transaction and 'amount' in transaction:
            transaction['category'] = self.categorize_expense(transaction['description'])
            transaction['amount'] = Decimal(str(transaction['amount']))
            table.put_item(Item=transaction)

            # SNS notification for high expenses
            if transaction['amount'] > Decimal("1000"):
                print("📢 Trying to send SNS alert...")
                try:
                    response = self.sns.publish(
                        TopicArn=self.sns_topic_arn,
                        Subject="High Expense Alert",
                        Message=f"An expense of ₹{transaction['amount']} was added."
                    )
                    print("✅ SNS alert sent successfully:", response)
                except Exception as e:
                    print("⚠️ SNS publish failed:", e)

            return transaction
        else:
            raise ValueError("Missing 'description' or 'amount' in transaction")
