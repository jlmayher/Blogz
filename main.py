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
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        validate = request.form['validate']

        
        existing_user = User.query.filter_by(username=username).first()
        if username == "" or password == "" or validate == "":
            flash("One or more fields are invalid.")
            return redirect('/signup')
        if existing_user:
            flash('This username is already in use.')
            return redirect('/signup')
        if password != validate:
            flash('Passwords must match')
            return redirect('/signup')
        if len(username) < 3:
            flash('Invalid username. Username must be at least 3 characters long.')
            return redirect('/signup')
        if len(password) < 3:
            flash('Invalid password. Password must be at least 3 characters long.')
            return redirect('/signup')
        
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = username
        return redirect('/newpost')
    
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
            return redirect('/newpost')
        if user and user.password != password:
            flash('Password is incorrect.')
            return redirect('/login')
        if not user:
            flash('This user does not exist.')
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog')
def blog():
    id = request.args.get('id')
    user = request.args.get('user')
    
    if id:
        display = Blog.query.get(id)
               
        return render_template('display.html', blog=display)
    if user:
        user_obj = User.query.filter_by(id=user).first()
        blogs = Blog.query.filter_by(owner_id=user).all()
        #display = Blog.query.filter_by(owner=user).all() 
        return render_template('userentries.html', user=user_obj, blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blogs.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['user']).first()
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-text']

        
        if blog_title == "":
            flash("Your new entry needs a title.")
            return redirect('/newpost')
    
        if blog_body == "":
            flash("Your new entry needs some content.")
            return redirect('newpost')

 
        
        blog = Blog(blog_title, blog_body, owner)
        db.session.add(blog)
        db.session.commit()
            
        id = blog.id
        id_str = str(id)
        return redirect('/blog?id=' + id_str)

    else:
        return render_template('post.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
