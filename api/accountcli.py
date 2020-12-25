#!/usr/bin/python
import bcrypt
import configparser
import getopt
import os
import sys
import uuid

from database_lib import SQLite_Database

def check_account(username, db_location, db_name):
  found_username = False
  home = (os.path.dirname(os.path.realpath(__file__)))
  db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)  
  params = [username]
  sql_statement = '''
                    SELECT * FROM accounts 
                    WHERE account_name = ? COLLATE NOCASE
                  '''
  results = db.run_database_query(sql_statement, params).get_database_results()
  db.database_close()

  if len(results) > 0:
    found_username = True
 
  return found_username

def insert_account(username, password, description, db_location, db_name):
  inserted_account = False
  try:
    home = (os.path.dirname(os.path.realpath(__file__)))
    db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)  
    params = [str(uuid.uuid4()), username, password, description]
    sql_statement = '''
                      INSERT INTO accounts (account_uuid, account_name, account_code, account_description)
                      VALUES (?, ?, ?, ?)                    
                    '''
    db.run_database_query(sql_statement, params).database_commit()
    db.database_close()
  except Exception as error:
    print (error)
  finally:
    inserted_account = True

  return inserted_account

def update_account(username, password, description, db_location, db_name):
  updated_account = False
  try:
    home = (os.path.dirname(os.path.realpath(__file__)))
    db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name) 
    if description == '': 
      params = [password, username]
      sql_statement = '''
                        UPDATE accounts SET account_code = ?
                        WHERE account_name = ?                  
                      '''
    else:
      params = [password, description, username]
      sql_statement = '''
                        UPDATE accounts SET account_code = ?, account_description = ?
                        WHERE account_name = ?                  
                      '''
    db.run_database_query(sql_statement, params).database_commit()
    db.database_close()
  except Exception as error:
    print (error)
  finally:
    updated_account = True

  return updated_account

def remove_account(username, db_location, db_name):
  removed_account = False
  try:
    home = (os.path.dirname(os.path.realpath(__file__)))
    db = SQLite_Database().database_connect(home + '\\' + db_location + '\\' + db_name)  
    params = [username]
    sql_statement = '''
                      DELETE FROM accounts
                      WHERE account_name = ?                  
                    '''
    db.run_database_query(sql_statement, params).database_commit()
    db.database_close()
  except Exception as error:
    print (error)
  finally:
    removed_account = True

  return removed_account

def main(argv):
  config = configparser.ConfigParser()
  config.read('config.ini')
  db_location = config['DATABASE']['LOCATION']
  db_name = config['DATABASE']['NAME']
  username = ''
  password = ''
  description = ''
  password_hash = ''
  create_user = False
  update_user = False
  remove_user = False
  short_options = "hc:u:r:p:d:"
  long_options = ["help", 'create-user=', 'update-user=', 'remove-user=', 'password=', 'description=' ]

  try:
    opts, args = getopt.getopt(argv,short_options,long_options)
  except getopt.GetoptError:
    print (
            f'''
              accountcli.py 
                Account Commands:
                  -c or --create-user <username>
                    optional:
                      -p or --password <password> (if not used a password with be generated)
                      -d or --description "<description>"
                  -u or --update-user <username> -p or --password <password>
                    optional:
                      -d or --description "<description>"
                  -r or --remove-user <username>
            '''
          )
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
        print (
                '''
                  accountcli.py 
                    Account Commands:
                      -c or --create-user <username>
                        optional:
                          -p or --password <password> (if not used a password with be generated)
                          -d or --description "<description>"
                      -u or --update-user <username> -p or --password <password>
                        optional:
                          -d or --description "<description>"
                      -r or --remove-user <username>
                '''
              )
        sys.exit()
    elif opt in ("-c", "--create-user"):
      create_user = True
      username  = arg
    elif opt in ("-u", "--update-user"):
      update_user = True
      username  = arg
    elif opt in ("-r", "--remove-user"):
      remove_user = True
      username  = arg
    elif opt in ("-p", "--password"):
      password  = arg    
    elif opt in ("-d", "--description"):
      description  = arg
  
  if create_user:
    if not check_account(username, db_location, db_name):
      print ('Creating User')
      created_password = False
      if password == '':
        password = str(uuid.uuid4())
        created_password = True
      password_hash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt()).decode('utf-8')
      if insert_account(username, password_hash, description, db_location, db_name):
        if created_password:
          print (f'Account has been created!\nPassword is {password}')          
        else:
          print ('Account has been created!')
      else:
        print ('Unable to create account!')
    else:
      print ('Account already exists!')
  elif update_user:
    if password == '':
      print ('Password needed!')
    else:
      print ('Updating User')
      password_hash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt()).decode('utf-8')
      if not check_account(username, db_location, db_name):
        print ('Account does not exists!')
      else:
        if update_account(username, password_hash, description, db_location, db_name):
          print ('Account has been updated!')
        else:
          print ('Unable to update account!')
  elif remove_user:
    print ('Removing User')
    if not check_account(username, db_location, db_name):
      print ('Account does not exists!')
    else:
      if remove_account(username, db_location, db_name):
        print ('Account has been removed!')
      else:
        print ('Unable to remove account!')
  else:
    print ('Account command not found!')

if __name__ == "__main__":
   main(sys.argv[1:])