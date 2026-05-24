
```markdown
# 🏙️ Society Management HUB ENTERPRISE

**Version:** 15.0.0-Titanium-Ultimate  
**Type:** Society Management HUB(SMH) Management System  
**Tech Stack:** Python 3.10+, Streamlit, MySQL 8.0+  
**Website:** https://Societymanagementhub.com  
**Support:** support@Societymanagementhub.com | +91-1800-SMART-SMH

---

## 🚀 Quick Start

### Run the Application
```bash
# Start the Streamlit application
streamlit run app.py

# Or with custom port
streamlit run app.py --server.port 8501
```

### Access via Ngrok (Remote Access)
```bash
# Start ngrok tunnel
ngrok http 8501
```

The application will open in your browser at `http://localhost:8501`.

---


## 💻 Prerequisites

- Python 3.10 or higher
- MySQL Server 8.0 or higher
- Windows / Linux / MacOS

---

## 🛠️ Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Society Management HUB"
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
```bash
pip install mysql-connector-python streamlit pandas bcrypt
```
### 4. Configure Database (Zero-Touch Setup)

You do **NOT** need to manually import any SQL files. The app features a Crash-Proof Auto-Schema Engine.
1. Open your `config.py` file.
2. Update the `MYSQL_CONFIG` dictionary with your local MySQL credentials:
   ```python
   MYSQL_CONFIG = {
       "host": "localhost",
       "port": 3306,  # Or 3307 based on your setup
       "user": "root",
       "password": "your_password",
       "database": "Society_management_hub"
   }
   ```
3. Run the app! The system will automatically create the database, build all 35+ tables, and apply any missing columns on startup.

---

## 📁 Project Structure

```
Society Management HUB/
├── app.py                     # Main application entry point & routing
├── config.py                  # Master configuration settings
├── db.py                      # Database layer (Auto-Schema & Connection Pooling)
├── requirements.txt           # Python dependencies
│
├── core/                      # Core functionality
│   ├── auth.py               # Authentication & authorization
│   ├── helpers.py            # Utility functions
│   └── ui_styles.py          # UI styling & CSS
│
├── components/                # Reusable UI components
│   └── cards.py              # Metric cards, badges, empty states
│
├── roles/                    # Role-based dashboards
│   ├── admin/
│   │   └── admin_dashboard.py    # Super Admin dashboard (Analytics, Users, Security)
│   ├── manager/
│   │   └── manager_dashboard.py  # Manager dashboard (Day-to-day operations)
│   ├── resident/
│   │   └── resident_portal.py    # Resident portal (Forums, Booking, Helpdesk)
│   └── guard/
│       └── guard_dashboard.py    # Guard dashboard (Gate, Patrols, SOS)
```

---

## 🌟 Features Overview

### Admin & Manager Dashboard
- 🔍 **Live Audit Logs & User Activity**
- 🛡️ **Security Control Center** *(SOPs, FAQs, Emergency Contacts)*
- 👥 Staff & User Management
- 📊 Analytics Dashboard (Live Gate Traffic & Tickets)
- 🏃 Amenity Management
- 📢 Announcement Manager
- 🖥️ System Overview & Settings

### Resident Portal
- 🏠 Home Dashboard
- 💬 **Interactive Community Forum** *(Posts, Comments, Likes)*
- 🚗 Vehicle Registration & My Vehicles
- 🚗 Visitor Pre-approval
- 🛠️ Helpdesk & Complaints
- ❓ FAQ & Knowledge Base
- 🆘 Emergency SOS Alerts
- 📄 Document Center

### Guard Dashboard
- 🏠 Security Home
- 🚶 Visitor Registration (Check-in/out)
- 🚗 Vehicle Management Logs
- 📦 Parcel Tracking
- 🔒 Security & SOS Overrides
- 🚶 Patrol Management & Logs
- 📋 Shift Handovers

---

## ⚙️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python 3.10+ |
| **Database** | MySQL 8.0+ |
| **Authentication** | bcrypt Hash + Persistent Sessions |
| **UI Framework** | Custom CSS injections |

---

## 💎 Premium UI Features

- 🎨 Dark/Light theme support
- ✨ Animated buttons & transitions
- 📱 Responsive layout mapping
- 🎯 Interactive dashboard metric cards
- 🔔 Status badges & Priority indicators
- 📉 Zero-Crash Data Handling (`{}` and `[]` fallbacks)

---

## 🚑 Troubleshooting

### Database Missing Column Errors (1054 / 42S22)
If you see an error like "Unknown column 'contact_type'":
- The system automatically patches missing columns. Just ensure `db.upgrade_database_schema()` is called right under `db.init_database()` at the bottom of your `app.py` file, then restart the app.

### Database Connection Issues
Verify your MySQL service is running:
```bash
mysql -u root -p
```
Check `config.py` to ensure the host and password are correct.

### Port Already in Use
If Streamlit fails to start because port 8501 is occupied:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8501
kill -9 <PID>
```

---

## 📞 Support

- **Email:** support@Society_management_hub.com
- **Phone:** +91-1800-SMART-SMH
- **Documentation:** See SRS_Document.md for complete technical details

---


### 🌐 How to Run Ngrok (Assuming it's already installed)

**Step 1: Start your app first**
Open your terminal and start your Society Management HUB normally. Leave this terminal open.
```bash
streamlit run app.py
```

**Step 2: Start the Ngrok Tunnel**
Open a **new** terminal window, and run the following command to forward your Streamlit port (8501):
```bash
ngrok http 8501
```

---

## 📄 License

Copyright © 2026 Society Management HUB Enterprise. All rights reserved.

---

**Version:** 15.0.0-Titanium-Ultimate  
**Last Updated:** April 2026
```
