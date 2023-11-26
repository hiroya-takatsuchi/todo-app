from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import or_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Post(db.Model):
    __searchable__ = ['title', 'detail']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False, index=True)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False, index=True)
    

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':

        sort = request.args.get('sort')  
        order = request.args.get('order')

        if sort and order:
            posts = Post.query.order_by(f"{sort} {order}").all()
        else:
            posts = Post.query.order_by(Post.due).all()

        return render_template('index.html', posts=posts, today=date.today())

    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    
@app.route('/search')
def search():
    q = request.args.get('q')
    posts = Post.query.filter(
        or_(Post.title.contains(q), Post.detail.contains(q))
    ).order_by(Post.due).all() 
    today = date.today()
    return render_template('index.html', posts=posts, today=today)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/detail/<int:id>')
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = request.form.get('due')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        db.session.commit()
        return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/posts')
def get_posts():
    sort = request.args.get('sort') # ソート対象のカラム名 
    order = request.args.get('order') 