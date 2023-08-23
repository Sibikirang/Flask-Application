from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysqlsibi',
    'db': 'namma_kadai',
    'cursorclass': pymysql.cursors.DictCursor
}

# Establish a connection to the database
connection = pymysql.connect(**db_config)



@app.route('/')
def index():
    # Fetch items from the database
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM item')
        items = cursor.fetchall()

        # Fetch purchases and sales
        cursor.execute('SELECT * FROM purchase')
        purchases = cursor.fetchall()
        
        cursor.execute('SELECT * FROM sales')
        sales = cursor.fetchall()

    # Calculate the initial cash balance (replace with actual calculation)
    initial_cash_balance = 1000

    # Calculate total purchase amount
    with connection.cursor() as cursor:
        cursor.execute('SELECT SUM(amount) AS total_purchase FROM purchase')
        total_purchase = cursor.fetchone()['total_purchase']

    # Calculate total sale amount
    with connection.cursor() as cursor:
        cursor.execute('SELECT SUM(amount) AS total_sale FROM sales')
        total_sale = cursor.fetchone()['total_sale']

    # Calculate the current cash balance
    cash_balance = initial_cash_balance + total_sale - total_purchase

    return render_template('index.html', cash_balance=cash_balance, items=items, purchases=purchases, sales=sales)


@app.route('/purchase', methods=['POST'])
def purchase():
    item_id = request.form['item_id']
    qty = int(request.form['qty'])
    rate = float(request.form['rate'])
    amount = qty * rate
    timestamp = datetime.now()

    try:
        # Update item quantity
        with connection.cursor() as cursor:
            cursor.execute('UPDATE item SET qty = qty + %s WHERE item_id = %s', (qty, item_id))
            
            # Insert into purchase table
            cursor.execute('INSERT INTO purchase (item_id, timestamp, qty, rate, amount) VALUES (%s, %s, %s, %s, %s)', (item_id, timestamp, qty, rate, amount))
        
        connection.commit()

    except Exception as e:
        print("Error:", str(e))
        connection.rollback()

    return redirect(url_for('index'))

@app.route('/sale', methods=['POST'])
def sale():
    item_id = request.form['item_id']
    qty = int(request.form['qty'])
    rate = float(request.form['rate'])
    amount = qty * rate
    timestamp = datetime.now()

    try:
        # Update item quantity
        with connection.cursor() as cursor:
            cursor.execute('UPDATE item SET qty = qty - %s WHERE item_id = %s', (qty, item_id))
            
            # Insert into sales table
            cursor.execute('INSERT INTO sales (item_id, timestamp, qty, rate, amount) VALUES (%s, %s, %s, %s, %s)', (item_id, timestamp, qty, rate, amount))
        
        connection.commit()

    except Exception as e:
        print("Error:", str(e))
        connection.rollback()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)