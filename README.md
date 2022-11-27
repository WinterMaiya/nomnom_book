<h1 align="center">The NomNom Book</h1>
<div id="header" align="center">
  <img src="https://media.giphy.com/media/YoKaNSoTHog8Y3550r/giphy.gif" width=250"/>                                                                              
</div>
                                                                                  

The NomNom Book is a website that lets you create and share recipes with your friends. Its creates a community cookbook where you can see every recipe your friends have added. This project was created as a fun personal project so I can share recipes I've made with my friends. However, anyone is allowed to use it or check it out!

## Deployed Website

<s>You can view the deployed website here: http://www.nomnombook.com. The website is being hosted by ***Heroku***.</s>
Heroku no longer allows a free addition to hosting so I am in the process of moving this application to a new site. 

## Getting Started:
### Create a username and password
*Your password is hashed using a bcrypt algorithm as well as a separate pepper.*

### Add friends:
You can add friends by typing in their **email address** and they will get a friend notification. Once they have accepted, congrats! You are now two cooks in the kitchen. Any recipes that you two add will be viewable by the other person. *Go and add as many friends as you would like.*

### Creating Recipes:
The most important part of the project is creating some amazing recipes. You can create these yourself using the add recipe button on the nav bar. However, if there is a recipe you love created by someone else you can click the add recipe from website button. Here you can add a **url** to any website recipe you want and using [spoonacular](https://spoonacular.com/food-api) it will grab the information for you. Be **warned** that the api is **not perfect**; therefore, you will have to edit the recipe to make sure everything is up to your standards. 

### Searching Recipes:
Using the categories tab on the main page you can easily filter which recipes you would like to see. Have a particular recipe you're looking for? Use the search bar on the navbar to quickly search for the recipe you're looking for. This will also include suggestions for fun recipes for you to try.

## External Api:
This project uses the [spoonacular](https://spoonacular.com/food-api) api. My website will connect to this api remotely to grab information on searched recipes as well as importing recipes from existing websites. This makes it **quick** and **easy** to grab your favorite recipes and quickly add them to your website.

## Technology Stack:
- Main Framework: **Flask, Jinja**
- **Bootstrap 5**
- **SQLAlchemy**
- **WTForms**
- **Flask Mail**
- **PostgreSQL**
- **Bcrypt**
- **ItsDangerous** *For secure tokens*
- **Cloudinary** *Lets me save images*

## License
[MIT](https://choosealicense.com/licenses/mit/)
