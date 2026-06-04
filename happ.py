from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'hospital_management_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    appointments = db.relationship('Appointment', backref='user', lazy=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    rating = db.Column(db.Float, default=4.5)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Booked')
    notes = db.Column(db.Text)

# Function to initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create sample data if tables are empty
        if Department.query.count() == 0:
            # Add departments
            cardiology = Department(name='Cardiology', description='Heart and blood vessel specialists')
            neurology = Department(name='Neurology', description='Brain and nervous system specialists')
            pediatrics = Department(name='Pediatrics', description='Children healthcare specialists')
            orthopedics = Department(name='Orthopedics', description='Bone and joint specialists')
            dermatology = Department(name='Dermatology', description='Skin and hair specialists')
            
            db.session.add_all([cardiology, neurology, pediatrics, orthopedics, dermatology])
            db.session.commit()
            
            # Add doctors
            doctor1 = Doctor(name='Dr. James Smith', specialization='Interventional Cardiologist', experience=15, rating=4.8, department_id=cardiology.id)
            doctor2 = Doctor(name='Dr. Sarah Johnson', specialization='Neurosurgeon', experience=12, rating=4.7, department_id=neurology.id)
            doctor3 = Doctor(name='Dr. Michael Williams', specialization='Pediatrician', experience=10, rating=4.9, department_id=pediatrics.id)
            doctor4 = Doctor(name='Dr. Robert Brown', specialization='Orthopedic Surgeon', experience=18, rating=4.6, department_id=orthopedics.id)
            doctor5 = Doctor(name='Dr. Emily Davis', specialization='Dermatologist', experience=8, rating=4.5, department_id=dermatology.id)
            
            db.session.add_all([doctor1, doctor2, doctor3, doctor4, doctor5])
            db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        # Determine if it's a login or registration
        form_type = request.form.get('form_type')
        
        if form_type == 'login':
            username = request.form['login_username']
            password = request.form['login_password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
        
        elif form_type == 'register':
            username = request.form['register_username']
            password = request.form['register_password']
            full_name = request.form['register_full_name']
            age = request.form['register_age']
            gender = request.form['register_gender']
            blood_group = request.form['register_blood_group']
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists!', 'danger')
                return redirect(url_for('auth'))
            
            # Create new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                username=username,
                password=hashed_password,
                full_name=full_name,
                age=age,
                gender=gender,
                blood_group=blood_group
            )
            
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
    
    return render_template('auth.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    appointments = Appointment.query.filter_by(user_id=user.id).order_by(Appointment.appointment_date.desc()).all()
    return render_template('dashboard.html', user=user, appointments=appointments)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(request.form['appointment_time'], '%H:%M').time()
        appointment_type = request.form['appointment_type']
        notes = request.form.get('notes', '')
        
        # Check if slot is available
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).first()
        
        if existing_appointment:
            flash('This time slot is already booked!', 'danger')
            return redirect(url_for('book_appointment'))
        
        # Create new appointment
        new_appointment = Appointment(
            user_id=session['user_id'],
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_type=appointment_type,
            notes=notes
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    departments = Department.query.all()
    return render_template('book_appointment.html', departments=departments)

@app.route('/get_doctors/<int:department_id>')
def get_doctors(department_id):
    doctors = Doctor.query.filter_by(department_id=department_id).all()
    doctor_list = []
    for doctor in doctors:
        doctor_list.append({
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization,
            'experience': doctor.experience,
            'rating': doctor.rating
        })
    return jsonify(doctor_list)

@app.route('/get_time_slots/<int:doctor_id>/<string:date_str>')
def get_time_slots(doctor_id, date_str):
    appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Get existing appointments for the doctor on that date
    existing_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date
    ).all()
    
    # Generate time slots (9 AM to 5 PM with 30-minute intervals)
    start_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')
    time_slots = []
    
    current_time = start_time
    while current_time <= end_time:
        time_str = current_time.strftime('%H:%M')
        
        # Check if slot is available
        is_available = True
        for apt in existing_appointments:
            if apt.appointment_time.strftime('%H:%M') == time_str:
                is_available = False
                break
        
        if is_available:
            time_slots.append(time_str)
        
        current_time += timedelta(minutes=30)
    
    return jsonify(time_slots)

@app.route('/update_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def update_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    appointment = Appointment.query.get(appointment_id)
    
    if appointment.user_id != session['user_id']:
        flash('You are not authorized to update this appointment!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(request.form['appointment_time'], '%H:%M').time()
        appointment_type = request.form['appointment_type']
        notes = request.form.get('notes', '')
        
        # Check if slot is available (excluding current appointment)
        existing_appointment = Appointment.query.filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.id != appointment_id
        ).first()
        
        if existing_appointment:
            flash('This time slot is already booked!', 'danger')
            return redirect(url_for('update_appointment', appointment_id=appointment_id))
        
        # Update appointment
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.appointment_type = appointment_type
        appointment.notes = notes
        
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('update_appointment.html', appointment=appointment)

@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    appointment = Appointment.query.get(appointment_id)
    
    if appointment.user_id != session['user_id']:
        flash('You are not authorized to cancel this appointment!', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True, port=8080)
