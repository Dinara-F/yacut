import random
import string

from flask import abort, flash, redirect, render_template

from . import app, db
from .forms import URLForm
from .models import URL_map


def get_unique_short_id():
    letters = string.ascii_letters
    digits = string.digits
    while True:
        result = ''.join(random.choices(letters + digits, k=6))
        if URL_map.query.filter_by(short=result).first():
            continue
        return result


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        original = form.original_link.data
        if URL_map.query.filter_by(short=form.custom_id.data).first():
            flash(f'Имя {form.custom_id.data} уже занято!')
            return render_template('index.html', form=form)
        short = form.custom_id.data or get_unique_short_id()
        url = URL_map(
            original=original,
            short=short
        )
        db.session.add(url)
        db.session.commit()
        return render_template('index.html', form=form, url=url)
    return render_template('index.html', form=form)


@app.route('/<short>')
def redirect_view(short):
    url = URL_map.query.filter_by(short=short).first()
    if url is None:
        abort(404)
    link = url.original
    if link.find("http://") != 0 and link.find("https://") != 0:
        link = "http://" + link
    return redirect(link)