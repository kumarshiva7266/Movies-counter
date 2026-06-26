// src/firebaseService.js
// All Firestore + Auth operations — mirrors firebase_service.py
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile,
  signOut,
} from 'firebase/auth'
import {
  doc, setDoc, getDoc, collection,
  addDoc, getDocs, deleteDoc,
  serverTimestamp, orderBy, query,
} from 'firebase/firestore'
import { auth, db } from './firebase'

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(email, password) {
  const cred = await signInWithEmailAndPassword(auth, email, password)
  return cred.user
}

export async function register(email, password, displayName) {
  const cred = await createUserWithEmailAndPassword(auth, email, password)
  const user = cred.user
  await updateProfile(user, { displayName })
  await setDoc(doc(db, 'users', user.uid), { email, displayName }, { merge: true })
  return user
}

export async function logout() {
  await signOut(auth)
}

// ── Profile ───────────────────────────────────────────────────────────────────

export async function getDisplayName(uid) {
  const snap = await getDoc(doc(db, 'users', uid))
  return snap.exists() ? snap.data().displayName || 'User' : 'User'
}

// ── Movies ────────────────────────────────────────────────────────────────────

export async function addMovie(uid, name) {
  const ref = await addDoc(
    collection(db, 'users', uid, 'movies'),
    { name: name.trim(), addedAt: serverTimestamp() }
  )
  return ref.id
}

export async function getMovies(uid) {
  const q    = query(collection(db, 'users', uid, 'movies'), orderBy('addedAt'))
  const snap = await getDocs(q)
  return snap.docs.map(d => ({ id: d.id, ...d.data() }))
}

export async function deleteMovie(uid, movieId) {
  await deleteDoc(doc(db, 'users', uid, 'movies', movieId))
}

// ── Watchlist ─────────────────────────────────────────────────────────────────

export async function addWatchlist(uid, name) {
  const ref = await addDoc(
    collection(db, 'users', uid, 'watchlist'),
    { name: name.trim(), addedAt: serverTimestamp() }
  )
  return ref.id
}

export async function getWatchlist(uid) {
  const q    = query(collection(db, 'users', uid, 'watchlist'), orderBy('addedAt'))
  const snap = await getDocs(q)
  return snap.docs.map(d => ({ id: d.id, ...d.data() }))
}

export async function deleteWatchlist(uid, itemId) {
  await deleteDoc(doc(db, 'users', uid, 'watchlist', itemId))
}

export async function addWebseries(uid, name) {
  const ref = await addDoc(
    collection(db, 'users', uid, 'webseries'),
    { name: name.trim(), addedAt: serverTimestamp() }
  )
  return ref.id
}

export async function getWebseries(uid) {
  const q    = query(collection(db, 'users', uid, 'webseries'), orderBy('addedAt'))
  const snap = await getDocs(q)
  return snap.docs.map(d => ({ id: d.id, ...d.data() }))
}

export async function deleteWebseries(uid, seriesId) {
  await deleteDoc(doc(db, 'users', uid, 'webseries', seriesId))
}
