import boto3
from decimal import Decimal
import uuid

class ExpenseManagerLib:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.s3 = boto3.client("s3")
        self.sns = boto3.client("sns")
        self.table_name = "ExpensesTable"
        self.s3_bucket = "expense-tracker-receipt"  # Replace if needed
        self.sns_topic_arn = "arn:aws:sns:eu-west-1:250738637992:ExpenseAlertTopic"

    def categorize_expense(self, description):
        desc = description.lower()
        if "food" in desc or "dinner" in desc:
            return "food"
        elif "uber" in desc or "taxi" in desc:
            return "transport"
        elif "rent" in desc or "lease" in desc:
            return "housing"
        else:
            return "others"

    def save_transaction(self, transaction):
        table = self.dynamodb.Table(self.table_name)

        # Generate transaction ID if missing
        if 'transaction_id' not in transaction or not transaction['transaction_id']:
            transaction['transaction_id'] = str(uuid.uuid4())

        if 'description' in transaction and 'amount' in transaction:
            transaction['category'] = self.categorize_expense(transaction['description'])
            transaction['amount'] = Decimal(str(transaction['amount']))

            print("✅ Using SNS ARN:", self.sns_topic_arn)

            # Save to DynamoDB
            table.put_item(Item=transaction)

            # Send SNS alert if amount > 1000
            if transaction['amount'] > Decimal("1000"):
                print("📢 Trying to send SNS alert...")
                try:
                    response = self.sns.publish(
                        TopicArn=self.sns_topic_arn,
                        Subject="High Expense Alert",
                        Message=f"An expense of ₹{transaction['amount']} was added."
                    )
                    print("✅ SNS alert response:", response)
                except Exception as e:
                    print("⚠️ SNS publish failed:", e)
            return transaction
        else:
            raise ValueError("Missing 'description' or 'amount' in transaction")

    # ✅ Add this function for expense splitting
    def split_expense(self, total_amount, users):
        try:
            total_amount = float(total_amount)
            num_users = len(users)
            if num_users == 0:
                raise ValueError("User list cannot be empty")
            share = round(total_amount / num_users, 2)
            return {user: share for user in users}
        except Exception as e:
            print("❌ Split expense error:", e)
            raise
