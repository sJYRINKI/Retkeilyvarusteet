import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
from werkzeug.security import check_password_hash
import config
import packs
import re
import users
import error
import db

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        return error.render_page("Kirjautuminen vaaditaan", "Virhe kirjautumisessa")

@app.route("/")
def index():
    all_packs = packs.get_packs()
    return render_template("index.html", packs=all_packs)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        return error.render_page("Käyttäjää ei löytynyt", "Virhe käyttäjän hakemisessa")
    comments = users.get_comments(user_id)
    packs = users.get_packs(user_id)
    return render_template("show_user.html", user=user, comments=comments, packs=packs)

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
        return error.render_page("Reppua ei löytynyt", "Virhe repun hakemisessa")
    classes = packs.get_classes(pack_id)
    comments = packs.get_comments(pack_id)
    images = packs.get_images(pack_id)
    return render_template("show_pack.html", pack=pack, classes=classes, comments=comments, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = packs.get_image(image_id)
    if not image:
        return error.render_page("Kuvaa ei löytynyt", "Virhe kuvan hakemisessa")

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/remove_comment/<int:comment_id>", methods=["POST"])
def remove_comment(comment_id):
    result = require_login()
    if result:
        return result

    comment = packs.check_comment(comment_id)
    pack_id = request.form["pack_id"]
    if not comment:
        return error.render_page("Kommentia ei löytynyt", "Virhe kommentin poistossa")
    if comment["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeutta poistaa kommenttia", "Virhe kommentin poistossa")

    packs.remove_comment(comment_id)
    return redirect("/pack/" + str(pack_id))

@app.route("/new_pack")
def new_pack():
    result = require_login()
    if result:
        return result
    classes = (packs.get_all_classes())
    return render_template("new_pack.html", classes=classes)

@app.route("/create_pack", methods=["POST"])
def create_pack():
    result = require_login()
    if result:
        return result

    title = request.form["title"]
    if not title or len(title) > 50 or not title.strip():
        return error.render_page("Virheellinen repun nimi", "Virhe repun lisäämisessä")
    description = request.form["description"]
    if not description or len(description) > 1000:
        return error.render_page("Virheellinen repun kuvaus", "Virhe repun lisäämisessä")
    weight = request.form["weight"]
    if not re.search("^[1-9][0-9]{0,2}$", weight):
        return error.render_page("Virheellinen paino repun sisällölle", "Virhe repun lisäämisessä")
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,3}$", price):
        return error.render_page("Virheellinen hinta repun sisällölle", "Virhe repun lisäämisessä")
    user_id = session["user_id"]

    all_classes = packs.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                return error.render_page("Virheellinen luokitus", "Virhe repun lisäämisessä")
            if class_value not in all_classes[class_title]:
                return error.render_page("Virheellinen luokitus", "Virhe repun lisäämisessä")
            classes.append((class_title, class_value))

    packs.add_pack(title, description, weight, price,  user_id, classes)

    pack_id = db.last_insert_id()
    return redirect("/pack/" + str(pack_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    result = require_login()
    if result:
        return result

    comment = request.form["comment"]
    if not comment or len(comment) > 200:
        return error.render_page("Kommentia ei löytynyt tai virhe kommentin pituudessa", "Virhe kommentin lisäämisessä")
    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe kommentin lisäämisessä")
    user_id = session["user_id"]

    all_classes = packs.get_all_classes()

    packs.add_comment(pack_id, user_id, comment)

    return redirect("/pack/" + str(pack_id))

@app.route("/edit_pack/<int:pack_id>")
def edit_pack(pack_id):
    result = require_login()
    if result:
        return result
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe repun muokkauksessa")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeuksia muokata reppua", "Virhe repun muokkauksessa")

    all_classes = packs.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in packs.get_classes(pack_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_pack.html", pack=pack, classes=classes, all_classes=all_classes)

@app.route("/edit_images/<int:pack_id>")
def edit_images(pack_id):
    result = require_login()
    if result:
        return result
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe kuvan muokkauksessa")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeuksia muokata kuvaa", "Virhe kuvan muokkauksessa")

    images = packs.get_images(pack_id)

    return render_template("edit_images.html", pack=pack, images=images)

@app.route("/show_images/<int:pack_id>")
def show_images(pack_id):
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe kuvien näyttämisessä")

    images = packs.get_images(pack_id)

    return render_template("show_images.html", pack=pack, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    result = require_login()
    if result:
        return result

    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe kuvan lisäyksessä")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeutta lisätä kuvaa", "Virhe kuvan lisäyksessä")

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        return error.render_page("Virhe tiedosto tyypissä", "Virhe kuvan lisäyksessä")

    image = file.read()
    if len(image) > 100 * 1024:
        return error.render_page("Virhe kuvan koossa", "Virhe kuvan lisäyksessä")

    packs.add_image(pack_id, image)
    return redirect("/edit_images/" + str(pack_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    result = require_login()
    if result:
        return result

    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Kuvaa ei löytynyt", "Virhe kuvan poistossa")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeutta kuvan poistoon", "Virhe kuvan poistossa")

    if "remove" in request.form:
        for image_id in request.form.getlist("image_id"):
            packs.remove_image(pack_id, image_id)
            return redirect("/edit_images/" + str(pack_id))
    else:
        return redirect("/pack/" + str(pack_id))

@app.route("/update_pack", methods=["POST"])
def update_pack():
    result = require_login()
    if result:
        return result
    pack_id = request.form["pack_id"]
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe repun päivityksessä")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeuksia päivittää reppua", "Virhe repun päivityksessä")

    title = request.form["title"]
    if not title or len(title) > 50 or not title.strip():
        return error.render_page("Virheellinen repun nimi", "Virhe repun päivityksessä")
    description = request.form["description"]
    if not description or len(description) > 1000:
        return error.render_page("Virheellinen kuvaus repulle", "Virhe repun päivityksessä")
    weight = request.form["weight"]
    if not re.search("^[1-9][0-9]{0,2}$", weight):
        return error.render_page("Virheellinen paino repun sisällölle", "Virhe repun päivityksessä")
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,3}$", price):
        return error.render_page("Virheellinen hinta repun sisällölle", "Virhe repun päivityksessä")

    if "update" in request.form:
        all_classes = packs.get_all_classes()

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    return error.render_page("Virheellinen luokitus", "Virhe repun päivityksessä")
                if class_value not in all_classes[class_title]:
                    return error.render_page("Virheellinen luokitus", "Virhe repun päivityksessä")
                classes.append((class_title, class_value))

        packs.update_pack(pack_id, title, description, weight, price, classes)
        return redirect("/pack/" + str(pack_id))

    else:
        return redirect("/pack/" + str(pack_id))

@app.route("/remove_pack/<int:pack_id>", methods=["GET", "POST"])
def remove_pack(pack_id):
    result = require_login()
    if result:
        return result
    pack = packs.get_pack(pack_id)
    if not pack:
        return error.render_page("Reppua ei löytynyt", "Virhe repun poistossa")
    if pack["user_id"] != session["user_id"]:
        return error.render_page("Käyttäjällä ei ole oikeuksia poistaa reppua", "Virhe repun poistossa")

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
    if not username or not password1 or not password2:
        return error.render_page("Kaikki kentät tulee täyttää",
                                 "Virhe rekisteröinnissä")
    if password1 != password2:
        return error.render_page("Salasanat eivät täsmää",
                                 "Virhe rekisteröinnissä")
    if len(username) < 3:
        return error.render_page("Käyttäjänimen tulee olla vähintään 3 merkkiä pitkä",
                                 "Virhe rekisteröinnissä")
    if len(password1) < 3:
        return error.render_page("Salasanan tulee olla vähintään 3 merkkiä pitkä",
                                 "Virhe rekisteröinnissä")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return error.render_page("Käyttäjänimi jo käytössä", "Virhe rekisteröinnissä")

    return render_template("user_created.html", message="Tunnus luotu")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return error.render_page("Kaikki kentät tulee täyttää", "Virhe kirjautumisessa")

        try:
            result = users.check_login(username)
            user_id = result["id"]
            password_hash = result["password_hash"]
        except:
            return error.render_page("käyttäjätunnusta ei ole rekisteröity", "Virhe kirjautumisessa")
        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        return error.render_page("Virheellinen käyttäjätunnus tai salasana", "Virhe kirjautumisessa")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

@app.route("/remove_user/<int:user_id>", methods=["GET", "POST"])
def remove_user(user_id):
    result = require_login()
    if result:
        return result
    user = users.get_user(user_id)
    user_id = user[0]
    if not user:
        return error.render_page("Käyttäjää ei löytynyt", "Virhe käyttäjätunnuksen poistossa")
    if user_id != session["user_id"]:
          return error.render_page("Käyttäjällä ei ole oikeuksia poistaa käyttäjää", "Virhe käyttäjätunnuksen poistossa")
    if request.method == "GET":
        return render_template("remove_user.html", user=user)

    if request.method == "POST":
        if "remove" in request.form:
            users.remove_user(user_id)
            del session["user_id"]
            del session["username"]
            return redirect("/")

        return redirect("/user/" + str(user_id))
