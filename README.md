# 🎵 Streamify - Video & Music Streaming Platform

A full-featured Django streaming platform similar to Spotify and Netflix.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Create a MySQL database:
```sql
CREATE DATABASE streamify_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Copy and edit the environment file:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

### 4. Run Setup
```bash
python setup.py
```
This will run migrations, load initial data, and prompt you to create an admin user.

### 5. Start the Server
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 📁 Project Structure

```
streamify/
├── apps/
│   ├── users/          # Authentication, profiles (Custom User model)
│   ├── content/        # Music/video content, likes, comments
│   ├── subscriptions/  # Plans and subscription management
│   ├── payments/       # Payment processing (Stripe-ready)
│   ├── playlists/      # Playlists and watchlists
│   ├── search/         # Search and filtering
│   └── analytics/      # Creator and admin analytics
├── templates/          # HTML templates (Bootstrap 5, dark theme)
├── static/             # CSS, JS, images
├── streamify_project/  # Django project settings
├── requirements.txt
├── manage.py
└── setup.py
```

---

## 🔑 Key Features

| Module | Features |
|--------|----------|
| **Users** | Register/Login/Logout, Profiles, Role-based (User/Creator/Admin) |
| **Content** | Upload music & videos, stream, like, comment, share |
| **Subscriptions** | Free & premium plans, subscription management |
| **Payments** | Stripe-ready checkout, payment history |
| **Playlists** | Create playlists, watchlists, add/remove content |
| **Search** | Search by title, artist, genre, filter by type |
| **Analytics** | Creator dashboard, admin platform stats |
| **REST API** | JWT-authenticated API endpoints |

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **User** | Browse, stream free content, create playlists, subscribe |
| **Creator** | All user permissions + upload content, view analytics |
| **Admin** | Full access, admin panel, platform analytics |

---

## 🔌 REST API

Base URL: `/api/v1/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/register/` | POST | Register new user |
| `/api/v1/users/login/` | POST | Get JWT tokens |
| `/api/v1/users/token/refresh/` | POST | Refresh access token |
| `/api/v1/users/profile/` | GET/PUT | User profile |
| `/api/v1/content/` | GET | List content |
| `/api/v1/content/{id}/` | GET | Content detail |
| `/api/v1/subscriptions/plans/` | GET | List plans |
| `/api/v1/subscriptions/my/` | GET | My subscriptions |

---

## 💳 Stripe Integration

1. Get your keys from [stripe.com](https://stripe.com)
2. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

---

## 🛠 Admin Panel

Visit `/admin/` to manage:
- Users and roles
- Content moderation (publish/unpublish)
- Subscription plans
- Payments
- Genres

---

## 📦 Tech Stack

- **Backend**: Django 4.2 (Python)
- **Database**: MySQL
- **Frontend**: Bootstrap 5, vanilla JS
- **Auth**: Django auth + JWT (DRF)
- **Payments**: Stripe (configurable)
- **Storage**: Local filesystem (extendable to S3)

---

## 🔮 Future Enhancements

- Mobile app (React Native / Flutter)
- AI-based recommendation engine
- Live streaming support
- Offline downloads
- Multi-language support
