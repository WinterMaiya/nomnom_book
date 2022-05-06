from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    EmailField,
    TextAreaField,
    FieldList,
    SelectField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed

recipe_categories = [
    ("appetizer", "Appetizer"),
    ("snack", "Snack"),
    ("breakfast", "Breakfast"),
    ("salad", "Salad"),
    ("main", "Main Course"),
    ("soup", "Soup"),
    ("dessert", "Dessert"),
    ("beverage", "Beverage"),
]


class SignUp(FlaskForm):
    """Form for signing up a user"""

    name = StringField("Name", validators=[DataRequired(), Length(max=30)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    favorite_food = StringField("Favorite Food", validators=[Length(max=20)])
    password = PasswordField(
        "Password",
        validators=[
            Length(min=6, max=50),
            EqualTo("password_confirm", message="Passwords don't match"),
            DataRequired(),
        ],
    )
    password_confirm = PasswordField(
        "Confirm Password", validators=[Length(min=6, max=50)]
    )

    def validate_password(self, password):
        EXCLUDED_CHARS = " "
        for char in self.password.data:
            if char in EXCLUDED_CHARS:
                raise ValidationError(f"Spaces are not allowed in your password")


class Login(FlaskForm):
    """Form for loging in a user"""

    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class EditUser(FlaskForm):
    """Form for signing up a user"""

    name = StringField("Name", validators=[DataRequired(), Length(max=30)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    favorite_food = StringField("Favorite Food", validators=[Length(max=20)])
    profile_pic = FileField(
        "Image File",
        validators=[
            FileAllowed(["jpg", "png"]),
        ],
    )
    password = PasswordField(
        "Re-Enter Your Password",
        validators=[
            Length(min=6, max=50),
            DataRequired(),
        ],
    )


class ChangePassword(FlaskForm):
    curr_password = PasswordField("Current Password", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            Length(min=6, max=50),
            EqualTo("password_confirm", message="Passwords don't match"),
            DataRequired(),
        ],
    )
    password_confirm = PasswordField(
        "Confirm Password", validators=[Length(min=6, max=50)]
    )


#########################################################################################################
class NewRecipeForm(FlaskForm):
    name = StringField("Recipe Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField(
        "Describe your recipe!", validators=[DataRequired(), Length(max=10000)]
    )
    picture = FileField(
        "Image File",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png"]),
        ],
    )

    ingredients = FieldList(
        StringField("Ingredient 1:", validators=[DataRequired()]),
        min_entries=1,
        max_entries=100,
    )

    directions = FieldList(
        TextAreaField("Part 1:", validators=[DataRequired()]),
        min_entries=1,
        max_entries=100,
    )

    category = SelectField(
        "Category", choices=recipe_categories, validators=[DataRequired()]
    )


class EditRecipeForm(FlaskForm):
    name = StringField("Recipe Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField(
        "Describe your recipe!", validators=[DataRequired(), Length(max=10000)]
    )
    picture = FileField(
        "Image File",
        validators=[
            FileAllowed(["jpg", "png"]),
        ],
    )

    ingredients = FieldList(
        StringField("Ingredient 1:", validators=[DataRequired()]),
        min_entries=1,
        max_entries=100,
    )

    directions = FieldList(
        TextAreaField("Part 1:", validators=[DataRequired()]),
        min_entries=1,
        max_entries=100,
    )

    category = SelectField(
        "Category", choices=recipe_categories, validators=[DataRequired()]
    )


class AddFriend(FlaskForm):
    email = EmailField("Friends Email", validators=[DataRequired()])
