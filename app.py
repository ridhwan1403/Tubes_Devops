from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/tubes_devsecop_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# Create database if not exists
def create_database():
    engine = create_engine('mysql+pymysql://root:@localhost')
    conn = engine.connect()
    conn.execute(text("CREATE DATABASE IF NOT EXISTS tubes_devsecop_app"))
    conn.close()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

# Middleware to validate API Key
@app.before_request
def require_api_key():
    if request.path.startswith('/api/'):
        api_key = request.headers.get('X-API-KEY')
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        login_type = request.args.get('type', 'user')
        return render_template('login.html', type=login_type)

    username = request.form['username']
    password = request.form['password']
    login_type = request.args.get('type', 'user')

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Account not found!", "error")
        return redirect(url_for('login', type=login_type))

    if not check_password_hash(user.password, password):
        flash("Invalid credentials!", "error")
        return redirect(url_for('login', type=login_type))

    if user.is_admin and login_type == 'user':
        flash("Admins cannot log in as users!", "error")
        return redirect(url_for('login', type='user'))

    if not user.is_admin and login_type == 'admin':
        flash("Users cannot log in as admins!", "error")
        return redirect(url_for('login', type='admin'))

    session['user_id'] = user.id
    session['is_admin'] = user.is_admin

    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = generate_password_hash(request.form['password'])

    if User.query.filter_by(username=username).first():
        flash("Username already exists!", "error")
        return redirect(url_for('register'))

    new_user = User(username=username, password=password, is_admin=False)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('home'))

    user_id = session['user_id']
    if request.method == 'POST':
        content = request.form['content']
        new_item = TodoItem(content=content, user_id=user_id)
        db.session.add(new_item)
        db.session.commit()

    todos = TodoItem.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', todos=todos)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_user':
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            is_admin = request.form.get('is_admin') == 'on'

            new_user = User(username=username, password=password, is_admin=is_admin)
            db.session.add(new_user)
            db.session.commit()

    users = User.query.all()
    todos = TodoItem.query.all()
    return render_template('admin_dashboard.html', users=users, todos=todos)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_todo/<int:todo_id>')
def delete_todo_admin(todo_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))

    todo = TodoItem.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

# API Routes
@app.route('/api/todos', methods=['GET', 'POST'])
def api_todos():
    if request.method == 'GET':
        todos = TodoItem.query.all()
        result = [{"id": todo.id, "content": todo.content, "user_id": todo.user_id} for todo in todos]
        return jsonify(result)

    if request.method == 'POST':
        data = request.json
        new_todo = TodoItem(content=data['content'], user_id=data['user_id'])
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({"message": "Todo created successfully!"}), 201

@app.route('/api/users', methods=['GET'])
def api_users():
    users = User.query.all()
    result = [{"id": user.id, "username": user.username, "is_admin": user.is_admin} for user in users]
    return jsonify(result)

if __name__ == '__main__':
    create_database()
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password=generate_password_hash('admin'), is_admin=True)
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True)
