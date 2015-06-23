=========================
Discourse SSO application
=========================

| |travis| |coveralls| |landscape| |scrutinizer| |codacy| |license|

.. |travis| image:: http://img.shields.io/travis/fmarco76/DiscourseSSO/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/fmarco76/DiscourseSSO

.. |coveralls| image:: https://coveralls.io/repos/fmarco76/DiscourseSSO/badge.svg?style=flat
    :alt: Coverage Status
    :target: https://coveralls.io/r/fmarco76/DiscourseSSO

.. |landscape| image:: https://landscape.io/github/fmarco76/DiscourseSSO/master/landscape.svg?style=flat
    :target: https://landscape.io/github/fmarco76/DiscourseSSO/master
    :alt: Code Quality Status

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/fmarco76/DiscourseSSO/master.png?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/fmarco76/DiscourseSSO/

.. |codacy| image:: https://www.codacy.com/project/badge/ff8b39c8455d4f2ca4ead7e034f6b6d6
    :alt: Codacy Status
    :target: https://www.codacy.com/app/marco-fargetta/DiscourseSSO

.. |license| image:: https://img.shields.io/github/license/fmarco76/DiscourseSSO.svg?style=flat 
    :alt: License
    :target: http://www.apache.org/licenses/LICENSE-2.0.txt


Discourse SSO application implements the SSO protocol requested by `discourse
forum application <http://www.discourse.org>`_. The real authentication is
performed by the web server running the application which is responsible of
verify the requests coming from discourse and prepare the token to send back
after the authentication.


Requirements
------------

DiscourseSSO application can execute in any web server supporting python code.
However it has been tested only with *apache httpd server* using *mod_wsgi* and
these are described in the installation section.

The authentication has to be performed by the web server and this require an additional
module. The module has to provide the user information the in application environment.
This is the case with many modules like *mod_shibboleth* for **SAML** described
in the installation.


Installation
------------

For the installation we consider Discourse container has been installed in the server
and work properly with local accounts.

Prepare the server where DiscourseSSO has to be deployed. The server could be
the same of the Discourse server using the same *nginx* to execute the sso code or an
additional *apache httpd* server taking care of not create conflict with the ports.

The installation of httpd server has to include *mod_wsgi* to execute the code, *mod_ssl*
to have the authentication over https and *mod_shib* (or equivalent) to implement the
authentication.

After the installation of all modules httpd has to be configured to work on the ssl port.
If mod_ssl comes with your distribution it should include the basic configuration,
otherwise have a look at the `apache httpd documentation <http://httpd.apache.org/docs/>`_
for your specific version. The standard http port **80** will not be used so it could be
disabled.

The next step is to configure mod_shib in order to allow the authentication
using saml (for details on mod_shib configuration look at the `official wiki
<https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPConfiguration>`_).

When the server is properly configured download/clone the **DiscourseSSO** package
from `GitHub <https://github.com/fmarco76/DiscourseSSO>`_ in a directory accessible
by apache. Configure mod_wsgi to include the source code of the package and add
the `DiscourseSSO.wsgi` script to the location to use for Discourse. Finally, shibboleth
has to protect the authentication directory so the user has to go to the IdP in order
be accepted. The configuration should look like: ::

    WSGIDaemonProcess discourse threads=5 python-path=<path-to-discourse>/DiscourseSSO/src
    WSGIScriptAlias /DiscourseSSO /var/www/DiscourseSSO/DiscourseSSO.wsgi
    WSGISocketPrefix /var/run/wsgi
    .
    .
    <Directory /var/www/DiscourseSSO>
        WSGIProcessGroup discourse
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
    <Location /DiscourseSSO/sso/auth>
        AuthType shibboleth
        ShibCompatWith24 On
        ShibRequestSetting requireSession 1
        require shib-session
    </Location>

Finally, both Discourse and DiscourseSSO need to be configured. Enable the sso in
Discourse following the `official documentation <https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045>`_.
The sso url to is the one going to your DiscourseSSO installation plus `sso/login`, so using
the above configuration the url is `https://<your-domain>/DisocurseSSO/sso/login`.

The sso_secret is a random string and has to be the same in both services. The configuration
file of DiscourseSSO is `src/config.py` and it require the secret key (`DISCOURSE_SECRET_KEY`),
the url of Discourse (`DISCOURSE_URL`) and the name of the environment variables
where mod_shibb will provide the user information(`DISCOURSE_USER_MAP`). This is a
map where the key is the attribute provided back to Discourse whereas the values
are the name of the variables to lookup. The name can be generated combining different
values but the other accept only one value. Default are good for a SAML based
authentication but for other authentication mechanism you have to modify them accordingly.

After the configuration restart the apache httpd daemon and enable the sso in Discourse.
