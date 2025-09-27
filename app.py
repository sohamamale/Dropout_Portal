from flask import Flask, render_template, request, redirect, url_for, session
import gspread
from google.oauth2.service_account import Credentials
import random, string
import json
import os

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

# Local storage file for teacher data
TEACHERS_FILE = "teachers_data.json"

# ------------------ LOCAL STORAGE FUNCTIONS ------------------
def load_teachers_data():
    """Load teacher data from local JSON file"""
    if os.path.exists(TEACHERS_FILE):
        try:
            with open(TEACHERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_teachers_data(teachers_data):
    """Save teacher data to local JSON file"""
    try:
        with open(TEACHERS_FILE, 'w') as f:
            json.dump(teachers_data, f, indent=2)
        return True
    except:
        return False

def add_teacher_to_local(teacher_data):
    """Add a new teacher to local storage"""
    teachers = load_teachers_data()
    
    # Check if user ID already exists
    for teacher in teachers:
        if teacher.get("teacherUserId") == teacher_data["teacherUserId"]:
            return False, "User ID already exists"
    
    # Add new teacher
    teachers.append(teacher_data)
    
    if save_teachers_data(teachers):
        return True, "Teacher registered successfully"
    else:
        return False, "Failed to save teacher data"

def check_teacher_credentials_local(userid, password):
    """Check teacher credentials from local storage"""
    teachers = load_teachers_data()
    
    for teacher in teachers:
        if (teacher.get("teacherUserId") == userid and 
            teacher.get("teacherPassword") == password):
            return True
    return False


@app.route("/test-form", methods=["POST"])
def test_form():
    print("TEST FORM DATA:", request.form)
    return "Check terminal for form data!"


# ------------------ HELPER FUNCTIONS ------------------
def fetch_student_data():
    headers = [
        "Sr No", "Student Name", "CGPA", "Present Days", "Total Days",
        "Attendance (%)", "GP", "Total Points", "Percent Garde points",
        "Dropout Chance", "Fees paid", "Total fees", "Contact Details"
    ]

    try:
        all_values = sheet.get_all_values()
        data = []

        if len(all_values) < 2:
            return data

        sheet_headers = all_values[0]
        for row in all_values[1:]:
            # Skip rows with empty Sr No
            if not row or not row[0] or row[0].strip() == "":
                continue
                
            row_dict = {}
            for i, h in enumerate(headers):
                try:
                    idx = sheet_headers.index(h)
                    row_dict[h] = row[idx] if idx < len(row) else ""
                except ValueError:
                    row_dict[h] = ""
            data.append(row_dict)
        return data
    except Exception as e:
        print(f"Error fetching student data: {e}")
        return []


def check_teacher_credentials(userid, password):
    if GOOGLE_SHEETS_AVAILABLE:
        try:
            # Use the specific spreadsheet name and sheet name
            teacher_sheet = CLIENT.open("Login And Register").worksheet("DATA")
            
            # Try to get records with expected headers to avoid duplicate header error
            expected_headers = ["UserID", "Password", "Name", "Email", "Phone", "Department", "Subject"]
            accounts = teacher_sheet.get_all_records(expected_headers=expected_headers)

            print("DEBUG: Accounts from sheet ->", accounts)

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
            print("ERROR in check_teacher_credentials (Google Sheets):", e)
            print("Falling back to local storage")
            return check_teacher_credentials_local(userid, password)
    else:
        print("Using local storage for teacher credentials")
        return check_teacher_credentials_local(userid, password)


def register_teacher(teacher_data):
    if GOOGLE_SHEETS_AVAILABLE:
        try:
            # Use the specific spreadsheet name and sheet name
            teacher_sheet = CLIENT.open("Login And Register").worksheet("DATA")
            
            # Check if headers exist, if not create them
            headers = teacher_sheet.row_values(1)
            if not headers or headers == ['']:
                headers = ["UserID", "Password", "Name", "Email", "Phone", "Department", "Subject"]
                teacher_sheet.insert_row(headers, 1)
            
            # Check if user ID already exists using expected headers
            expected_headers = ["UserID", "Password", "Name", "Email", "Phone", "Department", "Subject"]
            existing_records = teacher_sheet.get_all_records(expected_headers=expected_headers)
            for record in existing_records:
                if str(record.get("UserID", "")).strip() == str(teacher_data["teacherUserId"]).strip():
                    return False, "User ID already exists"
            
            # Add new teacher record
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
            print("ERROR in register_teacher (Google Sheets):", e)
            print("Falling back to local storage")
            return add_teacher_to_local(teacher_data)
    else:
        print("Using local storage for teacher registration")
        return add_teacher_to_local(teacher_data)




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

        if captcha_input != captcha_code:
            return render_template("teacher-login.html", captcha=captcha_code, error="CAPTCHA incorrect")

        if not check_teacher_credentials(userid, password):
            return render_template("teacher-login.html", captcha=captcha_code, error="Invalid UserID or Password")

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
    
    data = fetch_student_data()
    return render_template("dashboard.html", data=data)


# ------------------ STUDENT DASHBOARD ------------------
@app.route("/student-dashboard/<prn>")
def student_dashboard(prn):
    data = fetch_student_data()
    student = next((s for s in data if str(s.get("Sr No")) == str(prn)), None)
    if not student:
        return "Student not found", 404
    return render_template("student_profile.html", student=student)


# ------------------ STUDENT PROFILE ------------------
@app.route("/student/<int:sr_no>")
def student_profile(sr_no):
    data = fetch_student_data()
    student = next((s for s in data if str(s.get("Sr No")) == str(sr_no)), None)
    if not student:
        return "Student not found", 404
    return render_template("student_profile.html", student=student)


# ------------------ COUNSELING ------------------
@app.route("/schedule/<int:sr_no>", methods=["POST"])
def schedule_counseling(sr_no):
    message = request.form.get("message")
    print(f"Counseling scheduled for student {sr_no}: {message}")
    return redirect(url_for("student_profile", sr_no=sr_no))


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True)
