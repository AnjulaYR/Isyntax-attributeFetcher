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
                tablekeyList = sorted(list(table.keys()))
                tableSubElement = SubElement(tablesElement, "table")
                tableSubElement.set('tbname', str(table[tablekeyList[0]]))
                cursor.execute("select table_name, column_name, data_type, character_maximum_length "
                               "from INFORMATION_SCHEMA.COLUMNS "
                               "where table_name = %s;", table[tablekeyList[0]])
                connection.commit()
                atts = cursor.fetchall()
                attsSubElement = SubElement(tableSubElement, "attributes")
                for att in atts:
                    attKeyList = sorted(list(att.keys()))
                    print(attKeyList)
                    attSubElement = SubElement(attsSubElement, "attribute")
                    dataSubElement = SubElement(attSubElement, "dataType")
                    lengthSubElement = SubElement(attSubElement, "maxLength")
                    refTableSubElement = SubElement(attSubElement, "referencedTable")
                    refColumnSubElement = SubElement(attSubElement, "referencedColumn")
                    attSubElement.set('attname', str(att[attKeyList[1]]))
                    dataSubElement.text = str(att[attKeyList[2]])
                    lengthSubElement.text = str(att[attKeyList[0]])
                    cursor.execute("SELECT table_name,column_name,referenced_table_name,referenced_column_name "
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                                   "WHERE column_name = '"+str(att[attKeyList[1]])+"' AND table_name = '" + str(table[
                                       tablekeyList[0]]) + "' AND referenced_column_name IS NOT NULL;")
                    connection.commit()
                    foreigns = cursor.fetchall()
                    for foreign in foreigns:
                        foreignKeyList = sorted(list(foreign.keys()))
                        print(foreignKeyList)
                        if foreign:
                            print(foreign)
                            refTableSubElement.text = foreign[foreignKeyList[2]]
                            refColumnSubElement.text = foreign[foreignKeyList[1]]
            print(tostring(root, None, None))
            tree.write("output/" + dbname + ".xml")
    finally:
        connection.close()


username = input('enter username to the database: ')
password = input('input the password to the database: ')
dbname = input('database name: ')
con = makeConnection(dbname, username, password)
getTables(con)
