from flask import Flask, render_template, request, redirect, url_for
from bcrypt import hashpw, gensalt
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_very_strong_secret_key'  

def create_connection():
  conn = sqlite3.connect('database.db')
  return conn

def create_table(conn):
  cursor = conn.cursor()
  try:
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')
  except sqlite3.OperationalError as e:
    print(f"Table 'users' might already exist: {e}")
  conn.commit()

def hash_password(password):
  salt = gensalt()
  hashed_password = hashpw(password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')

def verify_password(hashed_password, password):
  return hashpw(password.encode('utf-8'), hashed_password.encode('utf-8')) == hashed_password

def login_user(user):
  session['user_id'] = user['id']

def is_logged_in():
  return 'user_id' in session

def logout_user():
  session.pop('user_id', None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    hashed_password = hash_password(password)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    return redirect(url_for('login'))
  return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(user['password'], password):
      login_user(user)
      return redirect(url_for('protected_page'))  
    else:
      return "Invalid username or password"

  return render_template('login.html')

@app.route('/protected_page')
def protected_page():
  if not is_logged_in():
    return redirect(url_for('login'))  
  return "Welcome to the protected page!"

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))

if __name__ == '__main__':
  create_table(create_connection())  
  app.run(debug=True)
