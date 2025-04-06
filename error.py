from flask import render_template

def render_page(message, error_type):
    return render_template("error.html", message=message, error_type=error_type)
