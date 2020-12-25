import bcrypt
import configparser
import os
import pav_logger

from imports import *

class Authorize(object):
  def __init__(self, roles = None):
    self._roles = roles
    self.plogger = pav_logger.PavLogger()
    self.plogger.log_path = "./logs/"
    self.log_name = 'activities.log'

  def check_account(self, account_name, account_code):
    try:
      home = (os.path.dirname(os.path.realpath(__file__)))
      config = configparser.ConfigParser()
      config.read('config.ini')
      db_location = config['DATABASE']['LOCATION']
      db_name = config['DATABASE']['NAME']

      db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)  
      params = [account_name]
      sql_statement = '''
                        SELECT * FROM accounts 
                        WHERE account_name = ? COLLATE NOCASE
                      '''
      results = db.run_database_query(sql_statement, params).get_database_results()
      db.database_close()

      if len(results) == 0:
        self.plogger.debug('Unable to find account.', log_name=self.log_name)
        return False
      else:
        if (bcrypt.checkpw(str.encode(account_code), str.encode(results[0]['account_code']))):
          self.plogger.debug('Account logged in.', log_name=self.log_name)
          return True
        else:
          self.plogger.debug('Account code is invalid.', log_name=self.log_name)
          return False
    except Exception as error:
      self.plogger.error(f'Function: check_account Message: {error}', show_Backtrace = False)
    
    return False

  def __auth_basic(self, username, password):
    #if username in user_account and user_account[username] == password:
    if not self.check_account(username, password):
      raise falcon.HTTPUnauthorized('Unauthorized', 'Invalid Username/Password.')

  def __call__(self, req, resp, resource, params):
    #print (req.auth)
    auth_exp = req.auth.split(' ') if req.auth is not None else (None, None, )

    if auth_exp[0] is not None and auth_exp[0].lower() == 'basic':
      auth = base64.b64decode(auth_exp[1]).decode('utf-8').split(':')
      username = auth[0]
      password = auth[1]
      self.__auth_basic(username, password)
      resp.status = falcon.HTTP_403
    else:
      resp.status = falcon.HTTP_405
      raise falcon.HTTPNotImplemented('Not Implement','You didi\'t use the right auth method')