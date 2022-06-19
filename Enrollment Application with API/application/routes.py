from operator import methodcaller
from sys import api_version
from application import app, db
from flask import Response, render_template, request, json, jsonify, redirect, flash, url_for, session
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
import requests
from application.courseList import courseList



courseData = [
    {"courseID":"1111","title":"HTML/CSS","description":"Introduction to HTML and CSS","credits":3,"term":"III"}, 
    {"courseID":"2222","title":"Java Script","description":"Introduction to Java Script","credits":4,"term":"II"}, 
    {"courseID":"3333","title":"React JS","description":"JavaScript Library","credits":3,"term":"IV"}, 
    {"courseID":"4444","title":"Python","description":"Introduction to Python Programming","credits":3,"term":"V"}, 
    {"courseID":"5555","title":"Python with Flask","description":"Python with Flask","credits":4,"term":"VI"}
]

############### API starts ###############

@app.route('/fetch', methods = ['GET', 'POST'])
def fetch():
   return jsonify(User.objects.all())

@app.route('/fetch/<idx>', methods = ['GET'])
def fetchID(idx):
   return jsonify(User.objects(user_id=idx))

@app.route('/addUser', methods=['POST'])
def addUser():
    user_id     = User.objects.count()  #For auto increment
    user_id     += 1
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    user = User(user_id=user_id,first_name=first_name, last_name=last_name, email=email, password=password)
    user.save()
    return jsonify(message="User created"), 201  #New record created

@app.route('/addUserJSON', methods=['POST'])
def addUserJSON():
    payload =request.get_json(force=True)
    user = User(user_id=payload['user_id'],first_name=payload['first_name'], last_name=payload['last_name'], email=payload['email'], password=payload['password'])
    user.save()
    return jsonify(message="User created"), 201  #New record created

@app.route('/put/<idx>',methods=['PUT'])
def put(idx):
    payload = request.get_json(force=True) #JSON given in Postman
    User.objects(user_id=idx).update(**payload)
    # return jsonify(message="User Updated"), 202  #Record updated
    return jsonify(User.objects(user_id=idx)), 202 

@app.route('/delete/<idx>',methods=['DELETE'])
def delete(idx):
    user = User.objects(user_id=idx).first()
    if user:
        User.objects(user_id=idx).delete()
        return jsonify(message=f"{user.first_name} is deleted"), 202
    else:
        return jsonify(message="User doesn't exists"), 404

############### API ends ###############

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", login=False, index=True)


@app.route("/courses")
@app.route("/courses/<string:term>")
def courses(term=None):  
    if term is None:
        term = "2022"  
    # classes = Course.objects.all()  #Course model object
    classes = Course.objects.order_by("courseID")  #Course model object; asc order sort
    # classes = Course.objects.orderby("-courseID")  #Course model object; desc order sort
    return render_template("courses.html", courseData=classes, courses=True, term=term)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id     = User.objects.count()  #For auto increment
        user_id     += 1
        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data
        
        user = User(user_id=user_id, email=email, password=password, first_name=first_name, last_name=last_name)
        # user.set_password(password)  #For hashing the password
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", form=form, title="Register", register=True)


@app.route("/login", methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email       = form.email.data
        password    = form.password.data

        user = User.objects(email=email).first()    #Fetch from db
        if user and password == user.password:
            flash(f"{user.first_name}, you are successfully logged in!", "success")
            #Create session variables
            session['user_id'] = user.user_id       #retrieved from db
            session['username'] = user.first_name

            return redirect("/index")
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template("login.html", title="Login", form=form, login=True )

@app.route("/enrollment",methods=["GET", "POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))

    # WITH POST : id = request.form['courseID']

    # WITH GET
    courseID    = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id     = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id,courseID=courseID):
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id,courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")

    classes = courseList(user_id)

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)    

@app.route('/logout')
def logout():
    session['user_id'] = False
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/api')
@app.route('/api/<idx>')  #Like github users api
def fetchAPI(idx=None):
    if (idx == None):
        jsonData = courseData
    else:
        jsonData = courseData[int(idx)]
    
    return Response(json.dumps(jsonData), mimetype='application/json')

 
@app.route('/user')
def user():
    # User(userID=1, first_name='Jyoti', last_name='Malhotra', email='jyoti@test.com', password='test').save()  #Save to DB
  
    # User(userID=2, first_name='Aashni', last_name='Jyoti', email='aashu@test.com', password='test').save()

    users = User.objects.all()
    return render_template('users.html', users=users)