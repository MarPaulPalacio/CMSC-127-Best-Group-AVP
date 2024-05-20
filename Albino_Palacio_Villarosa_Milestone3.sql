-- CREATE TABLES 
CREATE TABLE ACCOUNT (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    firstname VARCHAR(50) NOT NULL,
    middlename VARCHAR(50),
    lastname VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    user_type ENUM('customer','owner','admin') NOT NULL,
    password_ VARCHAR(255) NOT NULL
);

CREATE TABLE ESTABLISHMENT (
    establishment_id INT PRIMARY KEY AUTO_INCREMENT,
    address_location VARCHAR(100) NOT NULL UNIQUE,
    establishment_name VARCHAR(50) NOT NULL UNIQUE,
    average_rating DECIMAL(3,2),
    owner_id INT, 
    CONSTRAINT establishment_owner_fk FOREIGN KEY (owner_id) 
        REFERENCES ACCOUNT(user_id) 
);

CREATE TABLE FOOD (
    food_id INT PRIMARY KEY AUTO_INCREMENT,
    foodname VARCHAR(80) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    food_type ENUM('meat','vegetable','seafood','dessert','beverage') NOT NULL,
    average_rating DECIMAL(3,2),
    establishment_id INT NOT NULL,
    creator_id INT NOT NULL,  
    CONSTRAINT food_establishment_fk FOREIGN KEY (establishment_id) 
        REFERENCES ESTABLISHMENT(establishment_id),
    CONSTRAINT food_creator_fk FOREIGN KEY (creator_id) 
        REFERENCES ACCOUNT(user_id)
);

CREATE TABLE ESTABLISHMENT_REVIEW(
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    establishment_id INT NOT NULL,
    rating DECIMAL(3,2) NOT NULL,
    establishment_review VARCHAR(255),
    review_datetime DATETIME NOT NULL,
    CONSTRAINT est_review_user_fk FOREIGN KEY (user_id) 
        REFERENCES ACCOUNT(user_id),
    CONSTRAINT est_review_establishment_fk FOREIGN KEY (establishment_id) 
        REFERENCES ESTABLISHMENT(establishment_id)
);

CREATE TABLE FOOD_REVIEW(
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    food_id INT NOT NULL,
    rating DECIMAL(3,2) NOT NULL,
    food_review VARCHAR(255),
    review_datetime DATETIME NOT NULL,
    CONSTRAINT fd_review_user_fk FOREIGN KEY (user_id)
        REFERENCES ACCOUNT(user_id),
    CONSTRAINT fd_review_food_fk FOREIGN KEY (food_id)
        REFERENCES FOOD(food_id)
);

-- FEATURES
--1 Add, update, and delete a food review (on a food establishment or a food item)
    -- Add establishment review
    INSERT INTO ESTABLISHMENT_REVIEW (user_id, establishment_id, rating, establishment_review, review_datetime)
        VALUES (1, 1, 4.5, 'Great service! Nice ambiance.', NOW());
    
    -- Add food review
    INSERT INTO FOOD_REVIEW (user_id, food_id, rating, food_review, review_datetime)
        VALUES (1, 1, 4.5, 'Delicious!', NOW());

    -- Update establishment review
    UPDATE ESTABLISHMENT_REVIEW
        SET rating = 5, establishment_review = 'Excellent service! Great ambiance!'
        WHERE review_id = 1;

    -- Update food review
    UPDATE FOOD_REVIEW
        SET rating = 5, food_review = 'Absolutely delicious!'
        WHERE review_id = 1;

    -- Delete establishment review
    DELETE FROM ESTABLISHMENT_REVIEW
        WHERE review_id = 1;

    -- Delete food review
    DELETE FROM FOOD_REVIEW
        WHERE review_id = 1;

--2 Add, delete, search, and update a food establishment
    -- Add food establishment
    INSERT INTO ESTABLISHMENT (address_location, establishment_name, average_rating)
        VALUES ('New Address', 'New Establishment', 0.0);

    -- Delete a food establishment
    DELETE FROM ESTABLISHMENT WHERE establishment_id = 1;

    -- Search a food establishment by establishment name
    SELECT * FROM ESTABLISHMENT WHERE establishment_name = 'New Establishment';
    
    -- Update a food establishment
    UPDATE ESTABLISHMENT SET address_location = 'Brand New Address',average_rating = 4.7
        WHERE establishment_id = 1;

--3 Add, delete, search, and update a food item.
    -- Add a food item
    INSERT INTO FOOD (foodname, price, food_type, establishment_id, average_rating)
        VALUES ('New Food', 10.99, 'meat', 1, 0.0);
    
    -- Delete a food item
    DELETE FROM FOOD WHERE food_id = 1;

    -- Search a food item
    SELECT * FROM FOOD WHERE foodname = 'New Food';

    -- Update a food item
    UPDATE FOOD SET price = 11.99, food_type = 'meat', average_rating = 4.5
        WHERE food_id = 1;

--4 Add, delete, search, and update a user account
    -- Add a user account
    INSERT INTO ACCOUNT (username, firstname, middlename, lastname, email, user_type, password_)
        VALUES ('new_user', 'John', 'Middle', 'Doe', 'john@example.com', 'customer', 'password');

    -- Delete a user account
    DELETE FROM ACCOUNT WHERE user_id = 1;

    -- Search a user account
    SELECT * FROM ACCOUNT WHERE username = 'new_user';

    -- Update a user account
    UPDATE ACCOUNT SET firstname = 'Matthew', email = 'new_email@example.com'
        WHERE user_id = 1;

-- REPORTS TO BE GENERATED

--1 View all food establishments
    SELECT * FROM establishment;

--2 View all food reviews for an establishment or a food item
    -- For an establishment
    SELECT er.establishment_name, er.rating, er.establishment_review, er.review_datetime
        FROM ESTABLISHMENT_REVIEW er
        JOIN ESTABLISHMENT e ON er.establishment_id = e.establishment_id
        WHERE e.food_id = 1; 

    -- For a food item
    SELECT f.foodname, fr.rating, fr.food_review, fr.review_datetime
        FROM FOOD_REVIEW fr
        JOIN FOOD f ON fr.food_id = f.food_id
        WHERE f.establishment_id = 1;

--3 View all food items from an establishment
    SELECT * FROM FOOD WHERE establishment_id = 1; 

--4 View all food items from an establishment that belong to a food type (meat | veg | etc.)
    SELECT * FROM FOOD
        WHERE establishment_id = 1
        AND food_type = 'meat';

--5 View all reviews made within a month for an establishment or a food item
    SELECT * FROM FOOD_REVIEW
        WHERE establishment_id = 1
        AND review_datetime >= DATE_SUB(NOW(), INTERVAL 1 MONTH);

--6 View all establishments with a high average rating (rating >= 4). (ratings from 1-5; highest is 5)
    SELECT * FROM ESTABLISHMENT
        WHERE average_rating >= 4;

--7 View all food items from an establishment arranged according to price
    SELECT * FROM FOOD
        WHERE establishment_id = 1
        ORDER BY price;

--8 Search food items from any establishment based on a given price range and/or food type
    SELECT * FROM FOOD
        WHERE price BETWEEN 10 AND 150 
        AND food_type = 'meat';
