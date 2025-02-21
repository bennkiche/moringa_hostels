from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_serializer import Serializermixin

db = SQLAlchemy()

class User(db.Model, Serializermixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(100), nullable = False)
 
    booking = db.relationship('Booking', backref = 'user', lazy = True)
    accommodations = db.relationship('Accommodations', backref = 'user', lazy = True)
    user_verification = db.relationship('User_verification', backref = 'user', lazy = True)
    password_reset = db.relationship('Password_reset', backref = 'user', lazy = True)
   

    serialize_rules = ('-booking', '-accommodations.user' , '-user_verification.user', '-password_reset.user')
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"
    
    
class Accommodations(db.Model, Serializermixin):
    __tablename__ = 'accommodations'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    name  = db.Column(db.String(100), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(50), nullable=False)


    booking = db.relationship('Booking', backref = 'accommodations', lazy = True)
    user = db.relationship('User', backref = 'accommodations', lazy = True)


    serialize_rules = ('-user.accommodations', '-booking')

    def __repr__(self):
        return f"Accommodations('{self.name}', '{self.user_id}')"
    
class Booking(db.Model, Serializermixin):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accommodations_id = db.Column(db.Integer, db.ForeignKey('accommodations.id'), nullable=False)
    date_checkin = db.Column(db.DateTime, nullable=False)
    date_checkout = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref = 'booking', lazy = True)
    accommodations = db.relationship('Accommodations', backref = 'booking', lazy = True)
    payments = db.relationship('Payments', backref = 'booking', lazy = True)

    serialize_rules = ('-user.booking', '-payments', '-accommodations.booking')


    def __repr__(self):
        return f"Booking('{self.user_id}', '{self.accommodations_id}')"

class Payments(db.Model, Serializermixin):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)


    booking = db.relationship('Booking', backref = 'payments', lazy = True)

    
    serialize_rules = ('-booking')


    def __repr__(self):
        return f"Payment('{self.booking_id}', '{self.payment_amount}')"
    
class User_verification(db.Model, Serializermixin):
    __tablename__ = 'user_verification'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    

    user = db.relationship('User', backref = 'user_verification', lazy = True)

    serialize_rules =('-user.user_verification',)



class Password_reset(db.Model, Serializermixin):
    __tablename__ = 'password_reset'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reset_token = db.Column(db.String(100), nullable=False)
    reset_expires = db.Column(db.DateTime, nullable=False)
    

    user = db.relationship('User', backref = 'password_reset', lazy = True)

    serialize_rules = ('user.password_reset',)



    def __repr__(self):
        return f"Password_reset('{self.user_id}', '{self.reset_token}')"
