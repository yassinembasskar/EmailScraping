import pymysql

def get_db_connection():
    host = 'localhost'
    user = 'root'
    password = ''
    db = 'emailscrapperdb'

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=db
    )
    return connection