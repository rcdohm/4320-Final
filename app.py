from flask import Flask, render_template, request, url_for, flash, redirect, abort
import requests
import sqlite3

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


    return render_template('admin.html', authenticated=authenticated, chart = chart)

@app.route('/reservations', methods=['GET','POST'])
def reservations():
    chart = create_seating_chart()
    return render_template('reservations.html',chart = chart)


app.run(host="0.0.0.0")