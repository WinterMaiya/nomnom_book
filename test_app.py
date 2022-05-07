# Test Files for all functions
# Random Issue, whenever you run a test if you want to run the app normally you will have to
# clear your entire cache before it"ll open otherwise you'll get 404 errors
import os
import json
from unittest import TestCase
from sqlalchemy import exc, or_

from models import db, User, Friend, Recipe, DEFAULT_PROFILE_PIC

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False
os.environ["DATABASE_URL"] = "postgresql:///nomnom_test"
# app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False


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
            name="Florper",
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
        self.add_friend = Friend(
            user_request_sent_id=2, user_request_received_id=1, accepted=True
        )
        db.session.add(self.add_friend)
        self.add_friend_request = Friend(
            user_request_sent_id=3, user_request_received_id=1, accepted=False
        )
        db.session.add(self.add_friend_request)
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

    def test_search(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("/search?q=florp")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Florper", str(resp.data))

    def test_cookbook(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Create a community cookbook today!", str(resp.data))
            self.assertIn("Florper", str(resp.data))
            self.assertIn("Chihiro", str(resp.data))

    def test_homepage(self):
        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Create a community cookbook today!", str(resp.data))

    def test_recipe(self):
        with self.client as c:
            resp = c.get("/recipe/1")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Florper", str(resp.data))

    def test_recipe_delete(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("/recipe/1/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Successfully Deleted the Recipe", str(resp.data))

    def test_recipe_delete_unauthorized(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3

            resp = c.get("/recipe/1/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Successfully Deleted the Recipe", str(resp.data))

    def test_recipe_edit(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("recipe/1/edit")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<script src="/static/editrecipe.js"></script>', str(resp.data)
            )
            self.assertIn("Edit Recipe", str(resp.data))
            self.assertIn("Florper", str(resp.data))
            self.assertIn("A delicious recipe", str(resp.data))

    def test_recipe_edit_unauthorized(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2

            resp = c.get("recipe/1/edit")
            self.assertEqual(resp.status_code, 302)

    def test_recipe_add(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("/recipe/add")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("/static/newrecipe.js", str(resp.data))
            self.assertIn("New Recipe", str(resp.data))

    def test_friend_requests(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("/friends/requests")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Angel", str(resp.data))
            resp = c.get("/friends/requests/3?a=true", follow_redirects=True)
            self.assertIn("Cookbook", str(resp.data))
            self.assertIn("Angel", str(resp.data))

    def test_friend_requests_decline(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = c.get("/friends/requests")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Angel", str(resp.data))
            resp = c.get("/friends/requests/3?a=false", follow_redirects=True)
            self.assertIn("Cookbook", str(resp.data))
            self.assertNotIn("Angel", str(resp.data))

    def test_add_friend(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3
            resp = c.get("/friends/add")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add A Friend", str(resp.data))

            data = {"email": "test1@test.com"}
            resp = c.post("/friends/add", follow_redirects=True, data=data)
            self.assertNotIn("Romeo", str(resp.data))
            self.assertIn("Add A Friend", str(resp.data))

    def test_change_password(self):
        with self.client as c:
            resp = c.get("/password")
            self.assertEqual(resp.status_code, 302)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/password")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Change Your Password", str(resp.data))

    def test_edit_profile(self):
        with self.client as c:
            resp = c.get("/profile")
            self.assertEqual(resp.status_code, 302)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/profile")
            self.assertEqual(resp.status_code, 200)

    def test_api(self):
        """If this test fails double check that we haven't excceded our api limit"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/api/recipe/1439063")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Homemade yum yum", str(resp.data))

    def test_add_recipe_url(self):
        """If this test fails double check that we haven't excceded our api limit"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/api/external")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add A Recipe", str(resp.data))

            data = {
                "url": "https://foodista.com/recipe/ZHK4KPB6/chocolate-crinkle-cookies"
            }
            resp = c.post("/api/external", follow_redirects=True, data=data)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Cookbook", str(resp.data))
            self.assertIn("Cookies", str(resp.data))

    def test_404(self):
        with self.client as c:
            resp = c.get("/notaroute")
            self.assertEqual(resp.status_code, 404)

    def test_api_limit(self):
        with self.client as c:
            resp = c.get("/api/limit")
            self.assertEqual(resp.status_code, 402)

    def test_reset_password(self):
        with self.client as c:
            resp = c.get("/reset-password")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Reset Your Password", str(resp.data))

    def test_reset_password_login(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get("/reset-password")
            self.assertEqual(resp.status_code, 302)
