# 👥 Team Setup Instructions

## For Team Members (Your Colleagues)

### Quick Setup for Team Members

1. **Download the project** from GitHub
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Get the service account key** from your team lead
4. **Configure your email** in `email_config.py`
5. **Run the application**:
   ```bash
   python app.py
   ```

### What You Need from Your Team Lead

1. **Service Account Key File**: `turing-signer-471919-p2-206e681b55b2.json`
   - This file contains the credentials to access the shared Google Sheets
   - Rename it to `service-account-key.json`
   - Place it in the project root directory

2. **Access to Shared Spreadsheet**: "Students.Details"
   - Already shared with the service account
   - Contains all student data
   - All team members see the same data

### Email Configuration

Edit `email_config.py` with your own Gmail credentials:

```python
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-gmail-app-password"  # Use App Password
SCHOOL_NAME = "AISSMS IOIT"  # Keep this the same
```

### What You'll See

- **Same student data** as your teammates
- **All counselling records** from all team members
- **Real-time updates** when others add counselling sessions
- **Shared analytics** and dashboard

### Important Notes

- **Don't modify** the Google Sheets structure
- **Use your own Gmail** for sending counselling emails
- **All counselling records** are shared among team members
- **Student data** is read-only (managed by team lead)

## For Team Lead (You)

### Sharing the Service Account Key

1. **Share the file**: `turing-signer-471919-p2-206e681b55b2.json`
2. **Tell team members** to rename it to `service-account-key.json`
3. **Ensure the spreadsheet** "Students.Details" is shared with the service account

### Managing the Project

- **Update student data** in the Google Sheet
- **Monitor counselling records** from all team members
- **Share the service account key** securely with team members
- **Keep the main spreadsheet** updated with latest student information

### Security

- **Don't commit** the service account key to GitHub
- **Share the key** through secure channels (not email)
- **Monitor access** to the Google Sheets
- **Keep backups** of important data
