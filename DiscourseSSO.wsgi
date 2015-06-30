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
WSGI script to run the application.
Customise the file config.py or provide your own file using the environment
variable DISCOURSE_SSO_CONFIG in order to read the configuration for the
following variables:
    - DISCOURSE_URL: Discourse URL to send the user back
    - DISCOURSE_SECRET_KEY: Secret key shared with the Discourse server
    - DISCOURSE_USER_MAP: Attribute to read from the environment after user
                          validation
    - All Flask configuration values

To run in a virtual environment add the activation code. Es.:
    activate_this = '/path/to/env/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))
"""


from discourseSSO.sso import app as application
