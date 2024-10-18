from flask import Flask, render_template, request, flash
import mysql.connector
import os

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)  # Secure random key for sessions

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
        INSERT INTO adet_user (first_name, middle_name, last_name, birthdate, email, address) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        # Data to be inserted
        data = (
            user_data['first_name'],
            user_data['middle_name'],
            user_data['last_name'],
            user_data['birthdate'],
            user_data['email'],
            user_data['address']
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

@app.route('/')
def registration_form():
    # Render the registration form by default
    return render_template('index.html', success=False)

@app.route('/register', methods=['POST'])
def register():
    # Collect data from the form
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    birthdate = request.form['birthdate']
    email = request.form['email']
    address = request.form['address']

    # Create a dictionary of the user's data
    user_data = {
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'birthdate': birthdate,
        'email': email,
        'address': address
    }

    # Save the data to the MySQL database
    save_to_mysql(user_data)

    # Flash a success message and render the form with success flag
    flash('Registration successful!', 'success')
    return render_template('index.html', success=True)

if __name__ == '__main__':
    app.run(debug=True)
