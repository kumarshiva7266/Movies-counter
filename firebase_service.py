"""
firebase_service.py
Handles all Firebase Authentication and Firestore operations.
"""

import os
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
from dotenv import load_dotenv

load_dotenv()

# ── Pyrebase (Authentication via REST) ────────────────────────────────────────
_pyrebase_config = {
    "apiKey":            os.getenv("FIREBASE_API_KEY", ""),
    "authDomain":        os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "projectId":         os.getenv("FIREBASE_PROJECT_ID", ""),
    "storageBucket":     os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId":             os.getenv("FIREBASE_APP_ID", ""),
    "databaseURL":       "",   # Required field by pyrebase even if unused
}

_firebase = pyrebase.initialize_app(_pyrebase_config)
_auth     = _firebase.auth()

# ── Firebase Admin (Firestore) ─────────────────────────────────────────────────
_db = None

def _get_db():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            svc = os.getenv("FIREBASE_SERVICE_ACCOUNT", "firebase_config.json")
            cred = credentials.Certificate(svc)
            firebase_admin.initialize_app(cred)
        _db = admin_firestore.client()
    return _db


# ── Auth helpers ───────────────────────────────────────────────────────────────

def login(email: str, password: str) -> dict:
    """Sign in with email/password. Returns pyrebase user dict."""
    return _auth.sign_in_with_email_and_password(email, password)


def register(email: str, password: str, display_name: str) -> dict:
    """Create a new user account, then set their display name."""
    user = _auth.create_user_with_email_and_password(email, password)
    _auth.update_profile(user["idToken"], display_name=display_name)
    # Store display name in Firestore profile
    db = _get_db()
    db.collection("users").document(user["localId"]).set(
        {"email": email, "displayName": display_name}, merge=True
    )
    return user


def get_display_name(uid: str) -> str:
    """Fetch the display name stored in Firestore."""
    db = _get_db()
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict().get("displayName", "User")
    return "User"


def update_display_name(uid: str, name: str) -> None:
    db = _get_db()
    db.collection("users").document(uid).set({"displayName": name}, merge=True)


# ── Movies ─────────────────────────────────────────────────────────────────────

def add_movie(uid: str, name: str) -> str:
    db = _get_db()
    _, ref = db.collection("users").document(uid).collection("movies").add(
        {"name": name.strip(), "addedAt": admin_firestore.SERVER_TIMESTAMP}
    )
    return ref.id


def get_movies(uid: str) -> list[dict]:
    db = _get_db()
    docs = (
        db.collection("users")
        .document(uid)
        .collection("movies")
        .order_by("addedAt")
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def delete_movie(uid: str, movie_id: str) -> None:
    db = _get_db()
    db.collection("users").document(uid).collection("movies").document(movie_id).delete()


# ── Web Series ─────────────────────────────────────────────────────────────────

def add_webseries(uid: str, name: str) -> str:
    db = _get_db()
    _, ref = db.collection("users").document(uid).collection("webseries").add(
        {"name": name.strip(), "addedAt": admin_firestore.SERVER_TIMESTAMP}
    )
    return ref.id


def get_webseries(uid: str) -> list[dict]:
    db = _get_db()
    docs = (
        db.collection("users")
        .document(uid)
        .collection("webseries")
        .order_by("addedAt")
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def delete_webseries(uid: str, series_id: str) -> None:
    db = _get_db()
    db.collection("users").document(uid).collection("webseries").document(series_id).delete()
