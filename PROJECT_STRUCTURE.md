# Hostel Management System - Project Structure

## 📁 Directory Overview

```
hostel-management-system/
├── flask_app.py              # Main Flask application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (database config)
├── run.ps1                   # PowerShell script to run the app
├── README.md                 # Project documentation
├── LOGIN_CREDENTIALS.md      # Login credentials for testing
│
├── public/                   # Frontend files
│   ├── index.html           # Landing page
│   ├── login.html           # Login page
│   ├── student.html         # Student dashboard
│   ├── manager.html         # Manager dashboard
│   ├── style.css            # Styles
│   └── script.js            # JavaScript logic
│
├── sql_scripts/             # Database scripts
│   ├── insert_login_data.sql
│   ├── block_vacancy_triggers.sql
│   ├── add_fees_column.sql
│   ├── add_feespaid_to_studentinfo.sql
│   ├── fix_feespaid_column.sql
│   ├── remove_feespaid_column.sql
│   └── update_feesinfo.sql
│
├── tests/                   # Test scripts
│   ├── test_db.py
│   ├── test_login.py
│   ├── check_schema.py
│   ├── show_users.py
│   └── verify_login.py
│
└── flask_session/           # Session data (auto-generated)
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database:**
   - Update `.env` file with your MySQL credentials

3. **Run the application:**
   ```bash
   python flask_app.py
   ```
   Or use PowerShell script:
   ```powershell
   .\run.ps1
   ```

4. **Access the application:**
   - Open browser to: http://127.0.0.1:3000

## 📝 Key Features

- **Student Portal:** View profile, hostel details, fees information
- **Manager Portal:** Manage students, rooms, blocks, and fees
- **Room Assignment:** Automatic room and block assignment tracking
- **Fees Management:** Track and update student fees
- **Session Management:** Secure login with Flask sessions

## 🔧 Configuration

All database configuration is stored in the `.env` file:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=hostel_management
```

## 📊 Database Schema

The application uses the following main tables:
- `StudentInfo` - Student personal and hostel information
- `Login` - Authentication credentials
- `FeesInfo` - Fee structure and payments
- `Room` - Room details and occupancy
- `Block` - Building/block information

## 🧪 Testing

Test scripts are located in the `tests/` folder:
- `test_db.py` - Database connection test
- `test_login.py` - Login functionality test
- `check_schema.py` - Verify database schema
- `show_users.py` - Display user accounts
- `verify_login.py` - Verify login credentials

Run tests from the project root:
```bash
python tests/test_db.py
```

## 📂 SQL Scripts

Migration and setup scripts in `sql_scripts/`:
- Initial setup scripts
- Schema modifications
- Trigger definitions
- Data updates

## 🔐 Security Notes

- Change the `SECRET_KEY` in `flask_app.py` for production
- Update database credentials in `.env`
- Never commit `.env` file to version control
- Use HTTPS in production environment

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** MySQL with PyMySQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Session:** Flask-Session
- **CORS:** Flask-CORS

## 📱 Port Configuration

Default port: `3000`

To change the port, modify `flask_app.py`:
```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=True)
```
