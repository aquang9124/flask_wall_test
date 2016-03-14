from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import hashlib

app = Flask(__name__)
app.secret_key = "asdf333asdF"
mysql = MySQLConnector('thewall')
# This route takes you to the index page where you can register and log in
@app.route('/')
def index():
	return render_template('index.html')
# This route takes you to a function that inserts a new user
@app.route('/create', methods=['POST'])
def create():
	username = request.form['username']
	email = request.form['email']
	password = request.form['password']
	passconf = request.form['passconf']
	if len(username) < 1:
		flash('Your username field cannot be blank')
		return redirect('/')
	if len(email) < 1:
		flash('Your email field cannot be blank')
		return redirect('/')
	if len(password) < 6:
		flash('Your password field cannot be less than 6 characters')
		return redirect('/')
	if password != passconf:
		flash('Passwords must match!')
		return redirect('/')
	password = hashlib.md5(password.encode()).hexdigest()
	query = "INSERT INTO users (username, email, password, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(username, email, password)
	mysql.run_mysql_query(query)
	user = mysql.fetch("SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email))
	session['username'] = username
	session['user_id'] = user[0]['id']
	return redirect('/wall')
# This route takes you to a function that shows the main wall for the user
@app.route('/wall')
def show():
	query = "SELECT users.username, messages.message, messages.id as message_id, messages.created_at as posted_date FROM users JOIN messages ON users.id = messages.user_id WHERE users.id = '{}'".format(session['user_id'])
	messages = mysql.fetch(query)
	query2 = "SELECT users.username, comments.comment, comments.created_at, comments.id as comment_id, comments.message_id as parent_id FROM users JOIN messages ON users.id = messages.user_id JOIN comments ON messages.id = comments.message_id WHERE users.id = '{}' AND comments.message_id = messages.id".format(session['user_id'])
	comments = mysql.fetch(query2)
	return render_template('wall.html', messages=messages, comments=comments)
# This route takes you to a function that logs you in
@app.route('/login', methods=['POST'])
def log_in():
	email = request.form['email']
	password = request.form['password']
	user = mysql.fetch("SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email))
	user_pass = user[0]['password']
	inputted_pass = hashlib.md5(password.encode()).hexdigest()
	print(user_pass)
	print(inputted_pass)
	if user_pass == inputted_pass:
		session['username'] = user[0]['username']
		session['user_id'] = user[0]['id']
		return redirect('/wall')
	else:
		flash('Incorrect information')
		return redirect('/')
# This route takes you to a function that adds a new message. It takes user_id as an argument
@app.route('/add_message/<user_id>', methods=['POST'])
def add_message(user_id):
	message = request.form['message']
	query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(message, user_id)
	mysql.run_mysql_query(query)
	return redirect('/wall')
@app.route('/add_comment/<user_id>/<message_id>', methods=['POST'])
def add_comment(user_id, message_id):
	comment = request.form['comment']
	query = "INSERT INTO comments (comment, message_id, user_id, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(comment, message_id, user_id)
	mysql.run_mysql_query(query)
	return redirect('/wall')
# This route takes you to a function that logs you out
@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')
app.run(debug=True)