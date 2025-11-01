💇‍♀️ Salon Management Web App

A modern, responsive, and fully-featured web application for managing salon services, appointments, and users. Built with Django, HTML, CSS, and JavaScript.

🌟 Features
User Roles

Customer:

Browse available services

Book appointments

View service pricing and history

Manager:

Manage services (add/edit/remove)

Manage bookings and appointments

Track revenue and service popularity

Super Admin:

Full access to all system data

Manage managers, customers, and services

Generate reports and analytics

Salon Services

Browse services with details and pricing

Categorize services (Hair, Beauty, Nails, Spa, etc.)

Dynamic pricing management for each service

Appointment Booking

Customers can select date, time, and service

Managers can approve, cancel, or modify bookings

Email/notification reminders for upcoming appointments (optional)

Responsive UI

Mobile-first design for all devices

Smooth navigation with HTML, CSS, and JS

Dynamic interactivity (e.g., service selection, booking forms)

🛠️ Technologies Used

Backend: Python, Django, Django Allauth (for authentication)

Frontend: HTML5, CSS3, JavaScript

Database: SQLite / PostgreSQL

Libraries & Tools:

django-multiselectfield for service categories

django-js-asset for JS assets management

whitenoise for production-ready static file handling

📸 Screenshots

Home Page / Services Listing


Booking Appointment Page


Manager Dashboard


🚀 Installation

Clone the repository

git clone https://github.com/yourusername/salon-app.git
cd salon-app


Create & activate virtual environment

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate


Install dependencies

pip install -r requirements.txt


Apply migrations

python manage.py migrate


Create superuser (optional)

python manage.py createsuperuser


Run the development server

python manage.py runserver


Open in browser

http://127.0.0.1:8000

🌐 Deployment

Project is deployment-ready and can be hosted on Heroku, AWS, or any VPS.

Uses Whitenoise to handle static files in production.

📂 Project Structure
salon_app/
│
├── salon/                   # Django app
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   ├── models.py            # Services, bookings, users
│   ├── views.py             # App views
│   ├── urls.py              # App URLs
│   └── admin.py             # Admin configurations
│
├── .venv/                   # Python virtual environment
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies

⚙️ Notes

Supports multi-role authentication for Customers, Managers, and Super Admin.

Booking system is time-slot based to avoid overlaps.

Service pricing is dynamic and can be updated by managers.

💡 Future Enhancements

Email & SMS notifications for booking confirmations

Online payment integration for services

Service rating & reviews by customers

Analytics dashboard for revenue & service trends

📜 License

This project is licensed under MIT License.

🙌 Author

MH JAHED | https://github.com/mhjahed
