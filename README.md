# 🎬 Movie Counter

A modern glassmorphism-style desktop app to track your movies and web series, built with Python + CustomTkinter + Firebase.

---

## ✅ Setup in 4 Steps

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Create your Firebase project

1. Go to [https://console.firebase.google.com](https://console.firebase.google.com)
2. Click **"Add project"** → give it a name → create it
3. Enable **Authentication**:
   - Go to **Authentication** → **Sign-in method** → Enable **Email/Password**
4. Enable **Firestore**:
   - Go to **Firestore Database** → **Create database** → Start in **Test mode**

### Step 3 — Get your Firebase credentials

#### Web API Key (for login/register)
- Firebase Console → ⚙️ Project Settings → **General** tab
- Copy **"Web API Key"**

#### Service Account JSON (for Firestore)
- Firebase Console → ⚙️ Project Settings → **Service accounts** tab
- Click **"Generate new private key"** → download the JSON file
- Rename it to `firebase_config.json` and place it in this folder

### Step 4 — Configure `.env`

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Then open `.env` and fill in your values:

```
FIREBASE_API_KEY=AIza...your_key_here
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456:web:abc123
FIREBASE_SERVICE_ACCOUNT=firebase_config.json
```

---

## ▶️ Run the app

```bash
python main.py
```

---

## 🗂 Project Structure

```
movies counter/
├── main.py                  # Entry point
├── firebase_service.py      # Firebase Auth + Firestore logic
├── requirements.txt
├── .env                     # Your credentials (never share this)
├── .env.example             # Template
├── firebase_config.json     # Service account key (never share this)
└── screens/
    ├── login_screen.py      # Login / Register UI
    └── dashboard_screen.py  # Dashboard, stats, movies, web series
```

---

## 🔒 Security Note

Never commit `.env` or `firebase_config.json` to Git. Add them to `.gitignore`:

```
.env
firebase_config.json
```

---

## 🛠 Troubleshooting

| Error | Fix |
|---|---|
| `INVALID_API_KEY` | Check `FIREBASE_API_KEY` in `.env` |
| `FileNotFoundError: firebase_config.json` | Make sure you downloaded and placed the service account JSON |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Login fails with valid credentials | Make sure Email/Password auth is enabled in Firebase Console |
