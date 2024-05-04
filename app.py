from flask import Flask, render_template, request, url_for, flash, redirect, abort
import requests

app = Flask(__name__, static_folder='static')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form['option']
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
    return render_template('admin.html')

@app.route('/reservations', methods=['GET','POST'])
def reservations():
    return render_template('reservations.html')


app.run(host="0.0.0.0")