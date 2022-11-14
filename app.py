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
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'somesecretkey'    
app.app_context().push

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

headings = ("Course Name", "Teacher", "Time", "Student Enrolled")
data = (("Physics 121", "Susan Walker", "TR 11:00-11:50 AM", "5/10"),
        ("CS 106", "Ammon Hepworth", "MWF 2:00-2:50 PM", "4/10"))

data2 = (("Math 101", "Ralph Jenkins", "MWF 10:00-10:50 AM", "4/8"),
        ("CS 162", "Ammon Hepworth", "TR 3:00-3:500 PM", "4/4"))

"""
class User:
    def __init__(self, id, username, password, teacher):
        self.id = id
        self.username = username
        self.password = password
        self.teacher = teacher

    def __repr__(self):
        return f'<User: {self.username}>'
"""

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable = False, unique=True)
    password = db.Column(db.String(80), nullable = False)

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

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

with app.app_context():
    db.create_all()
    db.session.add_all([
        Users(id=1, username='Anthony', password='pass1'),
        Users(id=2, username='Jesus', password='thing2'),
        Users(id=3, username='Ammon', password='highsecurity')
        ])
    #db.session.commit()
api.add_resource(UsersListResource, '/userslist')

"""
"""

#table = pd.read_sql(Users.query.statement, con='sqlite:///database.db')
#print(table)

#users = []
#users.append(User(id=1, username='Anthony', password='pass1', teacher='false'))
#users.append(User(id=2, username='Jesus', password='thing2', teacher='false'))
#users.append(User(id=3, username='Ammon', password='highsecurity', teacher="true"))

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
students_schema = StudentsSchema(many=True)


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            print("You are a user")
            login_user(user)
            return redirect(url_for('studentProfile'))

    """
    if request.method == 'POST' :
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']

        table = pd.read_sql(Users.query.filter(Users.username))

        user = [x for x in table if x.username == username][0]
        print(user)
        if user and user.password == password:
            session['user_id'] = user.id
            if user.teacher == 'false':
                return redirect(url_for('studentProfile'))
            elif user.teacher == 'true':
                return redirect(url_for('adminProfile'))
        else:
            flash("There was a problem with the password")
            return render_template('login.html')"""
    
    return render_template('login.html', form=form)  

@app.route('/studentProfile', methods=['GET', 'POST'])
#@login_required
def studentProfile():
    """
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    '''
    if request.method == 'GET':
        return redirect(url_for('studentProfileAdd'))
    '''"""

    return render_template('studentProfile.html', headings=headings, data=data)

@app.route('/profCourses', methods=['GET', 'PUT', 'PATCH'])


@app.route('/adminProfile', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def adminProfile():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return render_template('profCourses.html', headings=headings, data=data)



@app.route('/studentProfile/add', methods=['GET', 'POST'])
def studentProfileAdd():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return render_template('studentProfileAdd.html', headings=headings, data=data2)

if __name__=='__main__':
    app.run(debug=True)
