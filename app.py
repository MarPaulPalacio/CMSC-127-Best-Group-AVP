from flask import *
import sqlite3
import bcrypt


app = Flask(__name__)

def create_tables():
    # Opening a connection to our database
    connection = sqlite3.connect("project.db")
    cursor = connection.cursor()

    # SQL queries for creating tables
    create_account_table = """
    CREATE TABLE IF NOT EXISTS ACCOUNT (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100) NOT NULL UNIQUE,
        firstname VARCHAR(50) NOT NULL,
        middlename VARCHAR(50),
        lastname VARCHAR(100) NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE,
        user_type VARCHAR(8) CHECK (user_type IN ('customer','owner')) NOT NULL,
        password_ VARCHAR(255) NOT NULL
    );
    """

    create_establishment_table = """
    CREATE TABLE IF NOT EXISTS ESTABLISHMENT (
        establishment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        address_location VARCHAR(100) NOT NULL UNIQUE,
        establishment_name VARCHAR(50) NOT NULL UNIQUE,
        average_rating DECIMAL(3,2)
    );
    """

    create_food_table = """
    CREATE TABLE IF NOT EXISTS FOOD (
        food_id INTEGER PRIMARY KEY AUTOINCREMENT,
        foodname VARCHAR(80) NOT NULL UNIQUE,
        price DECIMAL(10,2) NOT NULL,
        food_type VARCHAR(20) CHECK (food_type IN ('meat','vegetable','seafood','dessert','beverage')) NOT NULL,
        average_rating DECIMAL(3,2),
        establishment_id INTEGER NOT NULL,
        CONSTRAINT food_establishment_fk FOREIGN KEY (establishment_id) 
            REFERENCES ESTABLISHMENT(establishment_id)
    );
    """

    create_establishment_review_table = """
    CREATE TABLE IF NOT EXISTS ESTABLISHMENT_REVIEW(
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        establishment_id INTEGER NOT NULL,
        rating DECIMAL(3,2) NOT NULL,
        establishment_review VARCHAR(255),
        review_datetime DATETIME NOT NULL,
        CONSTRAINT est_review_user_fk FOREIGN KEY (user_id) 
            REFERENCES ACCOUNT(user_id),
        CONSTRAINT est_review_establishment_fk FOREIGN KEY (establishment_id) 
            REFERENCES ESTABLISHMENT(establishment_id)
    );
    """

    create_food_review_table = """
    CREATE TABLE IF NOT EXISTS FOOD_REVIEW(
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        rating DECIMAL(3,2) NOT NULL,
        food_review VARCHAR(255),
        review_datetime DATETIME NOT NULL,
        CONSTRAINT fd_review_user_fk FOREIGN KEY (user_id)
            REFERENCES ACCOUNT(user_id),
        CONSTRAINT fd_review_food_fk FOREIGN KEY (food_id)
            REFERENCES FOOD(food_id)
    );
    """

    # Execute the SQL queries
    cursor.execute(create_account_table)
    cursor.execute(create_establishment_table)
    cursor.execute(create_food_table)
    cursor.execute(create_establishment_review_table)
    cursor.execute(create_food_review_table)

    # Commit changes and close connection
    connection.commit()
    connection.close()

# Call the function to create tables
create_tables()

# Create user account
@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("SignUp.html")
    elif request.method == 'POST':
        # Get data from form in signup.html
        username = request.form.get("username")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        middlename = request.form.get("middlename")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        user_type = request.form.get("usertype")

        # Check if any required field is empty
        if not username or not password or not firstname or not lastname or not email or not user_type:
            return "All fields are required."
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Convert the hashed password bytes to string for storage in the database
        hashed_password_str = hashed_password.decode('utf-8')

        # Open a connection to project database
        connection = sqlite3.connect("project.db")
        cursor = connection.cursor()

        # Check if the account already exists
        check_user_sql = "SELECT * FROM ACCOUNT WHERE username = ? OR email = ?"
        cursor.execute(check_user_sql, (username,email))
        existing_user = cursor.fetchone()

        # If username or email already exists, close connection
        if existing_user:
            connection.close()
            return "Account already exists."
        # Else add new user
        else: 
            add_user_sql = "INSERT INTO ACCOUNT (username, firstname, middlename, lastname, email, user_type, password_) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(add_user_sql, (username, firstname, middlename, lastname, email, user_type, hashed_password_str))
            connection.commit()
            connection.close()
            return "New account created."
        
# Read user account
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("Login.html")
    elif request.method == 'POST':
        # Get data from form in login.html
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "All fields are required."
        
        # Open a connection to project database
        connection = sqlite3.connect("project.db")
        cursor = connection.cursor()

        # Check if the account exists
        check_user_sql = "SELECT * FROM ACCOUNT WHERE username = ?"
        cursor.execute(check_user_sql, (username,))
        existing_user = cursor.fetchone()

        # If account does not exist, close connection
        if not existing_user:
            connection.close()
            return "Account does not exist."
        # Else verify password
        else:
            stored_password = existing_user[7] # Index 7 corresponds to the password_ field
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                connection.close()
                return "Login Success."
            else:
                connection.close()
                return "Login Failed."

# Update user account

# Delete user account

# Create food establishment
@app.route('/admin/add-establishment', methods = ['GET','POST'])
def addEst():
    if request.method == 'GET':
        return render_template("AddEst.html")
    elif request.method == 'POST':
        # Get data from form in AddEst.html
        est_name = request.form.get("est_name")
        ave_rating = 0.0
        addr_loc = request.form.get("addr_loc")
        
        # Check if any required field is empty
        if not est_name or not addr_loc:
            return "All fields are required."
        
        # Open a connection to project database
        connection = sqlite3.connect("project.db")
        cursor = connection.cursor()

        # Check if the establishment already exists
        check_est_sql = "SELECT * FROM ESTABLISHMENT WHERE establishment_name = ? OR address_location = ?"
        cursor.execute(check_est_sql, (est_name,addr_loc))
        existing_est = cursor.fetchone()

        # If establishment already exists, close connection
        if existing_est:
            connection.close()
            return "Establishment already exists."
        # Else add new establishment
        else:
            add_est_sql = "INSERT INTO ESTABLISHMENT (address_location, establishment_name, average_rating) VALUES (?,?,?)"        
            cursor.execute(add_est_sql, (addr_loc,est_name,ave_rating))
            connection.commit()
            connection.close()
            return "New establishment created."

# Read food establishment

# Update food establishment

# Delete food establishment

if __name__ == "__main__":
    app.run(debug=True, port=3002)
