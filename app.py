import os
from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for
import json

#Connection to database
client = MongoClient(os.getenv("MONGO_HOST", "0.0.0.0"), 27017)
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
		ssn = request.form['ssn']
#ssn validation
		if int(ssn[:2]) <= 31:
			if int(ssn[2:4]) <=12:
				check = users.find_one({"email": email})
				if not check :
					users.insert_one({
					"name": username,
					"email": email,
					"password": password,
					"ssn": int(ssn),
					"category": "user",
					"orderHistory": []})		
				return redirect(url_for('login'))		
			else:
				return redirect(url_for('register', error=1))
		else:
				return redirect(url_for('register', error=1))	

@app.route("/index", methods=["GET", "POST"])
def index():
	#Checks if a user is logged in
	if session['loggedin'] == True:
		user = users.find({})
		return render_template("index.html", mail=session['email'], prod=products.find({}))
	else:
		return redirect(url_for('login'))	
			

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
				session['category']	= check['category']
				session['cart'] = []
				if session['category'] == 'admin':
					return render_template('admin.html')
				return redirect(url_for('index'))
			else:
				return redirect(url_for('login', error=1))

#Logout user 
@app.route('/logout')
def logout():
	session.pop('email', None)
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('cart', None)
	return redirect(url_for('login'))

#Admin panel
@app.route("/admin")
def admin():
	if session['category'] == 'admin':
		return render_template('admin.html') 
	else:
		return redirect('/index')

#For admin to add new entries to the database
@app.route("/admin/addprod", methods=["GET", "POST"])
def addprod():
	if session['category'] == 'admin':
		if request.method == "GET":
			return render_template('addprod.html')
		elif request.method == "POST":
			name = request.form['name']
			category = request.form['category']
			stock = int(request.form['stock'])
			description = request.form['description']
			price = int(request.form['price'])
			check = products.find_one({"name": name})
			if not check:
				products.insert_one({
				"name": name,
				"description": description,
				"price": price,
				"category": category,
				"stock": stock
				})
			return redirect('/admin/addprod')
		return render_template('addprod.html')
	else: return redirect('/logout')
#For admin to delete items from the database
@app.route("/admin/delprod", methods=("GET", "POST"))
def delprod():
	if session['category'] == 'admin':
		if request.method == "GET":
			return render_template('delprod.html', prod=products.find({}) )
		elif request.method == 'POST':
			id = request.form['id']
			check = products.find_one({"_id": ObjectId(id)})
			if not check :
				return redirect("/admin/delprod")
			else:
				products.delete_one( {"_id": ObjectId(id)})
				return redirect("/admin/delprod")

		return render_template('delprod.html', prod=products.find({}))
	else: return redirect('/logout')

#For Admin to update a selected product's info
@app.route("/admin/updateprod", methods=("GET", "POST"))
def updateprod():
	if session['category'] == 'admin':
		if request.method == "GET":
			return render_template('updateprod.html', prod=products.find({}))
		elif request.method == "POST":
			session["id"] = request.form['id']
			check = products.find_one({"_id": ObjectId(session["id"])})
			if not check :
				return render_template('updateprod.html', error=1, prod=products.find({}))
			else:
				return redirect('/admin/updateprodfield')
	else: return redirect('/logout')

#For Admin to update a selected product's info
@app.route("/admin/updateprodfield", methods=("GET", "POST"))
def updateprodfield():
	if session['category'] == 'admin':
		if request.method == "GET":
			name = products.find_one({"_id": ObjectId(session["id"])})["name"]
			category = products.find_one({"_id": ObjectId(session["id"])})["category"]
			stock = products.find_one({"_id": ObjectId(session["id"])})["stock"]
			description = products.find_one({"_id": ObjectId(session["id"])})["description"]
			price = products.find_one({"_id": ObjectId(session["id"])})["price"]
			return render_template("updateprodfield.html", name=name, category=category, stock=stock, description=description, price=price)
		if request.method == "POST":
			products.update_one({"_id": ObjectId(session["id"])}, {"$set": {"name": request.form["name"], "category": request.form["category"], "stock": int(request.form["stock"]), "description": request.form["description"], "price": int(request.form["price"])}})
		return redirect("/admin/updateprod")
	else: return redirect("/logout")


#products Search function
@app.route('/search', methods=["GET" , "POST"] )
def search():
	if session['loggedin'] == True:
		if request.method== "GET" :			
			return render_template("search.html", mail=session['email'])		
		else:
			prodsearch = request.form['search']	
			prodresult = products.find({"name": prodsearch})
			return render_template("search.html", mail=session['email'], prod=prodresult )
	else: return redirect('/logout')		

#Current Session user's shopping cart
@app.route("/cart", methods=["GET", "POST"])
def cart():
	if session['loggedin'] == True:
		if request.method=="GET":
			cart= []
			for i in session['cart']:	
				addto=[]
				name = products.find_one({"_id": ObjectId(i)})["name"]
				category = products.find_one({"_id": ObjectId(i)})["category"]
				description = products.find_one({"_id": ObjectId(i)})["description"]
				price = products.find_one({"_id": ObjectId(i)})["price"]
				addto.append(name)
				addto.append(category)
				addto.append(i)
				addto.append(description)
				addto.append(price)				
				cart.append(addto)				

			return render_template("cart.html", mail=session['email'], cart=cart)
		elif request.method=="POST":
			session["id"] = request.form['forcart']
			session['cart'].append(request.form['forcart'])
			session.modified=True
			return redirect("/cart")
	else: return redirect('/logout')
#Delete an item from the cart
@app.route("/delcart", methods=["GET", "POST"])
def delcart():
	if session['loggedin'] == True:
		if request.method == "POST":
			session["cart"].remove(request.form['delcart'])
			session.modified=True
			return redirect('/cart')
	else: return redirect('/logout')		


#Cart buy function
@app.route("/buy", methods=["GET", "POST"])
def buy():
	if session['loggedin'] == True:
			cart= []
			totalprice = 0
			for i in session['cart']:
				cartitems = products.find_one({'_id': ObjectId(i)})
				totalprice += (cartitems['price'])
				cart.append(cartitems)
				products.update_one({'_id': ObjectId(i)}, {"$inc": {"stock": -1}})
			return render_template("buy.html", mail=session['email'], cart=cart, totalprice=totalprice)
	else: return redirect('/logout')

@app.route("/userhistory", methods=["GET", "POST"])
def userhistory():
	if session['loggedin'] == True:
		if request.method == "POST":
			cart = []
			totalprice = 0
			for i in session['cart']:
				cartitems = products.find_one({'_id': ObjectId(i)})
				totalprice += (cartitems['price'])
				cart.append(cartitems)
			users.update_one({"email": session["email"]}, {"$push": {"orderHistory": cart}})
			products.delete_one({"stock": {"$lt": 1}})
			session['cart'] = []
			session.modified = True
		return redirect('/orderHistory')
	else: return redirect('/logout')


@app.route("/orderHistory", methods=["GET", "POST"])
def orderHistory():
	if session['loggedin'] == True:
		history = users.find_one({'email': session['email']})['orderHistory']
		return render_template('orderHistory.html', history=history)
	else: return redirect('/logout')

#Deletes the user from the database then redirects to logout
@app.route("/deluser")
def deluser():
	if session['loggedin'] == True:
		if session['category'] == 'user':
			users.delete_one({ 'email': session['email'] })
		return redirect("/logout")
	else: return redirect('/logout')



if __name__ == "__main__":
	if not 'users' in db.list_collection_names():
		with open('users.json') as f:
			user = json.load(f)	
			users.insert_many(user)
	if not 'products' in db.list_collection_names():
		with open('products.json') as p:
			product = json.load(p)
			products.insert_many(product)

	
	app.run(host='0.0.0.0', port=5000, debug=True)