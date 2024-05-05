from flask import Flask, render_template, request, url_for, flash, redirect, abort
import requests
import sqlite3
import uuid

app = Flask(__name__, static_folder='static')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('reservations.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

def generate_reservation_code(s):
    t="INFOTC4320"
    i = j = 0
    result = ""
    while i < len(s) and j < len(t):
        result += s[i] + t[j]
        i+=1
        j+=1
    while i < len(s):
        result += s[i]
        i += 1
    while j < len(t):
        result += t[j]
        j += 1
    return result
      

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

def calculate_total_sales():
    cost_matrix = get_cost_matrix()
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()

    total_sales = 0
    for reservation in reservations:
        seat_row = reservation['seatRow']
        seat_column = reservation['seatColumn']
        total_sales += cost_matrix[seat_row - 1][seat_column - 1]  # Adjust indices

    return total_sales

def create_seating_chart():
    conn = get_db_connection()

    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()

    chart = [['O' for x in range(4)] for y in range(12)]

    for seat in reservations:
        chart[seat['seatRow']][seat['seatColumn']] = 'X'

    for row in chart:
        print(row)        

    return chart
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form['siteselect']
        if not option:
            flash("Selection is required")
        elif option == "1":
            return redirect(url_for('admin'))
        elif option == "2":
            return redirect(url_for('reservations'))
        else:
            return redirect(url_for('index'))
    else:
        return render_template('index.html')
   # return render_template('index.html')


@app.route('/admin', methods=['GET','POST'])
def admin():
    authenticated = False
    if request.method == 'POST':
        conn = get_db_connection()

        users = conn.execute('SELECT * FROM admins').fetchall()

        conn.close()

        username = request.form['username']
        password = request.form['password']

        if not username:
            flash("Please enter a username")

        if not password:
            flash("Please enter a password")


        for user in users:
            if username == user['username'] and password == user['password']:
                authenticated = True
        
        if authenticated == False:
            flash("Login credentials invalid")
    
    chart = create_seating_chart()

    total_sales = calculate_total_sales()


    return render_template('admin.html', authenticated=authenticated, chart = chart,total_sales = total_sales)

@app.route('/reservations', methods=['GET','POST'])
def reservations():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        seat_row = int(request.form['row'])-1
        seat_column = int(request.form['column'])-1

        errors = {}
        if not first_name:
            errors['first_name'] = "First name is required"
        if not last_name:
            errors['last_name'] = "Last name is required"
        if seat_row < 0 or seat_row > 12:
            errors['row'] = "Invalid seat row"
        if seat_column < 0 or seat_column > 4:
            errors['column'] = "Invalid seat column"

        if errors:
            chart = create_seating_chart()
            return render_template('reservations.html', chart=chart, errors=errors)

        reservation_code = generate_reservation_code(first_name + last_name)

        conn = get_db_connection()
        conn.execute('INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)',
                     (first_name + ' ' + last_name, seat_row, seat_column, reservation_code))
        conn.commit()
        conn.close()

        flash("Reservation successful! Your Ticket number is: " + reservation_code)

        return redirect(url_for('index'))

    chart = create_seating_chart()
    return render_template('reservations.html',chart = chart)


app.run(host="0.0.0.0")