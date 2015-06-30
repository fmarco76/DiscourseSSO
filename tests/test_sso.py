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


from flask import url_for
import pytest
from urlparse import urlparse
from werkzeug.exceptions import BadRequest, Forbidden
from discourseSSO import sso

app = sso.app


class Test_sso():

    def test_payload_check(self):
        """Test the payload is properly managed and the user is sent to the
        authentication page
        """
        with app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                      'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
                                      'sig=2828aa29899722b35a2f191d34ef9b3ce'
                                      '695e0e6eeec47deb46d588d70c7cb56',
                                      method='GET'):
            res = sso.payload_check()
            assert res.status_code == 302
            assert urlparse(res.location).path == url_for('user_authz')

    def test_bad_payload_sig(self):
        """Test the error code 400 is sent if the signature do not match
        the payload
        """
        with app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                      'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
                                      'sig=2828aa29899722b35a2f191d34ef9b3ce'
                                      '695e0e6eeec47deb46d588d70c7cb58',
                                      method='GET'):
            with pytest.raises(BadRequest):
                sso.payload_check()

    def test_no_payload(self):
        """Test the error code 400 is sent if the sso field is not provided"""
        with app.test_request_context('/sso/login?sig=2828aa29899722b35a2f191'
                                      'd34ef9b3ce695e0e6eeec47deb46d588d70c7c'
                                      'b56',
                                      method='GET'):
            with pytest.raises(BadRequest):
                sso.payload_check()

    def test_no_hash(self):
        """Test the error code 400 is sent if the sig field is not provided"""
        with app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                      'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&',
                                      method='GET'):
            with pytest.raises(BadRequest):
                sso.payload_check()

    def test_authentication_no_shibboleth_attributes(self):
        """Test the authentication when shibboleth do not provide attributes"""
        with app.test_request_context('/sso/auth',
                                      method='GET'):
            with pytest.raises(Forbidden):
                sso.user_authz()

    def test_authentication_no_previous_session(self):
        """Test the authentication are properly send to Discourse"""
        with app.test_request_context('/sso/auth',
                                      method='GET',
                                      environ_base={
                                          'givenName': 'sam',
                                          'sn': '',
                                          'username': 'samsam',
                                          'mail': 'test@test.com',
                                          'eppn': 'hello123'}
                                      ):
            with pytest.raises(Forbidden):
                sso.user_authz()

    def test_authentication_generation(self):
        """Test the authentication are properly send to Discourse"""
        with app.test_request_context('/sso/auth',
                                      method='GET',
                                      environ_base={
                                          'givenName': 'sam',
                                          'sn': '',
                                          'username': 'samsam',
                                          'mail': 'test@test.com',
                                          'eppn': 'hello123'}
                                      ) as req:
            req.session['nonce'] = 'nonce=cb68251eefb5211e58c00ff1395f0c0b'
            resp = sso.user_authz()
            assert resp.status_code == 302
            # sso and sig are different from the one reported in
            # https://meta.discourse.org/t/official-single-sign-on-for-
            #        discourse/13045
            # This because ruby and python include new lines in different
            # positions during the base64 encoding (of course they do not
            # matter for the base64 but the following URLencoding and
            # signature are slightly different)
            assert resp.location == ('http://discuss.example.com/session/'
                                     'sso_login?sso=bm9uY2U9Y2I2ODI1MWVlZ'
                                     'mI1MjExZTU4YzAwZmYxMzk1ZjBjMGImbmFt'
                                     'ZT1zYW0mdXNlcm5hbWU9%0Ac2Ftc2FtJmVt'
                                     'YWlsPXRlc3QlNDB0ZXN0LmNvbSZleHRlcm5'
                                     'hbF9pZD1oZWxsbzEyMw%3D%3D%0A&sig=52'
                                     '92265340422c9ce2d528e25d2927a2e24b4'
                                     '81c3e91fa353516ad458d312ffd')

    def test_authentication_generation_with_full_name(self):
        """Test the authentication are properly send to Discourse"""
        with app.test_request_context('/sso/auth',
                                      method='GET',
                                      environ_base={
                                          'givenName': 'sam',
                                          'sn': 'big',
                                          'mail': 'test@test.com',
                                          'eppn': 'hello123'}
                                      ) as req:
            req.session['nonce'] = 'nonce=cb68251eefb5211e58c00ff1395f0c0b'
            resp = sso.user_authz()
            assert resp.status_code == 302
            assert resp.location == ('http://discuss.example.com/session/'
                                     'sso_login?sso=bm9uY2U9Y2I2ODI1MWVlZ'
                                     'mI1MjExZTU4YzAwZmYxMzk1ZjBjMGImbmFt'
                                     'ZT1zYW0gYmlnJnVzZXJu%0AYW1lPXNhbWJp'
                                     'Z19iNjQyJmVtYWlsPXRlc3QlNDB0ZXN0LmN'
                                     'vbSZleHRlcm5hbF9pZD1oZWxsbzEy%0AMw%'
                                     '3D%3D%0A&sig=2371c654bbfbc5b322340a'
                                     '8fc61de880147ba00cba0fd6d29a751ad12'
                                     'e87862b')


    def test_error_page_403(self):
        """Test the correct error code is propagated"""
        with app.test_request_context('/sso/auth',
                                      method='GET',
                                      environ_base={
                                          'givenName': 'sam',
                                          'sn': '',
                                          'username': 'samsam',
                                          'mail': 'test@test.com',
                                          'eppn': 'hello123'}
                                      ):
            resp = sso.attribuete_not_provided(None)
            assert resp[1] == 403