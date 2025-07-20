from flask import Flask, render_template, request, redirect, flash
from utils import add_user_to_ldap

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Needed for flash messages

@app.route("/", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        login = request.form["login"]
        password = request.form["password"]

        try:
            add_user_to_ldap(login, name, email, password)
            flash(f"User {login} added successfully!", "success")
        except Exception as e:
            flash(f"Error adding user: {str(e)}", "danger")

        return redirect("/")

    return render_template("add_user.html")


if __name__ == "__main__":
    app.run(debug=True, port=51515)
