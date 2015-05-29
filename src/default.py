class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'vWr,-n7NlGPv9SyIGBMr4ehwThUY92DpWPqIuh2NP_6Of-_8b3,h'
    DISCOURSE_URL = 'http://discuss.example.com'
    DISCOURSE_SECRET_KEY = 'd836444a9e4084d5b224a60c208dce14'
    DISCOURSE_USER_MAP = {
        'name': ['givenName', 'sn'],
        'username': '',
        'external_id': 'eppn',
        'email': 'mail'
    }
