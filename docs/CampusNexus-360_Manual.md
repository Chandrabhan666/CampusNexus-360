# CampusNexus-360
## Complete Project Manual (Developer + User Guide)

**Version:** 1.0  
**Project type:** Hybrid Academic Portal (Cloud + Localhost)  
**Backend:** Flask + SQLAlchemy  
**Database:** SQLite (localhost) OR Postgres (Supabase)  
**Hosting (cloud):** Render  

---

## 1. What This Project Is

CampusNexus-360 is a role-based academic portal that supports:

- Attendance tracking (manual + face recognition)
- Student and parent dashboards
- Teacher/admin dashboard
- Notes and syllabus PDF uploads
- Announcements
- Hybrid usage:
  - **Localhost (offline-capable):** works fully with SQLite and can use **server-side webcam** (OpenCV)
  - **Cloud (online):** works via Render + Supabase, and can use **browser webcam** (camera runs in the teacher's browser)

---

## 2. Roles and What Each Role Can Do

### 2.1 Student
- Login using Student ID + password
- View:
  - Dashboard summary
  - Attendance history
  - Routine
  - Activity
  - Notes PDFs
  - Announcements
  - Curriculum (syllabus)

### 2.2 Parent
- Login using parent username + password (by default: same as student ID/password)
- View linked student attendance/dashboard

### 2.3 Teacher
- Login
- Dashboard metrics:
  - Total students
  - Total attendance records
  - Today present / absent counts
- Mark attendance:
  - Manual (enter Student ID)
  - Face attendance using **browser camera**
  - Local webcam mode (OpenCV server-side camera; localhost only)
- Upload:
  - Syllabus PDFs
  - Notes PDFs
- Add announcements

### 2.4 Admin
- Same capabilities as teacher (admin opens teacher dashboard)

---

## 3. Tech Stack and Main Components

### 3.1 Backend
- Flask web server: `app.py`
- Jinja templates in `templates/`
- CSS in `static/css/`

### 3.2 Database Layer
- SQLAlchemy models in `app.py`:
  - `Student`
  - `User`
  - `Attendance`
  - `Announcement`
  - `Resource`

### 3.3 Face Recognition
- Capture face dataset (local): `capture_faces.py`
- Train model (local): `train_model.py`
- Model file: `model/face_model.xml`
- Recognition:
  - Cloud/browser mode: teacher browser sends a captured image to backend for recognition
  - Local webcam mode: backend opens webcam using `cv2.VideoCapture(0)` (localhost only)

---

## 4. Project Folder Structure (What Each File Does)

Top-level important files:

- `app.py`
  - Flask routes, auth logic, SQLAlchemy models, attendance logic, uploads, notifications, face verification
- `requirements.txt`
  - Python dependencies
- `auth_users.json`
  - Demo credentials (admin/teacher/student/parent)
- `student_data.json`
  - Student directory + contact details (email/phone)
- `announcements.json`
  - Seed announcement data (first-time DB seed)
- `syllabus.json`
  - Syllabus mapping for seed (local files)
- `templates/`
  - HTML pages for all dashboards and forms
- `static/css/student.css`, `static/css/teacher.css`
  - UI styling
- `dataset/`
  - Captured face images for training (local only)
- `model/face_model.xml`
  - Trained LBPH model used for recognition
- `uploads/`
  - Syllabus files (local fallback)
- `notes/`
  - Notes PDFs (local fallback)
- `render.yaml`
  - Render deployment blueprint (optional)
- `CLOUD_SETUP.md`, `WINDOWS_SETUP.md`
  - Additional quick guides

---

## 5. How the Backend Works (Code Walkthrough)

### 5.1 Database configuration (app startup)

In `app.py`, the database URL is chosen from an environment variable:

```python
raw_db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'attendance.db')}")
```

- If `DATABASE_URL` is not set, it uses SQLite: `attendance.db` (localhost-friendly)
- If `DATABASE_URL` is set (cloud), it uses Postgres (Supabase)
- The app automatically appends `?sslmode=require` if Postgres URL has no sslmode

### 5.2 Lazy DB initialization

The app creates tables and seeds initial data via `init_db()` and `seed_data()`.

- Seed uses:
  - `student_data.json` to create `Student` rows
  - `auth_users.json` to create `User` rows
  - `announcements.json` to seed announcements
  - `syllabus.json` and local files to seed resources (if present)

Important:
- If you edit `student_data.json` or `auth_users.json`, restart the server so seeding can run again.

### 5.3 Authentication (login)

Routes:
- `/login/student`
- `/login/parent`
- `/login/teacher`
- `/login/admin`

Each route:
- Reads the user from the `users` table
- On success: sets session keys like `role`, `student`, `teacher`, etc.
- On failure: shows an error message

### 5.4 Attendance marking

Manual attendance:
- Teacher/Admin dashboard uses `/mark-attendance-manual`

Face attendance (browser webcam):
- UI page: `/teacher/face-attendance`
- Verification endpoint: `/teacher/face-attendance/verify` (POST JSON with `image`)

Local webcam mode (server-side camera):
- Route: `/mark-attendance`
- Requires the server machine to have a webcam (works on localhost)

### 5.5 Notes/Syllabus uploads

Uploads create a `Resource` row in DB.

Storage options:
- Local (localhost): saves PDF in `uploads/` or `notes/`
- Cloud (Render + Supabase): uploads to Supabase Storage if configured

---

## 6. User Manual (How to Use the App)

### 6.1 Login portal

Open:
- Local: `http://127.0.0.1:5000/login`
- Cloud: your Render URL + `/login`

Choose role:
- Student Login
- Parent Login
- Teacher Login
- Admin Login

### 6.2 Demo credentials (from auth_users.json)

Admin:
- Username: `admin`
- Password: `0010`

Teacher:
- Username: `teacher1`
- Password: `teach123`

Student example:
- `12312037` / `2037`

Parent example (same as student by default):
- `12312037` / `2037`

---

## 7. Localhost Setup (Mac)

### 7.1 Open the project folder

Example path (yours may differ):

```bash
cd /Users/chandrabhanpatel/Downloads/SmartAttendance
```

### 7.2 Create and activate venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 7.3 Install dependencies

```bash
pip install -r requirements.txt
```

### 7.4 Run the server (localhost)

```bash
python3 app.py
```

Open:
- `http://127.0.0.1:5000/login`

### 7.5 Offline DB mode (SQLite)

To use SQLite offline mode, ensure `DATABASE_URL` is NOT set in your terminal:

```bash
unset DATABASE_URL
python3 app.py
```

---

## 8. Localhost Setup (Windows)

```bat
cd C:\path\to\CampusNexus-360
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:
- `http://127.0.0.1:5000/login`

---

## 9. Add a New Student (Correct Way)

This project uses two places:

1. `student_data.json` (details + contact)
2. `auth_users.json` (credentials)

### 9.1 Edit student_data.json

File:
- `student_data.json`

Add a new student (IDs should be digits only, recommended):

```json
"12319999": {
  "name": "New Student",
  "branch": "CSE",
  "year": "3rd Year",
  "email": "newstudent@gmail.com",
  "phone": "9000000000"
}
```

### 9.2 Edit auth_users.json

File:
- `auth_users.json`

Add student login:
- Username = Student ID
- Password = last 4 digits

```json
"students": {
  "12319999": { "password": "9999", "name": "New Student" }
}
```

Add parent login (same id/password by your current design):

```json
"parents": {
  "12319999": { "password": "9999", "name": "Parent of New Student", "students": ["12319999"] }
}
```

### 9.3 Restart the app

Stop with `Ctrl + C`, then:

```bash
python3 app.py
```

Now the student/parent can login.

---

## 10. Face Attendance (Training + Usage)

### 10.1 Important rule about Student ID

Your `train_model.py` converts folder names to integers:

```python
labels.append(int(student_id))
```

So Student IDs used for face training must be **numeric digits only** (example: `12312037`).

### 10.2 Capture face images (local webcam required)

Run:

```bash
python3 capture_faces.py
```

It will ask:
- `Enter Student ID:`

It captures ~30 face images and saves them in:
- `dataset/<student_id>/`

Stop condition:
- ESC key OR 30 images captured

### 10.3 Train face model

Run:

```bash
python3 train_model.py
```

This generates:
- `model/face_model.xml`

### 10.4 Use face attendance (two modes)

#### Mode A: Browser webcam (works on localhost AND cloud)
- Login as teacher/admin
- Go: Teacher Dashboard → **Face Attendance (Online/Offline)**
- Click **Start Camera**
- Click **Capture & Mark**

How it works:
- Browser captures JPEG frames and sends them to:
  - `POST /teacher/face-attendance/verify`
- Server recognizes face using `model/face_model.xml`

#### Mode B: Local webcam mode (localhost only)
- Teacher Dashboard → **Local Webcam Mode**
- This runs `cv2.VideoCapture(0)` on the server machine

NOTE:
- Cloud servers cannot access your laptop webcam.
- So Local Webcam Mode is for localhost usage only.

---

## 11. Cloud Setup (Render + Supabase)

### 11.1 Why Supabase is used
- Postgres DB (central database)
- Storage bucket for notes/syllabus PDFs (optional but recommended for cloud)

### 11.2 Required environment variables (Render)

Set these in Render → Environment:

- `SECRET_KEY`
  - Any strong random string

- `DATABASE_URL`
  - Use Supabase **Session Pooler** connection string
  - Must include `sslmode=require`
  - Example:
    ```text
    postgresql://postgres.<projectRef>:<PASSWORD>@aws-...pooler.supabase.com:5432/postgres?sslmode=require
    ```

- `SUPABASE_URL`
  - Example:
    ```text
    https://<projectRef>.supabase.co
    ```

- `SUPABASE_SERVICE_ROLE_KEY`
  - From Supabase Project Settings → API Keys
  - Keep this secret (server-side only)

- `SUPABASE_STORAGE_BUCKET`
  - Example: `smartattendance` (or your chosen bucket name)

### 11.3 Render build and start commands

Build:
```bash
pip install -r requirements.txt
```

Start (recommended for free plan stability):
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
```

---

## 12. Common Problems and Fixes (Fast Troubleshooting)

### 12.1 Render shows “Application loading…”
- Render free tier sleeps after idle
- Wait 30-60 seconds, then refresh

### 12.2 “Server busy. Please try again…”
- This message usually means a DB query failed
- Check Render logs for DB connection errors:
  - wrong password
  - wrong pooler host
  - missing env vars

### 12.3 Internal Server Error on localhost
- Most common:
  - Missing dependency install
  - Wrong python command (`python` vs `python3`)
  - OpenCV package mismatch

Fix:
```bash
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### 12.4 Face not recognized / lighting problems
- Ensure you trained model with correct student
- Move closer, face camera directly
- Improve lighting
- Browser mode uses burst capture + lighting fallback, but extreme darkness still fails

---

## 13. Security Notes (Important)

- Do NOT put secrets in GitHub:
  - `DATABASE_URL`
  - Supabase keys
  - SMTP passwords
  - Twilio tokens

- Use Render environment variables instead.

---

## 14. Route Reference (Main Pages)

- Portal: `/login`
- Student login: `/login/student`
- Parent login: `/login/parent`
- Teacher login: `/login/teacher`
- Admin login: `/login/admin`

- Student dashboard: `/student/dashboard`
- Parent dashboard: `/parent/dashboard`

- Teacher dashboard: `/teacher/dashboard`
- Teacher face attendance: `/teacher/face-attendance`
- Face verify endpoint: `/teacher/face-attendance/verify`
- Local webcam attendance: `/mark-attendance`
- Manual attendance: `/mark-attendance-manual`

- Upload syllabus: `/upload-syllabus`
- Upload notes: `/teacher/upload-notes`
- Add announcement: `/teacher/add-announcement`

- Health check: `/healthz`

---

## 15. Appendix: “How This Was Built” (High-Level Steps)

1. Designed role-based portal pages (student/parent/teacher/admin).
2. Built database models using SQLAlchemy.
3. Implemented login sessions per role.
4. Implemented attendance:
   - manual marking
   - face recognition using OpenCV + LBPH model
5. Implemented uploads:
   - local storage fallback
   - Supabase storage support for cloud
6. Deployed backend to Render and database to Supabase.

