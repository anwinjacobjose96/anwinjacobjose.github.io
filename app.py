from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, add_user, verify_user, add_period, get_periods, get_cycle_stats, clear_periods
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database
init_db()

# Add default user (only one user allowed)
add_user('admin', 'password123')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        add_period(session['user_id'], start_date)
        flash('Period date added successfully!', 'success')
        return redirect(url_for('index'))
    
    periods = get_periods(session['user_id'])
    stats = get_cycle_stats(session['user_id'])
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    return render_template('index.html', periods=periods, stats=stats, current_date=current_date)

@app.route('/clear-periods', methods=['POST'])
def clear_all_periods():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    clear_periods(session['user_id'])
    flash('All period data cleared successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verify_user(username, password)
        if user:
            session['username'] = username
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
