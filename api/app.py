import falcon

from routes import *

class TestResource:
  def on_get(self, req, resp):
    """Handles GET requests"""
    home = (os.path.dirname(os.path.realpath(__file__)))
    config = configparser.ConfigParser()
    config.read('config.ini')
    app_name = config['APP']['NAME']
    app_version = config['APP']['VERSION']

    reponse = f'Welcome to {app_name} {app_version}'  
    resp.media = reponse

@falcon.before(Authorize())
class AccountTestResource:
  def on_get(self, req, resp):
    """Handles GET requests"""
    reponse = f'Account credentials are correct.'  
    resp.media = reponse

api = falcon.API()
api.add_route('/', TestResource())
api.add_route('/test', AccountTestResource())
load_routes(api)