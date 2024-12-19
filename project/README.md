![alt text](image.png)
# ✈️🧳 Backpackify Web

## 💼 Introduction

### 💼 Context

Backpackify's main idea was born, well, at a random time of the day, i thought about when i used to travel frequently, one issue i had was always forgetting what i needed to bring with me in my bag, and this is when it "clicked for me"

Initially, this was planned to be an mobile app, but i had difficulties with Kotlin, then moved on to Flutter, but had tons of issues with the AVDs.

Finally, i decided to implement Backpackify Web, the browser version of the original Backpackify app idea.

### 💼 Expected outcome

Backpackify's main functionality is to store information about bags, including their name, type (backpack/luggage/others), destiny (where you will go with it), use (for what are you using it for) and finally, content.

Those bags are similar to phones notes apps, but instead of storing notes on your phone, your would store 'containers' called storages.

To guarantee the user could acess theses storages anywhere at anytime, users can register, log in and log out, having permanent accounts, safely stored in a database, with hashed passwords.

The user will be greeted with a landing page at landing.html, with the options to log in, register or recover forgotten passwords.

From there, the user can register at register.html, log in and being redirected to index.html, trying to recover an account with recover.html or, if anything goes wrong, be redirected to error.html. Well, these are all html templates, using Jinja for backend data display, bootstrap + custom css for styling and javascript ocasionally for AJAX searches at index.html! But if we only had these options, everything would be static, and the log in and register wouldn't even work, that is why there is a backend, implemented using Flask and Python.

## ✈️ Back-end Introduction

### ✈️ Full code walkthrough

The back-end is composed of 3 main files: app.py, helpers.py and backpackify.db.

I used 2 Python files: the main app.py, with the entire back-end functionality, and helpers.py with 3 helper functions (login_required, token_required and apology), and lastly, the actual database.

### ✈️ helpers.py

For the helper functions, i "imported" the login_required decorated function from week 9's problem set "Finance", where it will check if the user has an id stored in session, which means that the user has logged in, and will redirect the user in case this is False. I also modified it to check for the user's generated token instead of the id, implementing with that the token_required function, used later in the password recovery feature so the user won't be able to log in while validate the token. The apology function will render an HTML template (error.html), getting the arguments code and message and passing it to the HTML template via Jinja, informing the user in case anything goes wrong.

### ✈️ backpackify.db

For the database, 3 tables were created => users, backpacks and recoveries.
There are indexes in each table, for faster queries.

The users table stores the registered users, containig attached to each one, their email, username, id (user_id), (hashed) password, it is used mainly for SQL queries involving users infos.

The backpacks table stores the storages of each user, being relational with the users table, mainly in the (users) id <=> (backpacks) user_id relation. For each user storage, the user's id and storage's name/type/location/use/content is stored. The storage's location and use is optional, as it will not result in errors being NULL, but the storage's name, type and content will, as these informations are essential. Also, each user_id -> storage_name combination should be UNIQUE and will result in a error if the same user tries to create multiple storages with the same name.

The recoveries table stores the user's id, username, randomly generated string token, and the TIMESTAMP recording the date and time the token was generated. The username -> token combo is also UNIQUE and will result in errors if the same user generates the same token (which is statistically really really rare to occur, but it is possible). This table is meant only for the password recover process.

## 🧳 app.py => Outside the routes

### 🧳 Introduction

Finally, we reach the app.py file, the main back-end file.

Before we get into the main routes and requests, i will tackle the details outside of the routes.

We start importing all the libraries and dependencies we need for the back-end implementation, such as Flask, Flask_session, Flask_mail, Datetime, Werkzeug.security and more.

Then, the Flask app is initialized through the app variable.

We proceed to configure the recovery e-mail process for the password recovery option. The sender's email and password is stored in the enviroment variables folder, hidden, and through open() and read() these credentials are included inside the app.py file. The configuration includes the MAIL_SERVER + MAIL_PORT (in this casee, i chose Gmail), MAIL_USE_TLS, MAIL_USE_SSL and finally, the actual use of the credentials, with MAIL_USERNAME and MAIL_PASSWORD, than the email is set as the default sender with MAIL_DEFAULT_SENDER. The flask_mail Mail class is then initialized through the mail variable.

I chose to maintain the process inside one function, for better readability of code instead of just keeping it tossed around. The subject and body of the e-mail is declared and kept that way by default. I built the e-mail through Message() and stored it in the msg variable. Later, there is an attempt at sending the e-mail with the try and except blocks, catching any errors in the process and displaying it for debugging if necessary.

Then, the database is initialized through CS50's SQL() function, and stored in the db variable. The session feature is also initialized and additional configurations such SESSION_PERMANENT, SESSION_TYPE and after_request are done.

Now, we reach the Flask routes.

## 📍 Flask Routes

#### 📍 OBS.

Routes with the @login_required decorator use the login_required helper function, the same repeats with @token_required decorated routes

### 📍 /login

This route is "imported" from the "Finance" problem set previously mentioned, it firstly clears any previous sessions, and checks the request method, if it is a POST request, the typed data is gathered (username and password), and the back-end will query the database for matches of the informed username, and (hashed) password. If everything goes well, the user is logged in (session remembers the user's id) and redirected to the home-page (index.html or / route). A flash is also displayed informing the user about the successfull log in.

### 📍 /logout

For the log out route, also "imported" from the "Finance" problem set, to log the user out, the back-end will forget all the user's data through the clear() method, and redirect the user back into the landing page (landing.html or /landing route)

### 📍 /

The home-page route gathers everything (*) from the user's data in the backpacks table (matching with the currently logged in user's id through session["user_id"]) and sends it to the HTML index.html template through Jinja, the data is mainly used for Bootstrap modals functionalities.

### 📍 /landing

The landing page route will render the landing page HTML template (landing.html).

### 📍 /register

The register route will register any previously non-existing users into the database, furthermore allowing them to log in.

The back-end checks for the POST request, then gathers all the filled input fields, checks for any incorrect/empty input or password-confirmation mismatch, and in positive case, moves on into hashing the user's password and attempting to store everything inside the database's users table, automatically incrementing the user's id and confirming the registration, displayed as a flash() for the user to know.

### 📍 /create

The storage creation route is used to create and store new storages, maintaining their data together for each registered user.

If the request method is POST, the desired storage's name, type, destiny (location), use and content is gathered and processed, checking for incorrect/empty inputs (not for location and use, as they are optional input fields), all this data is then stored in the database and any error returned is handled and the feedback (be it positive or negative) is displayed to the user.

### 📍 /delete

Similar to /create, but simpler, the storage deletion route will delete any referred storage.

Every delete button refers to some storage, through the storage's name.

When the delete button is clicked, and confirmed through the deletion modal, the storage's name is gathered, and the referred storage (via storage_name) is deleted from the database, also referring to the currently logged user.

### 📍 /search

The /search GET request route complements the AJAX search JavaScript code, receiving the query and executing it through a search in the database, the result is then returned via JSON file (being it an empty list or not)

### 📍 /recover

This begins the password recovery process, going through 3 different routes (/recover, /validatetoken and /passwordchange).

This initial route checks for a POST request, then receives the user's username, desired to recover the account belonging to that username. The back-end then queries for that username's e-mail and id. A randomly generated 16-digits long string is stored in the token variable and now is the valid token for that password change request. The token's exact creation timestamp is registered in the created_at variable, to keep track of the token's expiration time (5 minutes away from the creation timestamp), the back-end then remembers the username and the referred token, and before moving on, for safety reasons, any previous tokens attached to that username are deleted. Then there is an attempt to register that token attached to the username into the recoveries table inside the database. If there is success, then a e-mail is sent to that username's referred e-mail address, containing inside the valid token. The user is then redirected to the token validation step.


### 📍 /validatetoken

For the token validation, when there is a POST request, the back-end will try to match the typed in token, though the current session username and the previously registered token, if there is success, the token matches and it is valid (before expiration), the user can now change the desired account's password, being redirected to the password change step.


### 📍 /passwordchange

The user types in it's new password and confirms it, and then proceeds to send a POST request to the back-end.

The back-end will receive the new password and confirmation, check if the match, if everything goes right, the new password will be hashed and there will be an UPDATE query on the database, referred to that account. The token will then be deleted, and the user will be redirected to the landing page, while the session will be cleared, for safety measures, so the user will need to finally log in with the new password.

## 🎯 Conclusion

Well, this is it! I am really happy to finish this project, it for sure taught me A LOT about full-stack development, and as i always heard, practice makes perfect, so being able to learn from actually making things is for me one of the best if not the best way to actually learn things with efficiency.

And also, i am really glad for David and all the CS50 staff for granting me the experience of this amazing course! I came from CS50P and i for sure loved CS50x and learned a lot from it.

As David's initial concerns were about people being able to program in itself, i am proud to say i learned to program in any language or method, always being aware of that technology's documentation.

Thank you, CS50!
Thank you, dear reader, or for anyone that interests in this project. There is a piece of my heart in it, for sure.

Thank you once again! :)

Yours sincerely, talindev