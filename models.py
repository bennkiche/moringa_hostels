from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_serializer import Serializermixin

db = SQLAlchemy()

class Users(db.Model, Serializermixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(100), nullable = False)
 
    bookings = db.relationship('Bookings', backref = 'user', lazy = True)
    accommodation = db.relationship('Accommodation', backref = 'user', lazy = True)
    user_verification = db.relationship('User_verification', backref = 'user', lazy = True)
    password_reset = db.relationship('Password_reset', backref = 'user', lazy = True)
   

    serialize_rules = ('-bookings', '-accommodation.user' , '-user_verification.user', '-password_reset.user')
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"
    
    
class Accommodation(db.Model, Serializermixin):
    __tablename__ = 'accommodation'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    name  = db.Column(db.String(100), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(50), nullable=False)


    bookings = db.relationship('Bookings', backref = 'accommodation', lazy = True)
    user = db.relationship('Users', backref = 'accommodation', lazy = True)


    serialize_rules = ('-user.accommodation', '-bookings')

    def __repr__(self):
        return f"Accommodation('{self.title}', '{self.user_id}')"
    
class Bookings(db.Model, Serializermixin):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodation.id'), nullable=False)
    date_checkin = db.Column(db.DateTime, nullable=False)
    date_checkout = db.Column(db.DateTime, nullable=False)

    user = db.relationship('Users', backref = 'bookings', lazy = True)
    accommodation = db.relationship('Accommodation', backref = 'bookings', lazy = True)
    payments = db.relationship('Payments', backref = 'bookings', lazy = True)

    serialize_rules = ('-user.bookings', '-payments', '-accommodation.bookings')


    def __repr__(self):
        return f"Bookings('{self.user_id}', '{self.accommodation_id}')"

class Payments(db.Model, Serializermixin):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    bookings_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)


    bookings = db.relationship('Bookings', backref = 'payments', lazy = True)

    
    serialize_rules = ('-bookings')


    def __repr__(self):
        return f"Payment('{self.bookings_id}', '{self.payment_amount}')"
    
class User_verification(db.Model, Serializermixin):
    __tablename__ = 'user_verification'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    

    user = db.relationship('Users', backref = 'user_verification', lazy = True)

    serialize_rules =('-user.user_verification',)



class Password_reset(db.Model, Serializermixin):
    __tablename__ = 'password_reset'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reset_token = db.Column(db.String(100), nullable=False)
    reset_expires = db.Column(db.DateTime, nullable=False)
    

    user = db.relationship('Users', backref = 'password_reset', lazy = True)

    serialize_rules = ('user.password_reset',)



    def __repr__(self):
        return f"Password_reset('{self.user_id}', '{self.password}')"
