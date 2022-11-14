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

app = Flask(__name__)
app.secret_key = 'somesecretkey'

headings = ("Course Name", "Teacher", "Time", "Student Enrolled")
data = (("Physics 121", "Susan Walker", "TR 11:00-11:50 AM", "5/10"),
        ("CS 106", "Ammon Hepworth", "MWF 2:00-2:50 PM", "4/10"))

data2 = (("Math 101", "Ralph Jenkins", "MWF 10:00-10:50 AM", "4/8"),
        ("CS 162", "Ammon Hepworth", "TR 3:00-3:500 PM", "4/4"))

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

    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return render_template('profCourses.html', headings=headings, data=data)

#test