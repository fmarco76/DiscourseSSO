# Copyright 2015 INFN
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
SSO FLASK Application for Discourse
The configuration file is defined with the variable "DISCOURSE_SSO_CONFIG",
for the most significant values look at the sso/default.py file
"""


from flask import abort, Flask, redirect, render_template, request, url_for, \
    session

import base64
import hashlib
import hmac
import urllib
import re

app = Flask(__name__)
app.config.from_object('discourseSSO.default.Config')
app.config.from_pyfile('config.py')
app.config.from_envvar('DISCOURSE_SSO_CONFIG', True)


@app.route('/sso/login')
def payload_check():
    """
    Verify the payload and signature coming from a Discourse server and if
    correct redirect to the authentication page
    :return: The redirection page to the authentication page
    """
    payload = request.args.get('sso', '')
    signature = request.args.get('sig', '')

    app.logger.debug('Request to login with payload="%s" signature="%s"',
                     payload, signature)
    if not payload or not signature:
        abort(400)

    app.logger.debug('Session Secret Key: %s',
                     app.secret_key)
    app.logger.debug('SSO Secret Key: %s',
                     app.config.get('DISCOURSE_SECRET_KEY'))
    dig = hmac.new(
        app.config.get('DISCOURSE_SECRET_KEY'),
        payload,
        hashlib.sha256
    ).hexdigest()
    app.logger.debug('Calculated hash: %s', dig)
    if dig != signature:
        abort(400)
    decoded_msg = base64.decodestring(payload)
    session['nonce'] = decoded_msg
    return redirect(url_for('user_authz'))


@app.route('/sso/auth')
def user_authz():
    """
    Read the user attributes provided by the application server (generally
    it is apache httpd) as environment variables and create the payload to
    send to discourse
    :return: The redirection page to Discourse
    """
    attribute_map = app.config.get('DISCOURSE_USER_MAP')
    user_flag_filters = app.config.get('DISCOURSE_USER_FLAGS')
    email = request.environ.get(attribute_map['email'])
    external_id = request.environ.get(attribute_map['external_id'])
    if not (email and external_id):
        abort(403)
    name_list = []
    for name_to_map in attribute_map['name']:
        if request.environ.get(name_to_map):
            name_list.append(request.environ.get(name_to_map))
    name = ' '.join(name_list)
    if request.environ.get(attribute_map['username']):
        username = request.environ.get(attribute_map['username'])
    else:
        username = (name.replace(' ', '') +
                    "_" +
                    hashlib.md5(email).hexdigest()[0:4]
                    )
    avatar_url = request.environ.get(attribute_map['avatar_url'])
    bio = request.environ.get(attribute_map['bio'])
    app.logger.debug('Authenticating "%s" with username "%s" and email "%s"',
                     name, username, email)
    if 'nonce' not in session:
        abort(403)
    query = (session['nonce'] +
             '&name=' + name +
             '&username=' + username +
             '&email=' + urllib.quote(email) +
             '&external_id=' + urllib.quote(external_id))
    if avatar_url:
        query = query + '&avatar_url=' + urllib.quote(avatar_url)
    if bio:
        query = query + '&bio=' + urllib.quote(bio)
    flags = {}
    for user_flag in user_flag_filters:
        if 'filter' in user_flag:
            filter = user_flag['filter'].split('=')
            reg_exp = re.compile(filter[1])
            if (request.environ.get(filter[0]) and
                    reg_exp.match(request.environ.get(filter[0]))):
                flags[user_flag['name']] = user_flag['value']
        else:
            flags[user_flag['name']] = user_flag['value']
    for flags_name in sorted(flags.keys()):
        query = query + '&' + flags_name + '=' + flags[flags_name]
    app.logger.debug('Query string to return: %s', query)
    query_b64 = base64.encodestring(query)
    app.logger.debug('Base64 query string to return: %s', query_b64)
    query_urlenc = urllib.quote(query_b64)
    app.logger.debug('URLEnc query string to return: %s', query_urlenc)
    sig = hmac.new(
        app.config.get('DISCOURSE_SECRET_KEY'),
        query_b64,
        hashlib.sha256
    ).hexdigest()
    app.logger.debug('Signature: %s', sig)
    redirect_url = (app.config.get('DISCOURSE_URL') +
                    '/session/sso_login?'
                    'sso=' + query_urlenc +
                    '&sig=' + sig)

    return redirect(redirect_url)


@app.errorhandler(403)
def attribuete_not_provided(error):
    """
    Render a custom error page in case the IdP authenticate the user but does
    not provide the requested attributes

    :type error: object
    """
    return render_template('403.html'), 403
