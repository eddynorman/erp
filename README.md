# Enterprise Resource Planning (ERP) System

A comprehensive ERP system built with Django that integrates various business operations including sales, inventory, asset management, attendance tracking, and reporting.

## 🌟 Features

### Core Modules
- **Company Management**
  - Company profile and settings
  - User management and authentication
  - Role-based access control

- **Sales Management**
  - Sales tracking and analytics
  - Customer management
  - Order processing
  - Sales reporting

- **Inventory Management**
  - Stock tracking
  - Product management
  - Inventory alerts
  - Stock movement history

- **Asset Management**
  - Asset tracking
  - Maintenance scheduling
  - Asset depreciation
  - Asset history

- **Attendance Management**
  - Fingerprint-based attendance
  - Break management
  - Attendance reporting
  - Real-time dashboard
  - Export functionality

- **Reporting System**
  - Customizable reports
  - Data visualization
  - Export to PDF/Excel
  - Scheduled reports

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/eddynorman/erp.git
   cd erp
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL Database**
   ```sql
   CREATE DATABASE mtomawe;
   CREATE USER 'emperor'@'localhost' IDENTIFIED BY 'Ed666*zub';
   GRANT ALL PRIVILEGES ON mtomawe.* TO 'emperor'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=mysql://emperor:Ed666*zub@localhost/mtomawe
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
erp/
├── attendance/          # Attendance management app
├── assets/             # Asset management app
├── company/            # Company management app
├── inventory/          # Inventory management app
├── sales/              # Sales management app
├── users/              # User management app
├── reports/            # Reporting system
├── expenses/           # Expense tracking
├── erp/                # Project settings
│   ├── settings.py     # Project configuration
│   ├── urls.py         # URL routing
│   └── wsgi.py         # WSGI configuration
└── manage.py           # Django management script
```

## 🔧 Configuration

### Database Settings
The project uses MySQL as the database backend. Configure your database settings in `erp/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtomawe',
        'USER': 'emperor',
        'PASSWORD': 'Ed666*zub',
        'HOST': 'localhost'
    }
}
```

### Email Configuration
Configure email settings in `erp/settings.py` for notifications and password resets:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''  # Your email
EMAIL_HOST_PASSWORD = ''  # Your email password
```

## 👥 User Roles

- **Superuser**: Full access to all features and settings
- **Staff**: Access to management features and reports
- **Regular User**: Basic access to assigned modules

## 📊 Reports

The system includes various reports:
- Sales reports
- Inventory reports
- Asset reports
- Attendance reports
- Financial reports

Reports can be exported in multiple formats (PDF, Excel) and scheduled for automatic generation.

## 🔐 Security

- CSRF protection
- XSS protection
- SQL injection prevention
- Password hashing
- Session management
- Role-based access control

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 guidelines. Use a linter to maintain code quality:
```bash
flake8
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Eddy Norman

## 🙏 Acknowledgments

- Django Framework
- Bootstrap
- Font Awesome
- jQuery
- MySQL

## 📞 Support

For support, email [your-email@example.com] or create an issue in the repository. 