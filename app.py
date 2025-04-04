from flask import Flask, render_template, request, redirect, session, url_for
import json
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production
DATA_FILE = "data.json"


# Load JSON data
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "items": []}


# Save JSON data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Register User
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        data = load_data()

        # Check if user exists
        if any(user["username"] == username for user in data["users"]):
            return "User already exists!"

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        data["users"].append({"username": username, "password": hashed_pw})

        save_data(data)
        return redirect("/login")

    return render_template("register.html")


# Login User
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        data = load_data()
        user = next((u for u in data["users"] if u["username"] == username), None)

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session["user"] = username
            return redirect("/")
        return "Invalid username or password"

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# Home Page (CRUD Items)
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    return render_template("index.html", items=data["items"], user=session["user"])


# Create Item
@app.route("/add", methods=["POST"])
def add_item():
    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]
    content = request.form["content"]

    data = load_data()
    new_item = {"id": len(data["items"]) + 1, "title": title, "content": content}
    data["items"].append(new_item)

    save_data(data)
    return redirect("/")


# Update Item
@app.route("/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    for item in data["items"]:
        if item["id"] == item_id:
            item["title"] = request.form["title"]
            item["content"] = request.form["content"]
            break

    save_data(data)
    return redirect("/")


# Delete Item
@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    data["items"] = [item for item in data["items"] if item["id"] != item_id]

    save_data(data)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
