# Hostel Management System

A Flask-based hostel management application with MySQL database backend.

## Features

### Fees Management
- **Manager**: Can add fees when creating new students (0-50,000)
- **Manager**: Can edit student fees using "Edit Fees" button
- **Manager**: Cannot delete students with unpaid fees (< 50,000)
- **Student**: Can view fees status in dashboard
- **Total Fees**: ₹50,000 per student

## Setup

### 1. Create and activate a virtual environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure database connection

Update the database credentials in `flask_app.py` (lines 17-22) or set environment variables:

```powershell
$env:DB_HOST='localhost'
$env:DB_USER='root'
$env:DB_PASSWORD='your_password'
$env:DB_NAME='hostel_db'
```

### 4. Set up the database

Make sure your MySQL database is running and execute the necessary SQL scripts:

```sql
mysql -u root -p hostel_db < add_fees_column.sql
```

### 5. Run the Flask application

**Option 1: Using the run script (Windows PowerShell)**
```powershell
.\run.ps1
```

**Option 2: Manual start**
```powershell
.\.venv\Scripts\Activate.ps1
python flask_app.py
```

### 6. Access the application

Open your browser at: http://localhost:3000

## Notes

- The Flask app serves the frontend from the `public/` directory
- Sessions are stored in the filesystem using Flask-Session
- The application uses PyMySQL to connect to the MySQL database
- All API endpoints are prefixed with `/api/`
