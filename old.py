from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for
import json

#Connection to database
client = MongoClient('mongodb://localhost:27017')
db = client['DSPharmacy']
users = db['users']
products = db['products']

# Flask create
app = Flask(__name__)
app.secret_key =('secret')

#User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == "GET":	
		return render_template("register.html", error=("error" in request.args))
		
	elif request.method == 'POST':		
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		check = users.find_one({"email": email})	
		#check if user already exists
		if not check:
			users.insert_one({
			"name": username,
			"email": email,
			"password": password,
			"category": "user"})		
			return redirect(url_for('login'))		
		else:
			return redirect(url_for('register', error=1))		

#User login (the default page)
@app.route("/", methods=["GET", "POST"])
def login():
	if request.method == "GET":	
		return render_template("login.html", error=("error" in request.args))
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		check = users.find_one({'email': email})	
	#check if user exists
	if not check:
		return	redirect(url_for('login', error=1))
	else:
		#check if user password is correct
		if password == check['password']:
			session['email'] = email
			session['loggedin'] = True		
			return redirect(url_for('index'))
		else:
			return redirect(url_for('login', error=1))
	return print('error')
#Logout user 
@app.route('/logout')
def logout():
	session.pop('email', None)
	session.pop('loggedin', None)
	return redirect(url_for('login'))
	
#Main page after login
@app.route("/index", methods=["GET"])
def index():
	#Checks if a user is logged in
	if session['loggedin'] == True:
		user = users.find({})
		return render_template("index.html", mail=session['email'], mov=products)
	else:
		return redirect(url_for('login'))
#Ticket buy function
@app.route("/buy", methods=["GET", "POST"])
def buy():
	if session['loggedin'] == True:
		products = products.find({})
		return render_template("buy.html", mail=session['email'], mov=products)

#products Search function
# @app.route('/search', methods=["GET" , "POST"] )
# def search():
# 	if session['loggedin'] == True:
# 		if request.method== "GET" :			
# 				return render_template("search.html", mail=session['email'])		
# 		else:
# 			msearch = request.form['search']	
# 			movresult = products.find({"title": msearch})
# 			return render_template("search.html", mail=session['email'], mov=movresult )

if __name__ == "__main__":
	if not 'users' in db.list_collection_names():
		with open('users.json') as f:
			user = json.load(f)	
			users.insert_many(user)

	
	app.run(host='localhost', port=5000, debug=True)