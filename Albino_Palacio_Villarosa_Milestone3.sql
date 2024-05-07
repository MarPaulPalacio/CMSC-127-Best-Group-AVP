-- FEATURE 2

INSERT INTO ESTABLISHMENT VALUES ("1234567", "JOHN STREET", "JOANNA AVENUE", 10)


-- Reports to be generated

--1
SELECT * FROM establishment;

--2
SELECT FR.food_review, FR.date_reviewed, FR.time_reviewed, FR.taste_review, FR.rating FROM FOOD_REVIEW FR JOIN FOOD F ON FR.food_name = F.foodname;

--3
SELECT F.foodname, F.price, F.food_type, F.average_rating
FROM FOOD F
JOIN ESTABLISHMENT E ON F.establishment_id = E.establishment_id;

--4
Select * FROM food where foodtype = "meat"

--5
Select * FROM  ESTABLISHMENT_REVIEW where date_reviewed = "__/03/____"
Select * FROM  USER_REVIEW where date_reviewed = "__/03/____"

--6
SELECT * FROM establishment where average_rating>=4

--8
SELECT * FROM food where food_type = "meat" && price_range >1000 && price_range<2000
