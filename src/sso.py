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
SSO Application tests
"""


from flask import abort, Flask, redirect, request, url_for, session

import base64
import hashlib
import hmac
import urllib

app = Flask(__name__)
app.config.from_object('default.Config')
app.config.from_envvar('DISCOURSE_SSO_CONFIG', True)


@app.route('/sso/login')
def payload_check():

    payload = request.args.get('sso', '')
    signature = request.args.get('sig', '')

    app.logger.debug('Request to login with '
                     'payload="' + payload + '" '
                     'signature="' + signature + '"'
                     )
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
    app.logger.debug('Calculated hash: ' + dig)
    if dig != signature:
        abort(400)
    decoded_msg = base64.decodestring(payload)
    session['nonce'] = decoded_msg
    return redirect(url_for('user_authz'))


@app.route('/sso/auth')
def user_authz():
    attribute_map = app.config.get('DISCOURSE_USER_MAP')
    name_list = []
    for name_to_map in attribute_map['name']:
        name_list.append(request.environ.get(name_to_map))
    name = ' '.join(name_list)
    username = request.environ.get(attribute_map['username'])
    email = request.environ.get(attribute_map['email'])
    external_id = request.environ.get(attribute_map['external_id'])

    query = (session['nonce'] +
             '&name=' + name +
             '&username=' + username +
             '&email=' + email +
             '&external_id=' + external_id)
    app.logger.debug('Query string to return: ' + query)
    query_b64 = base64.encodestring(query)
    app.logger.debug('Base64 query string to return: ' + query_b64)
    query_urlenc = urllib.quote(query_b64)
    app.logger.debug('URLEnc query string to return: ' + query_b64)
    sig = hmac.new(
        app.config.get('DISCOURSE_SECRET_KEY'),
        query_urlenc,
        hashlib.sha256
    ).hexdigest()

    redirect_url = (app.config.get('DISCOURSE_URL') +
                    '/session/sso_login?'
                    'sso=' + query_urlenc +
                    '&sig=' + sig)

    return redirect(redirect_url)


if __name__ == '__main__':
    app.run()
