# CMSC 127 Project: Food Review Information System

## PROJECT DETAILS

### Description
The Food Review Information System is designed to record data on food reviews and food items from various food establishments in electronic form.

### Task
The task for the project team is to design a flexible and realistic database and implement it using any chosen programming language with RDBMS limited to MySQL, MariaDB, or PostgreSQL.

## FEATURES
1. Add, update, and delete a food review (on a food establishment or a food item)
2. Add, delete, search, and update a food establishment
3. Add, delete, search, and update a food item
4. Add, delete , search, and update a user account (Optional)

## REPORTS TO BE GENERATED
1. View all food establishments
2. View all food reviews for an establishment or a food item
3. View all food items from an establishment
4. View all food items from an establishment that belong to a food type (meat, veg, etc.)
5. View all reviews made within a month for an establishment or a food item
6. View all establishments with a high average rating (rating >= 4)
7. View all food items from an establishment arranged according to price
8. Search food items from any establishment based on a given price range and/or food type

## MILESTONES
1. [Entity Relationship Diagram](https://drive.google.com/drive/folders/1AFLIX-kvRMt2HdSvfaRq2RXgexBnTtO5?usp=drive_link)
2. [Relational Tables](https://drive.google.com/drive/folders/1UVV4l7a8Zo09bhGMYfhCZXnHvmlyeX2E?usp=drive_link)
3. [SQL Sample Queries](Albino_Palacio_Villarosa_Milestone3.sql)
4. [Project Application](https://cmsc-127-project-ibonns-projects-5b997b82.koyeb.app/)

## TECHNOLOGY STACK
- ### PostgreSQL
    An open-source relational database management system (RDBMS) known for its reliability, robustness, and extensive feature set. It supports SQL queries, transactions, indexing, and advanced data types, making it suitable for handling complex data models and high-volume workloads.

    For this project, the database has been deployed via [Supabase](https://supabase.com/). The configuration for the connection string for the database can be seen below.

    ```python
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
    ```
    
- ### Python Flask 
   Lightweight web framework for Python. Used to define routes, handle requests, and manage application logic. Below are some libraries that have been used. 

    1. **datetime**: Used for formatting, arithmetic, and comparison on dates and times.

    2. **bcrypt**: Used for hashing the passwords stored in ACCOUNT table.

    3. **psycopg2**: PostgreSQL adapter for Python used to interact with PostgreSQL database. Provides support for executing SQL queries, managing connections, and working with result sets.

    4. **urllib**: Used for making HTTP requests and handling URLs.

    5. **gunicorn**: A WSGI HTTP server for Python web applications. Serves as a production-ready server for running Flask applications.

    6. **itsdangerous**: Used for securely serializing and signing data. Used in generating and validating secure tokens and session cookies.

    7. **Jinja2**: Templating engine for Python. Used in generating dynamic HTML content in Flask applications, helped separate logic from presentation and create reusable templates.

    8. **MarkupSafe**: Used for escaping and preserving HTML markup in Python strings. Helped prevent cross-site scripting (XSS) attacks by sanitizing user input and ensuring that HTML content is safely rendered in web pages.

    9. **packaging**: Used for packaging, distributing, and installing Python code, making it easier to deploy the project.

    10. **blinker**: Used for implementing and dispatching signals. Used in creating custom signals and connect them to event handlers.

    12. **Werkzeug**: A comprehensive WSGI utility library for Python. It provides a collection of reusable components for building web applications, including request and response objects, URL routing, form parsing, and HTTP utilities.

    Libraries **5** and **12** were used for deployment. Thus, this python flask app is functional for both _local_ and _deployed_ servers. The app was deployed using [Koyeb](https://www.koyeb.com/). The project can be accessed through this [link](https://cmsc-127-project-ibonns-projects-5b997b82.koyeb.app/).

- ### Tailwind
    The utility-first CSS framework that was used to quickly build responsive and customizable user interfaces. Unlike traditional CSS frameworks that come with pre-designed components, Tailwind CSS provides low-level utility classes that you can use to style HTML elements directly. 

## FILE STRUCTURE
1. Environement Variables  
    Found in **.venv**, this directory stores the Python environment variables for the Flask application.
2. HTML Templates  
    Found in **/templates**, this directory stores the HTML files that were used to generate the user interface of the project. 
3. Python Flask Application  
    Filename **app.py**, this stores the entire Python Flask code for the project.
4. Procfile  
    A file used for deployment to Koyeb. And used Heroku deployments to specify the commands that should be executed by the app's dynos (containers) on startup.
5. Dependencies  
    Filename **requirements.txt**, this file stores all libraries or dependencies that were used in the development of this application.

## SETTING UP PROJECT ENVIRONMENT FOR LOCAL SERVER
1. Clone the repository

    ```bash
    git clone https://<TOKEN>@github.com/MarPaulPalacio/CMSC-127-Best-Group-AVP.git
    ```
2. Go to Main branch

    ```bash
    git checkout main
    ```
3. Run the line below in your terminal to install python dependencies, you should be in the `CMSC-127-Best-Group-AVP` folder/directory where requirements.txt is located when running this command.

    ```bash
    pip install -r requirements.txt
    ```
	Note: This is similar to the npm install of React from MERN stack.
4. Try running the local server of the python flask app by running the line below (still inside the `CMSC-127-Best-Group-AVP` directory).  

    ```bash
    python ./app.py
    ```

Note: You can also follow the **Prerequisites** section in this tutorial [Python and Flask Tutorial in Visual Studio Code](https://code.visualstudio.com/docs/python/tutorial-flask) then follow the **Create a project environment for the Flask tutorial**, but instead of doing this in a folder called `hello_flask` do this inside our folder project `CMSC-127-Best-Group-AVP` to set up the Python environment.


## USER MANUAL

### SIGN UP  
1. Visit the home page '/', there are two buttons: Sign Up and Login.

2. Click the Sign Up button, you'll be redirected to the sign up page '/signup'

3. Fill out all the necessary information and click "Sign Up" button to submit the form. Note:  
    - All fields are required. 
    - Username and email must be unique. You cannot have two accounts with the same email.
    - Remember your password because there is no way of retrieving this password.
4. You're account has been created, you'll be redirected to login page '/login'.

### LOG IN
1. Enter your username and password. 
2. Click the login button.
3. You will be redirected to the Establishment List for either ADMIN or CUSTOMER depending on your user type.

### AS OWNER
    
### Create Establishment
1. In Establishment list page '/admin/establishment-list', click the Add Establishment button on the tool sidebar on the left.
2. You will be redirected to Add Establishment page 'admin/add-establishment', here you enter the Establishment Name and Address Location. Note: 
    - The average rating of your newly created establishment is initially zero. 
    - Your address and establishment name must be unique. Both fields are required.
3. Once created, you will be redirected back to the establishment list page for admin.

### Edit Establishment
1. In the establishment list page, there is the list of establishments table. Left most column of this table is the action buttons. Here, you'll find the Edit button for an establishment. Click the edit button.
2. You'll be redirected to the Edit Establishment page 'admin/edit-establishment/est_id' where you can enter the new name or new address of your establishment.
3. Click save to save your data. Once successfully edited, you will be redirected back to establishment list page.

### Delete Establishment
1. Simply click the delete button located at the action column in the establishment table.

### View Establishments
1. In Establishment List page, you can view the list of establishments you own. You can also search by name or address, sort by name or rating, or filter by rating the list of establishments.

### Create Food Item 
1. In Food list page '/admin/food-list', click the Add Food Item button on the tool sidebar on the left.
2. You will be redirected to Add Food page 'admin/add-food', here you enter the necessary infromation of the food item. Note: 
    - The average rating of your newly created food item is initially zero. 
    - You can only select existing establishments you own.
    - All form fields are required.
3. Once created, you will be redirected back to the establishment list page for admin.

### Edit Food Item 

1. In the Food list page, there is the list of food items table. Left most column of this table is the action buttons. Here, you'll find the Edit button for an establishment. Click the edit button.
2. You'll be redirected to the Edit Food page 'admin/edit-food/food_id' where you can enter the information you want to update.
3. Click save to save your data. Once successfully edited, you will be redirected back to food list page.

### Delete Food Item 
1. Simply click the delete button located at the action column in the food table.

### View Food Item 
1. In Food List page, you can view the list of food items. You can also search by name or address, sort by name or rating, or filter by rating the list of food items.

### AS CUSTOMER

### 1. Browse all food items

### 2. Browse establishments

### 3. Browse food items of a specific establishment

### 4. Create a review for a food or an establishment

### 5. View reviews for a food or an establishment

### 6. Edit or Delete a food or establishment review



---
Authors:
- Clarine Yvonne Albino ([@cyalbino](https://github.com/cyalbino))
- Mar Paul Palacio ([@MarPaulPalacio](https://github.com/MarPaulPalacio))
- James Villarosa ([@JamesVillarosa](https://github.com/JamesVillarosa))