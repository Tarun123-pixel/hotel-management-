import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from forms import SignupForm, LoginForm
from datetime import datetime
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, template_folder='templates', instance_relative_config=True)

# CSRF protection
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to your actual secret key
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.urandom(24)  # You must set a secret key
csrf = CSRFProtect(app)
# Database Setup
instance_path = os.path.join(app.instance_path, 'users.db')

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{instance_path}'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}')"

# Entry Model for other application data
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Entry('{self.title}', '{self.date_created}')"

# Ensure database tables are created
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def Main():
    return render_template('Main.html')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password, form.password.data):
            # On successful login
            flash('Login successful!', 'success')
            return redirect(url_for('Home'))  # Redirect to home or dashboard page
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('Login.html', form=form)

@app.route('/Home')
def Home():
    return render_template('Main.html')

@app.route('/Signup', methods=['GET', 'POST'])
def Signup():
    form = SignupForm()

    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please choose another one.', 'danger')
            return redirect(url_for('Signup'))

        # Hash password before storing
        hashed_password = generate_password_hash(form.password.data)

        # Create and add the new user to the database
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_password,
            phone=form.phone.data,
            dob=form.dob.data,
            address=form.address.data,
            gender=form.gender.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please login!', 'success')
        return redirect(url_for('Login'))

    return render_template('Signup.html', form=form)

@app.route('/Rooms')
def Rooms():
    return render_template('Rooms.html')

@app.route('/Tables')
def Tables():
    return render_template('Tables.html')

@app.route('/Checkin')
def Checkin():
    return render_template('checkin.html')

@app.route('/Checkout')
def Checkout():
    return render_template('checkout.html')

# Route for creating entries in the database
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_entry = Entry(title=title, content=content)

        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for('Main'))
        except Exception as e:
            return f"There was an issue adding your entry: {str(e)}"
    else:
        return render_template('create.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)
