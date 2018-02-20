# ServerApp

# Architecture Details

- Application is written in python
- ServerApp is built using the flask web framework
- A sqlite db is used with SQLAlchemy as the ORM (Object Relational Mapper)
- Database Diagram in Database Diagram.pdf
- Details of db table implementation can be found in models.py
- URL routing and request handling logic can be found in routes.py
- Marshmallow is used for schema validation
- All request params are sent as JSON and responses are also JSON

# How to Run
source env/bin/activate -> setup virtual environment

# Initialize the db
1. flask db init -> initialize directory for database migrations
2. flask db migrate -> create a new db migration
3. flask db upgrade -> apply migration

# Running the App
1. Export FLASK_APP=testdb.py
2. Export FLAKS_DEBUG=1
3. flask run

App will begin running on localhost:5000

App can be tested using httpie cli
https://httpie.org/

# Examples of REST API Usage (using httpie)
get list of users
- http GET :5000/users

create new user
- http POST :5000/users first_name=nadeesha last_name=amarasinghe phone_number=4082213286

get user with user.id = user_id
- http GET :5000/users/<user_id>

update user
- http PUT :5000/users/<user_id> first_name=nadeesha last_name=amarasinghe phone_number=4082213286

get list of restaurants
- http GET :5000/restaurants

query restaurant by parameters (i.e. city, state, name, total score)
- http GET:5000/restaurants totalscore=3.0 city="santa clara"

Add a restaurant 
- http POST :5000/restaurants name=dennys category=breakfast address:='{"address":"1 dennys drive","state":"CA","zipcode":"95054","city":"santa clara"}'

Update a restaurant 
- http PUT :5000/restaurants/1 name=McD 

get list of ratings
- http GET :5000/ratings

add rating for a user
- http POST :5000/ratings/user/1 cost=4 food=4 cleanliness=4 service=4 restaurant_id=1

update rating by a user for a restaurant
- http PUT :5000/ratings/user/<user_id>/<rating_id> cost=1

get all ratings for a user
- http GET :5000/ratings/user/<user_id>

get all ratings for a restaurant
- http GET :5000/ratings/restaurant/<restaurant_id>
