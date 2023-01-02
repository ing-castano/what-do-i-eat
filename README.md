# What do I eat? :yum: 
Web App to suggest what to cook with the user's ingredients available at their homes!

#### Video Demo:  <https://youtu.be/ATdL_jr6PLc>
#### Description:

The purpose of this final project is to deliver recipes suggestions based on the ingredients that the user has at his home.

This project is a Web Application that combines 
 - HTML, CSS, Javascript for Front-End user experience
 - SQLite for managing server databases
 - Flask - Python framework to asset server logic and communications.

As a result of the flask framework, the project has 3 different folders. 

__~/static__ 

~/images - Inside the static folders there is an "/images" directory which purpose is to store the user recipes images, correctly named and ordered.

__javascript.js__ - contains all the client-side code that make the user experiencie more comfortable. These includes:  

__USER INPUT HANDLING__

*async fetch()* - Function to ask the server for the lastest INGREDIENTS availables.

*add_ingredient()* - Using the lastest ingredients called in a global array "INGREDIENTS[]", validate user input so that it is valid and not repeated. HTML element with id=filters is updated (and hidden) with a string so that the form can then be submitted via GET request method. Also, adds and event listener to eliminate a user input in case of clicking the X button.

__LOG IN VALIDATION__

*validate_user()* - Validates username using RegEx to enter only valid characters (letters or numbers or underscore)

*validate_pass()* - Validates password using RegEx to include a special character, one capital letter, at least one number and minimum length of 8 characters.

*validate_confirmation()* - Using JQuery, every key up triggers a string comparison between password and confirmation and change bootstrap style properties.

__FAVOURITE HANDLING__

*add_bookmark()* - Simple but tricky AJAX + JQuery code to send a GET request to the server with the id of the post that we want to store as favourite. On response, HTML attribute is changed so that the next time we click on it drop_bookmark is called instead.

*drop_bookmark()* - The inverse of add_bookmark().

__IMAGE DRAG & DROP ZONE__

The whole point of these 3 functions is to upload an image to the server by draggin it to the browser.

*dropColor()* - Changes the color of the drag&drop section

*allowDrop()* - Prevent default behaivour on HTML elements

*drop()* - store the image in a file object, which is appended to the HTML form.

__styles.css__ - This projects is almost entirely made with bootstrap styling features but some color of the nav-bar and other @media queries for responsive design where introduced in this file.

__~/templates__

Contains all the HTML files needed to render the web application.

*layout.html* - Display a single layout common to all pages for this app, including some flask conditionals whether the user is logged in or not.

*register.html* - Let the user register to the web page.

*login.html* - Let the user log to the web page.

*changepass.html* - Let the user change the user password.

*index.html* - Allocate the form to do the query with the user input. Communicate with server through GET request

*myrecipes.html* - Homepage to users that are logged in. Contains recipes that have been uploaded by the user and recipes that have been marked as favourite one. 

*search.html* - Show the query's results. Has perfect match for recipes that can be done with the ingredients the user has. At the bottom of the page, Near match contains inspiration ideas from where at least one ingredients is in the user input.

*upload.html* - A form HTML tag with enctype="multipart/form-data" that let the user upload to the server all the information needed to post the recipe to web public. 


__~/app.py__

The server brain of the flask framework run with python. 

*@app.route("/")* - Refers to the homepage of the web app.

*@app.route("/ingredients")* - Return a dictionary in .JSON format to give the information updated from the SQL table "ing_table" to the web page.

*@app.route("/search")* - Contains the server logic to do the search of recipes in table "recipes" searching by where ingredients are NOT LIKE !user_query, i.e. hides everything else that is not part of the user query.

*@app.route("/register")* - Store the password and username in SQL table named "users".

*@app.route("/login")* - Set session['user_id'] = to the username to login.

*@app.route("/logout")* - Clear out user's session.

*@app.route("/change_password")* - After validation, old password is deleted and new password is stored.

*@app.route("/myrecipes")* - Query SQL table "recipes" filtering user_id. It also gives all the user_id's favourites recipes information to the web.

*@app.route("/add_bookmark")* - Insert into SQL table "favourites" the post id and user_id information retrieved from the web.

*@app.route("/drop_bookmark")* - Delete from SQL table "favourites" the post id and user_id information retrieved from the web.

*@app.route("/upload")* - If request is POST, then it store the user information (consisting of recipe's photo, name, ingredients, and instructions) into SQL table "recipes".


Finally, below it is shown the recipes.db .schema that is described above.

CREATE TABLE __ing_table__ (id INTEGER, ingredients TEXT NOT NULL, PRIMARY KEY(id));

CREATE INDEX ing_table_index on ing_table(ingredients);

CREATE TABLE __users__ (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);

CREATE INDEX users_index on users(username);

CREATE TABLE IF NOT EXISTS __"recipes"__(
id INTEGER PRIMARY KEY,
section INTEGER,
type TEXT,
name TEXT,
ingredients TEXT,
photo TEXT,
recipe TEXT,
user_id INTEGER,
likes INTEGER DEFAULT 0,
total_ing TEXT,
FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX ing_index ON recipes(ingredients);

CREATE TABLE __favourites__ (
recipes_id INTEGER,
user_id INTEGER,
FOREIGN KEY(recipes_id) REFERENCES recipes(id),
FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX user_favs ON favourites(user_id);