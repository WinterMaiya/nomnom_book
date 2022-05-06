# TODO: Edit Friends
# TODO: Add recipe from website
# TODO: Add Reset Password
# TODO: Add Tests
import os
import requests
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
import random
import string
from cloudinary import CloudinaryImage
from flask import Flask, render_template, g, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from secret import s_api_key, s_cloud_api_key, s_cloud_api_secret, s_cloud_name
from models import User, connect_db, db, Friend, Recipe
from forms import (
    SignUp,
    Login,
    NewRecipeForm,
    AddFriend,
    recipe_categories,
    EditUser,
    EditRecipeForm,
    ChangePassword,
)
from werkzeug.utils import secure_filename

IMAGE_URL = (
    "https://res.cloudinary.com/grandsloth/image/upload/w_1000,ar_1:1,c_fill,g_auto"
)
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///nomnom_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "Secret")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

api_key = os.environ.get("SPOON_API_KEY", s_api_key)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", s_cloud_name),
    api_key=os.environ.get("CLOUDINARY_API_KEY", s_cloud_api_key),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", s_cloud_api_secret),
)


connect_db(app)
###########################################################################
# Users
@app.before_request
def add_user_to_g():
    """If a user is logged in it will add them to the global variable g"""

    if CURR_USER_KEY in session:
        g.friend_request = False
        # Adds the user to the current global variable
        g.user = User.query.get_or_404(session[CURR_USER_KEY])
        # Looks to see if any friend requests exist
        g.f_requests = Friend.query.filter(
            Friend.user_request_received_id == g.user.id,
            Friend.accepted == False,
        ).all()
        if g.f_requests:
            g.friend_request = True
            g.request_length = len(g.f_requests)

        # Compiles all the friends the user has for easy display
        friend_group = Friend.query.filter(
            or_(
                Friend.user_request_received_id == g.user.id,
                Friend.user_request_sent_id == g.user.id,
            ),
            Friend.accepted == True,
        ).all()
        data = []
        for req in friend_group:
            if req.user_request_sent_id != g.user.id:
                friend_id = req.user_request_sent_id
            else:
                friend_id = req.user_request_received_id
            user = User.query.get(friend_id)
            data.append(user)
        g.friends = data

    else:
        g.user = None


def do_login(user):
    """logs in a user"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """logs out the user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def check_user():
    """This makes sure the user is logged in to access a route. Otherwise it redirects to login with a warning"""
    if not g.user:
        flash("Must be logged in", "danger")
        return redirect("/login")


@app.route("/logout")
def logout():
    """Logs out the user"""

    do_logout()

    flash("You have successfully logged out!", "success")
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Logs in the user.
    Creates a user and adds them to the DB. Then redirect back to the homepage.
    If a email already exists return an error"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = SignUp()

    if form.validate_on_submit():
        try:
            user = User.signup(
                name=form.name.data,
                email=form.email.data,
                favorite_food=form.favorite_food.data,
                password=form.password.data,
            )
            db.session.commit()
        except IntegrityError as e:
            flash("Email already taken", "danger")
            print(e)
            return render_template("/signup.html", form=form)

        do_login(user)
        flash(f"Thanks for Signing up {user.name}!", "success")
        return redirect("/")

    else:
        return render_template("/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs in a user and checks their credentials"""

    form = Login()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Successfully logged you in {user.name}!", "success")
            return redirect("/")

        flash("Invalid email or password", "danger")
    return render_template("/login.html", form=form)


#########################################################################
# Basic Routes and homepages


@app.route("/")
def homepage():
    """Show the homepage
    If a user is not logged in show the default welcome page
    if a user is logged in show their cookbook"""
    if g.user:
        # Runs through and creates all the recipes in a nice list to display to the user
        recipes = []
        for recipe in g.user.recipes:
            recipes.append(recipe)
        for friend in g.friends:
            for recipe in friend.recipes:
                recipes.append(recipe)
        return render_template("/cookbook.html", recipes=recipes)
    else:
        return render_template("/index.html")


@app.route("/profile", methods=["GET", "POST"])
def edit_profile():
    """Allows the user to edit their profile. Also has links to changing your password"""
    check_user()
    form = EditUser()
    if form.validate_on_submit():
        user = User.authenticate(g.user.email, form.password.data)
        if user:
            user.name = form.name.data
            user.email = form.email.data
            user.favorite_food = form.favorite_food.data
            if form.profile_pic.data:
                cloudinary.uploader.destroy(f"users/{user.image_id}", invalidate=True)
                letters = string.ascii_letters
                filename = f"{g.user.name}" + "".join(
                    random.choice(letters) for i in range(10)
                )
                form.profile_pic.data.filename = filename
                cloudinary.uploader.upload(
                    form.profile_pic.data,
                    public_id=f"users/{filename}",
                    resource_type="image",
                )
                image = str(CloudinaryImage(f"/users/{filename}"))
                user.profile_pic = f"{IMAGE_URL}{image}"
                user.image_id = filename
            db.session.add(user)
            db.session.commit()
            flash("Profile Updated Successfully", "success")
            return redirect("/")
        flash("Incorrect Password", "warning")
        return redirect("/profile")
    else:
        form.name.data = g.user.name
        form.email.data = g.user.email
        form.favorite_food.data = g.user.favorite_food
        return render_template("edit_profile.html", form=form)


@app.route("/password", methods=["GET", "POST"])
def change_password():
    """Allows the user to change their password. Takes their current password and a new password"""
    check_user()
    form = ChangePassword()
    if form.validate_on_submit():
        user = User.authenticate(g.user.email, form.curr_password.data)
        if user:
            user.password = User.change_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Password Changed!")
            return redirect("/profile")
        flash("Incorrect Password", "warning")
        return redirect("/password")

    return render_template("change_password.html", form=form)


#############################################################################
# Routes for external Api


@app.route("/search")
def search():
    """Allows the user to search. If the limit on the api is reached display a 402 error page"""
    if g.user:
        search = request.args.get("q")

        if not search:
            flash("Must have a Search Term", "warning")
            return redirect("/")

        resp = requests.get(
            "https://api.spoonacular.com/recipes/complexSearch",
            params={
                "apiKey": api_key,
                "query": search,
                "number": 6,
            },
        )
        response_data = resp.json()
        if not response_data:
            return redirect("/api/limit"), 402

        return render_template("/api/search.html", data=response_data, search=search)

    else:
        flash("Error must be logged in", "warning")
        return redirect("/login")


@app.route("/api/recipe/<int:recipe_id>")
def show_api_recipe(recipe_id):
    """Shows the full details of the recipe. If a user would like to add the recipe
    to their cook book there will be a button that says add to my cook book.
    this will copy the recipe into my database and show it along with the user"""
    check_user()

    resp = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params={"apiKey": api_key},
    )
    resp2 = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions",
        params={"apiKey": api_key},
    )

    response_data = resp.json()
    response_data2 = resp2.json()
    try:
        if response_data.status_code or response_data2.status_code == 402:
            return redirect("/api/limit")
    except:
        return render_template(
            "/api/recipe.html", data=response_data, directions=response_data2
        )


@app.route("/api/limit")
def api_402():
    """Api daily limit has been reached. Check back tomorrow. Informs the user of the error"""
    return render_template("/api/limit.html")


@app.route("/api/recipe/add/<int:recipe_id>")
def add_api_recipe(recipe_id):
    """Adds a recipe from the API to the nomnom database. We save data in
    the session to save the amount of times we have to request data. Not the most
    ideal but with a free api this is what I have to work with
    we basically use the data to setup a recipe as it would be in my database.
    then it removes the recipes from the session"""
    check_user()
    try:
        resp = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/information",
            params={"apiKey": api_key},
        )
        resp2 = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions",
            params={"apiKey": api_key},
        )

        data = resp.json()
        directions = resp2.json()

        ingredients = []
        direct = []
        # This is to set up all my arrays
        for item in data["extendedIngredients"]:
            ingredients.append(item["original"])
        for item in directions[0]["steps"]:
            direct.append(item["step"])
        # This is to find the right category. Just finds the first most relevant one
        for item in data["dishTypes"]:
            if item in recipe_categories:
                if item == "main course":
                    category = "main"
                category = item
                break
        # Create the recipe and add it to the database
        recipe = Recipe(
            name=data["title"],
            description=data["summary"],
            picture=data["image"],
            homemade=False,
            ingredients=json.dumps(ingredients),
            directions=json.dumps(direct),
            created_by=data["sourceName"],
            user_id=g.user.id,
        )
        db.session.add(recipe)
        db.session.commit()
        # Remove data from the session
        flash("Recipe added successfully", "success")
    except:
        flash("Sorry an error occurred when we tried to add the recipe", "warning")
    return redirect("/")


###############################################################################################################
# Routes for internal recipes


@app.route("/recipe/add", methods=["GET", "POST"])
def add_recipe():
    """Lets the user add their own custom recipe to their cookbook"""
    if g.user:
        form = NewRecipeForm()

        if form.validate_on_submit():
            ingredients = json.dumps(form.ingredients.data)
            directions = json.dumps(form.directions.data)

            letters = string.ascii_letters
            filename = f"{g.user.name}" + "".join(
                random.choice(letters) for i in range(10)
            )
            form.picture.data.filename = filename
            cloudinary.uploader.upload(
                form.picture.data,
                public_id=f"recipes/{filename}",
                resource_type="image",
            )
            image = str(CloudinaryImage(f"/recipes/{filename}"))
            recipe = Recipe(
                name=form.name.data,
                description=form.description.data,
                picture=f"{IMAGE_URL}{image}",
                image_id=filename,
                homemade=True,
                ingredients=ingredients,
                directions=directions,
                created_by=g.user.name,
                user_id=g.user.id,
                category=form.category.data,
            )
            db.session.add(recipe)
            db.session.commit()
            flash("Recipe Successfully Added!", "success")
            return redirect(f"/recipe/{recipe.id}")
        return render_template("recipes/newrecipe.html", form=form)
    else:
        flash("Error must be logged in", "warning")
        return redirect("/login")


@app.route("/recipe/<int:id>/edit", methods=["GET", "POST"])
def edit_recipe(id):
    if g.user:
        form = EditRecipeForm()
        recipe = Recipe.query.get_or_404(id)

        if form.validate_on_submit():
            ingredients = json.dumps(form.ingredients.data)
            directions = json.dumps(form.directions.data)
            if form.picture.data:
                # Edits the picture only if a picture has been uploaded with the request. Otherwise it doesn't change anything
                cloudinary.uploader.destroy(
                    f"recipe/{recipe.image_id}", invalidate=True
                )
                letters = string.ascii_letters
                filename = f"{g.user.name}" + "".join(
                    random.choice(letters) for i in range(10)
                )
                form.picture.data.filename = filename
                cloudinary.uploader.upload(
                    form.picture.data,
                    public_id=f"recipes/{filename}",
                    resource_type="image",
                )
                image = str(CloudinaryImage(f"/recipes/{filename}"))
                recipe.picture = f"{IMAGE_URL}{image}"
                recipe.image_id = filename
            recipe.name = form.name.data
            recipe.description = form.description.data
            recipe.ingredients = ingredients
            recipe.directions = directions
            recipe.category = form.category.data
            db.session.add(recipe)
            db.session.commit()
            flash("Recipe Successfully Edited", "success")
            return redirect(f"/recipe/{recipe.id}")
        else:
            ingredients = json.loads(recipe.ingredients)
            directions = json.loads(recipe.directions)
            form.name.data = recipe.name
            form.description.data = recipe.description
            form.directions.pop_entry()
            for part in directions:
                form.directions.append_entry(part)
            form.ingredients.pop_entry()
            for part in ingredients:
                form.ingredients.append_entry(part)
            form.category.data = recipe.category
            return render_template("recipes/editrecipe.html", form=form)
    else:
        flash("Error must be logged in", "warning")
        return redirect("/login")


@app.route("/recipe/<int:id>")
def recipe_view(id):
    """Displays a recipe in the database to a user"""
    check_user()
    recipe = Recipe.query.get_or_404(id)
    ingredients = json.loads(recipe.ingredients)
    directions = json.loads(recipe.directions)
    return render_template(
        "/recipes/recipe.html",
        data=recipe,
        ingredients=ingredients,
        directions=directions,
    )


@app.route("/recipe/<int:id>/delete")
def delete_recipe(id):
    check_user()
    recipe = Recipe.query.get_or_404(id)
    if recipe.user_id == g.user.id:
        cloudinary.uploader.destroy(f"recipes/{recipe.image_id}", invalidate=True)
        db.session.delete(recipe)
        db.session.commit()
        flash("Successfully Deleted the Recipe", "success")
        return redirect("/")
    else:
        flash("Can't delete a recipe that isn't yours!", "danger")
        return redirect("/")


##############################################################################
# Friends
@app.get("/friends/requests")
def friend_requests():
    """Finds all the friend requests that have been sent"""
    check_user()
    if g.friend_request:
        f_requests = Friend.query.filter(
            Friend.user_request_received_id == g.user.id,
            Friend.accepted == False,
        ).all()
        data = []
        for req in f_requests:
            user = User.query.get(req.user_request_sent_id)
            data.append(user)
        return render_template("/friends/requests.html", requests=f_requests, data=data)
    flash("No friend requests at the moment", "warning")
    return redirect("/")


@app.route("/friends/requests/<id>")
def accept_decline_friend(id):
    """Accepts or declines a friend request"""
    check_user()
    if g.friend_request:
        try:
            choice = request.args.get("a")
            f_requests = Friend.query.filter(
                Friend.user_request_sent_id == id,
                Friend.user_request_received_id == g.user.id,
                Friend.accepted == False,
            ).first()
            if choice == "true":
                f_requests.accepted = True
                db.session.add(f_requests)
                db.session.commit()
                flash(f"Friend Request Accepted", "success")
            elif choice == "false":
                db.session.delete(f_requests)
                db.session.commit()
                flash(f"Friend Request Rejected", "success")
            else:
                flash("not a correct value", "danger")
        except:
            flash("Something went wrong", "warning")

        return redirect("/friends/requests")


@app.route("/friends/add", methods=["GET", "POST"])
def add_friend():
    """Creates the form which allows users to add friends"""
    check_user()
    form = AddFriend()

    if form.validate_on_submit():
        try:
            Friend.send_request(self_email=g.user.email, friend_email=form.email.data)
            flash("Thanks! We'll send that user a request", "success")
            return redirect("/friends/add")
        except:
            flash("You've already added that user!", "warning")
            return redirect("/friends/add")
    return render_template("/friends/add.html", form=form)
