from datetime import datetime
from functools import wraps
from tempfile import mkdtemp

import os, re
from cs50 import SQL
from flask import Flask,flash, jsonify, redirect, render_template, request, session
#from flask_login import LoginManager, current_user, login_user
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Global Variables for uploading files
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_NAME"] = "session"
app.session_cookie_name = "session"

# Configure Upload path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)

# (DOCs) The login manager contains the code that lets your application and Flask-Login work together, 
# such as how to load a user from an ID, where to send users when they need to log in, and the like.
#login_manager = LoginManager()
#login_manager.init_app(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///recipes.db")

# Define Global Varialbe 
INGREDIENTS = []

# (Flask DOCs) You will need to provide a user_loader callback. This callback is used to reload the user object 
# from the user ID stored in the session. It should take the str ID of a user, and return the 
# corresponding user object.
#@login_manager.user_loader
#def load_user(user_id):
#    return User.get(user_id)

# Load ingredients availables at database on global INGREDIENTS
def load_ingredients():

    # Query Database
    ingredients_sql = db.execute("SELECT ingredients FROM ing_table ORDER BY ingredients")

    # Iterate through each ingredient and append to INGREDIENTS
    for ing in ingredients_sql:
        INGREDIENTS.append(ing['ingredients'])
load_ingredients()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def update_ingredients(word):
    """Update INGREDIENTS array and ing_table SQL database"""
    # Update ingredients sql table
    ing = db.execute("SELECT * FROM ing_table WHERE ingredients = ?", word)
    if not ing:
        db.execute("INSERT INTO ing_table (ingredients) VALUES (?)", word)

    # Insert element in sorted INGREDIENTS array
    for key, ingredient in enumerate(INGREDIENTS):
        if word == '':
            return
        if word == ingredient:
            return
        if word < ingredient:
            INGREDIENTS.insert(key, word)
            return
        if key + 1 == len(INGREDIENTS):
            INGREDIENTS.insert(key + 1, word)
            return


def last_filename():
    last_number = db.execute("SELECT id FROM recipes ORDER BY id DESC LIMIT 1")
    return last_number[0]['id']


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/suggest") 
def suggest():
    q = request.args.get("q")
    if q:
        ing_from_table = db.execute("SELECT ingredients FROM ing_table WHERE ingredients LIKE ? LIMIT 5", q + "%")
    else:
        ing_from_table = []

    return jsonify(ing_from_table)


@app.route("/ingredients")
def ingredients():
    return jsonify(INGREDIENTS)


@app.route("/search", methods=["GET", "POST"])
def search():
    
#Turn user query into usable server filters
    # Request query
    q = request.args.get("q")
    # Sort elements
    filters = q.split(",") 
    filters.sort()
    # Define search string for ingredients column
    search_code = ""
    for index, filter in enumerate(filters):
        if(index == len(filters) - 1):
            search_code += '"%' + str(filter) + '%"'
        else:
            search_code += '"%' + str(filter) + '%"' + ' OR ingredients LIKE '

# Search SQL database for all possible recipes with those ingredients (including partials)
    # Define list of search exclusions
    not_ingredients = INGREDIENTS.copy()
    for ingredient in INGREDIENTS:
        if ingredient in filters:
            not_ingredients.remove(ingredient)
    # Query DB by excluding VALUES
    i = 0
    complete_query = ""
    for ingredient in not_ingredients:
        if i == len(not_ingredients) - 1:
            complete_query += '"%' + ingredient + '%"'
        else:
            complete_query += '"%' + ingredient + '%"' + ' AND ingredients NOT LIKE '
        i += 1

    recipes = db.execute("SELECT * FROM recipes WHERE ingredients NOT LIKE " + complete_query + "ORDER BY length(ingredients) DESC")

# Search SQL database for related match
    related_recipes = db.execute("SELECT * FROM recipes WHERE ingredients LIKE" + search_code )
    # Eliminate duplicates
    for recipe in recipes:
        if recipe in related_recipes:
            related_recipes.remove(recipe)
            
# Load favs from user if it is logged in
    if 'user_id' not in session.keys():
        favs = []
    else:
        favs = db.execute("SELECT recipes_id FROM favourites WHERE user_id = ?", session["user_id"])


    return render_template("search.html", exact_match=recipes, related_match=related_recipes, favs=favs);


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Validation
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE username = ?", name)

        if not name or not password:
            flash("Must provide valid username/password")
            return redirect("/register")
        elif password != confirmation: 
            flash("Password do not match")
            return redirect("/register")
        elif rows:
            flash("Username is already taken")
            return redirect("/register")

        # New user registration
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", name, generate_password_hash(password))

        # User auto-login
        rows = db.execute("SELECT * FROM users WHERE username = ?", name)
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash("Thank you for registering!")
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Forget any user_id
        session.clear()
        
        # Validation
        if not request.form.get("username"):
            flash("Must provide user")
            return redirect("/login")

        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query USERS table
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check for username & pass
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Log in user
        #login_user(rows[0]["id"])
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["SESSION_COOKIE_NAME"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # Link or redirect goes here
    else:
        # Security issue: if /login was manually written by user, then force log out. 
        # If session.clear() is outside of the else, flash messages does not show because they are also cleared.
        if (session.get('user_id') == True):
            session.clear()
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """Change user password"""
    if request.method == "POST":

        # Validation
        name = request.form.get("username")
        password = request.form.get("oldpassword")
        new_password = request.form.get("password")
        new_confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE username = ?", name)

        if not name or not password or not rows:
            flash("Must provide valid username/password")
            return redirect("/change_password")
        elif (not rows[0]["id"] == session["user_id"]) or not check_password_hash(rows[0]["hash"], password):
            flash("Must provide valid username/password")
            return redirect("/change_password")
        elif new_password != new_confirmation:
            flash("Passwords do not match")
            return redirect("/change_password")

        # Change user password
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), session["user_id"])
        flash("Password changed succesfully")
        return redirect("/")

    else:
        return render_template("changepass.html")


@app.route("/myrecipes", methods=["GET", "POST"])
@login_required
def myrecipes():
    """ Show personal recipes and favorites ones """
    # Query for recipes from logged user
    uploads = db.execute("SELECT * FROM recipes WHERE user_id = ?", session["user_id"])
    # Query for saved user recipes
    favs = db.execute("SELECT * FROM recipes WHERE id IN (SELECT recipes_id FROM favourites WHERE user_id = ?)",session["user_id"])
    return render_template("myrecipes.html", uploads=uploads, favs=favs)


@app.route("/add_bookmark")
@login_required
def add_bookmark():
    # Request query
    recipe_id = request.args.get("id")
    # Insert favourite
    favs = db.execute("INSERT INTO favourites(recipes_id, user_id) VALUES (?,?)", recipe_id, session["user_id"])

    return str(recipe_id)


@app.route("/drop_bookmark")
@login_required
def drop_bookmark():
    # Request query
    recipe_id = request.args.get("id")
    # Drop favourite
    favs = db.execute("DELETE FROM favourites WHERE recipes_id = ? AND user_id = ?", recipe_id, session["user_id"])

    return str(recipe_id)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":

        # Request form data via POST
        file = request.files['file']
        recipe_name = request.form.get("recipe-name")
        recipe_ing = request.form.get("recipe-ing")
        recipe_total_ing = request.form.get("recipe-total-ing")
        recipe_txt = request.form.get("recipe-txt")
        
        # Validate user entry
        if not file:
            flash('No selected file')
            return render_template("upload.html")
        elif (not recipe_name or not recipe_ing or not recipe_total_ing or not recipe_txt):
            flash("Please complete all fields")
            return render_template("upload.html")
        else:
            # Prevent attacks with user filename
            filename = secure_filename(file.filename)

            # Correct photo filename and validate extension
            words = filename.split('.')
            extension = ''
            for word in words:
                if word.lower() in ALLOWED_EXTENSIONS:
                    extension = word
            if extension == '':
                flash('Extension file not valid')
                return render_template("upload.html")

        # Correct ingredients input
        recipe_valid_ing = re.sub("[^A-Za-z,\s]|[0-9]", "", recipe_ing).strip(",").lower()
        recipe_valid_total_ing = re.sub("[^A-Za-z,\s]|[0-9]", "", recipe_total_ing).strip(",").lower()

        # Save photo in static Flask Folder 
        number = last_filename() + 1
        filename = str(number) + '_photo1.' + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save recipe data in sql database
        db.execute("INSERT INTO recipes (name, ingredients, photo, recipe, user_id, total_ing) VALUES (?, ?, ?, ?, ?, ?)",
                           recipe_name, recipe_valid_ing, filename, recipe_txt, session["user_id"], recipe_valid_total_ing)

        # Update INGREDIENTS list
        words = recipe_valid_ing.split(",")
        for word in words:
            update_ingredients(word.strip(" "))
        
        # Everything OK, render_template
        flash("Upload successfull")
        return render_template("myrecipes.html")

    else:
        return render_template("upload.html")
  

""" fetch function updated by server response.
@app.route("/serv_likes", methods=["GET"])
def serv():
    p = request.args.get('p')
    if p is not None:
        postlikes = db.execute("SELECT * FROM recipes WHERE id = ?", p)
    else:
        postlikes = " ";
    
    return str(postlikes[0]["likes"])


@app.route("/favs")
@login_required
def favs():
    f = request.args.get('f')
    if f is not None:
        saved_post = db.execute("SELECT * FROM favourites WHERE user_id = ? AND recipes_id = ?", session["user_id"], f)
    else:
        saved_post = [];
    
    return jsonify(saved_post)
"""