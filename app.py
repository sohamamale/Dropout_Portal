from flask import Flask, render_template, request, redirect, url_for, session
import gspread
from google.oauth2.service_account import Credentials
import random, string
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to something strong

# ------------------ GOOGLE SHEETS SETUP ------------------
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Try to initialize Google Sheets, fallback to local storage if it fails
GOOGLE_SHEETS_AVAILABLE = False
CLIENT = None
sheet = None

try:
    CREDS = Credentials.from_service_account_file(
        r"D:\Desktop\Droupout\Portal\turing-signer-471919-p2-206e681b55b2.json",
        scopes=SCOPE
    )
    CLIENT = gspread.authorize(CREDS)
    SHEET_NAME = "Students.Details"   # <-- spreadsheet name
    sheet = CLIENT.open(SHEET_NAME).sheet1   # main student details (first sheet)
    GOOGLE_SHEETS_AVAILABLE = True
    print("Google Sheets connection successful")
except Exception as e:
    print(f"Google Sheets not available: {e}")
    print("Using local file storage as fallback")

# Teacher data is now stored exclusively in Google Sheets

# ------------------ EMAIL CONFIGURATION ------------------
# Import email configuration
try:
    from email_config import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, SCHOOL_NAME, ADMIN_EMAIL
except ImportError:
    # Fallback configuration if email_config.py doesn't exist
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "soham.username@gmail.com"  # Change this to your Gmail
    EMAIL_PASSWORD = "tqqv ttol jkby gkil"    # Change this to your Gmail App Password
    SCHOOL_NAME = "School Administration"
    ADMIN_EMAIL = "admin@school.com"

# ------------------ COUNSELLING STORAGE ------------------
def store_counselling_record(sr_no, student_name, teacher_name, message, timestamp):
    """Store counselling record in Google Sheets"""
    try:
        if GOOGLE_SHEETS_AVAILABLE:
            # Try to open counselling sheet
            try:
                counselling_sheet = CLIENT.open("Students.Details").worksheet("Counselling")
            except:
                # Create counselling sheet if it doesn't exist
                counselling_sheet = CLIENT.open("Students.Details").add_worksheet(title="Counselling", rows=1000, cols=6)
                # Add headers
                counselling_sheet.insert_row(["Sr No", "Student Name", "Teacher", "Message", "Timestamp", "Status"], 1)
            
            # Add new record
            new_row = [sr_no, student_name, teacher_name, message, timestamp, "Sent"]
            counselling_sheet.append_row(new_row)
            return True, "Counselling record stored"
        else:
            # Store locally
            return store_counselling_local(sr_no, student_name, teacher_name, message, timestamp)
    except Exception as e:
        print(f"Error storing counselling record: {e}")
        return store_counselling_local(sr_no, student_name, teacher_name, message, timestamp)

def store_counselling_local(sr_no, student_name, teacher_name, message, timestamp):
    """Store counselling record locally"""
    try:
        counselling_file = "counselling_records.json"
        if os.path.exists(counselling_file):
            with open(counselling_file, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        new_record = {
            "sr_no": sr_no,
            "student_name": student_name,
            "teacher_name": teacher_name,
            "message": message,
            "timestamp": timestamp,
            "status": "Sent"
        }
        records.append(new_record)
        
        with open(counselling_file, 'w') as f:
            json.dump(records, f, indent=2)
        
        return True, "Counselling record stored locally"
    except Exception as e:
        print(f"Error storing counselling locally: {e}")
        return False, str(e)

def get_counselling_history(sr_no):
    """Get counselling history for a student"""
    try:
        if GOOGLE_SHEETS_AVAILABLE:
            try:
                counselling_sheet = CLIENT.open("Students.Details").worksheet("Counselling")
                all_records = counselling_sheet.get_all_records()
                # Filter records for this student
                student_records = [r for r in all_records if str(r.get("Sr No")) == str(sr_no)]
                return student_records
            except:
                return get_counselling_history_local(sr_no)
        else:
            return get_counselling_history_local(sr_no)
    except Exception as e:
        print(f"Error getting counselling history: {e}")
        return get_counselling_history_local(sr_no)

def get_counselling_history_local(sr_no):
    """Get counselling history from local storage"""
    try:
        counselling_file = "counselling_records.json"
        if os.path.exists(counselling_file):
            with open(counselling_file, 'r') as f:
                records = json.load(f)
            # Filter records for this student
            student_records = [r for r in records if str(r.get("sr_no")) == str(sr_no)]
            return student_records
        return []
    except Exception as e:
        print(f"Error getting counselling history locally: {e}")
        return []

def get_counselling_counts():
    """Get counselling count for each student"""
    try:
        if GOOGLE_SHEETS_AVAILABLE:
            try:
                counselling_sheet = CLIENT.open("Students.Details").worksheet("Counselling")
                all_records = counselling_sheet.get_all_records()
                counts = {}
                for record in all_records:
                    sr_no = str(record.get("Sr No"))
                    if sr_no:
                        counts[sr_no] = counts.get(sr_no, 0) + 1
                return counts
            except:
                return get_counselling_counts_local()
        else:
            return get_counselling_counts_local()
    except Exception as e:
        print(f"Error getting counselling counts: {e}")
        return get_counselling_counts_local()

def get_counselling_counts_local():
    """Get counselling counts from local storage"""
    try:
        counselling_file = "counselling_records.json"
        if os.path.exists(counselling_file):
            with open(counselling_file, 'r') as f:
                records = json.load(f)
            counts = {}
            for record in records:
                sr_no = str(record.get("sr_no"))
                if sr_no:
                    counts[sr_no] = counts.get(sr_no, 0) + 1
            return counts
        return {}
    except Exception as e:
        print(f"Error getting counselling counts locally: {e}")
        return {}

# ------------------ EMAIL FUNCTIONS ------------------
def send_counselling_email(student_email, student_name, teacher_name, message):
    """Send counselling email to student"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = student_email
        msg['Subject'] = f"Counselling Session - {student_name}"
        
        # Email body
        body = f"""
Dear {student_name},

You have been scheduled for a counselling session.

Teacher: {teacher_name}
Message: {message}

Please contact your teacher for further details.

Best regards,
{SCHOOL_NAME}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, student_email, text)
        server.quit()
        
        return True, "Email sent successfully"
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, f"Failed to send email: {str(e)}"


@app.route("/test-form", methods=["POST"])
def test_form():
    print("TEST FORM DATA:", request.form)
    return "Check terminal for form data!"


# ------------------ HELPER FUNCTIONS ------------------
def fetch_student_data():
    try:
        all_values = sheet.get_all_values()
        data = []

        if len(all_values) < 2:
            return data, []

        # Use actual column headers from the spreadsheet
        sheet_headers = all_values[0]
        print(f"DEBUG: Found columns in spreadsheet: {sheet_headers}")
        
        # Filter out empty columns and formula columns
        filtered_headers = []
        filtered_indices = []
        
        for i, header in enumerate(sheet_headers):
            # Skip empty headers or headers that are just spaces
            if not header or header.strip() == "":
                continue
            # Skip columns that are likely formulas (contain parentheses or start with =)
            if "(" in header or ")" in header or header.strip().startswith("="):
                continue
            # Skip columns that are just single letters (likely formula references)
            if len(header.strip()) == 1 and header.strip().isalpha():
                continue
                
            filtered_headers.append(header)
            filtered_indices.append(i)
        
        print(f"DEBUG: Filtered headers for display: {filtered_headers}")
        
        for row in all_values[1:]:
            # Skip rows with empty first column (assuming first column is ID/Sr No)
            if not row or not row[0] or row[0].strip() == "":
                continue
                
            # Create row dictionary using only filtered columns
            row_dict = {}
            for i, header in enumerate(filtered_headers):
                col_index = filtered_indices[i]
                row_dict[header] = row[col_index] if col_index < len(row) else ""
            data.append(row_dict)
            
        print(f"DEBUG: Processed {len(data)} student records with {len(filtered_headers)} columns")
        return data, filtered_headers
    except Exception as e:
        print(f"Error fetching student data: {e}")
        return [], []


def check_teacher_credentials(userid, password):
    if not GOOGLE_SHEETS_AVAILABLE:
        print("ERROR: Google Sheets not available - authentication cannot proceed")
        return False
    
    try:
        teacher_sheet = CLIENT.open("Login And Register").worksheet("DATA")
        # Fetch all values and map to headers manually
        all_values = teacher_sheet.get_all_values()
        if not all_values or len(all_values) < 2:
            print("No teacher data found in Google Sheets")
            return False
            
        headers = all_values[0]
        accounts = []
        for row in all_values[1:]:
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            account = dict(zip(headers, row))
            accounts.append(account)

        print("DEBUG: Checking credentials against Google Sheets")
        print(f"DEBUG: Found {len(accounts)} teacher accounts")

        for account in accounts:
            user = str(account.get("UserID", "")).strip()
            pw = str(account.get("Password", "")).strip()
            print(f"DEBUG comparing: input=({userid},{password}) vs sheet=({user},{pw})")

            if user == str(userid).strip() and pw == str(password).strip():
                print("DEBUG: MATCH FOUND ✅")
                return True

        print("DEBUG: NO MATCH ❌")
        return False
        
    except Exception as e:
        print(f"ERROR in check_teacher_credentials (Google Sheets): {e}")
        print("Authentication failed - Google Sheets connection error")
        return False


def register_teacher(teacher_data):
    if not GOOGLE_SHEETS_AVAILABLE:
        print("ERROR: Google Sheets not available - registration cannot proceed")
        return False, "Registration service unavailable - Google Sheets connection required"
    
    try:
        teacher_sheet = CLIENT.open("Login And Register").worksheet("DATA")
        headers = teacher_sheet.row_values(1)
        if not headers or headers == ['']:
            headers = ["UserID", "Password", "Name", "Email", "Phone", "Department", "Subject"]
            teacher_sheet.insert_row(headers, 1)
            headers = teacher_sheet.row_values(1)  # Refresh headers

        # Fetch all values and map to headers manually
        all_values = teacher_sheet.get_all_values()
        if not all_values or len(all_values) < 2:
            existing_records = []
        else:
            sheet_headers = all_values[0]
            existing_records = []
            for row in all_values[1:]:
                if len(row) < len(sheet_headers):
                    row += [""] * (len(sheet_headers) - len(row))
                record = dict(zip(sheet_headers, row))
                existing_records.append(record)

        for record in existing_records:
            if str(record.get("UserID", "")).strip() == str(teacher_data["teacherUserId"]).strip():
                return False, "User ID already exists"

        new_row = [
            teacher_data["teacherUserId"],
            teacher_data["teacherPassword"],
            teacher_data["teacherName"],
            teacher_data["teacherEmail"],
            teacher_data["teacherPhone"],
            teacher_data["teacherDepartment"],
            teacher_data["teacherSubject"]
        ]
        teacher_sheet.append_row(new_row)
        return True, "Teacher registered successfully"

    except Exception as e:
        print(f"ERROR in register_teacher (Google Sheets): {e}")
        return False, "Registration failed - Google Sheets connection error"




# ------------------ ROUTES ------------------

@app.route("/")
def index():
    return render_template("index.html")


# ------------------ STUDENT LOGIN ------------------
@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        prn = request.form.get("studentPRN")  # from login form
        otp = request.form.get("studentOTP")
        captcha_input = request.form.get("captchaInput")
        captcha_code = session.get("captcha")

        # Verify OTP
        if otp != "123456":
            return "<script>alert('Invalid OTP'); window.location='/student-login';</script>"

        # Verify CAPTCHA
        if captcha_input != captcha_code:
            return "<script>alert('CAPTCHA incorrect'); window.location='/student-login';</script>"

        # Login success → redirect to student dashboard
        return redirect(url_for("student_dashboard", prn=prn))

    # GET request: generate CAPTCHA
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session["captcha"] = captcha
    return render_template("student-login.html", captcha=captcha)


# ------------------ TEACHER REGISTRATION ------------------
@app.route("/teacher-register", methods=["GET", "POST"])
def teacher_register():
    if request.method == "POST":
        print("DEBUG: POST request received for teacher registration")
        print("DEBUG: Form data:", request.form)
        
        teacher_data = {
            "teacherName": request.form.get("teacherName"),
            "teacherUserId": request.form.get("teacherUserId"),
            "teacherPassword": request.form.get("teacherPassword"),
            "teacherEmail": request.form.get("teacherEmail"),
            "teacherPhone": request.form.get("teacherPhone"),
            "teacherDepartment": request.form.get("teacherDepartment"),
            "teacherSubject": request.form.get("teacherSubject")
        }
        
        print("DEBUG: Teacher data:", teacher_data)
        
        # Validate required fields
        required_fields = ["teacherName", "teacherUserId", "teacherPassword", "teacherEmail", "teacherPhone", "teacherDepartment", "teacherSubject"]
        for field in required_fields:
            if not teacher_data[field]:
                print(f"DEBUG: Missing field: {field}")
                return render_template("teacher-register.html", error=f"Please fill in all required fields")
        
        print("DEBUG: All fields validated, calling register_teacher")
        # Register teacher
        success, message = register_teacher(teacher_data)
        print(f"DEBUG: Registration result - Success: {success}, Message: {message}")
        
        if success:
            return render_template("teacher-register.html", success=message)
        else:
            return render_template("teacher-register.html", error=message)
    
    # GET request: show registration form
    print("DEBUG: GET request for teacher registration form")
    return render_template("teacher-register.html")


# ------------------ TEACHER LOGIN ------------------
@app.route("/teacher-login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        userid = request.form.get("teacherUserId")
        password = request.form.get("teacherPassword")
        captcha_input = request.form.get("captchaInput")
        captcha_code = session.get("captcha")

        # Check CAPTCHA first before regenerating
        if captcha_input != captcha_code:
            # Generate fresh CAPTCHA for next attempt
            fresh_captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            session["captcha"] = fresh_captcha
            return render_template("teacher-login.html", captcha=fresh_captcha, error="CAPTCHA incorrect")

        if not check_teacher_credentials(userid, password):
            # Generate fresh CAPTCHA for next attempt
            fresh_captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            session["captcha"] = fresh_captcha
            if not GOOGLE_SHEETS_AVAILABLE:
                return render_template("teacher-login.html", captcha=fresh_captcha, error="Authentication service unavailable - Google Sheets connection required")
            else:
                return render_template("teacher-login.html", captcha=fresh_captcha, error="Invalid UserID or Password")

        # ✅ Success → store teacher session and redirect
        session['teacher_logged_in'] = True
        session['teacher_userid'] = userid
        return redirect(url_for("teacher_dashboard"))

    # GET request: show fresh CAPTCHA
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session["captcha"] = captcha
    return render_template("teacher-login.html", captcha=captcha)

# ------------------ TEACHER LOGOUT ------------------
@app.route("/teacher-logout")
def teacher_logout():
    session.pop('teacher_logged_in', None)
    session.pop('teacher_userid', None)
    return redirect(url_for('index'))

# ------------------ TEACHER DASHBOARD ------------------
@app.route("/teacher-dashboard")
def teacher_dashboard():
    # Check if teacher is logged in
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))
    
    data, headers = fetch_student_data()
    
    # Get counselling counts for each student
    counselling_counts = get_counselling_counts()
    
    # Add counselling count to each student record
    for student in data:
        sr_no = str(student.get('Sr No', ''))
        student['counselling_count'] = counselling_counts.get(sr_no, 0)
    
    return render_template("dashboard.html", data=data, headers=headers)


# ------------------ STUDENT DASHBOARD ------------------
@app.route("/student-dashboard/<prn>")
def student_dashboard(prn):
    data, headers = fetch_student_data()
    student = next((s for s in data if str(s.get("Sr No")) == str(prn)), None)
    if not student:
        return "Student not found", 404
    return render_template("student_profile.html", student=student, headers=headers)


# ------------------ STUDENT PROFILE ------------------
@app.route("/student/<int:sr_no>")
def student_profile(sr_no):
    data, headers = fetch_student_data()
    student = next((s for s in data if str(s.get("Sr No")) == str(sr_no)), None)
    if not student:
        return "Student not found", 404
    
    # Get counselling history for this student
    counselling_history = get_counselling_history(sr_no)
    
    return render_template("student_profile.html", student=student, headers=headers, counselling_history=counselling_history)


# ------------------ COUNSELING ------------------
@app.route("/schedule/<int:sr_no>", methods=["POST"])
def schedule_counseling(sr_no):
    # Check if teacher is logged in
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))
    
    message = request.form.get("message")
    teacher_name = session.get('teacher_userid', 'Teacher')
    
    # Get student data to find email
    data, headers = fetch_student_data()
    student = next((s for s in data if str(s.get("Sr No")) == str(sr_no)), None)
    
    if not student:
        return "Student not found", 404
    
    student_name = student.get("Student Name", "Student")
    student_email = student.get("Students Email", "")
    
    if not student_email:
        return f"Student email not found for {student_name}", 400
    
    # Send counselling email
    success, email_message = send_counselling_email(student_email, student_name, teacher_name, message)
    
    if success:
        # Store counselling record
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store_success, store_message = store_counselling_record(sr_no, student_name, teacher_name, message, timestamp)
        
        print(f"Counselling email sent to {student_name} ({student_email}): {message}")
        if store_success:
            print(f"Counselling record stored: {store_message}")
        else:
            print(f"Failed to store counselling record: {store_message}")
        
        return redirect(url_for("student_profile", sr_no=sr_no))
    else:
        print(f"Failed to send counselling email: {email_message}")
        return f"Failed to send email: {email_message}", 500


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True)
