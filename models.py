from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
    # Relationship definition
    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    user_verification = db.relationship('User_verification', back_populates='user', lazy=True)
    password_reset = db.relationship('Password_reset', back_populates='user', lazy=True)

    serialize_rules = ('-bookings', '-user_verification.user', '-password_reset.user')

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

    
    
class Accommodations(db.Model, SerializerMixin):
    __tablename__ = 'accommodations'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    name  = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    availability = db.Column(db.String, nullable=False)

    bookings = db.relationship('Booking', back_populates = 'accommodations', lazy = True)
    rooms = db.relationship('Rooms', back_populates = 'accommodations', lazy = True)

    serialize_rules = ('-bookings', '-rooms',)

    def __repr__(self):
        return f"Accommodations('{self.name}', '{self.price}', '{self.image}', '{self.description}', '{self.availability}' )"
    
class Rooms(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.Integer, nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.id'), nullable=False)
    availability = db.Column(db.String, nullable=False)

    accommodations = db.relationship('Accommodations', back_populates='rooms', lazy=True)
    bookings = db.relationship('Booking', back_populates='room', lazy=True)

    __table_args__ = (UniqueConstraint('room_no', 'accommodation_id', name='_room_accommodation_uc'),)

    serialize_rules = ('-accommodations.rooms', '-bookings')
    
class Booking(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Define the relationship with User without conflict
    user = db.relationship('User', back_populates='bookings', lazy=True)
    accommodations = db.relationship('Accommodations', back_populates='bookings', lazy=True)
    room = db.relationship('Rooms', back_populates='bookings', lazy=True)
    payments = db.relationship('Payments', back_populates='book', lazy=True)

    serialize_rules = ('-user.bookings', '-payments', '-accommodations.bookings', '-room.bookings')

    def __repr__(self):
        return f"Booking('{self.user_id}', '{self.accommodations_id}', '{self.room}', '{self.start_date}', '{self.end_date}')"


class Payments(db.Model, SerializerMixin):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)


    book = db.relationship('Booking', back_populates = 'payments', lazy = True)

    
    serialize_rules = ('-booking')


    def __repr__(self):
        return f"Payment('{self.booking_id}', '{self.payment_amount}')"
    
class User_verification(db.Model, SerializerMixin):
    __tablename__ = 'user_verification'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    

    user = db.relationship('User', back_populates = 'user_verification', lazy = True)

    serialize_rules =('-user.user_verification',)



class Password_reset(db.Model, SerializerMixin):
    __tablename__ = 'password_reset'

    id = db.Column(db.Integer, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reset_token = db.Column(db.String(100), nullable=False)
    reset_expires = db.Column(db.DateTime, nullable=False)
    

    user = db.relationship('User', back_populates = 'password_reset', lazy = True)

    serialize_rules = ('user.password_reset',)



    def __repr__(self):
        return f"Password_reset('{self.user_id}', '{self.reset_token}')"
