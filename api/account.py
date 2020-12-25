import bcrypt
import pav_logger
import uuid

from imports import *
from authorization import *

class Account(object):
  def __init__(self):
    self.plogger = pav_logger.PavLogger()
    self.plogger.log_path = "./logs/"
    self.log_name = 'activities.log'

  def get_accounts(self):
    try:
      home = (os.path.dirname(os.path.realpath(__file__)))
      config = configparser.ConfigParser()
      config.read('config.ini')
      db_location = config['DATABASE']['LOCATION']
      db_name = config['DATABASE']['NAME']

      db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)
      params = []
      sql_statement = '''
                        SELECT * FROM accounts 
                      '''
      results = db.run_database_query(sql_statement, params).get_database_results()

      return {
          'error':False,
          'error_msg':'',
          'response':results
        }
    except Exception as error:
      self.plogger.error(f'Class: Account Function: get_accounts Message: {error}', show_Backtrace = False)
      return {
        'error':True,
        'error_msg':error
      }

  def check_account(self, result):
    home = (os.path.dirname(os.path.realpath(__file__)))
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_location = config['DATABASE']['LOCATION']
    db_name = config['DATABASE']['NAME']
    account_exist = False

    db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)
    params = [result['name']]
    sql_statement = '''
                      SELECT * FROM accounts 
                      WHERE account_name = ?
                    '''
    results = db.run_database_query(sql_statement, params).get_database_results()

    if len(results) > 0:
      account_exist = True

    return account_exist
  
  def insert_account(self, result):
    try:
      if Account().check_account(result):
        return {
          'error':True,
          'error_msg':'Account already exists!',
          'response':''
        }
      else:
        home = (os.path.dirname(os.path.realpath(__file__)))
        config = configparser.ConfigParser()
        config.read('config.ini')
        db_location = config['DATABASE']['LOCATION']
        db_name = config['DATABASE']['NAME']

        db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)
        params = [str(uuid.uuid4())]
        sql_statement = '''
                          INSERT INTO accounts 
                        '''
        if 'description' in result:
          params.append(result['name'])
          params.append(bcrypt.hashpw(str.encode(result['code']), bcrypt.gensalt()).decode('utf-8'))
          params.append(result['description'])
          sql_statement += '(account_uuid, account_name, account_code, account_description)'
          sql_statement += 'VALUES (?, ?, ?, ?)'
        else:
          params.append(result['name'])
          params.append(bcrypt.hashpw(str.encode(result['code']), bcrypt.gensalt()).decode('utf-8'))
          sql_statement += '(account_uuid, account_name, account_code)'
          sql_statement += 'VALUES (?, ?, ?)'  

        db.run_database_query(sql_statement, params).database_commit()
        db.database_close()

        return {
          'error':False,
          'error_msg':'',
          'response':'Account has been created!'
        }
    except Exception as error:
      self.plogger.error(f'Class: Account Function: insert_account Message: {error}', show_Backtrace = False)
      return {
        'error':True,
        'error_msg':error,
        'response':''
      }

  def update_account(self, result):
    try:
      if not Account().check_account(result):
        return {
          'error':True,
          'error_msg':'Account does not exists!',
          'response':''
        }
      else:      
        home = (os.path.dirname(os.path.realpath(__file__)))
        config = configparser.ConfigParser()
        config.read('config.ini')
        db_location = config['DATABASE']['LOCATION']
        db_name = config['DATABASE']['NAME']

        db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)
        params = []
        sql_statement = '''
                          UPDATE accounts SET 
                        '''
        
        if 'code' in result:
          params.append(bcrypt.hashpw(str.encode(result['code']), bcrypt.gensalt()).decode('utf-8'))
          sql_statement += 'account_code = ?, '

        if 'description' in result:
          params.append(result['description'])
          sql_statement += 'account_description = ?, '

        params.append(result['name'])
        sql_statement = sql_statement[:-2] + ' WHERE account_name = ?'

        db.run_database_query(sql_statement, params).database_commit()
        db.database_close()

        return {
          'error':False,
          'error_msg':'',
          'response':'Account has been updated!'
        }
    except Exception as error:
      self.plogger.error(f'Class: Account Function: update_account Message: {error}', show_Backtrace = False)
      return {
        'error':True,
        'error_msg':error,
        'response':''
      }

  def delete_user(self, result):
    try:
      if not Account().check_account(result):
        return {
          'error':True,
          'error_msg':'Account does not exists!',
          'response':''
        }
      else:      
        home = (os.path.dirname(os.path.realpath(__file__)))
        config = configparser.ConfigParser()
        config.read('config.ini')
        db_location = config['DATABASE']['LOCATION']
        db_name = config['DATABASE']['NAME']

        db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)
        params = []
        sql_statement = '''
                          DELETE FROM accounts
                        '''

        params.append(result['name'])
        sql_statement += ' WHERE account_name = ?'

        db.run_database_query(sql_statement, params).database_commit()
        db.database_close()

        return {
          'error':False,
          'error_msg':'',
          'response':'Account has been deleted!'
        }
    except Exception as error:
      self.plogger.error(f'Class: Account Function: delete_user Message: {error}', show_Backtrace = False)
      return {
        'error':True,
        'error_msg':error,
        'response':''
      }

@falcon.before(Authorize())
class AccountResource:
  def __init__(self):
    self.plogger = pav_logger.PavLogger()
    self.plogger.log_path = "./logs/"
    self.log_name = 'activities.log'

  def on_get(self, req, resp):
    #Get Accounts
    try:
      resp.status = falcon.HTTP_200
      response = Account().get_accounts()
    except Exception as error:
      resp.status = falcon.HTTP_500
      self.plogger.error(f'Class: AccountResource Function: on_get Message: {error}', show_Backtrace = False)
      response = {
          'error':True,
          'error_msg':error,
          'response':''
        }

    resp.body = json.dumps(response)

  def on_post(self, req, resp):
    #Insert New Account
    try:
      resp.status = falcon.HTTP_200
      body = json.loads(req.stream.read())
      response = Account().insert_account(body)   
    except Exception as error:
      resp.status = falcon.HTTP_500
      self.plogger.error(f'Class: AccountResource Function: on_post Message: {error}', show_Backtrace = False)
      response = {
          'error':True,
          'error_msg':'Missing parameters',
          'response':''
        }
    
    resp.body = json.dumps(response)

  def on_put(self, req, resp):
    #Update Account
    try:
      resp.status = falcon.HTTP_200
      body = json.loads(req.stream.read())
      response = Account().update_account(body)
    except Exception as error:
      resp.status = falcon.HTTP_500
      self.plogger.error(f'Class: AccountResource Function: on_put Message: {error}', show_Backtrace = False)
      response = {
          'error':True,
          'error_msg':error,
          'response':''
        }   

    resp.body = json.dumps(response)

  def on_delete(self, req, resp):
    #Delete Account
    try:
      resp.status = falcon.HTTP_200
      body = json.loads(req.stream.read())
      response = Account().delete_user(body)
    except Exception as error:
      resp.status = falcon.HTTP_500
      self.plogger.error(f'Class: AccountResource Function: on_delete Message: {error}', show_Backtrace = False)
      response = {
          'error':True,
          'error_msg':error,
          'response':''
        }

    resp.body = json.dumps(response)
