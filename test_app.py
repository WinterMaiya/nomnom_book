# Test Files for all functions
from multiprocessing.sharedctypes import Value
import os
import json
from unittest import TestCase
from sqlalchemy import exc, or_

from models import db, connect_db, User, Friend, Recipe, DEFAULT_PROFILE_PIC
from bs4 import BeautifulSoup

os.environ["DATABASE_URL"] = "postgresql:///nomnom_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class TestApp(TestCase):
    """Tests various functions of the app"""

    def setUp(self):
        """Creates the test client and adds a bunch of random data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Create a bunch of random users
        self.testuser = User.signup(
            name="Chihiro",
            email="test@test.com",
            password="Test12345!",
            favorite_food="Fish Oil",
        )

        self.testfriend1 = User.signup(
            name="romeo",
            email="test1@test.com",
            password="Test12345!",
            favorite_food="Ear Plugs",
        )

        self.testfriend2 = User.signup(
            name="Angel",
            email="test2@test.com",
            password="Test12345!",
            favorite_food="Ice Cream",
        )

        db.session.commit()

        # Adds in a test recipe
        self.recipe1 = Recipe(
            name="Fish Tacos",
            description="A delicious recipe",
            picture="",
            homemade=True,
            ingredients=json.dumps(["test1", "test2"]),
            directions=json.dumps(["test3", "test4"]),
            image_id=0,
            created_by="Chihiro",
            category="main",
            user_id=1,
        )

        db.session.add(self.recipe1)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_user_model(self):
        """Tests if signing up works"""
        u = User(
            email="model@model.com",
            name="Test",
            password="hashedpassword",
            favorite_food="yum yum",
        )

        db.session.add(u)
        db.session.commit()

        # Checks to make sure no friends or recipes exist
        self.assertEqual(len(u.friends), 0)
        self.assertEqual(len(u.recipes), 0)

    def test_valid_signup(self):
        u = User.signup(
            email="ubble@ubble.com",
            name="Ubble",
            favorite_food="Chapstick",
            password="Password12345!",
        )
        db.session.commit()

        u = User.query.get(4)
        self.assertIsNotNone(u)
        self.assertEqual(u.email, "ubble@ubble.com")
        self.assertEqual(u.name, "Ubble")
        self.assertEqual(u.favorite_food, "Chapstick")
        self.assertEqual(u.profile_pic, DEFAULT_PROFILE_PIC)
        # Checks to make sure the password is hashed
        self.assertNotEqual(u.password, "Password12345!")
        self.assertTrue(u.password.startswith("$2b$"))
        # Checks to make sure no friends exist
        self.assertEqual(len(u.friends), 0)

    def test_invalid_email_signup(self):
        invalid = User.signup(
            email=None,
            name="Ubble",
            password="Password12345!",
            favorite_food="Chapstick",
        )
        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    def test_duplicate_email_signup(self):
        invalid = User.signup(
            email="test@test.com",
            name="Ubble",
            password="Password12345!",
            favorite_food="Chapstick",
        )
        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    def test_invalid_name_signup(self):
        invalid = User.signup(
            email="ubble@ubble.com",
            name=None,
            password="Password12345!",
            favorite_food="Chapstick",
        )
        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    def test_valid_authentication(self):
        u = User.authenticate(email=self.testuser.email, password="Test12345!")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser.id)

    def test_invalid_email(self):
        self.assertFalse(User.authenticate(email="notrealemail", password="Test12345!"))

    def test_wrong_password(self):
        self.assertFalse(
            User.authenticate(email=self.testuser.email, password="tEST67890#")
        )

    def test_friend_request(self):
        Friend.send_request(
            self_email=self.testfriend1.email, friend_email=self.testfriend2.email
        )
        f_requests = Friend.query.filter(
            Friend.user_request_received_id == self.testfriend2.id,
            Friend.accepted == False,
        ).first()

        self.assertIsNotNone(f_requests)
        self.assertEqual(f_requests.user_request_sent_id, self.testfriend1.id)

        self.assertEqual(self.testfriend2.friends, [])

        f_requests.accepted = True
        db.session.add(f_requests)
        db.session.commit()
        friend_group = Friend.query.filter(
            or_(
                Friend.user_request_received_id == self.testfriend2.id,
                Friend.user_request_sent_id == self.testfriend2.id,
            ),
            Friend.accepted == True,
        ).all()
        data = []
        for req in friend_group:
            if req.user_request_sent_id != self.testfriend2.id:
                friend_id = req.user_request_sent_id
            else:
                friend_id = req.user_request_received_id
            user = User.query.get(friend_id)
            data.append(user)

        self.assertIsNotNone(data)
        self.assertEqual(data, [self.testfriend1])
