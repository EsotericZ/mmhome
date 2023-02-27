import pyodbc as p

server = '10.0.1.130\E2SQLSERVER'
db = 'MONARCH_SHOP'
un = 'sa'
pw = 'Mon@rch09'

cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
cursor = cnxn.cursor()

def equip():
    cursor.execute("SELECT DISTINCT PartNo FROM Estim WHERE ProdCode='EQUIP'")

    row = cursor.fetchall()
    equip = []
    for r in row:
        equip.append(r[0])
    equip = sorted(equip)

    return equip
