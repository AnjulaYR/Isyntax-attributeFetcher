import pymysql.cursors


def makeConnection(dbname, username, password):
    connection = pymysql.connect(host='localhost',
                                 user=username,
                                 password=password,
                                 db=dbname,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def getTables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            connection.commit()
            tables = cursor.fetchall()
            print(tables)
            for table in tables:
                cursor.execute("select table_name, column_name, data_type, character_maximum_length "
                               "from INFORMATION_SCHEMA.COLUMNS "
                               "where table_name = %s;", table['Tables_in_crud'])
                connection.commit()
                atts = cursor.fetchall()
                for att in atts:
                    print(att)
                    cursor.execute("SELECT table_name,column_name,referenced_table_name,referenced_column_name "
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                                   "WHERE column_name = %s AND table_name = '" + table[
                                       'Tables_in_crud'] + "' AND referenced_column_name IS NOT NULL;",
                                   att['column_name'])
                    connection.commit()
                    foreign = cursor.fetchall()
                    if foreign is not None:
                        print(foreign)
    finally:
        connection.close()


username = input('enter username to the database: ')
password = input('input the password to the database: ')
dbname = input('database name: ')
con = makeConnection(dbname, username, password)
getTables(con)