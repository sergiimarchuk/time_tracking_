import os
import sys

from flask import Flask, render_template, request, redirect, flash

from users_utils import add_user_to_ldap, insert_user_to_db
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route("/", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        sname = request.form["sname"]
        email = request.form["email"]
        login = request.form["login"]
        password = request.form["password"]
        einfo = request.form["einfo"]

        try:
            # Simulate generating or getting LDAP UUID (could also be from LDAP response)
            ldap_entry_uuid = str(uuid.uuid4())

            # Add to LDAP
            add_user_to_ldap(login, name, email, password)

            # Insert to PostgreSQL
            insert_user_to_db(name, sname, email, einfo, ldap_entry_uuid)

            flash(f"User {login} added successfully!", "success")
        except Exception as e:
            flash(f"Error adding user: {str(e)}", "danger")

        return redirect("/")

    return render_template("add_user.html")



if __name__ == "__main__":
    app.run(debug=True, port=51515)
