from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy.exc import IntegrityError

from app import app
from app import db
from app.models import User, Restaurant, Rating, Address
from app.models import UserSchema,RestaurantSchema,AddressSchema,RatingSchema,RatingSchemaUpdate

from marshmallow import ValidationError

from datetime import datetime,timedelta
from sqlalchemy import func
from sqlalchemy.sql import label

users_schema = UserSchema(many=True)
user_schema = UserSchema()

restaurants_schema = RestaurantSchema(many=True)
restaurant_schema = RestaurantSchema()

address_schema = AddressSchema()

rating_schema = RatingSchema()
ratingupdate_schema = RatingSchemaUpdate()
ratings_schema = RatingSchema(many=True)

import pdb

#function to add object to database
def db_add(obj,schema):
    try:
        db.session.add(obj)
        db.session.commit()
        return jsonify({'record':schema.dump(obj)})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message':'record could not be added'}),400

#function to update record in database
def db_update(obj,schema):
    try:
        db.session.commit()    
        return jsonify({'record':schema.dump(obj)})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message':'record could not be updated'}),400


@app.route('/')
@app.route('/index')
def index():
   return render_template('index.html', title='Hello', name='Nadeesha') 

#get list of users
@app.route('/users')
def get_users():
    users = User.query.all()
    return jsonify({'users':users_schema.dump(users)})

#get user by user_id
@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({'user':user_schema.dump(user)})
    else:
        return jsonify({'message':'user could not be found'}),404

#create new user
@app.route('/users',methods=['POST'])
def add_user():
    req_data = request.get_json()
    err = user_schema.validate(req_data)
    if err:
        return jsonify(err),400
    else:
        user_dat,err = user_schema.load(req_data)
        user = User(**user_dat)
        return db_add(user,user_schema)
        
#update user
@app.route('/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user:
        req_data = request.get_json()
        user_dat,err = user_schema.load(req_data,partial=True)
       
        user.update(**user_dat)
        return db_update(user,user_schema)
    else:
        return jsonify({'message':'user could not be found'}),404

#get list of restaurants by query
@app.route('/restaurants')
def get_restaurants():
    req_args = request.get_json()
    restaurant_query = Restaurant.query
    if req_args is None:
        restaurants = restaurant_query.all()
        return jsonify({'restaurants':restaurants_schema.dump(restaurants)})
    else:
        #query restaurants by total score
        qu = db.session.query(Restaurant,Address,func.avg(Rating.totalscore)).group_by(Restaurant)
        if 'totalscore' in req_args:
            qu = qu.filter(Rating.totalscore > float(req_args['totalscore']))
        #query restaurants by city, name, zipcode, category
        if 'city' in req_args:
            qu = qu.filter(Address.city == req_args['city'])
        if 'name' in req_args:
            qu = qu.filter(Restaurant.name == req_args['name'])
        if 'zipcode' in req_args:
            qu = qu.filter(Address.zipcode == req_args['zipcode'])
        if 'category' in req_args:
            qu = qu.filter(Restaurant.category== req_args['category'])

        #extract restaurants from query
        restaurants = [restaurant for restaurant,Address,totalscore in qu.all()]

        return jsonify({'restaurants':restaurants_schema.dump(restaurants)})

@app.route('/restaurants',methods=['POST'])
def add_restaurant():
    req_data = request.get_json()
    err = restaurant_schema.validate(req_data)
    if err:
        return jsonify(err),400
    else:
        restaurant_dat,err = restaurant_schema.load(req_data)
        restaurant = Restaurant(**restaurant_dat)
        return db_add(restaurant,restaurant_schema)

@app.route('/restaurants/<int:restaurant_id>',methods=['PUT'])
def update_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant:
        req_data = request.get_json()
        restaurant_dat,err = restaurant_schema.load(req_data,partial=True)
        restaurant.update(**restaurant_dat)

        return db_update(restaurant,restaurant_schema)
    else:
        return jsonify({'message':'restaurant could not be found'}),404

@app.route('/ratings')
def get_ratings():
    ratings = Rating.query.all()
    return jsonify({'ratings':ratings_schema.dump(ratings)})

@app.route('/ratings/user/<int:user_id>',methods=['POST'])
def add_rating(user_id):
    user = User.query.get(user_id)
    if user:
        req_data = request.get_json()

        err = rating_schema.validate(req_data)
        if err:
            return jsonify(err),400
        else:
            rating_dat,err = rating_schema.load(req_data)
            restaurant_id = rating_dat['restaurant_id']
            restaurant = Restaurant.query.get(restaurant_id)
            if restaurant:
                rating_dat['user'] = user
                rating_dat['restaurant'] = restaurant
                del rating_dat['restaurant_id']
               
                #ensure the user is not rating the same retaurant in less than a month
                most_recent_rating = Rating.query.filter_by(user=user,restaurant=restaurant).order_by(Rating.date.desc()).first()
                if most_recent_rating:
                    if (datetime.utcnow() - most_recent_rating.date) < timedelta(days=30):
                        return jsonify({'message':'please wait longer than a month to rate the same restaurant'}),400

                #if total score is 1.0 ensure there is a comment
                rating = Rating(**rating_dat)
                if rating.comment == '' and rating.totalscore == 1.0:
                    return jsonify({'message':'please supply a comment for rating'}),400

                return db_add(rating,rating_schema)
            else:
                return jsonify({'message':'restaurant could not be found'}),404

    else:
        return jsonify({'message':'user could not be found'}),404

#update rating for a given user
@app.route('/ratings/user/<int:user_id>/<int:rating_id>',methods=['PUT'])
def update_rating(user_id,rating_id):
    rating = Rating.query.get(rating_id)
    if rating:
        req_data = request.get_json()
        err = ratingupdate_schema.validate(req_data,partial=True)
        if err:
            return jsonify(err),400
        
        rating_dat,err = ratingupdate_schema.load(req_data,partial=True)
        rating.update(**rating_dat)
  
        return db_update(rating,rating_schema)
    else:
        return jsonify({'message':'rating could not be found'}),404

#get all ratings for a given user
@app.route('/ratings/user/<int:user_id>')
def get_ratings_user_id(user_id):
    user = User.query.get(user_id)
    if user:
        ratings = Rating.query.filter_by(user=user).all()
        return jsonify({'ratings':ratings_schema.dump(ratings)})
    else:
        return jsonify({'message':'user could not be found'}),404

#get all ratings for a given restaurant
@app.route('/ratings/restaurant/<int:restaurant_id>')
def get_ratings_restaurant_id(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant:
        ratings = Rating.query.filter_by(restaurant=restaurant).all()
        return jsonify({'ratings':ratings_schema.dump(ratings)})
    else:
        return jsonify({'message':'restaurant could not be found'}),404


