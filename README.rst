=========================
Discourse SSO application
=========================

Discourse SSO application implements the SSO protocol requested by `discourse
forum application <http://www.discourse.org>`_. The real authentication is
performed by the web server running the application which is responsible of
verify the requests coming from discourse and prepare the token to send back
after the authentication.