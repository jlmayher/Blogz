from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


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
            return redirect('/blog')

        else:
            return render_template('post.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)

    else:
        return render_template('post.html')

if __name__ == "__main__":
    app.run()
