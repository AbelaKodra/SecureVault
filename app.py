import csv
from flask import Response
from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
from models import db, User, PasswordEntry
from encryption import encrypt_password, decrypt_password
app = Flask(__name__)

app.config["SECRET_KEY"] = "securevault-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "Benutzer existiert bereits"

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            username=username,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
            user.password_hash,
            password
        ):

            session["user_id"] = user.id
            session["username"] = user.username

            return redirect("/dashboard")

        return "Falsche Anmeldedaten"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    passwords = PasswordEntry.query.filter_by(
        user_id=session["user_id"]
    ).all()

    decrypted_passwords = []

    for p in passwords:

        decrypted_passwords.append({
            "id": p.id,
            "title": p.title,
            "website": p.website,
            "username": p.username,
            "password": decrypt_password(
                p.encrypted_password
            )
        })

    return render_template(
        "dashboard.html",
        username=session["username"],
        passwords=decrypted_passwords
    )

@app.route("/search")
def search():

    if "user_id" not in session:
        return redirect("/login")

    query = request.args.get("q", "")

    results = PasswordEntry.query.filter(
        PasswordEntry.title.contains(query),
        PasswordEntry.user_id == session["user_id"]
    ).all()

    decrypted = []

    for p in results:

        decrypted.append({
            "id": p.id,
            "title": p.title,
            "website": p.website,
            "username": p.username,
            "password": decrypt_password(
                p.encrypted_password
            )
        })

    return render_template(
        "dashboard.html",
        username=session["username"],
        passwords=decrypted
    )

@app.route("/add", methods=["POST"])
def add_password():

    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    website = request.form["website"]
    username = request.form["username"]
    password = request.form["password"]

    encrypted = encrypt_password(password)

    entry = PasswordEntry(
        title=title,
        website=website,
        username=username,
        encrypted_password=encrypted,
        user_id=session["user_id"]
    )

    db.session.add(entry)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete_password(id):

    if "user_id" not in session:
        return redirect("/login")

    entry = PasswordEntry.query.get(id)

    if entry:
        db.session.delete(entry)
        db.session.commit()

    return redirect("/dashboard")

@app.route("/export")
def export_csv():

    if "user_id" not in session:
        return redirect("/login")

    passwords = PasswordEntry.query.filter_by(
        user_id=session["user_id"]
    ).all()

    def generate():

        yield "Titel,Website,Username,Passwort\n"

        for p in passwords:

            yield (
                f"{p.title},"
                f"{p.website},"
                f"{p.username},"
                f"{decrypt_password(p.encrypted_password)}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=passwords.csv"
        }
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
