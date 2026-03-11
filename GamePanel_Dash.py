import os
import json
from pathlib import Path
import threading
import webbrowser
from flask import Flask, render_template_string, request, redirect, url_for, flash, session

# --- Pfade ---
documents_path = Path.home() / "Documents"
core_path = documents_path / "GamePanel" / "core"
users_path = core_path / "users"
users_file = users_path / "users.json"

# Legacy-Popup, falls core fehlt
if not core_path.exists():
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Windows Legacy Error",
        "You need to install the core app via the CLI first."
    )
    exit()

users_path.mkdir(parents=True, exist_ok=True)

# --- Benutzer laden/speichern ---
def load_users():
    if users_file.exists():
        with open(users_file, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

# Standard-Admin automatisch einfügen
users = load_users()
if "admin" not in users:
    users["admin"] = {"password": "0"}
    save_users(users)

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- HTML Templates ---
login_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>GamePanel Login</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
body { margin:0; font-family:'Roboto', sans-serif; background: linear-gradient(135deg,#1e1e2f,#2a2a3f); display:flex; justify-content:center; align-items:center; height:100vh; }
.container { background:#2a2a3f; padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.5); width:350px; text-align:center; animation:fadeIn 1s ease; }
h1 { color:#fff; margin-bottom:10px; }
p { color:#aaa; margin-bottom:30px; }
input { width:80%; padding:12px; margin:10px 0; border:none; border-radius:10px; outline:none; }
button { width:85%; padding:12px; margin-top:20px; border:none; border-radius:10px; background:#00aaff; color:#fff; font-weight:bold; cursor:pointer; transition:0.3s; }
button:hover { background:#0088cc; transform:scale(1.05); }
.flash { color:#ff5555; margin-bottom:10px; }
@keyframes fadeIn { from {opacity:0; transform:translateY(-20px);} to {opacity:1; transform:translateY(0);} }
</style>
</head>
<body>
<div class="container">
<h1>GamePanel</h1>
<p>Login to continue</p>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <div class="flash">{{ messages[0] }}</div>
  {% endif %}
{% endwith %}
<form method="post" action="/login">
<input type="text" name="username" placeholder="Username" required><br>
<input type="password" name="password" placeholder="Password" required><br>
<button type="submit">Login</button>
</form>
<p>Don't have an account? <a href="/register" style="color:#00aaff;">Register</a></p>
</div>
</body>
</html>
"""

register_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>GamePanel Register</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
body { margin:0; font-family:'Roboto', sans-serif; background: linear-gradient(135deg,#1e1e2f,#2a2a3f); display:flex; justify-content:center; align-items:center; height:100vh; }
.container { background:#2a2a3f; padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.5); width:350px; text-align:center; animation:fadeIn 1s ease; }
h1 { color:#fff; margin-bottom:10px; }
input { width:80%; padding:12px; margin:10px 0; border:none; border-radius:10px; outline:none; }
button { width:85%; padding:12px; margin-top:20px; border:none; border-radius:10px; background:#00aaff; color:#fff; font-weight:bold; cursor:pointer; transition:0.3s; }
button:hover { background:#0088cc; transform:scale(1.05); }
.flash { color:#ff5555; margin-bottom:10px; }
@keyframes fadeIn { from {opacity:0; transform:translateY(-20px);} to {opacity:1; transform:translateY(0);} }
</style>
</head>
<body>
<div class="container">
<h1>Register</h1>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <div class="flash">{{ messages[0] }}</div>
  {% endif %}
{% endwith %}
<form method="post" action="/register">
<input type="text" name="username" placeholder="Username" required><br>
<input type="password" name="password" placeholder="Password" required><br>
<button type="submit">Register</button>
</form>
<p>Already have an account? <a href="/" style="color:#00aaff;">Login</a></p>
</div>
</body>
</html>
"""

servers_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>GamePanel Servers</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
body { margin:0; font-family:'Roboto', sans-serif; background:#f4f4f5; color:#333;}
header { background:#1e1e2f; padding:20px; color:white; display:flex; justify-content:space-between; align-items:center;}
header h1 { margin:0; font-size:24px; }
.container { padding:50px; text-align:center; }
.admin-btn { padding:10px 20px; background:#00aaff; color:white; border:none; border-radius:10px; cursor:pointer; transition:0.3s; }
.admin-btn:hover { background:#0088cc; transform:scale(1.05);}
</style>
</head>
<body>
<header>
<h1>GamePanel</h1>
{% if is_admin %}
<button class="admin-btn">Admin Panel</button>
{% endif %}
</header>
<div class="container">
{% if not is_admin %}
<p style="font-size:24px;">You don't have any servers.</p>
{% else %}
<p style="font-size:24px;">Admin view: No servers yet.</p>
{% endif %}
</div>
</body>
</html>
"""

# --- Flask Routen ---
from flask import session
app.config['SESSION_TYPE'] = 'filesystem'

@app.route("/", methods=["GET"])
def index():
    return render_template_string(login_page)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    users = load_users()
    if username in users and users[username]["password"] == password:
        session['username'] = username
        return redirect("/servers")
    flash("Invalid username or password!")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    global users
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
        if username in users or username.lower() == "admin":
            flash("Username not allowed or already exists!")
            return redirect("/register")
        users[username] = {"password": password}
        save_users(users)
        flash("Account created! You can login now.")
        return redirect("/")
    return render_template_string(register_page)

@app.route("/servers", methods=["GET"])
def servers():
    username = session.get('username')
    if not username:
        return redirect("/")
    is_admin = (username == "admin")
    return render_template_string(servers_page, is_admin=is_admin)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect("/")

# --- Starte Webserver + Browser ---
def start_app():
    threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False), daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    start_app()
    # Halte Script am Leben
    import time
    while True:
        time.sleep(1)
