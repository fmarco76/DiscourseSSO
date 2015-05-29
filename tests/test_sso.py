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


from flask import Flask, url_for
import pytest
from urlparse import urlparse
from werkzeug.exceptions import BadRequest
import sso

app = sso.app

class Test_sso():


    def test_payload_check(self):
        with app.test_client() as c:
            res = c.get('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                        'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
                        'sig=2828aa29899722b35a2f191d34ef9b3ce'
                        '695e0e6eeec47deb46d588d70c7cb56')
            assert res.status_code == 302
            assert urlparse(res.location).path == url_for('user_authz')

    def test_bad_payload_sig(self):
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
