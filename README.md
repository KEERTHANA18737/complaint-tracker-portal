# ComplaintTracker 🛡️

> A production-ready Government Complaint & Issue Tracking System built with Python 3.13, Django 5, Bootstrap 5, and Chart.js.

---

## 📋 Features

- **Role-Based Access Control** — Citizen, Officer, Admin
- **Complaint Lifecycle** — Submit → Assign → In Progress → Resolve → Close
- **Full Audit Trail** — Immutable ComplaintHistory on every status change
- **In-App Notifications** — Citizens notified on status change
- **Rich Dashboard** — Chart.js doughnut, bar, and pie charts
- **Search & Filter** — by title, location, status, priority, category, officer
- **Image Uploads** — with client & server-side validation (5 MB, jpg/png/gif/webp)
- **Password Reset** — Django built-in email flow
- **Customised Django Admin** — inline history, search, filters
- **Responsive UI** — dark navy government theme, Bootstrap 5

---

## 🚀 Quick Start

### 1. Clone / unzip

```bash
cd ComplaintTracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6. Load sample data (optional)

```bash
python manage.py loaddata fixtures/initial_data.json
```

> **Note:** The fixture users have unusable passwords (the hashed value is a placeholder).
> After loading, reset passwords via the admin panel or use `createsuperuser`.

### 7. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🔑 Default URLs

| URL | Description |
|-----|-------------|
| `/` | Redirects to Dashboard |
| `/accounts/login/` | Sign in |
| `/accounts/register/` | Citizen registration |
| `/accounts/profile/` | Edit profile |
| `/dashboard/` | Role-aware dashboard |
| `/complaints/` | Complaint list |
| `/complaints/new/` | Submit a complaint |
| `/complaints/<id>/` | Complaint detail + timeline |
| `/complaints/<id>/edit/` | Edit complaint |
| `/complaints/<id>/delete/` | Delete complaint |
| `/complaints/notifications/` | In-app notifications |
| `/admin/` | Django admin panel |

---

## 👥 Roles

| Role | Can Submit | Can Edit Own | Can Change Status | Can Assign | Can Delete Any |
|------|:---:|:---:|:---:|:---:|:---:|
| Citizen | ✅ | ✅ | ❌ | ❌ | ❌ |
| Officer | ❌ | ✅ | ✅ | ✅ | ❌ |
| Admin   | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 📁 Project Structure

```
ComplaintTracker/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                  # created after migrate
├── fixtures/
│   └── initial_data.json       # 5 categories, 10 users, 20 complaints
│
├── ComplaintTracker/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   # Custom User + Auth
│   ├── models.py               # User (role, phone, address, avatar)
│   ├── views.py                # Register, Login, Logout, Profile
│   ├── forms.py                # RegistrationForm, LoginForm, ProfileForm
│   ├── urls.py
│   ├── admin.py
│   └── context_processors.py  # unread_notification_count
│
├── complaints/                 # Core complaint domain
│   ├── models.py               # Category, Complaint, ComplaintHistory, Notification
│   ├── views.py                # CRUD CBVs + status update + notifications
│   ├── forms.py                # ComplaintForm, StatusUpdateForm, SearchForm
│   ├── urls.py
│   ├── admin.py                # Inline history, search, filters
│   └── signals.py              # Auto-creates history + notifications on save
│
├── dashboard/                  # Stats & charts
│   ├── views.py                # index() with Chart.js data
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── includes/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   └── footer.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── password_reset*.html
│   ├── complaints/
│   │   ├── complaint_list.html
│   │   ├── complaint_detail.html
│   │   ├── complaint_form.html
│   │   ├── complaint_confirm_delete.html
│   │   └── notifications.html
│   ├── dashboard/
│   │   └── dashboard.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/
│   │   └── style.css           # Dark navy government theme
│   └── js/
│       ├── main.js             # Sidebar, alerts, CSRF, duplicate-submit
│       └── dashboard.js        # Chart.js doughnut/bar/pie init
│
└── media/
    └── complaint_images/       # Uploaded complaint images (auto-created)
```

---

## ⚙️ Configuration

Key settings in `ComplaintTracker/settings.py`:

```python
MAX_UPLOAD_SIZE = 5 * 1024 * 1024          # 5 MB max image size
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # swap for SMTP in prod
```

For production, also set:
```python
DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = ['yourdomain.com']
```

---

## 📸 Screenshots

> _[ Dashboard — Statistics cards + Chart.js charts ]_

> _[ Complaint List — Searchable cards with status/priority badges ]_

> _[ Complaint Detail — Timeline history + status update panel ]_

> _[ Submit Complaint — Form with live image preview ]_

---

## 🧪 Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/initial_data.json

# Collect static files (production)
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.0.6 | Web framework |
| Pillow | 10.3.0 | Image upload support |
| django-crispy-forms | 2.1 | Bootstrap form rendering |
| crispy-bootstrap5 | 2024.2 | Crispy Bootstrap 5 template pack |

CDN (loaded at runtime, no install needed):
- Bootstrap 5.3.3
- Bootstrap Icons 1.11.3
- Chart.js 4.4.3
