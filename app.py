import datetime
from flask import *
import bcrypt
import psycopg2
import urllib

app = Flask(__name__)

# Set a secret key for the session
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# DEPLOYED PostgreSQL configuration
username = "postgres.dnwjgeuyjcopiwjpbygs"
password = "3,dq5?C%pZJ,vX9"  # Your Supabase password
hostname = "aws-0-ap-southeast-1.pooler.supabase.com"
port = "5432"
database_name = "postgres"

# Properly encode the password
encoded_password = urllib.parse.quote(password, safe='')

# Construct the connection string
supabase_connection_string = f"postgres://{username}:{encoded_password}@{hostname}:{port}/{database_name}"

# LOCAL PostgreSQL configuration
un = "admin127"
pw = "ilove127"
hn = "localhost"
p = "5432"
db_n = "project_db"

# LOCAL Construct the connection string
# supabase_connection_string = f"dbname={db_n} user={un} password={pw} host={hn} port={p}"

##############################################################################################################################################################
# TABLE CREATION
##############################################################################################################################################################

# Function to create tables
def create_tables():
    # Opening a connection to our database
    connection = psycopg2.connect(supabase_connection_string)

    cursor = connection.cursor()

    # SQL queries for creating tables
    create_account_table = """
    CREATE TABLE IF NOT EXISTS ACCOUNT (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        firstname VARCHAR(50) NOT NULL,
        middlename VARCHAR(50),
        lastname VARCHAR(100) NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE,
        user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('customer', 'owner','admin')),
        password_ VARCHAR(255) NOT NULL
    )
    """

    create_establishment_table = """
    CREATE TABLE IF NOT EXISTS ESTABLISHMENT (
        establishment_id SERIAL PRIMARY KEY,
        address_location VARCHAR(100) NOT NULL UNIQUE,
        establishment_name VARCHAR(50) NOT NULL UNIQUE,
        average_rating DECIMAL(3,2),
        owner_id INT,
        CONSTRAINT establishment_owner_fk FOREIGN KEY (owner_id) 
            REFERENCES ACCOUNT(user_id)
    )
    """

    create_food_table = """
    CREATE TABLE IF NOT EXISTS FOOD (
        food_id SERIAL PRIMARY KEY,
        foodname VARCHAR(80) NOT NULL UNIQUE,
        price DECIMAL(10,2) NOT NULL,
        food_type VARCHAR(20) NOT NULL CHECK (food_type IN ('meat','vegetable','seafood','dessert','beverage')),
        average_rating DECIMAL(3,2),
        establishment_id INT NOT NULL,
        creator_id INT NOT NULL,
        CONSTRAINT food_establishment_fk FOREIGN KEY (establishment_id) 
            REFERENCES ESTABLISHMENT(establishment_id),
        CONSTRAINT food_creator_fk FOREIGN KEY (creator_id) 
            REFERENCES ACCOUNT(user_id)
    )
    """

    create_establishment_review_table = """
    CREATE TABLE IF NOT EXISTS ESTABLISHMENT_REVIEW (
        review_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        establishment_id INT NOT NULL,
        rating DECIMAL(3,2) NOT NULL,
        establishment_review VARCHAR(255),
        review_datetime TIMESTAMP NOT NULL,
        CONSTRAINT est_review_user_fk FOREIGN KEY (user_id) 
            REFERENCES ACCOUNT(user_id),
        CONSTRAINT est_review_establishment_fk FOREIGN KEY (establishment_id) 
            REFERENCES ESTABLISHMENT(establishment_id)
    )
    """

    create_food_review_table = """
    CREATE TABLE IF NOT EXISTS FOOD_REVIEW (
        review_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        food_id INT NOT NULL,
        rating DECIMAL(3,2) NOT NULL,
        food_review VARCHAR(255),
        review_datetime TIMESTAMP NOT NULL,
        CONSTRAINT fd_review_user_fk FOREIGN KEY (user_id)
            REFERENCES ACCOUNT(user_id),
        CONSTRAINT fd_review_food_fk FOREIGN KEY (food_id)
            REFERENCES FOOD(food_id)
    )
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

##############################################################################################################################################################
# ADDITIONAL ROUTES
##############################################################################################################################################################

# Home/Landing Page
@app.route('/')
def index():
    return render_template("Landing.html")

# Unauthorized route
@app.route('/unauthorized')
def unauth():
    return render_template("Unauthorized.html")

##############################################################################################################################################################
# ACCOUNT METHODS
##############################################################################################################################################################

# Sign up user account
@app.route('/signup', methods=['GET', 'POST'])
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
            flash("All fields are required.", "error")
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Convert the hashed password bytes to string for storage in the database
        hashed_password_str = hashed_password.decode('utf-8')

        # Open a connection to project database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # Check if the account already exists
        check_user_sql = "SELECT * FROM ACCOUNT WHERE username = %s OR email = %s"
        cursor.execute(check_user_sql, (username, email))
        existing_user = cursor.fetchone()

        # If username or email already exists, close connection
        if existing_user:
            connection.close()
            flash("Account already exists.", "error")
            return redirect(url_for('signup'))
        # Else add new user
        else: 
            add_user_sql = "INSERT INTO ACCOUNT (username, firstname, middlename, lastname, email, user_type, password_) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(add_user_sql, (username, firstname, middlename, lastname, email, user_type, hashed_password_str))
            connection.commit()
            connection.close()
            flash("Account created successfully!", "success")
            return redirect(url_for('login'))  # Redirect to homepage or any other desired page

# Login user account 
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("Login.html")
    elif request.method == 'POST':
        # Get data from form in login.html
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('login'))
        
        # Open a connection to the project database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # Check if the account exists
        check_user_sql = "SELECT * FROM ACCOUNT WHERE username = %s"
        cursor.execute(check_user_sql, (username,))
        existing_user = cursor.fetchone()

        # If account does not exist, close connection
        if not existing_user:
            connection.close()
            flash("Account does not exist.", "error")
            return redirect(url_for('login'))
        # Else verify password
        else:
            stored_password = existing_user[7] # Index 7 corresponds to the password_ field
            print("Stored Password:", stored_password)
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                # Get the user ID from the database
                user_id = existing_user[0]  # Index 0 corresponds to the user_id field
                # Store the user ID in the session
                session['user_id'] = user_id
                # Check if user type is owner
                if existing_user[6] == 'owner' or existing_user[6] == 'admin':  # Index 6 corresponds to the user_type field
                    connection.close()
                    return redirect(url_for('see_est'))
                else:
                    connection.close()
                    return redirect(url_for('view_est'))
            else:
                connection.close()
                flash("Wrong password!", "error")
                return redirect(url_for('login'))

# Logout
@app.route('/logout', methods=['GET'])
def logout():
    # Remove user_id from session
    session.pop('user_id', None)
    return redirect(url_for('index'))  # Redirect to homepage or any other desired page

# Helper function for user authentication
def get_user_id_from_database(username):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM ACCOUNT WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]  # Fetch the user ID from the result
    connection.close()
    return user_id

##############################################################################################################################################################
# RUD METHODS OF ACCOUNTS FOR ADMIN
##############################################################################################################################################################

# See all user accounts as admin
@app.route('/admin/user-list', methods=['GET'])
def see_users():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    
    # Get user ID from the session
    user_id = session['user_id']

    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Fetch the user type
    cursor.execute("SELECT user_type FROM ACCOUNT WHERE user_id = %s", (user_id,))
    user_type = cursor.fetchone()[0]

    # If the user is admin, continue
    if user_type == 'admin':    
        cursor.execute("SELECT user_id, username, email, user_type, firstname, middlename, lastname FROM ACCOUNT")
        users = cursor.fetchall()
        connection.close()
        return render_template("UserList.html", users=users)
    else:
        return redirect(url_for('unauth'))

# Update user account as admin
@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'GET':
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, username, email, user_type, firstname, middlename, lastname FROM ACCOUNT WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        connection.close()
        return render_template('EditUser.html', user=user)
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user_type = request.form['user_type']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE ACCOUNT
            SET username = %s, email = %s, user_type = %s, firstname = %s, middlename = %s, lastname = %s
            WHERE user_id = %s
        """, (username, email, user_type, firstname, middlename, lastname, user_id))
        connection.commit()
        connection.close()
        return redirect(url_for('see_users'))

# Delete user account as admin
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM ACCOUNT WHERE user_id = %s", (user_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('see_users'))

##############################################################################################################################################################
# CRUD METHODS OF ESTABLISHMENT FOR ADMIN
##############################################################################################################################################################

# Create food establishment
@app.route('/admin/add-establishment', methods=['GET', 'POST'])
def add_est():
    if request.method == 'GET':
        return render_template("AddEst.html")
    elif request.method == 'POST':
        # Get data from form in AddEst.html
        est_name = request.form.get("est_name")
        addr_loc = request.form.get("addr_loc")
        
        # Check if any required field is empty
        if not est_name or not addr_loc:
            flash("All fields are required.", "error")
            return redirect(url_for('add_est'))
        
        # Check if the user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))
        
        # Get the user ID from the session
        owner_id = session['user_id']

        # Open a connection to the project database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # Check if the establishment already exists
        check_est_sql = "SELECT * FROM ESTABLISHMENT WHERE establishment_name = %s OR address_location = %s"
        cursor.execute(check_est_sql, (est_name, addr_loc))
        existing_est = cursor.fetchone()

        # If establishment already exists, close connection
        if existing_est:
            connection.close()
            flash("Establishment already exists.", "error")
            return redirect(url_for('add_est'))
        # Else add new establishment
        else:
            add_est_sql = "INSERT INTO ESTABLISHMENT (address_location, establishment_name, owner_id, average_rating) VALUES (%s, %s, %s, %s)"        
            cursor.execute(add_est_sql, (addr_loc, est_name, owner_id, 0.0))
            connection.commit()
            connection.close()
            return redirect(url_for('see_est'))

# Read food establishment as Owner/Admin
@app.route('/admin/establishment-list', methods=['GET', 'POST'])
def see_est():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']

    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Check the user type
    cursor.execute("SELECT user_type FROM ACCOUNT WHERE user_id = %s", (user_id,))
    user_type = cursor.fetchone()[0]

    if request.method == 'GET':
        # Retrieve sorting and filtering parameters from the request URL
        sort_by = request.args.get('sort')
        filter_by = request.args.get('filter')

        # Base query to select establishments
        if user_type == 'admin':
            query = "SELECT establishment_id, establishment_name, address_location, average_rating FROM ESTABLISHMENT"
            query_params = []
        elif user_type == 'owner':
            query = "SELECT establishment_id, establishment_name, address_location, average_rating FROM ESTABLISHMENT WHERE owner_id = %s"
            query_params = [user_id]
        else:
            connection.close()
            return redirect(url_for('unauth'))

        # Apply filtering based on average rating if a filter is specified
        if filter_by:
            filter_query = {
                '1-1.99': 'AND average_rating BETWEEN 1 AND 1.99',
                '2-2.99': 'AND average_rating BETWEEN 2 AND 2.99',
                '3-3.99': 'AND average_rating BETWEEN 3 AND 3.99',
                '4-4.99': 'AND average_rating BETWEEN 4 AND 4.99',
                '5': 'AND average_rating = 5 ',
            }
            query += f" {filter_query.get(filter_by, '')}"

        # Apply sorting based on the specified sort parameter
        if sort_by:
            sort_query = {
                'name_asc': 'ORDER BY establishment_name ASC',
                'name_desc': 'ORDER BY establishment_name DESC',
                'rating_asc': 'ORDER BY average_rating ASC',
                'rating_desc': 'ORDER BY average_rating DESC'
            }
            query += f" {sort_query.get(sort_by, '')}"

        # Execute the final SQL query
        cursor.execute(query, query_params)
        # Fetch all the results from the executed query
        establishments = cursor.fetchall()
        # Close the connection
        connection.close()

        return render_template("EstList.html", establishments=establishments)
    elif request.method == 'POST':
        est_search = request.form.get('est_search')
        est_address = request.form.get('est_address')

        if user_type == 'admin':
            query_params = [f"%{est_search}%", f"{est_address}%"]
            est_name_query = """SELECT E.establishment_id, E.establishment_name, E.address_location, E.average_rating
                FROM ESTABLISHMENT E
                WHERE E.establishment_name ILIKE %s AND E.address_location ILIKE %s"""
        elif user_type == 'owner':
            query_params = [f"%{est_search}%", user_id, f"{est_address}%"]
            est_name_query = """SELECT E.establishment_id, E.establishment_name, E.address_location, E.average_rating
                FROM ESTABLISHMENT E
                WHERE E.establishment_name ILIKE %s AND E.owner_id = %s AND E.address_location ILIKE %s"""
        else:
            connection.close()
            return redirect(url_for('unauth'))

        # Connect to the database
        with psycopg2.connect(supabase_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(est_name_query, query_params)
                establishments = cursor.fetchall()

        return render_template('EstList.html', establishments=establishments)

# Update food establishment
@app.route('/admin/edit-establishment/<int:establishment_id>', methods=['GET', 'POST'])
def edit_est(establishment_id):
    if request.method == 'GET':
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT establishment_id, establishment_name, address_location, average_rating FROM ESTABLISHMENT WHERE establishment_id = %s", (establishment_id,))
        establishment = cursor.fetchone()
        connection.close()
        return render_template('EditEst.html', establishment=establishment)
    elif request.method == 'POST':
        est_name = request.form['est_name']
        addr_loc = request.form['addr_loc']
        # ave_rating = request.form['ave_rating']
        
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE ESTABLISHMENT
            SET establishment_name = %s, address_location = %s
            WHERE establishment_id = %s
        """, (est_name, addr_loc, establishment_id))
        connection.commit()
        connection.close()
        return redirect(url_for('see_est'))

# Delete food establishment
@app.route('/admin/delete-establishment/<int:establishment_id>', methods=['POST'])
def delete_est(establishment_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM ESTABLISHMENT WHERE establishment_id = %s", (establishment_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('see_est'))

##############################################################################################################################################################
# READ METHODS OF ESTABLISHMENT FOR CUSTOMER
##############################################################################################################################################################

# Read food establishment as Customer
@app.route('/customer/establishment-list', methods=['GET','POST'])
def view_est():
    # Check if the user is logged in by verifying if 'user_id' is in the session
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
        
    if request.method == 'GET':
        # Retrieve sorting and filtering parameters from the request URL
        sort_by = request.args.get('sort')
        filter_by = request.args.get('filter')

        # Connecting to database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # SQL query to retrieve establishment details along with their reviews
        query = """
            SELECT E.establishment_id, E.establishment_name, E.address_location, E.average_rating, COALESCE(RE.reviews, '{}') AS reviews
            FROM ESTABLISHMENT E
            LEFT JOIN (
                SELECT establishment_id, json_agg(json_build_object('review_id', review_id, 'user_id', user_id, 'rating', rating, 'review', establishment_review, 'datetime', review_datetime)) AS reviews
                FROM ESTABLISHMENT_REVIEW
                GROUP BY establishment_id
            ) RE ON E.establishment_id = RE.establishment_id
        """

        # Apply filtering based on average rating if a filter is specified
        if filter_by:
            filter_query = {
                '1-1.99': 'WHERE E.average_rating BETWEEN 1 AND 1.99',
                '2-2.99': 'WHERE E.average_rating BETWEEN 2 AND 2.99',
                '3-3.99': 'WHERE E.average_rating BETWEEN 3 AND 3.99',
                '4-4.99': 'WHERE E.average_rating BETWEEN 4 AND 4.99',
                '5' : 'WHERE E.average_rating = 5',
            }
            query += f" {filter_query.get(filter_by, '')}"

        # Apply sorting based on the specified sort parameter
        if sort_by:
            sort_query = {
                'name_asc': 'ORDER BY E.establishment_name ASC',
                'name_desc': 'ORDER BY E.establishment_name DESC',
                'rating_asc': 'ORDER BY E.average_rating ASC',
                'rating_desc': 'ORDER BY E.average_rating DESC'
            }
            query += f" {sort_query.get(sort_by, '')}"

        # Execute the final SQL query
        cursor.execute(query)
        # Fetch all the results from the executed query
        establishments = cursor.fetchall()
        # Close database
        connection.close()

        return render_template("ViewEst.html", establishments=establishments)
    elif request.method=='POST':
        est_search = request.form.get('est_search')
        est_address = request.form.get('est_address')

        query_params = [f"%{est_search}%", f"{est_address}%"]
        
        # Building dynamic query based on provided filters
        est_name_query = """SELECT E.establishment_id, E.establishment_name, E.address_location, E.average_rating
            FROM ESTABLISHMENT E
            where E.establishment_name ILIKE %s AND E.address_location ILIKE %s"""
        
        
        # Connect to the database
        with psycopg2.connect(supabase_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(est_name_query, query_params)
                establishments = cursor.fetchall()

        return render_template('ViewEst.html', establishments=establishments)

##############################################################################################################################################################
# CRUD METHODS OF FOOD FOR ADMIN
##############################################################################################################################################################

# Create food item 
@app.route('/admin/add-food', methods=['GET','POST'])
def add_fd():
    if request.method == 'GET':
        # Get the user ID from the session
        user_id = session['user_id']

        # Open a connection to the database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # Fetch establishments owned by the current user
        cursor.execute("SELECT establishment_id, establishment_name FROM ESTABLISHMENT WHERE owner_id = %s", (user_id,))
        establishments = cursor.fetchall()

        # Close the connection
        connection.close()

        # Pass the establishments to the template
        return render_template("AddFood.html", establishments=establishments)
    elif request.method == 'POST':
        # Get data from form in AddFood.html
        foodname = request.form.get("foodname")
        price = request.form.get("price")
        food_type = request.form.get("food_type")
        est_id = request.form.get("est_id")

        # Check if any required field is empty
        if not foodname or not price or not food_type or not est_id:
            flash("All fields are required.", "error")
            return redirect(url_for('add_fd'))
        
        # Check if user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))
        
        # Get the user ID from the session
        owner_id = session['user_id']

        # Open a connection to the project database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()

        # Check if the food item already exists
        check_fd_sql = "SELECT * FROM FOOD WHERE foodname = %s AND establishment_id = %s"
        cursor.execute(check_fd_sql, (foodname,est_id))
        existing_fd = cursor.fetchone()

        # If food item already exists, close connection
        if existing_fd:
            connection.close()
            flash("Food item already exists in that establishment.", "error")
            return redirect(url_for('add_fd'))
        else:
            add_fd_sql = "INSERT INTO FOOD (foodname, price, food_type, average_rating, establishment_id, creator_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(add_fd_sql,(foodname,price,food_type,0.0,est_id,owner_id))
            connection.commit()
            connection.close()
            return redirect(url_for('see_fd'))

# Read food item as admin/owner
@app.route('/admin/food-list', methods=['GET', 'POST'])
def see_fd():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    
    # Get the user ID from the session
    user_id = session['user_id']

    # Initialize query parameters
    food_search = None
    price_range = None
    food_type = None
    sort_by = None

    # Handle POST requests for form submissions
    if request.method == 'POST':
        food_search = request.form.get('food_search')
        price_range = request.form.get('price_range')
        food_type = request.form.get('type')
        sort_by = request.form.get('sort')

        # Redirect to the GET route with query parameters
        return redirect(url_for('see_fd', food_search=food_search, price_range=price_range, type=food_type, sort=sort_by))

    # Handle GET requests for URL parameters
    elif request.method == 'GET':
        food_search = request.args.get('food_search')
        price_range = request.args.get('price_range')
        food_type = request.args.get('type')
        sort_by = request.args.get('sort')

    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Check the user type
    cursor.execute("SELECT user_type FROM ACCOUNT WHERE user_id = %s", (user_id,))
    user_type = cursor.fetchone()[0]

    # Base query to select food items
    query = """
        SELECT FOOD.food_id, FOOD.foodname, FOOD.price, FOOD.food_type, FOOD.average_rating, ESTABLISHMENT.establishment_name
        FROM FOOD
        JOIN ESTABLISHMENT ON FOOD.establishment_id = ESTABLISHMENT.establishment_id
    """
    
    query_params = []

    # Apply filtering based on user type
    if user_type == 'owner':
        query += " WHERE FOOD.creator_id = %s"
        query_params.append(user_id)

    # Apply search filter
    if food_search:
        if "WHERE" in query:
            query += " AND FOOD.foodname ILIKE %s"
        else:
            query += " WHERE FOOD.foodname ILIKE %s"
        query_params.append(f"%{food_search}%")

    # Apply price range filtering
    if price_range and price_range != "none":
        min_price, max_price = map(int, price_range.split('-'))
        if "WHERE" in query:
            query += " AND FOOD.price BETWEEN %s AND %s"
        else:
            query += " WHERE FOOD.price BETWEEN %s AND %s"
        query_params.extend([min_price, max_price])

    # Apply food type filtering
    if food_type and food_type != "none":
        if "WHERE" in query:
            query += " AND FOOD.food_type = %s"
        else:
            query += " WHERE FOOD.food_type = %s"
        query_params.append(food_type)

    # Apply sorting based on the specified sort parameter
    if sort_by:
        sort_query = {
            'name_asc': 'ORDER BY FOOD.foodname ASC',
            'name_desc': 'ORDER BY FOOD.foodname DESC',
            'rating_asc': 'ORDER BY FOOD.average_rating ASC NULLS LAST',
            'rating_desc': 'ORDER BY FOOD.average_rating DESC NULLS LAST'
        }
        query += f" {sort_query.get(sort_by, '')}"

    # Execute the final SQL query
    cursor.execute(query, query_params)
    # Fetch all the results from the executed query
    food_items = cursor.fetchall()
    # Close database connection
    connection.close()

    return render_template("FoodList.html", food_items=food_items, show_establishment_name=True)

# Update food item
@app.route('/admin/edit-food/<int:food_id>', methods=['GET', 'POST'])
def edit_fd(food_id):
    if request.method == 'GET':
        # Create connection to database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        # Fetch food item details
        cursor.execute("SELECT food_id, foodname, price, food_type, average_rating, establishment_id FROM FOOD WHERE food_id = %s", (food_id,))
        food = cursor.fetchone()
        # Fetch establishments owned by the current user
        user_id = session['user_id']
        cursor.execute("SELECT establishment_id, establishment_name FROM ESTABLISHMENT WHERE owner_id = %s", (user_id,))
        establishments = cursor.fetchall()
        # Close connection, and render page
        connection.close()
        return render_template('EditFood.html', food=food, establishments=establishments)
    elif request.method == 'POST':
        # Get data from EditFood.html
        foodname = request.form['foodname']
        price = request.form['price']
        food_type = request.form['food_type']
        est_id = request.form['est_id']
        # Create connection to database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        # Update Food item
        cursor.execute("""
            UPDATE FOOD
            SET foodname = %s, price = %s, food_type = %s, establishment_id = %s
            WHERE food_id = %s
        """, (foodname, price, food_type, est_id,food_id))
        connection.commit()
        connection.close()
        return redirect(url_for('see_fd'))

# Delete food item
@app.route('/admin/delete-food/<int:food_id>', methods=['POST'])
def delete_fd(food_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM FOOD WHERE food_id = %s", (food_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('see_fd'))

##############################################################################################################################################################
# READ METHODS OF FOOD FOR CUSTOMER
##############################################################################################################################################################

# Read food item as customer
@app.route('/customer/food-list', methods=['GET', 'POST'])
def view_all_fd():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    # Initialize query parameters
    sort_by = None
    filter_by = None
    food_search = None
    price_range = None

    # Handle POST requests for form submissions
    if request.method == 'POST':
        food_search = request.form.get('food_search')
        price_range = request.form.get('price_range')
        filter_by = request.form.get('filter')
        sort_by = request.form.get('sort')
        
        # Redirect to the GET route with query parameters
        return redirect(url_for('view_all_fd', food_search=food_search, price_range=price_range, filter=filter_by, sort=sort_by))

    # Handle GET requests for URL parameters
    elif request.method == 'GET':
        food_search = request.args.get('food_search')
        price_range = request.args.get('price_range')
        filter_by = request.args.get('filter')
        sort_by = request.args.get('sort')

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Base query to select all food items
    query = """
        SELECT F.food_id, F.foodname, F.price, F.food_type, F.average_rating, E.establishment_name
        FROM FOOD F
        JOIN ESTABLISHMENT E ON F.establishment_id = E.establishment_id
    """
    
    query_params = []

    # Apply filtering based on food type if a filter is specified
    if filter_by and filter_by != "none":
        query += " WHERE F.food_type = %s"
        query_params.append(filter_by)

    # Apply search filter
    if food_search:
        if "WHERE" in query:
            query += " AND F.foodname ILIKE %s"
        else:
            query += " WHERE F.foodname ILIKE %s"
        query_params.append(f"%{food_search}%")

    # Apply price range filtering
    if price_range and price_range != "none":
        min_price, max_price = map(int, price_range.split('-'))
        if "WHERE" in query:
            query += " AND F.price BETWEEN %s AND %s"
        else:
            query += " WHERE F.price BETWEEN %s AND %s"
        query_params.extend([min_price, max_price])

    # Apply sorting based on the specified sort parameter
    if sort_by:
        sort_query = {
            'name_asc': 'ORDER BY F.foodname ASC',
            'name_desc': 'ORDER BY F.foodname DESC',
            'rating_asc': 'ORDER BY F.average_rating ASC NULLS LAST',
            'rating_desc': 'ORDER BY F.average_rating DESC NULLS LAST'
        }
        query += f" {sort_query.get(sort_by, '')}"

    # Execute the final SQL query
    cursor.execute(query, query_params)
    # Fetch all the results from the executed query
    food_items = cursor.fetchall()
    # Close database connection
    connection.close()

    return render_template("ViewFood.html", food_items=food_items, show_establishment_name=True)

# Read food items of an establishment as a Customer
@app.route('/customer/food-list/<int:establishment_id>', methods=['GET'])
def view_fd(establishment_id):
    # Check if user is logged in
    if 'user_id' not in session:
        return "You need to log in first."

    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Fetch food items for the specified establishment
    cursor.execute("""
        SELECT food_id, foodname, price, food_type, average_rating 
        FROM FOOD 
        WHERE establishment_id = %s
    """, (establishment_id,))
    food_items = cursor.fetchall()

    # Close the connection
    connection.close()

    # Render the template with the food items and show_establishment_name variable set to False
    return render_template("ViewFood.html", food_items=food_items, show_establishment_name=False)

##############################################################################################################################################################
# ESTABLISHMENT REVIEWS
##############################################################################################################################################################

# Add establishment review
@app.route('/customer/review-establishment/<int:establishment_id>', methods=['GET', 'POST'])
def review_establishment(establishment_id):
    
    # If the request method is GET, render the review form
    if request.method == 'GET':
        return render_template('ReviewEstablishment.html', establishment_id=establishment_id)
    # If the request method is POST, handle form submission
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        
        # Check if user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']

        # Connect to the database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        
        # Insert review into the database
        add_review_sql = """
        INSERT INTO ESTABLISHMENT_REVIEW (user_id, establishment_id, rating, establishment_review, review_datetime)
        VALUES (%s, %s, %s, %s, NOW())
        """
        # Execute the SQL command to insert a new review into the ESTABLISHMENT_REVIEW table.
        cursor.execute(add_review_sql, (user_id, establishment_id, rating, review))
        # Save Changes
        connection.commit()
        
        # Update average rating of the establishment
        update_avg_rating_sql = """
        UPDATE ESTABLISHMENT
        SET average_rating = (
            SELECT AVG(rating) FROM ESTABLISHMENT_REVIEW WHERE establishment_id = %s
        )
        WHERE establishment_id = %s
        """

        # Execute the SQL query to update the average rating
        cursor.execute(update_avg_rating_sql, (establishment_id, establishment_id))
        # Save Changes
        connection.commit()
        
        # Close the database connection
        connection.close()
        
        flash("Review submitted successfully!", "success")
        return redirect(url_for('view_est'))

# Update establishment review
@app.route('/customer/review-establishment/<int:review_id>/<int:establishment_id>', methods=['GET', 'POST'])
def update_review_establishment(review_id, establishment_id):
    
    # If the request method is GET, render the review form
    if request.method == 'GET':
        return render_template('UpdateReviewEstablishment.html', review_id=review_id, establishment_id = establishment_id)
    # If the request method is POST, handle form submission
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        

        print(request.form)
        # Connect to the database
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        
        # Insert review into the database
        update_review_sql = """
    UPDATE ESTABLISHMENT_REVIEW
        SET rating = %s, establishment_review = %s,review_datetime = NOW()
        WHERE review_id = %s;
        """
        # Execute the SQL command to insert a new review into the ESTABLISHMENT_REVIEW table.
        cursor.execute(update_review_sql, (rating, review, review_id))
        # Save Changes
        connection.commit()
        
        # Update average rating of the establishment
        update_avg_rating_sql = """
        UPDATE ESTABLISHMENT
        SET average_rating = (
            SELECT AVG(rating) FROM ESTABLISHMENT_REVIEW WHERE establishment_id = %s
        )
        WHERE establishment_id = %s
        """

        # Execute the SQL query to update the average rating
        cursor.execute(update_avg_rating_sql, (establishment_id, establishment_id))
        # Save Changes
        connection.commit()
        
        # Close the database connection
        connection.close()
        
        flash("Review submitted successfully!", "success")
        return redirect(url_for('view_est'))

# See all review for an establishment   
@app.route('/customer/establishment-reviews/<int:establishment_id>', methods=['GET'])
def view_establishment_reviews(establishment_id):

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Query to get the establishment name
    establishment_name_query = "SELECT establishment_name FROM ESTABLISHMENT WHERE establishment_id = %s"
    cursor.execute(establishment_name_query, (establishment_id,))
    establishment_name = cursor.fetchone()

    # If the establishment is found, retrieve the name
    if establishment_name:
        establishment_name = establishment_name[0]
    else:
        flash("Establishment not found.", "error")
        return redirect(url_for('view_est'))

    # Query to select all establishment reviews for the specific establishment
    select_reviews_query = """
    SELECT er.rating, er.establishment_review, er.review_datetime
    FROM ESTABLISHMENT_REVIEW er
    WHERE er.establishment_id = %s 
    """

    # Execute the SQL command to insert a new review into the ESTABLISHMENT_REVIEW table and save changes
    cursor.execute(select_reviews_query, (establishment_id,))
    establishment_reviews = cursor.fetchall()

    # Close the database connection
    connection.close()

    return render_template('ViewEstablishmentReviews.html', establishment_reviews=establishment_reviews, establishment_name=establishment_name, establishment_id = establishment_id)

# See all reviews for an establishment by a user
@app.route('/customer/establishment-reviews/user/<int:establishment_id>', methods=['GET'])
def view_establishment_reviews_user(establishment_id):

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Query to get the establishment name
    establishment_name_query = "SELECT establishment_name FROM ESTABLISHMENT WHERE establishment_id = %s"
    cursor.execute(establishment_name_query, (establishment_id,))
    establishment_name = cursor.fetchone()

    # If the establishment is found, retrieve the name
    if establishment_name:
        establishment_name = establishment_name[0]
    else:
        flash("Establishment not found.", "error")
        return redirect(url_for('view_est'))

    # Query to select all establishment reviews for the specific establishment
    select_reviews_query = """
    SELECT er.rating, er.establishment_review, er.review_datetime, er.review_id
    FROM ESTABLISHMENT_REVIEW er
    WHERE er.establishment_id = %s
    and
    er.user_id = %s
    """

    # Execute the SQL command to insert a new review into the ESTABLISHMENT_REVIEW table and save changes
    cursor.execute(select_reviews_query, (establishment_id, user_id))
    establishment_reviews = cursor.fetchall()

    # Close the database connection
    connection.close()

    return render_template('ViewEstablishmentReviewsUser.html', establishment_reviews=establishment_reviews, establishment_name=establishment_name, establishment_id = establishment_id)

# See all reviews within a month
@app.route('/customer/establishment-reviews/month/<int:establishment_id>', methods=['GET'])
def view_establishment_reviews_month(establishment_id):

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Query to get the establishment name
    establishment_name_query = "SELECT establishment_name FROM ESTABLISHMENT WHERE establishment_id = %s"
    cursor.execute(establishment_name_query, (establishment_id,))
    establishment_name = cursor.fetchone()

    # If the establishment is found, retrieve the name
    if establishment_name:
        establishment_name = establishment_name[0]
    else:
        flash("Establishment not found.", "error")
        return redirect(url_for('view_est'))

    # Query to select all establishment reviews for the specific establishment
    select_reviews_query = """
    SELECT er.rating, er.establishment_review, er.review_datetime, er.review_id
    FROM ESTABLISHMENT_REVIEW er
    WHERE er.establishment_id = %s
    AND er.review_datetime >= (CURRENT_DATE - INTERVAL '1 month');
    """

    # Execute the SQL command to insert a new review into the ESTABLISHMENT_REVIEW table and save changes
    cursor.execute(select_reviews_query, (establishment_id,))
    establishment_reviews = cursor.fetchall()

    # Close the database connection
    connection.close()

    return render_template('ViewEstablishmentReviews.html', establishment_reviews=establishment_reviews, establishment_name=establishment_name, establishment_id = establishment_id)

# Delete an establishment review
@app.route('/customer/delete-review/<int:review_id>', methods=['POST'])
def delete_establishment_review(review_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()


    cursor.execute("DELETE FROM ESTABLISHMENT_REVIEW WHERE review_id = %s", (review_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('view_est'))

##############################################################################################################################################################
# FOOD REVIEWS
##############################################################################################################################################################

# Add food review
@app.route('/customer/review-food/<int:food_id>', methods=['GET', 'POST'])
def review_food(food_id):

    # If the request method is GET, render the review form
    if request.method == 'GET':
        return render_template('ReviewFood.html', food_id=food_id)
    # If the request method is POST, handle form submission
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        
        # Check if user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']

        # Connect to the connection
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        
        # Insert review into the database
        add_review_sql = """
        INSERT INTO FOOD_REVIEW (user_id, food_id, rating, food_review, review_datetime)
        VALUES (%s, %s, %s, %s, NOW())
        """
        # Execute the SQL query to add a review for a food item into the database and save changes
        cursor.execute(add_review_sql, (user_id, food_id, rating, review))
        connection.commit()
        
        # Update average rating of the food item
        update_avg_rating_sql = """
        UPDATE FOOD
        SET average_rating = (
            SELECT AVG(rating) FROM FOOD_REVIEW WHERE food_id = %s
        )
        WHERE food_id = %s
        """

        # Execute the SQL query to update the average rating and save changes
        cursor.execute(update_avg_rating_sql, (food_id, food_id))
        connection.commit()
        
        # Close the connection to the database
        connection.close()
        
        flash("Review submitted successfully!", "success")
        return redirect(url_for('view_food_reviews', food_id=food_id))

# Update food review as customer
@app.route('/customer/update/review-food/<int:review_id>/<int:food_id>', methods=['GET', 'POST'])
def update_review_food(review_id, food_id):
    if request.method == 'GET':
        return render_template('UpdateReviewFood.html', review_id=review_id, food_id=food_id)
    
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')

        try:
            with psycopg2.connect(supabase_connection_string) as connection:
                with connection.cursor() as cursor:
                    update_review_sql = """
                    UPDATE FOOD_REVIEW
                    SET rating = %s, food_review = %s,review_datetime = NOW()
                    WHERE review_id = %s;
                    """
                    cursor.execute(update_review_sql, (rating, review, review_id))

                    update_avg_rating_sql = """
                    UPDATE FOOD
                    SET average_rating = (
                        SELECT AVG(rating) FROM FOOD_REVIEW WHERE food_id = %s
                    )
                    WHERE food_id = %s
                    """
                    cursor.execute(update_avg_rating_sql, (food_id, food_id))
            
            flash("Review submitted successfully!", "success")
            return redirect(url_for('view_food_reviews', food_id=food_id))
        
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('update_review_food', review_id=review_id, food_id=food_id))

# See all reviews for a food by a user
@app.route('/customer/food-reviews/users/<int:food_id>', methods=['GET'])
def view_food_reviews_user(food_id):

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    

    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Query to get the food name
    food_name_query = "SELECT food.foodname FROM FOOD WHERE food_id = %s"
    cursor.execute(food_name_query, (food_id,))
    food_name = cursor.fetchone()

    

    # If the food item is found, retrieve the name
    if food_name:
        food_name = food_name[0]
    else:
        flash("Food item not found.", "error")
        return redirect(url_for('view_all_fd'))

    # Query to select all food reviews for the specific food item
    select_reviews_query = """
    SELECT fr.rating, fr.food_review, fr.review_datetime, fr.review_id
    FROM FOOD_REVIEW fr
    WHERE fr.food_id = %s and fr.user_id = %s
    """
    # Execute the SQL query to select all food reviews for the specific food item
    cursor.execute(select_reviews_query, (food_id, user_id))
    # Fetch all the selected food reviews
    food_reviews = cursor.fetchall()

    # Close the connection to the database
    connection.close()

    return render_template('ViewFoodReviewsUser.html', food_reviews=food_reviews, food_name=food_name, food_id = food_id)

# See all reviews for a food within a month
@app.route('/customer/food-reviews/month/<int:food_id>', methods=['GET'])
def view_food_reviews_month(food_id):

    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    

    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Query to get the food name
    food_name_query = "SELECT food.foodname FROM FOOD WHERE food_id = %s"
    cursor.execute(food_name_query, (food_id,))
    food_name = cursor.fetchone()

    

    # If the food item is found, retrieve the name
    if food_name:
        food_name = food_name[0]
    else:
        flash("Food item not found.", "error")
        return redirect(url_for('view_all_fd'))

    # Query to select all food reviews for the specific food item
    select_reviews_query = """
    SELECT fr.rating, fr.food_review, fr.review_datetime, fr.review_id
    FROM FOOD_REVIEW fr
    WHERE fr.food_id = %s 
    AND fr.review_datetime >=(CURRENT_DATE - INTERVAL '1 month')
    """
    # Execute the SQL query to select all food reviews for the specific food item
    cursor.execute(select_reviews_query, (food_id,))
    # Fetch all the selected food reviews
    food_reviews = cursor.fetchall()

    # Close the connection to the database
    connection.close()

    return render_template('ViewFoodReviews.html', food_reviews=food_reviews, food_name=food_name, food_id = food_id)

# See all reviews for a food
@app.route('/customer/food-reviews/<int:food_id>', methods=['GET'])
def view_food_reviews(food_id):
    # Connect to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Query to get the food name
    food_name_query = "SELECT food.foodname FROM FOOD WHERE food_id = %s"
    cursor.execute(food_name_query, (food_id,))
    food_name = cursor.fetchone()

    # If the food item is found, retrieve the name
    if food_name:
        food_name = food_name[0]
    else:
        flash("Food item not found.", "error")
        return redirect(url_for('view_all_fd'))

    # Query to select all food reviews for the specific food item
    select_reviews_query = """
    SELECT fr.rating, fr.food_review, fr.review_datetime, fr.review_id
    FROM FOOD_REVIEW fr
    WHERE fr.food_id = %s
    """
    # Execute the SQL query to select all food reviews for the specific food item
    cursor.execute(select_reviews_query, (food_id,))
    # Fetch all the selected food reviews
    food_reviews = cursor.fetchall()

    # Close the connection to the database
    connection.close()

    return render_template('ViewFoodReviews.html', food_reviews=food_reviews, food_name=food_name, food_id = food_id)

# Delete a food review as customer
@app.route('/customer/delete-review/<int:review_id>', methods=['POST'])
def delete_food_review(review_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()


    cursor.execute("DELETE FROM FOOD_REVIEW WHERE review_id = %s", (review_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('view_all_fd'))

# Main application
if __name__ == "__main__":
    app.run(debug=True, port=3002)  
