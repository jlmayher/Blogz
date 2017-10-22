from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'randomkey'
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request  
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        validate = request.form['validate']

        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('This username is already in use.')
            return redirect('/register')
        if password != validate:
            flash('Passwords must match')
        if len(username) < 3 or len(password) < 3:
            flash('Username and password must be at least 3 characters long.')
            return redirect('/register')
        
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = username
        return redirect('/blog')
    
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])  
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            flash("Logged In")
            return redirect('/blog')
        if user and user.password != password:
            flash('Password is incorrect.')
            return redirect('/login')
        if not user:
            flash('This user does not exist.')
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/blog')
def index():
    id = request.args.get('id')
    if id:
        display = Blog.query.get(id)
        return render_template('display.html', blog=display)
    else:
        blogs = Blog.query.all()
        return render_template('index.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-text']

        title_error = ""
        body_error = ""

        if blog_title == "":
            title_error = "Your new entry needs a title."
            blog_title = ""
    
        if blog_body == "":
            body_error = "Your entry is blank. What did you want to say?"
            blog_body = ""

 
        if not title_error and not body_error:
            blog = Blog(blog_title, blog_body)
            db.session.add(blog)
            db.session.commit()
            
            id = blog.id
            id_str = str(id)
            return redirect('/blog?id=' + id_str)

        else:
            return render_template('post.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)

    else:
        return render_template('post.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
