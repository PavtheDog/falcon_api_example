import datetime
import calendar
import logging
import os, sys
import traceback
import uuid
import sqlite3

import calendar
import time

from . import utils

__author__ = 'Jonathan Berns'
__version__ = '1.0.0'

class PavLogger(object):

    def __init__(self):
        self.log_to_database = False
        self.log_path = '{0}/logs'.format(utils.get_app_base_path())
        self.__sqlite_db = None
        self.__sqlite_cursor = None

    def __insert_to_database(self, **kwargs):
        log_severity = kwargs.get('log_severity', 0)             
        log_message = str(kwargs.get('message', ''))      
        show_Backtrace = kwargs.get('show_Backtrace', False)
        database_name = 'debug.db' if kwargs.get('database_name', 'debug.db') is None else kwargs.get('database_name', 'debug.db')

        if show_Backtrace:
            log_message = 'Message: {0}\n'.format(log_message) 
            for line in traceback.format_stack():
                line = line.replace('\n', "")
                log_message = '{0} {1}\n'.format(log_message, ("Backtrace: {0}".format(str(line))))

        self.__insert_log(
                        log_severity = log_severity,
                        log_message = log_message, 
                        database_name = database_name
        )

    def __insert_to_text(self, **kwargs):       
        message = str(kwargs.get('message', ''))      
        show_Backtrace = kwargs.get('show_Backtrace', False)
        logger_type = kwargs.get('debuglogger', 'DEBUG')
        log_name = kwargs.get('log_name', 'debug.log')
        line_divider = kwargs.get('line_divider', '####################')

        try:                
            debuglogger = logging.getLogger(logger_type)
            if not debuglogger.handlers:

                if logger_type == 'DEBUG':
                    debuglogger.setLevel(logging.DEBUG)
                else:
                    debuglogger.setLevel(logging.ERROR)

                fh = logging.FileHandler('{0}/{1}'.format(self.log_path, log_name))
                if logger_type == 'DEBUG':
                    fh.setLevel(logging.DEBUG)
                else:
                    fh.setLevel(logging.ERROR)
                
                formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', 
                                            datefmt='%m/%d/%Y %H:%M:%S')
                fh.setFormatter(formatter)
                debuglogger.addHandler(fh)                
            debuglogger.debug('Message: {0}'.format(message)) if logger_type == 'DEBUG' else debuglogger.error('Message: {0}'.format(message))
            if show_Backtrace:
                for line in traceback.format_stack():
                    line = line.replace('\n', "")
                    debuglogger.debug("Backtrace: {0}".format(str(line))) if logger_type == 'DEBUG' else debuglogger.error("Backtrace: {0}".format(str(line)))
            debuglogger.debug("{0}{0}{0}{0}".format(line_divider)) if logger_type == 'DEBUG' else debuglogger.error("{0}{0}{0}{0}".format(line_divider))
        except Exception as error:
            sys.stderr.write("Error in Logger: {0}\n".format(str(error)))
    
    def debug(self, message, **kwargs):
        show_Backtrace = kwargs.get('show_Backtrace', False)
        log_name = kwargs.get('log_name', 'debug.log')
        line_divider = kwargs.get('line_divider', '####################')
        log_severity = kwargs.get('log_severity', 0)

        utils.check_and_create_folder(self.log_path)
        
        if self.log_to_database:
            kwargs['message'] = message
            kwargs['database_name'] = 'debug.db'
            kwargs['show_Backtrace'] = show_Backtrace
            kwargs['log_severity'] = log_severity

            self.__insert_to_database(**kwargs)
        else:
            kwargs['message'] = message
            kwargs['debuglogger'] = 'DEBUG'
            kwargs['log_name'] = log_name
            kwargs['show_Backtrace'] = show_Backtrace
            kwargs['line_divider'] = line_divider
            self.__insert_to_text(**kwargs)
        
    def error(self, message, **kwargs):     
        show_Backtrace = kwargs.get('show_Backtrace', True)
        log_name = kwargs.get('log_name', 'exception.log')
        line_divider = kwargs.get('line_divider', '####################')
        log_severity = kwargs.get('log_severity', 4)
       
        if self.log_to_database:
            kwargs['message'] = message
            kwargs['database_name'] = 'exception.db'
            kwargs['show_Backtrace'] = show_Backtrace
            kwargs['log_severity'] = log_severity
            kwargs['log_message'] = message

            self.__insert_to_database(**kwargs)
        else:
            kwargs['message'] = message
            kwargs['debuglogger'] = 'EXCEPTION'
            kwargs['log_name'] = log_name
            kwargs['show_Backtrace'] = show_Backtrace
            kwargs['line_divider'] = line_divider
            self.__insert_to_text(**kwargs)

    def __insert_log(self, **kwargs):
        new_log_id = str(uuid.uuid4())
        log_severity = kwargs.get('log_severity', 0)             
        log_message = str(kwargs.get('log_message', ''))      
        log_timestamp = kwargs.get('log_timestamp', utils.get_current_unix_time())
        log_database_name = 'debug.db' if kwargs.get('database_name', 'debug.db') is None else kwargs.get('database_name', 'debug.db')

        self.__sqlite_db = sqlite3.connect('{0}/{1}'.format(self.log_path, log_database_name))
        self.__sqlite_db.row_factory = self.__dict_factory
        self.__sqlite_cursor = self.__sqlite_db.cursor()

        self.__create_log_table()        
        
        params = [new_log_id, log_severity, log_message, log_timestamp]
        sql_statement = '''
                            INSERT INTO 
                                Logs (log_uuid, log_severity, log_message, log_timestamp)
                            VALUES (?, ?, ?, ?)                                       
                        '''
        self.__sqlite_cursor.execute(sql_statement, params)
        self.__sqlite_db.commit()
        self.__sqlite_db.close()

    def __dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __check_if_table_exists(self, object_type, tablename):
            params = [object_type, tablename]
            sql_statement = '''
                                SELECT name 
                                FROM sqlite_master 
                                WHERE type=? AND name=?;    
                            '''
            return_value = self.__sqlite_cursor.execute(sql_statement, params).fetchall()

            if len(return_value) == 0:
                return False
            
            return True

    def __create_log_table(self):
        if not self.__check_if_table_exists('table', 'logs'):
            params = []
            sql_statement = '''
                            CREATE TABLE [logs] (
                                    [log_uuid] TEXT  PRIMARY KEY NOT NULL,
                                    [log_severity] INTEGER  NULL,
                                    [log_message] TEXT  NULL,
                                    [log_timestamp] TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL
                            )
                            '''
            self.__sqlite_cursor.execute(sql_statement, params)
            self.__sqlite_db.commit()