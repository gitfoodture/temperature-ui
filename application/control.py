from flask import Blueprint, redirect, render_template
from flask_login import login_required
from time import time
import humanize
from .process import initialize_database, check_containers, run_lambda
from .models import Check, Container, Set
from . import db
import datetime as dt

control = Blueprint('control', __name__)


@control.route('/control')
@login_required
def tasks():
    containers = Container.query.all()
    length = len(containers)
    checks = Check.query.order_by(Check.timestamp.desc()).limit(length)
    keyed_checks = {c.container: c for c in checks}
    refresh = max(int(c.timestamp) for c in checks)
    refresh = humanize.naturaltime(dt.timedelta(seconds=(time() - refresh)))
    return render_template(
        'control.html',
        containers=containers,
        len=length,
        sets=Set.query.all(),
        checks=keyed_checks,
        refresh=refresh
    )


@control.route("/control/initialize", methods=["POST"])
@login_required
def init_db():
    initialize_database()
    return redirect('/control')


@control.route("/control/check", methods=["POST"])
@login_required
def check():
    Check.query.where(Check.timestamp < (int(time()) - 24*60*60)).delete()
    db.session.commit()
    # check_containers()
    values = run_lambda()
    print(values)
    return redirect('/control')

