from secrets import token_hex

ACCESS_LEVEL = {
    0: 'Public',
    1: 'General',
    2: 'Private'
}
DATABASE = 'DataBase/link-shortener.db'
DBSCRIPT = 'DataBase/db_script.sql'
DEBUG = True
SECRET_KEY = token_hex()
