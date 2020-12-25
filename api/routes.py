from authorization import *
from account import *

def load_routes(app_name):
  app_name.add_route('/account', AccountResource())