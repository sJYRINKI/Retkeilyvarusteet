import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
import db
import config
import packs
import re
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_packs = packs.get_packs()
    return render_template("index.html", packs=all_packs)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    packs = users.get_packs(user_id)
    return render_template("show_user.html", user=user, packs=packs)

@app.route("/find_pack")
def find_pack():
    query = request.args.get("query")
    if query:
        results = packs.find_packs(query)
    else:
        query = ""
        results = []
    return render_template("find_pack.html", query=query, results=results)

@app.route("/pack/<int:pack_id>")
def show_pack(pack_id):
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    classes = packs.get_classes(pack_id)
    comments = packs.get_comments(pack_id)
    images = packs.get_images(pack_id)
    return render_template("show_pack.html", pack=pack, classes=classes, comments=comments, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = packs.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/remove_comment/<int:comment_id>", methods=["POST"])
def remove_comment(comment_id):
    require_login()

    comment = packs.check_comment(comment_id)
    pack_id = request.form["pack_id"]
    if comment["user_id"] != session["user_id"]:
        abort(403)
    if not comment:
        abort(404)

    packs.remove_comment(comment_id)
    return redirect("/pack/" + str(pack_id))

@app.route("/new_pack")
def new_pack():
    require_login()
    classes = (packs.get_all_classes())
    return render_template("new_pack.html", classes=classes)

@app.route("/create_pack", methods=["POST"])
def create_pack():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,3}$", price):
        abort(403)
    user_id = session["user_id"]

    all_classes = packs.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    packs.add_pack(title, description, price,  user_id, classes)

    return redirect("/")

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()

    comment = request.form["comment"]
    if not comment or len(comment) > 200:
        abort(403)
    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    user_id = session["user_id"]

    all_classes = packs.get_all_classes()

    packs.add_comment(pack_id, user_id, comment)

    return redirect("/pack/" + str(pack_id))

@app.route("/edit_pack/<int:pack_id>")
def edit_pack(pack_id):
    require_login()
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    all_classes = packs.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in packs.get_classes(pack_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_pack.html", pack=pack, classes=classes, all_classes=all_classes)

@app.route("/images/<int:pack_id>")
def edit_images(pack_id):
    require_login()
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    images = packs.get_images(pack_id)

    return render_template("images.html", pack=pack, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()

    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    packs.add_image(pack_id, image)
    return redirect("/images/" + str(pack_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()

    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    if "remove" in request.form:
        for image_id in request.form.getlist("image_id"):
            packs.remove_image(pack_id, image_id)
            return redirect("/images/" + str(pack_id))
    else:
        return redirect("/pack/" + str(pack_id))

@app.route("/update_pack", methods=["POST"])
def update_pack():
    require_login()
    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,3}$", price):
        abort(403)

    if "update" in request.form:
        all_classes = packs.get_all_classes()

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                classes.append((class_title, class_value))

        packs.update_pack(pack_id, title, description, price, classes)
        return redirect("/pack/" + str(pack_id))

    else:
        return redirect("/pack/" + str(pack_id))

@app.route("/remove_pack/<int:pack_id>", methods=["GET", "POST"])
def remove_pack(pack_id):
    require_login()
    pack = packs.get_pack(pack_id)
    if not pack:
        abort(404)
    if pack["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_pack.html", pack=pack)

    if request.method == "POST":
        if "remove" in request.form:
            packs.remove_pack(pack_id)
            return redirect("/")
        else:
            return redirect("/pack/" + str(pack_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
