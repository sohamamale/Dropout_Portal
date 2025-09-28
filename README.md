# 🎓 Student Dropout Prevention Portal

A comprehensive web application for teachers to monitor student performance, track attendance, and manage counselling sessions to prevent student dropouts.

**Team Project**: This application uses shared Google Sheets for collaborative data management.

## ✨ Features

- **📊 Analytics Dashboard**: Modern UI with charts for attendance and CGPA distribution
- **👥 Student Management**: View detailed student profiles and performance metrics
- **💬 Counselling System**: Schedule and track counselling sessions with email notifications
- **🔐 Teacher Authentication**: Secure login and registration system
- **📈 Performance Tracking**: Monitor dropout risk and academic performance
- **📧 Email Integration**: Automated counselling email notifications
- **☁️ Cloud Storage**: Google Sheets integration with local fallback

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Access to the shared Google Sheets (provided by team lead)
- **No Gmail setup needed** - email is already configured for the team

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <your-repo-url>
   cd Portal
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration files**
   
   **Email Configuration:**
   ```bash
   cp email_config.py.example email_config.py
   ```
   **No changes needed** - the email configuration is already set up for team use.

   **Google Sheets Configuration:**
   ```bash
   cp service-account-key.json.example service-account-key.json
   ```
   **IMPORTANT**: Get the actual service account key file from your team lead. The example file contains placeholder data.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 📋 Setup Instructions

### Email Setup (Team Members)

**No email setup required** - the team Gmail account is already configured:
- **Email**: soham.username@gmail.com
- **App Password**: Already set up
- **School Name**: AISSMS IOIT

All team members will send counselling emails from the same account.

### Google Sheets Setup (Team Members)

**For Team Members**: The Google Sheets are already set up and shared. You just need:

1. **Get the service account key file** from your team lead
2. **Rename it to** `service-account-key.json`
3. **Place it in the project root directory**
4. **The spreadsheet "Students.Details" is already shared** with the service account

**Note**: All team members will access the same data and see each other's counselling records.

### Student Data Format

The shared Google Sheet "Students.Details" already contains the required columns:
- Sr No
- Student Name
- CGPA
- Present Days
- Total Days
- Attendance (%)
- GP
- Total Points
- Percent Grade points
- Dropout Chance
- Fees paid
- Total fees
- Contact Details
- Students Email

**Team Collaboration**: All team members can view and add counselling records to the same spreadsheet.

## 🔧 Configuration

### Environment Variables (Optional)

You can set these environment variables instead of using config files:

```bash
export SECRET_KEY="your-secret-key"
export GOOGLE_SERVICE_ACCOUNT_FILE="path/to/service-account.json"
```

### Local Storage Fallback

If Google Sheets is not available, the application will automatically use local JSON files:
- `teachers_data.json` - Teacher registration data
- `counselling_records.json` - Counselling session history

## 📱 Usage

### Teacher Registration
1. Go to the main page
2. Click "Teacher Registration"
3. Fill in your details
4. Submit the form

### Teacher Login
1. Go to the main page
2. Click "Teacher Dashboard"
3. Enter your credentials
4. Complete the CAPTCHA

### Student Management
1. After logging in, view the analytics dashboard
2. Click on any student name to view their profile
3. Use the counselling form to send emails to students
4. View counselling history for each student

## 🛠️ Troubleshooting

### Common Issues

**"Google Sheets not available"**
- Check if `service-account-key.json` exists
- Verify the service account has access to your spreadsheet
- Ensure Google Sheets API is enabled

**"Failed to send email"**
- Verify Gmail credentials in `email_config.py`
- Use App Password, not regular Gmail password
- Check if 2-Step Verification is enabled

**"Module not found" errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**"Permission denied" errors**
- Check file permissions
- Ensure the application has write access to the directory

### Getting Help

1. Check the console output for error messages
2. Verify all configuration files are set up correctly
3. Ensure all dependencies are installed
4. Check that ports 5000 is not blocked

## 🔒 Security Notes

- Never commit sensitive files to version control
- Use environment variables for production deployments
- Regularly rotate your Gmail App Passwords
- Keep your service account keys secure

## 📁 Project Structure

```
Portal/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── email_config.py.example        # Email configuration template
├── service-account-key.json.example # Google Sheets configuration template
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
└── templates/                     # HTML templates
    ├── index.html                 # Main landing page
    ├── teacher-login.html         # Teacher login page
    ├── teacher-register.html      # Teacher registration page
    ├── dashboard.html             # Analytics dashboard
    └── student_profile.html       # Individual student profile
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework for web development
- Google Sheets API for data storage
- Chart.js for analytics visualization
- Gmail SMTP for email functionality
