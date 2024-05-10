## HealthX: A Healthcare Management System

### Overview
This repository contains the source code for HealthX, a comprehensive healthcare management system designed to streamline patient-doctor interactions, medical record management, and appointment scheduling. It is built using Flask for the backend, SQLAlchemy for database management, and HTML/CSS/JavaScript for the frontend.

### Features
- User authentication and authorization for patients and doctors.
- Patient dashboard to view medical reports, appointments, and prescription history.
- Doctor dashboard to manage appointments, view patient history, and prescribe medication.
- Secure uploading of medical reports and prescriptions.
- Appointment scheduling with notification reminders.
- Responsive design for seamless usage across devices.

### Installation
To run this application locally, follow these steps:
1. Clone this repository to your local machine.
2. Install dependencies using `pip install -r requirements.txt`.
3. Set up the database by running `flask db init`, `flask db migrate`, and `flask db upgrade`.
4. Set up environment variables as specified in the `.env.example` file.

### Usage
1. Start the Flask development server by running `flask run`.
2. Access the application through your web browser at `http://localhost:5000`.
3. Sign up as a patient or doctor to access the respective dashboards.
4. Upload medical reports, schedule appointments, and manage prescriptions as needed.

### Contributing
Contributions are welcome! To contribute to this project, follow these steps:
1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contact
For inquiries, issues, or suggestions regarding this project, please contact Jay at jayrane2004@gmail.com.
