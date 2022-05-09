"""SQL Models for Nom Nom Book"""
import os
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

try:
    from secret import s_pepper
except:
    s_pepper = None
from itsdangerous import URLSafeTimedSerializer as Serializer

bcrypt = Bcrypt()
db = SQLAlchemy()
pepper = os.environ.get("PEPPER", s_pepper)

DEFAULT_PROFILE_PIC = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

secret_key_token = os.environ.get("SECRET_KEY_TOKEN", "itsasecret")


class Friend(db.Model):
    """Creates friends allowing users to combine recipe books"""

    __tablename__ = "friends"

    user_request_sent_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"),
        primary_key=True,
    )

    user_request_received_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"),
        primary_key=True,
    )

    accepted = db.Column(
        # This is to check if they have both confirmed they are friends
        db.Boolean,
        nullable=False,
        default=False,
    )

    @classmethod
    def send_request(cls, self_email, friend_email):
        """This will send an email to the user saying that a friend request has been sent
        If the user accepts it then the accepted boolean will change to True"""

        sender = User.query.filter_by(email=self_email).first()
        receiver = User.query.filter_by(email=friend_email).first()

        if sender and receiver:
            friend_to_be = Friend(
                user_request_sent_id=sender.id,
                user_request_received_id=receiver.id,
            )
            db.session.add(friend_to_be)
            db.session.commit()


class User(db.Model):
    """Creating a User"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    name = db.Column(
        db.String(30),
        nullable=False,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    profile_pic = db.Column(
        db.Text,
        default=DEFAULT_PROFILE_PIC,
    )

    favorite_food = db.Column(
        db.String(20),
    )

    image_id = db.Column(db.Text)

    friends = db.relationship(
        "User",
        secondary="friends",
        primaryjoin=(Friend.user_request_sent_id == id),
        secondaryjoin=(Friend.user_request_received_id == id),
    )

    recipes = db.relationship("Recipe")

    def __repr__(self):
        return f"<User #{self.id}, {self.name}, {self.email}, {self.favorite_food}"

    @classmethod
    def signup(cls, email, name, password, favorite_food):
        """Sign's Up a New User"""

        encrypt_pwd = bcrypt.generate_password_hash(password + pepper).decode("UTF-8")

        user = User(
            email=email,
            name=name,
            password=encrypt_pwd,
            favorite_food=favorite_food,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Finds the user and checks to see if passwords match"""

        user = cls.query.filter_by(email=email.lower()).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password + pepper)
            if is_auth:
                return user
        return False

    @classmethod
    def change_password(cls, password):
        """Allows the user to change password and encrypt it"""
        encrypt_pwd = bcrypt.generate_password_hash(password + pepper).decode("UTF-8")
        return encrypt_pwd

    def get_reset_password(self):
        """Creates secure key for user to reset password"""

        s = Serializer(secret_key_token)
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_password(token, expires_sec=1800):
        """Verifies the token is correct if not return None"""
        s = Serializer(secret_key_token)
        try:
            user_id = s.loads(token, expires_sec)["user_id"]
            return User.query.get(user_id)
        except:
            return None


class Recipe(db.Model):
    """A design for all recipes"""

    __tablename__ = "recipes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(500),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    picture = db.Column(db.Text)

    homemade = db.Column(
        db.Boolean,
        nullable=False,
    )

    ingredients = db.Column(
        db.Text,
        nullable=False,
    )

    directions = db.Column(
        db.Text,
        nullable=False,
    )

    image_id = db.Column(db.Text)

    created_by = db.Column(db.Text, default="Unknown")

    category = db.Column(db.Text, default="none")

    link = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship("User", overlaps="recipes")


def connect_db(app):
    """Connect to the database in flask"""

    db.app = app
    db.init_app(app)
