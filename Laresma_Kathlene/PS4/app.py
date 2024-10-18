from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
import hashlib

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'my_secret_key'  # Replace with a strong secret key

# MySQL Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'adet'
}

# Function to save data to MySQL database
def save_to_mysql(user_data):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to insert data into adet_user table
        query = """
        INSERT INTO adet_user (first_name, middle_name, last_name, birthdate, email, address, username, password) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Data to be inserted
        data = (
            user_data['first_name'],
            user_data['middle_name'],
            user_data['last_name'],
            user_data['birthdate'],
            user_data['email'],
            user_data['address'],
            user_data['username'],
            user_data['password']  # This should be hashed before saving
        )

        # Execute the query and commit changes
        cursor.execute(query, data)
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate login credentials
def validate_user(username, password):
    hashed_password = hash_password(password)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to retrieve user by username and password
        query = "SELECT * FROM adet_user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        return user  # Returns user data if valid, otherwise None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect data from the form
        user_data = {
            'first_name': request.form['first_name'],
            'middle_name': request.form['middle_name'],
            'last_name': request.form['last_name'],
            'birthdate': request.form['birthdate'],
            'email': request.form['email'],
            'address': request.form['address'],
            'username': request.form['username'],
            'password': hash_password(request.form['password'])  # Hash the password
        }

        # Save the data to the MySQL database
        save_to_mysql(user_data)

        # Flash a success message and redirect to login
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)

        if user:
            # Store user data in session
            session['user_id'] = user[0]  # Store user ID in session
            session['first_name'] = user[1]
            session['middle_name'] = user[2]
            session['last_name'] = user[3]
            session['birthdate'] = user[4]
            session['email'] = user[5]
            session['address'] = user[6]
            session['username'] = user[7]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You must log in first', 'danger')
        return redirect(url_for('login'))

    # Render the dashboard with the user's first name
    first_name = session['first_name']
    return render_template('dashboard.html', first_name=first_name)

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
