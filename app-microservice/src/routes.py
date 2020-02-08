import time
from flask import Blueprint, request, session, jsonify
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from src.models import db, User, OAuth2Client
from src.oauth2 import authorization, require_oauth

bp = Blueprint(__name__, "home")

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route("/create_client", methods=["POST"])
def create_client():


    user = current_user()
    
    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at
    )

    if client.token_endpoint_auth_method == "none":
        client.client_secret = ""
    else:
        client.client_secret = gen_salt(48)

    form = request.form

    client_metadata = {
        "client_name": form["client_name"],
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "scopes": form["scopes"],
        "website": form["website"]
    }

    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    
    return jsonify(client_metadata)

@bp.route("/oauth/revoke", methods=["POST"])
def revoke_token():
    return authorization.create_endpoint_response('revocation')

@bp.route("/oauth/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()

@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)
