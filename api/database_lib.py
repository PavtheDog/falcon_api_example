import sys
import hashlib
import os
import base64

from string import ascii_lowercase

#Linux requires a different library for SQLCipher
if sys.platform.lower() == 'linux':
    try:
        from pysqlcipher3 import dbapi2 as sqlite3
    except:
        import sqlite3
else:
    import sqlite3

try:    
    import psycopg2
    import psycopg2.extras
    from psycopg2.extras import RealDictCursor
except ImportError:
    pass


class SQLite_Database(object):

    def __init__(self, database_encrypted=False):
        self.sqlite_db = None
        self.sqlite_cursor = None
        self.sqlite_query = ''
        self.sqlite_results = None
        self.sqlite_rowcount = 0
        self.sqlite_params = None
        self.database_encrypted = database_encrypted
        self.db_key = ''

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def change_password(self):
        LETTERS = {letter: str(index) for index, letter in enumerate(ascii_lowercase, start=1)} 
        password = self.db_key.lower()
        numbers = [LETTERS[character] for character in password if character in LETTERS]

        salt = base64.b64encode(password.encode('utf-8')).decode('utf-8').lower()
        salt_numbers = [LETTERS[character] for character in salt if character in LETTERS]
        database_password = str(int(''.join(numbers)) * int(''.join(salt_numbers)))
        #print (database_password)
        return (database_password)

    def database_connect(self, dbname = None, db_key = ''):
        if dbname is None:
            raise Exception('No database has been selected!')

        self.db_key = db_key
        self.sqlite_db = sqlite3.connect(dbname)
            
        self.sqlite_db.row_factory = self.dict_factory
        self.sqlite_cursor = self.sqlite_db.cursor()
        if self.database_encrypted:
            self.sqlite_cursor.execute('pragma key={0}'.format(self.change_password()))
        return self

    def run_database_query(self, query = '', params = [], db_key = ''):
        is_error = False
        error_msg = None

        if query == '':
            raise Exception("Query cannot be blank")

        self.sqlite_query = query
        self.sqlite_params = params
            
        try:
            if self.database_encrypted and db_key != '':
                self.sqlite_cursor.execute('pragma key={0}'.format(self.change_password()))
            self.sqlite_cursor.execute(self.sqlite_query, self.sqlite_params)
        except Exception as sqlite_error:
            self.sqlite_db.rollback()
            error_msg = sqlite_error
            is_error = True

        if is_error:
            raise Exception("Database Error: {0}".format(error_msg))
        return self

    def run_database_many_query(self, query = '', params = [], db_key = ''):
        is_error = False
        error_msg = None

        if query == '':
            raise Exception("Query cannot be blank")

        self.sqlite_query = query
        self.sqlite_params = params

        try:
            if self.database_encrypted and db_key != '':
                self.sqlite_cursor.execute('pragma key={0}'.format(self.change_password()))
            self.sqlite_cursor.executemany(self.sqlite_query, self.sqlite_params)
        except Exception as sqlite_error:
            self.sqlite_db.rollback()
            error_msg = sqlite_error
            is_error = True

        if is_error:
            raise Exception("Database Error: {0}".format(error_msg))
        return self
    
    def database_commit(self):
        try:
            self.sqlite_db.commit()
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        finally:
            return self

    def database_rollback(self):
        try:
            self.sqlite_db.rollback()
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        finally:
            return self

    def get_database_results(self):
        try:
            self.sqlite_results = self.sqlite_cursor.fetchall()
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        finally:
            return self.sqlite_results
        
    def get_database_count(self):
        try:
            self.sqlite_rowcount = self.sqlite_cursor.rowcount
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        finally:
            return self.sqlite_rowcount

    def get_database_insert_id(self):
        try:
            return self.sqlite_cursor.lastrowid
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        
    def database_close(self):
        try:
            self.sqlite_db.close()
        except sqlite3.Error as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))
        except Exception as sqlite_error:
            raise Exception("Database Error: {0}".format(sqlite_error))

    def database_is_connected(self):
        if self.sqlite_db is not None:
            return True
        else:
            return False

class Postgres_Database(object):

    def __init__(self):
        self.postgres_conn = None
        self.postgres_cursor = None
        self.postgres_results = None
        self.postgres_rowcount = 0
        self.postgres_params = None
        self.postgres_lastval = None
        self.postgres_query = ''

    def database_connect(self, connection_dict = {}):
        try:
            self.postgres_conn = psycopg2.connect(**connection_dict)
        except psycopg2.OperationalError as postgres_error:
            raise Exception("Database Error: {0}".format(postgres_error))
        except Exception as error:
            raise Exception("Database Error: {0}".format(error))
        finally:
            return self

    def run_database_query(self, query = None, params = []):
        if query is None:
            raise Exception("Query cannot be blank")

        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")

        is_error = False
        error_msg = None

        try:
            self.postgres_query = query
            self.postgres_params = params 

            if 'select' in self.postgres_query.lower():
                self.postgres_cursor = self.postgres_conn.cursor(cursor_factory = RealDictCursor)
            else:
                self.postgres_cursor = self.postgres_conn.cursor()

            self.postgres_cursor.execute(query, params)
        except psycopg2.ProgrammingError as postgres_error:
            error_msg = postgres_error
            is_error = True
            raise Exception("Database Error: {0}".format(postgres_error))
        except Exception as error:
            error_msg = error
            is_error = True
            raise Exception("Database Error: {0}".format(error_msg))
        finally:
            if is_error:
                raise Exception("Database Error: {0}".format(error_msg))
            return self

    def get_database_count(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        try:
            self.postgres_rowcount = self.postgres_cursor.rowcount
        except (Exception, psycopg2.DatabaseError) as postgres_error:    
            raise Exception("Database Error: {0}".format(postgres_error))
        except Exception as postgres_error:
            raise Exception("Database Error: {0}".format(postgres_error))
        finally:
            return self.postgres_rowcount

    def database_commit(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        try:
            self.postgres_conn.commit()
        except (Exception, psycopg2.DatabaseError) as postgres_error:    
            raise Exception("Database Error: {0}".format(postgres_error))
        except Exception as postgres_error:
            raise Exception("Database Error: {0}".format(postgres_error))
        finally:
            return self

    def database_rollback(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        try:
            self.postgres_conn.rollback()
        except (Exception, psycopg2.DatabaseError) as postgres_error:    
            raise Exception("Database Error: {0}".format(postgres_error))
        finally:
            return self

    def get_database_results(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        try:
            self.postgres_results = self.postgres_cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as postgres_error:    
            raise Exception("Database Error: {0}".format(postgres_error))
        finally:
            if self.postgres_results is None:
                return []
            else:
                return self.postgres_results

    def get_database_insert_id(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        params = []
        sql_statement = '''
                            SELECT LASTVAL()
                        '''
        self.run_database_query(sql_statement, params)

        self.postgres_lastval =  self.postgres_cursor.fetchone()['lastval']

        return self
    
    def database_close(self):
        if self.postgres_conn is None:
            raise Exception("Datbase Not Connected")
        try:
            self.postgres_conn.close()
        except (Exception, psycopg2.DatabaseError) as postgres_error:    
            raise Exception("Database Error: {0}".format(postgres_error))

    def database_is_connected(self):
        if self.postgres_conn is not None:
            return True
        else:
            return False

if __name__ == '__main__':
    db_obj = SQLite_Database(True)    

    if not os.path.isfile('database_test_pass.db'):
        db_obj.database_connect('database_test_pass.db', 'Testing This Out')
        params = []
        sql_statement = '''
                            CREATE TABLE test_table (
                                test_field TEXT NOT NULL
                            )
                        '''
        db_obj.run_database_query(sql_statement, params).database_commit()

        params = ['Test']
        sql_statement = '''
                            INSERT INTO test_table (test_field) VALUES (?)
                        '''
        db_obj.run_database_query(sql_statement, params).database_commit()

        db_obj.database_close()
