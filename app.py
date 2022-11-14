from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    g,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'somesecretkey'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    user_id = db.Column(db.Integer)

class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    user_id = db.Column(db.Integer)

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(25))
    teacher_id = db.Column(db.Integer)
    number_enrolled = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    time  = db.Column(db.Integer)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    grade = db.Column(db.Integer)

class UsersSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")
        model = Users

class StudentsSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "user_id")
        model = Students

class UsersListResource(Resource):
    def get(self):
        users = Users.query.all()
        return users_schema.dump(users)

class StudentsListResource(Resource):
    def get(self):
        students = Students.query.all()
        return students_schema.dump(students)

db.create_all()
api.add_resource(UsersListResource, '/userslist')

"""
db.session.add_all([
    Users(id=1, username='Anthony', password='pass1'),
    Users(id=2, username='Jesus', password='thing2'),
    Users(id=3, username='Ammon', password='highsecurity')
])"""
#db.session.commit()

#table = pd.read_sql(Users.query.statement, con='sqlite:///test.db')
#print(table)

#users = []
#users.append(User(id=1, username='Anthony', password='pass1', teacher='false'))
#users.append(User(id=2, username='Jesus', password='thing2', teacher='false'))
#users.append(User(id=3, username='Ammon', password='highsecurity', teacher="true"))

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
students_schema = StudentsSchema(many=True)

'''
class User:
    def __init__(self, id, username, password, teacher):
        self.id = id
        self.username = username
        self.password = password
        self.teacher = teacher

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='Anthony', password='pass1', teacher='false'))
users.append(User(id=2, username='Jesus', password='thing2', teacher='false'))
users.append(User(id=3, username='Ammon', password='highsecurity', teacher="true"))
'''

headings = ("Course Name", "Teacher", "Time", "Student Enrolled")
headings2 = ("Student Name", "Grade")
data0 = (("Anthony", "92"), ("Jesus", "76"))
data = (("Physics 121", "Susan Walker", "TR 11:00-11:50 AM", "5/10"),
        ("CS 106", "Ammon Hepworth", "MWF 2:00-2:50 PM", "4/10"))

data2 = (("Math 101", "Ralph Jenkins", "MWF 10:00-10:50 AM", "4/8"),
        ("CS 162", "Ammon Hepworth", "TR 3:00-3:500 PM", "4/4"))

data1 = data + data2

nameClass = []

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']

        table = pd.read_sql(Users.query.filter(Users.username))

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            if user.teacher == 'false':
                return redirect(url_for('studentProfile'))
            elif user.teacher == 'true':
                return redirect(url_for('adminProfile'))
        else:
            flash("There was a problem with the password")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/studentProfile', methods=['GET', 'POST'])
def studentProfile():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    '''
    if request.method == 'GET':
        return redirect(url_for('studentProfileAdd'))
    '''

    return render_template('studentProfile.html', headings=headings, data=data)

@app.route('/studentProfile/add', methods=['GET', 'POST'])
def studentProfileAdd():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return render_template('studentProfileAdd.html', headings=headings, data=data2)


@app.route('/adminProfile', methods=['GET', 'POST'])
def adminProfile():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST' and request.form.get('sign') == 'Signout':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    if request.method == 'GET' and request.args.get('classButt') != None:
        nameClass.append(request.args.get('classButt'))
        for x in data1:
            if nameClass[0] in x[0]:
                nameClass[0] = x[0]
        return redirect(url_for('adminProfileView'))

    return render_template('profCourses.html', headings=headings, data=data)

@app.route('/adminProfile/class', methods=['GET', 'POST'])
def adminProfileView():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST' and request.form.get('sign') == 'Signout':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    if request.method == 'POST' and request.form.get('back') == 'backout':
        nameClass.clear()
        return redirect(url_for('adminProfile'))

    return render_template('profViewCourse.html', className=nameClass[0], headings=headings2, data=data0)