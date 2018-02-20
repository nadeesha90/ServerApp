from app import db
from marshmallow import Schema, fields, ValidationError, pre_load, post_load
from marshmallow import validate
from datetime import datetime

class User(db.Model):
    """
    Create a user table
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    phone_number = db.Column(db.String(60), index=True)

    ratings = db.relationship("Rating",backref="user")

    __table_args__ = (db.UniqueConstraint('first_name','last_name','phone_number',name='first_last_phone_uc'),)

    def __repr__(self):
        return '<User First Name: {} Last Name: {} Phone Number: {}>'.format(self.first_name,self.last_name,self.phone_number)

    def update(self,first_name=None,last_name=None,phone_number=None):
        self.first_name = first_name if first_name else self.first_name
        self.last_name = last_name if last_name else self.last_name
        self.phone_number = phone_number if phone_number else self.phone_number

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone_number = fields.Str(required=True)

class Restaurant(db.Model):
    """
    Create a Restaurant table
    """
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60),unique=True)
    category = db.Column(db.String(60))
    address_id = db.Column(db.Integer,db.ForeignKey('addresses.id'))

    ratings = db.relationship("Rating",backref="restaurant")
 
    __table_args__ = (db.UniqueConstraint('name','category','address_id',name='name_category_address'),)

    def __repr__(self):
        return '<Restaurant name: {} category: {} address: {}>'.format(self.name,self.category,self.address)

    def __init__(self,name,category,address):
        self.name = name
        self.category = category
        self.address = Address(**address)

    def update(self,name=None,category=None,address=None):
        self.name = name if name else name
        self.category = category if category else self.category
        self.address = Address(**address) if address else self.address

class Address(db.Model):
    """
    Create a Address table
    """
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(60))
    state = db.Column(db.String(30))
    city = db.Column(db.String(30))
    zipcode = db.Column(db.String(20))
 
    restaurants = db.relationship("Restaurant",backref="address")

    __table_args__ = (db.UniqueConstraint('address','state','city','zipcode',name='addr_state_city_zip'),)

    def __repr__(self):
        return '<Adress: {} state: {} city: {} zipcode: {}>'.format(self.address,self.state,self.city,self.zipcode)

class AddressSchema(Schema):
    id = fields.Int(dump_only=True)
    address = fields.Str(required=True)
    state = fields.Str(required=True)
    city = fields.Str(required=True)
    zipcode = fields.Str(required=True)
    
class RestaurantSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    address = fields.Nested(AddressSchema,required=True)

class Rating(db.Model):
    """
    Create a Rating table
    """
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer)
    food = db.Column(db.Integer)
    cleanliness = db.Column(db.Integer)
    service = db.Column(db.Integer)
    totalscore = db.Column(db.Float)
    comment = db.Column(db.String(120))

    restaurant_id = db.Column(db.Integer,db.ForeignKey('restaurants.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    date = db.Column(db.DateTime,index=True,default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('restaurant_id','user_id','date',name='restaurant_user_date'),)

    def __init__(self,cost,food,cleanliness,service,restaurant,user,comment=''):
        self.cost = cost
        self.food = food 
        self.cleanliness = cleanliness 
        self.service = service 
        self.totalscore = (cost + food + cleanliness + service)/4.0
        self.restaurant = restaurant
        self.user = user
        self.comment = comment

    def update(self,cost=None,food=None,cleanliness=None,service=None,comment=None):
        self.cost = cost if cost else self.cost 
        self.food = food if food else self.food
        self.cleanliness = cleanliness if cleanliness else self.cleanliness
        self.service = service if service else self.service
        self.comment = comment if comment else self.comment

        self.totalscore = (self.cost + self.food + self.cleanliness + self.service)/4.0
        self.date = datetime.utcnow()

#add validaton for ratings
class RatingSchema(Schema):
    id = fields.Int(dump_only=True)
    cost = fields.Int(required=True,validate=validate.Range(min=0,max=5))
    food = fields.Int(required=True,validate=validate.Range(min=0,max=5))
    cleanliness = fields.Int(required=True,validate=validate.Range(min=0,max=5))
    service = fields.Int(required=True,validate=validate.Range(min=0,max=5))
    comment = fields.Str()

    restaurant_id = fields.Int(required=True,load_only=True)

    restaurant = fields.Nested(RestaurantSchema,dump_only=True)
    user = fields.Nested(UserSchema,dump_only=True) 
    totalscore = fields.Float(dump_only=True)
    date = fields.DateTime(dump_only=True)
    
class RatingSchemaUpdate(Schema):
    cost = fields.Int(validate=validate.Range(min=0,max=5))
    food = fields.Int(validate=validate.Range(min=0,max=5))
    cleanliness = fields.Int(validate=validate.Range(min=0,max=5))
    service = fields.Int(validate=validate.Range(min=0,max=5))
    comment = fields.Str()

 
