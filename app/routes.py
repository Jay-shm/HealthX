from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from . import db, bcrypt, Patient, Doctor, Report
from datetime import datetime, timedelta
bp = Blueprint('routes', __name__)

@bp.route('/')
def login_page():
    return render_template('log-in.html')

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    if not username or not password or not user_type:
        return jsonify({'error': 'Incomplete data provided'}), 400

    # Check user type and query the corresponding table
    if user_type == 'user':
        user = Patient.query.filter_by(username=username).first()
    elif user_type == 'doctor':
        user = Doctor.query.filter_by(username=username).first()
    else:
        return jsonify({'error': 'Invalid user type'}), 400

    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, password):
        # User authenticated successfully
        session['user_id'] = user.id  # Store the user ID in the session
        session['user_type'] = user_type  # Store the user type in the session
        session['username'] = user.username  # Store the username in the session
        if user_type == 'user':
            return jsonify({'redirect_url': url_for('routes.patient_dashboard')})
        elif user_type == 'doctor':
            return jsonify({'redirect_url': url_for('routes.doctor_dashboard')})

    return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Incomplete data provided'}), 400
    
    existing_user = Patient.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = Patient(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/signup', methods=['GET'])
def signup_form():
    return render_template('sign-up.html')

@bp.route('/signup-doctor', methods=['POST'])
def signup_doctor():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    admin_password = data.get('admin_password')

    # Hardcoded admin password for demonstration purposes
    if admin_password != 'admin':
        return jsonify({'error': 'Admin password is incorrect'}), 401

    if not username or not email or not password:
        return jsonify({'error': 'Incomplete data provided'}), 400
    
    existing_user = Doctor.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = Doctor(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Doctor account created successfully'}), 201

@bp.route('/signup-doctor', methods=['GET'])
def signup_doctor_form():
    return render_template('sign-up_DAC.html')

@bp.route('/patient-dashboard')
def patient_dashboard():
    if 'user_id' in session and 'user_type' in session and session['user_type'] == 'user':
        return render_template('user-home.html', username=session.get('username'))
    else:
        return redirect(url_for('routes.login_page'))

@bp.route('/doctor-dashboard')
def doctor_dashboard():
    if 'user_id' in session and 'user_type' in session and session['user_type'] == 'doctor':
        return render_template('doctor-home.html', username=session.get('username'))
    else:
        return redirect(url_for('routes.login_page'))

# Define the route to get report dates for the current user
@bp.route('/get_report_dates')
def get_report_dates():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Get the current user's ID from the session
    user_id = session['user_id']
    
    # Query the database to get the report dates for the current user
    reports = Report.query.filter_by(patient_id=user_id).order_by(Report.date_uploaded.desc()).limit(8).all()
    
    # Extract the doctor names and dates from the reports
    report_dates = []
    for report in reports:
        doctor = Doctor.query.get(report.doctor_id)
        if doctor:
            report_dates.append(f'Visited Dr {doctor.username} on {report.date_uploaded.strftime("%Y-%m-%d")}')
    
    # Return the report dates as JSON
    return jsonify({'report_dates': report_dates})

# Function to get the last appointment date for the current user
def get_last_appointment_date(user_id):
    # Query the database to get the last report date for the current user
    last_report = Report.query.filter_by(patient_id=user_id).order_by(Report.date_uploaded.desc()).first()
    
    if last_report:
        return last_report.date_uploaded
    else:
        return None

# Function to calculate the appointment message
def get_appointment_message(appointment_date):
    if appointment_date:
        # Calculate the difference in days between today and the appointment date
        days_difference = (datetime.now() - appointment_date).days

        # Format the message
        if days_difference == 0:
            return "Today"
        elif days_difference == 1:
            return "Yesterday"
        else:
            return f"{days_difference} days ago"
    else:
        return "No appointments available"

@bp.route('/get_appoint')
def get_appointment():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Get the current user's ID from the session
    user_id = session['user_id']
    
    # Get the last appointment date for the current user
    appointment_date = get_last_appointment_date(user_id)
    
    # Calculate the appointment message
    message = get_appointment_message(appointment_date)
    
    # Return the message in JSON format
    return jsonify({"appointment": message})

@bp.route('/accreport')
def access_user():
    if 'user_id' in session and 'user_type' in session and session['user_type'] == 'doctor':
        return render_template('doctor-access.html', username=session.get('username'))
    else:
        return redirect(url_for('routes.login_page'))


@bp.route('/upload_data', methods=['POST'])
def upload_data():
    data = request.json

    # Check if data is provided
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract data from JSON
    symptoms = data.get('symptoms')
    prescription = data.get('prescription')
    user_id = data.get('user_id')

    # Check if required fields are provided
    if not symptoms or not prescription or not user_id:
        return jsonify({'error': 'Incomplete data provided'}), 400

    # Get the current date and time
    date_uploaded = datetime.utcnow()

    # Get doctor ID from session
    doctor_id = session.get('user_id')

    try:
        # Create a new Report object
        new_report = Report(symptoms=symptoms, prescription=prescription, date_uploaded=date_uploaded,
                            patient_id=user_id, doctor_id=doctor_id)

        # Add the new report to the database session
        db.session.add(new_report)

        # Commit the changes to the database
        db.session.commit()

        # Return success message
        return jsonify({'message': 'Report uploaded successfully'}), 200
    except Exception as e:
        # If an error occurs, rollback the changes and return an error message
        db.session.rollback()
        return jsonify({'error': f'Failed to upload report: {str(e)}'}), 500
    

@bp.route('/get_username', methods=['GET'])
def get_username():
    # Check if the user is logged in
    if 'user_type' in session and session['user_type'] == 'doctor':
        # Retrieve the username from the session
        username = session.get('username')
        return jsonify({'username': username})
    else:
        return jsonify({'error': 'User not logged in'}), 401
    

@bp.route('/get_reports', methods=['GET'])
def get_reports():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    # Query the database to retrieve reports for the specified user
    reports = Report.query.filter_by(patient_id=user_id).all()
    
    # Serialize the report data
    serialized_reports = [{'id': report.id, 'symptoms': report.symptoms, 'prescription': report.prescription, 'date_uploaded': report.date_uploaded} for report in reports]
    
    return jsonify({'reports': serialized_reports})

@bp.route('/get_report', methods=['GET'])
def get_report():
    report_id = request.args.get('report_id')
    if not report_id:
        return jsonify({'error': 'Report ID not provided'}), 400
    
    # Query the database to retrieve the report with the specified ID
    report = Report.query.get(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    # Serialize the report data
    serialized_report = {'id': report.id, 'symptoms': report.symptoms, 'prescription': report.prescription, 'date_uploaded': report.date_uploaded}
    
    return jsonify({'report': serialized_report})


@bp.route('/accrep')
def accreport():
    if 'user_id' in session and 'user_type' in session and session['user_type'] == 'doctor':
        return render_template('doctor-disp.html', username=session.get('username'))
    else:
        return redirect(url_for('routes.login_page'))


@bp.route('/disp_visits')
def disprep():
    if 'user_id' in session and 'user_type' in session and session['user_type'] == 'user':
        return render_template('user-visit.html', username=session.get('username'))
    else:
        return redirect(url_for('routes.login_page'))


@bp.route('/get_all_reports', methods=['GET'])
def get_all_reports():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Get the current user's ID from the session
    user_id = session['user_id']
    
    # Query the database to retrieve all reports for the current user
    user_reports = Report.query.filter_by(patient_id=user_id).all()
    
    # Serialize the report data
    serialized_reports = [{'id': report.id, 'symptoms': report.symptoms, 'prescription': report.prescription, 'date_uploaded': report.date_uploaded.strftime("%Y-%m-%d %H:%M:%S"), 'patient_id': report.patient_id, 'doctor_id': report.doctor_id, 'is_appointment': report.is_appointment} for report in user_reports]
    
    # Return the reports as JSON
    return jsonify({'reports': serialized_reports})

# Define the route to get a specific report by ID for the current user
@bp.route('/get_report2', methods=['GET'])
def get_report_by_id():
    # Get the report ID from the request parameters
    report_id = request.args.get('report_id')

    # Check if the report ID is provided
    if not report_id:
        return jsonify({'error': 'Report ID not provided'}), 400
    
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Get the current user's ID from the session
    user_id = session['user_id']
    
    # Query the database to retrieve the report with the specified ID for the current user
    report = Report.query.filter_by(id=report_id, patient_id=user_id).first()
    
    # Check if the report exists
    if not report:
        return jsonify({'error': 'Report not found or unauthorized access'}), 404
    
    # Serialize the report data
    serialized_report = {'id': report.id, 'symptoms': report.symptoms, 'prescription': report.prescription, 'date_uploaded': report.date_uploaded.strftime("%Y-%m-%d %H:%M:%S"), 'patient_id': report.patient_id, 'doctor_id': report.doctor_id, 'is_appointment': report.is_appointment}
    
    # Return the report as JSON
    return jsonify({'report': serialized_report})


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404