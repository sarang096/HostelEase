# 🔐 Login Credentials for Hostel Management System

## 📍 Access the Application
**URL:** http://localhost:3000

## 👥 Available Users

### 👨‍🎓 Student Accounts
| Username   | Password | Role    |
|------------|----------|---------|
| student3   | pass123  | student |
| sarang     | pass123  | student |
| neha       | pass123  | student |
| sanjana    | pass123  | student |
| shreehari  | pass123  | student |
| sanjoli    | pass123  | student |
| avrit      | pass123  | student |

### 👨‍💼 Manager Accounts
| Username  | Password  | Role    |
|-----------|-----------|---------|
| manager1  | admin123  | manager |
| manager2  | admin123  | manager |

## 🚀 Quick Start

1. **Start the Flask server:**
   ```powershell
   .\run.ps1
   ```
   
   Or manually:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python flask_app.py
   ```

2. **Open your browser:**
   Go to http://localhost:3000

3. **Login:**
   - For student dashboard: Use any student username (e.g., `shreehari` / `pass123`)
   - For manager dashboard: Use any manager username (e.g., `manager1` / `admin123`)

## ✨ Features

### Student Portal
- View profile information
- Check fees status (Paid/Remaining)
- View room and hostel block assignments
- Change password

### Manager Portal
- View all students
- Add new students
- Edit student information
- Update fees
- Delete students (only if fees fully paid)
- Manage hostel blocks, rooms, and mess

## 🐛 Troubleshooting

### Can't login?
- **Make sure Flask server is running** - You should see output like "Running on http://127.0.0.1:3000"
- **Use correct credentials** - Username and password are case-sensitive
- **Check browser console** (F12) for any error messages
- **Clear browser cache** - Try Ctrl+Shift+R to hard refresh

### Server not starting?
- Make sure MySQL is running
- Check database credentials in `.env` file
- Ensure virtual environment is activated
- Check if port 3000 is not already in use

### Database connection error?
- Verify MySQL service is running
- Check credentials in `.env` file match your MySQL setup
- Ensure database `hostel_db` exists

## 📝 Notes
- Default fees total: ₹50,000 per student
- Students cannot be deleted if they have unpaid fees
- Sessions are stored in the `flask_session/` directory
