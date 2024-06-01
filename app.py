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
connection_string = f"dbname={db_n} user={un} password={pw} host={hn} port={p}"

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

# Home/Landing Page
@app.route('/')
def index():
    return render_template("Landing.html")

@app.route('/unauthorized')
def unauth():
    return render_template("Unauthorized.html")

# Sign up user account (Create)
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

def get_user_id_from_database(username):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM ACCOUNT WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]  # Fetch the user ID from the result
    connection.close()
    return user_id

# Login user account (Read)
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
        
@app.route('/logout', methods=['GET'])
def logout():
    # Remove user_id from session
    session.pop('user_id', None)
    return redirect(url_for('index'))  # Redirect to homepage or any other desired page

# See all user accounts (Read)
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

# Update user account
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

# Delete user account
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM ACCOUNT WHERE user_id = %s", (user_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('see_users'))

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
@app.route('/admin/establishment-list', methods=['GET'])
def see_est():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    # Get the user ID from the session
    user_id = session['user_id']

    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Check the user type
    cursor.execute("SELECT user_type FROM ACCOUNT WHERE user_id = %s", (user_id,))
    user_type = cursor.fetchone()[0]

    # Fetch establishments based on user type
    if user_type == 'admin':
        cursor.execute("SELECT establishment_id, establishment_name, address_location, average_rating FROM ESTABLISHMENT")
    elif user_type == 'owner':
        cursor.execute("SELECT establishment_id, establishment_name, address_location, average_rating FROM ESTABLISHMENT WHERE owner_id = %s", (user_id,))
    else:
        connection.close()
        return redirect(url_for('unauth'))

    # Fetch establishments
    establishments = cursor.fetchall()

    # Close the connection
    connection.close()

    # Render the template with the establishments
    return render_template("EstList.html", establishments=establishments)

# Read food establishment as Customer
@app.route('/customer/establishment-list', methods=['GET'])
def view_est():
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT E.establishment_id, E.establishment_name, E.address_location, E.average_rating, COALESCE(RE.reviews, '{}') AS reviews
        FROM ESTABLISHMENT E
        LEFT JOIN (
            SELECT establishment_id, json_agg(json_build_object('review_id', review_id, 'user_id', user_id, 'rating', rating, 'review', establishment_review, 'datetime', review_datetime)) AS reviews
            FROM ESTABLISHMENT_REVIEW
            GROUP BY establishment_id
        ) RE ON E.establishment_id = RE.establishment_id
    """)
    establishments = cursor.fetchall()
    connection.close()

    return render_template("ViewEst.html", establishments=establishments)


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
        ave_rating = request.form['ave_rating']
        
        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE ESTABLISHMENT
            SET establishment_name = %s, address_location = %s, average_rating = %s
            WHERE establishment_id = %s
        """, (est_name, addr_loc, ave_rating, establishment_id))
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
@app.route('/admin/food-list', methods=['GET'])
def see_fd():
    #Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    
    # Get the user ID from the session
    user_id = session['user_id']

    # Open a conncetion to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Check the user type
    cursor.execute("SELECT user_type FROM ACCOUNT WHERE user_id = %s", (user_id,))
    user_type = cursor.fetchone()[0]

    # Fetch food items based on user type
    if user_type == 'admin':
        cursor.execute("""
            SELECT FOOD.food_id, FOOD.foodname, FOOD.price, FOOD.food_type, FOOD.average_rating, ESTABLISHMENT.establishment_name
            FROM FOOD
            JOIN ESTABLISHMENT ON FOOD.establishment_id = ESTABLISHMENT.establishment_id
        """)
    elif user_type == 'owner':
        cursor.execute("""
            SELECT FOOD.food_id, FOOD.foodname, FOOD.price, FOOD.food_type, FOOD.average_rating, ESTABLISHMENT.establishment_name
            FROM FOOD
            JOIN ESTABLISHMENT ON FOOD.establishment_id = ESTABLISHMENT.establishment_id
            WHERE FOOD.creator_id = %s
        """, (user_id,))
    else:
        connection.close()
        return redirect(url_for('unauth'))
    
    # Fetch food items
    food_items = cursor.fetchall()

    # Close the connection 
    connection.close()

    # Render the template with the food items
    return render_template("FoodList.html", food_items=food_items)

# Read food item as customer
@app.route('/customer/food-list', methods=['GET'])
def view_all_fd():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    
    # Open a connection to the database
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Fetch all food items with establishment names
    cursor.execute("""
        SELECT FOOD.food_id, FOOD.foodname, FOOD.price, FOOD.food_type, FOOD.average_rating, ESTABLISHMENT.establishment_name
        FROM FOOD
        JOIN ESTABLISHMENT ON FOOD.establishment_id = ESTABLISHMENT.establishment_id
    """)
    food_items = cursor.fetchall()

    # Close the connection
    connection.close()

    # Render the template with the food items and show_establishment_name variable set to True
    return render_template("ViewFood.html", food_items=food_items, show_establishment_name=True)

# Read food items of an establishment as a Customer
@app.route('/customer/food-list/<int:establishment_id>', methods=['GET'])
def view_fd(establishment_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))
    
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


# Add establishment review
@app.route('/customer/review-establishment/<int:establishment_id>', methods=['GET', 'POST'])
def review_establishment(establishment_id):
    if request.method == 'GET':
        return render_template('ReviewEstablishment.html', establishment_id=establishment_id)
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        
        # Check if user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']

        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        
        # Insert review into the database
        add_review_sql = """
        INSERT INTO ESTABLISHMENT_REVIEW (user_id, establishment_id, rating, establishment_review, review_datetime)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(add_review_sql, (user_id, establishment_id, rating, review))
        connection.commit()
        
        # Update average rating of the establishment
        update_avg_rating_sql = """
        UPDATE ESTABLISHMENT
        SET average_rating = (
            SELECT AVG(rating) FROM ESTABLISHMENT_REVIEW WHERE establishment_id = %s
        )
        WHERE establishment_id = %s
        """
        cursor.execute(update_avg_rating_sql, (establishment_id, establishment_id))
        connection.commit()
        
        connection.close()
        
        flash("Review submitted successfully!", "success")
        return redirect(url_for('view_est'))


# See all review for an establishment   
@app.route('/customer/establishment-reviews/<int:establishment_id>', methods=['GET'])
def view_establishment_reviews(establishment_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Query to get the establishment name
    establishment_name_query = "SELECT establishment_name FROM ESTABLISHMENT WHERE establishment_id = %s"
    cursor.execute(establishment_name_query, (establishment_id,))
    establishment_name = cursor.fetchone()

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
    cursor.execute(select_reviews_query, (establishment_id,))
    establishment_reviews = cursor.fetchall()

    connection.close()

    return render_template('EstablishmentReviews.html', establishment_reviews=establishment_reviews, establishment_name=establishment_name)


@app.route('/customer/food-list', methods=['GET'])
def view_food():
    if 'user_id' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT F.food_id, F.food_name, F.price, F.food_type, F.average_rating, COALESCE(FR.reviews, '{}') AS reviews
        FROM FOOD F
        LEFT JOIN (
            SELECT food_id, json_agg(json_build_object('review_id', review_id, 'user_id', user_id, 'rating', rating, 'review', food_review, 'datetime', review_datetime)) AS reviews
            FROM FOOD_REVIEW
            GROUP BY food_id
        ) FR ON F.food_id = FR.food_id
    """)
    food_items = cursor.fetchall()
    connection.close()

    return render_template("ViewFood.html", food_items=food_items, show_establishment_name=False)
    
# Add food review
@app.route('/customer/review-food/<int:food_id>', methods=['GET', 'POST'])
def review_food(food_id):
    if request.method == 'GET':
        return render_template('ReviewFood.html', food_id=food_id)
    elif request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        
        # Check if user is logged in
        if 'user_id' not in session:
            flash("You need to login first.", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']

        connection = psycopg2.connect(supabase_connection_string)
        cursor = connection.cursor()
        
        # Insert review into the database
        add_review_sql = """
        INSERT INTO FOOD_REVIEW (user_id, food_id, rating, food_review, review_datetime)
        VALUES (%s, %s, %s, %s, NOW())
        """
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
        cursor.execute(update_avg_rating_sql, (food_id, food_id))
        connection.commit()
        
        connection.close()
        
        flash("Review submitted successfully!", "success")
        return redirect(url_for('view_food'))

# See all review for a food
@app.route('/customer/food-reviews/<int:food_id>', methods=['GET'])
def view_food_reviews(food_id):
    connection = psycopg2.connect(supabase_connection_string)
    cursor = connection.cursor()

    # Query to get the food name
    food_name_query = "SELECT food.foodname FROM FOOD WHERE food_id = %s"
    cursor.execute(food_name_query, (food_id,))
    food_name = cursor.fetchone()

    if food_name:
        food_name = food_name[0]
    else:
        flash("Food item not found.", "error")
        return redirect(url_for('view_food'))

    # Query to select all food reviews for the specific food item
    select_reviews_query = """
    SELECT fr.rating, fr.food_review, fr.review_datetime
    FROM FOOD_REVIEW fr
    WHERE fr.food_id = %s
    """
    cursor.execute(select_reviews_query, (food_id,))
    food_reviews = cursor.fetchall()

    connection.close()

    return render_template('FoodReviews.html', food_reviews=food_reviews, food_name=food_name)


if __name__ == "__main__":
    app.run(debug=True, port=3002)