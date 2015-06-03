=========================
Discourse SSO application
=========================

| |travis| |coveralls| |landscape| |scrutinizer|

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

Discourse SSO application implements the SSO protocol requested by `discourse
forum application <http://www.discourse.org>`_. The real authentication is
performed by the web server running the application which is responsible of
verify the requests coming from discourse and prepare the token to send back
after the authentication.