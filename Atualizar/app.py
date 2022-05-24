from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def current_user(user_id):      # Always drops the person who is logged in
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    # user.profile

    def __str__(self):
        return self.name


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Unicode(124), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __str__(self):
        return self.name


@app.route("/")
def index():
    users = User.query.all()  # Select * from users in DB
    return render_template("PaginaInicial.html", users=users)


@app.route("/user/<int:id>")
def unique(id):
    user = User.query.get(id)
    return render_template("user.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User()
        user.name = request.form["name"]
        user.email = request.form["email"]
        for i in db.session():
            if i in User.query.filter_by(email=request.form["email"]).first():
                print("Esse usuario já existe")
            else:
                user.password = generate_password_hash(request.form["password"])
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("index"))
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        errors = {}

        if not user:
            flash("Credenciais Inválidas")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("Credenciais Inválidas")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/user/delete/<int:id>")
def delete(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect("/")

@app.route("/painel")
def painel():
    users = User.query.all()
    return render_template("painel.html", users=users)

@app.route("/profissao")
def profissao   ():
    users = User.query.all()
    return render_template("profissao.html", users=users)

@app.route("/reset")
def reset():
    return render_template("reset.html")



if __name__ == "__main__":
    app.run(debug=True)
