# Hospital Management System 🏥

A modern, responsive, and lightweight web application built with **Flask**, **SQLAlchemy**, and **Bootstrap 5** that allows patients to manage appointments, browse medical departments, view specialist doctors, and book time slots dynamically.

---

## 🚀 Key Features

* **Secure Authentication:** User signup and login utilizing cryptographically hashed passwords (`pbkdf2:sha256` via Werkzeug).
* **Interactive Appointment Booking:** 
  * Select medical departments dynamically.
  * Pick specialists from the selected department.
  * Live time slot checker: Choose a date, and the application dynamically generates 30-minute slots between **9:00 AM and 5:00 PM**, hiding any already-booked slots for that doctor on that date.
* **Patient Dashboard:** View personal profile details (age, gender, blood group) and track all booked appointments in descending chronological order.
* **Reschedule & Cancel:** Modify booking details (date, time, appointment type, notes) or cancel bookings directly from the dashboard.
* **Auto-Seeded Mock Data:** On initial startup, the system automatically builds the database and seeds it with mock departments (Cardiology, Neurology, Pediatrics, Orthopedics, Dermatology) and doctor profiles.

---

## 🛠️ Technology Stack

* **Backend:** [Python](https://www.python.org/) & [Flask](https://flask.palletsprojects.com/)
* **Database & ORM:** [SQLite](https://sqlite.org/) managed via [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
* **Security:** [Werkzeug](https://werkzeug.palletsprojects.com/) (Security Helpers)
* **Frontend:** [Bootstrap 5](https://getbootstrap.com/), [Bootstrap Icons](https://icons.getbootstrap.com/), & Vanilla JavaScript
* **Templating Engine:** [Jinja2](https://jinja.palletsprojects.com/)

---

## 📁 Project Structure

```text
hospital_management/
│
├── instance/               # Local SQLite database (hospital.db) generated on runtime
├── templates/              # HTML layout and pages
│   ├── base.html           # Main template containing layout, header, footer, & styles
│   ├── index.html          # Landing page with departments overview
│   ├── auth.html           # User login and registration panel
│   ├── dashboard.html      # Patient profile and appointment list
│   ├── book_appointment.html # Dynamic appointment scheduler
│   └── update_appointment.html # Rescheduling panel
│
├── .gitignore              # Files ignored by Git (caches, local database, IDE folders)
├── README.md               # Documentation
└── happ.py                 # Core application logic, routing, & database schema
```

---

## ⚙️ Installation & Local Setup

Follow these steps to run the application locally:

### 1. Prerequisites
Ensure you have **Python 3.x** installed. You can check your version using:
```bash
python --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/avanti0111/hospital_management_system.git
cd hospital_management_system
```

### 3. Install Dependencies
Install the required packages using `pip`:
```bash
pip install Flask Flask-SQLAlchemy
```

### 4. Run the Application
Start the Flask development server:
```bash
python happ.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

---

## 🗄️ Database Schema & Models

The database contains four tables:
1. **User:** Stores patient profiles (`id`, `username`, `password`, `full_name`, `age`, `gender`, `blood_group`).
2. **Department:** Categorizes healthcare practices (`id`, `name`, `description`).
3. **Doctor:** Profiles of specialists (`id`, `name`, `specialization`, `experience`, `rating`, `department_id`).
4. **Appointment:** Tracks schedules (`id`, `user_id`, `doctor_id`, `appointment_date`, `appointment_time`, `appointment_type`, `status`, `notes`).