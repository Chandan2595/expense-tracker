from flask import Flask, request, jsonify, render_template
from ExpenseManagerLib import ExpenseManagerLib
import logging
import watchtower
import os
from werkzeug.utils import secure_filename

print("📁 Using ExpenseManagerLib from:", ExpenseManagerLib.__module__)

app = Flask(__name__)
manager = ExpenseManagerLib()

# Set up CloudWatch logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
try:
    handler = watchtower.CloudWatchLogHandler(log_group='ExpenseTrackerLogGroup')
    logger.addHandler(handler)
except Exception as e:
    print("CloudWatch logging failed:", e)

# ✅ Route for form-based expense submission
@app.route("/submit_expense", methods=["GET", "POST"])
def submit_expense():
    if request.method == "POST":
        description = request.form["description"]
        amount = request.form["amount"]
        date = request.form["date"]
        transaction = {
            "description": description,
            "amount": amount,
            "date": date
        }
        result = manager.save_transaction(transaction)
        return jsonify({"status": "success", "transaction": result})
    return render_template("form.html")

# ✅ API route to add expense
@app.route("/add_expense", methods=["POST"])
def add_expense():
    try:
        data = request.json
        print("📥 Incoming data:", data)
        result = manager.save_transaction(data)
        print("✅ Saved to DB:", result)
        return jsonify({"status": "success", "transaction": result})
    except Exception as e:
        print("❌ Error occurred:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ API route to split expenses (POST)
@app.route("/split_expense", methods=["POST"])
def split_expense():
    data = request.json
    result = manager.split_expense(data['total_amount'], data['users'])
    logger.info(f"Expense split result: {result}")
    return jsonify({"status": "success", "split_details": result})

# ✅ HTML form route to test split expenses in browser
@app.route("/split_form", methods=["GET", "POST"])
def split_form():
    if request.method == "POST":
        total_amount = float(request.form["total_amount"])
        users = request.form["users"].split(",")  # comma-separated usernames
        result = manager.split_expense(total_amount, users)
        return jsonify({"status": "success", "split_details": result})
    return '''
        <h2>Split Expense Form</h2>
        <form method="post">
            Total Amount: <input type="text" name="total_amount"><br><br>
            Users (comma-separated): <input type="text" name="users"><br><br>
            <input type="submit" value="Split Expense">
        </form>
    '''

# ✅ Upload receipt to S3
@app.route("/upload_receipt", methods=["POST"])
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join("/tmp", filename)
    file.save(filepath)

    try:
        manager.s3.upload_file(filepath, manager.s3_bucket, filename)
        logger.info(f"Receipt uploaded: {filename}")
        return jsonify({
            "status": "success",
            "message": f"Uploaded {filename} to S3",
            "s3_url": f"s3://{manager.s3_bucket}/{filename}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ Home route
@app.route("/", methods=["GET"])
def home():
    return "Welcome to the AI-Based Expense Tracker API! Use /add_expense, /submit_expense, /upload_receipt, /split_expense or /split_form."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
@app.route("/split_form", methods=["GET", "POST"])
def split_form():
    if request.method == "POST":
        total_amount = float(request.form["total_amount"])
        users = request.form.getlist("users")
        result = manager.split_expense(total_amount, users)
        return render_template("split_result.html", result=result)
    return render_template("split_form.html")
