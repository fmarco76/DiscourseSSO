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


from flask import abort
from flask import Flask
from flask import request
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

    dig = hmac.new(
        app.config.get('SECRET_KEY'),
        payload,
        hashlib.sha256
    ).hexdigest()
    app.logger.debug('Calculated hash: ' + dig)
    if dig != signature:
        abort(400)
    
    return 'Hello World!'


@app.route('/sso/auth')
def user_authz():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
