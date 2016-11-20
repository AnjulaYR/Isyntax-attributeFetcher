import pymysql.cursors
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree


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

            # forming an XML
            root = Element('database')
            root.set('dbname', dbname)
            tree = ElementTree(root)
            tablesElement = Element('tables')
            root.append(tablesElement)

            # Using Cursor to fetch data as SQL queries
            cursor.execute("SHOW TABLES")
            connection.commit()
            tables = cursor.fetchall()
            print(tables)
            for table in tables:
                tableSubElement = SubElement(tablesElement, "table")
                tableSubElement.set('tbname', str(table['Tables_in_crud']))
                cursor.execute("select table_name, column_name, data_type, character_maximum_length "
                               "from INFORMATION_SCHEMA.COLUMNS "
                               "where table_name = %s;", table['Tables_in_crud'])
                connection.commit()
                atts = cursor.fetchall()
                attsSubElement = SubElement(tableSubElement, "attributes")
                for att in atts:
                    print(att)
                    attSubElement = SubElement(attsSubElement, "attribute")
                    dataSubElement = SubElement(attSubElement, "dataType")
                    lengthSubElement = SubElement(attSubElement, "maxLength")
                    refTableSubElement = SubElement(attSubElement, "referencedTable")
                    refColumnSubElement = SubElement(attSubElement, "referencedColumn")
                    attSubElement.set('attname', (att['column_name']))
                    dataSubElement.text = (att['data_type'])
                    lengthSubElement.text = str(att['character_maximum_length'])
                    cursor.execute("SELECT table_name,column_name,referenced_table_name,referenced_column_name "
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                                   "WHERE column_name = %s AND table_name = '" + table[
                                       'Tables_in_crud'] + "' AND referenced_column_name IS NOT NULL;",
                                   att['column_name'])
                    connection.commit()
                    foreigns = cursor.fetchall()
                    for foreign in foreigns:
                        if foreign:
                            print(foreign)
                            refTableSubElement.text = foreign['referenced_table_name']
                            refColumnSubElement.text = foreign['referenced_column_name']
            print(tostring(root, None, None))
            tree.write("output/" + dbname + ".xml")
    finally:
        connection.close()


username = input('enter username to the database: ')
password = input('input the password to the database: ')
dbname = input('database name: ')
con = makeConnection(dbname, username, password)
getTables(con)
