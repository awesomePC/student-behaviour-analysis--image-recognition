"""This module does database connectivity."""

import os
from pymongo import MongoClient
from cryptography.fernet import Fernet
import logging
import json

from utils.error_handling import trace_error

from config.settings import db_configuration_filename, secret_key

logger = logging.getLogger(__name__)
# print(__name__)

def read_database_config():
    """
    * Read database configuration from file
    * -------------------------------------
    * Reads -
        1) DB
        2) Username
        3) Password
        4) Host
    * -------------------------------------*
    """
    data = None

    if os.path.isfile(db_configuration_filename):
        with open(db_configuration_filename) as json_data_file:

            encrypted_str = json_data_file.read()
            encrypted_byte = encrypted_str.encode()
            fernet = Fernet(secret_key)
            decrypted_byte = fernet.decrypt(encrypted_byte)
            decrypted_str = decrypted_byte.decode()
            double_quoted_str = decrypted_str.replace("'",'"')
            data_json = json.loads(double_quoted_str)

            data = data_json
    else:
        message = f"Error .. File not exists with name {db_configuration_filename}"
        print(message)
    return data


def connect_database():
    """
    * connect to database as per configuration defined'
    * in file named "db_config"
    """
    db_config = read_database_config()
    
    if db_config:
        database_name = db_config['db']
        try:
            client = MongoClient(f"mongodb://{db_config['host']}:27017/")
            db = client[database_name]
            
            try:
                db.authenticate(db_config['username'], db_config['password'])
                logger.info(
                    f'Authentication successfull to database "{database_name}"'
                )
            except Exception as e:
                print(f'Error in authentication...  {e}')
                error = trace_error()
                logger.error(error)
                print(error)
                
            # print(client)
            # print(f'{db_config}')
            # print(f"{db_config['host']} and database {db_config['db']}")
            return (client, db)
    
        except Exception as e:
            err_msg = trace_error()
            print(err_msg)
            logger.error(err_msg)

            db_config['password'] = '*' * len(db_config.get('password'))
            print(f'db_config used :  {db_config}')
            logger.error(f'db_config used :  {db_config}')
            pass
            return (False, False)
    else:
        message = f'Empty database configuration returned by  \
                    read_database_config() '
        print(message)
        logger.error(message)
        return (None, None)
    