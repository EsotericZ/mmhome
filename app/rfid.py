import mysql.connector

cnx = mysql.connector.connect(user='cj', password='password', host='10.0.1.26', database='rfid')

try:
    cursor = cnx.cursor()
    cursor.execute("""select tag from users""")
    # cursor.execute("""insert into users (id, name, active, tag) values (2, 'cj', true, '4433');""")
    result = cursor.fetchone()
    print(result)
    # cnx.commit()
    # print('added')
    # if result[0] == '3000deb010':
    #     cursor.execute("""insert into users (id, name, active, tag) values (3, 'ADDED', true, '4433');""")
    #     cnx.commit()
    #     print('added')
    # else:
    #     cursor.execute("""insert into users (name, active, tag) values (4, 'KEY NOT FOUND', true, '4433');""")
    #     cnx.commit()
    #     print('nope')
finally:
    cnx.close()
