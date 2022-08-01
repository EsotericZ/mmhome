import os
import pyodbc as p
import pandas as pd
import numpy as np
from pandas import DataFrame
import sqlite3
from sqlite3 import Error
from os import listdir
from os.path import isfile, join
# from var import cust

pd.options.mode.chained_assignment = None

def dbtl():
    # TUBE LASER SCHEDULER
    server = '10.0.1.130\E2SQLSERVER'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='211 TLASER'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='211 TLASER' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN'"""
    df1 = pd.read_sql(sql, con=cnxn)
    dff = df1.values.tolist()
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')
    # if not df4['User_Date1'] == 0:
    #     df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    #     df4['User_Date1'] = df4['User_Date1'].fillna('-')

    # DOES PROGRAM EXIST FOR CURRENT JOB NUMBER
    fe = []
    r = []
    for f in dff:
        job = f[1]
        part = f[5]
        cust = f[13]
        # TLASER FILE
        cad = 'TLASER'
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        path = server+'/'+cust+'/'+part+'/'+cad
        d = os.path.exists(path)
        r = []
        if d == True:
            r += [each for each in os.listdir(path) if each.lower().endswith(('.atd'))]
            if r:
                fe.append(job)
    print('fe', fe)
    dfp = pd.DataFrame(fe, columns=['JobNo'])
    print(dfp)

    # DF5 IS FOR ALL JOBS ON TLASER
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON TLASER
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON TLASER
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON TLASER
    df8 = df4.loc[df4['mtl'] == 'on']
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON TLASER
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER TLASER
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))

    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': ' '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)

    return [df5, df6, df7, df8, df9, df10, df11, df12]





def dbeng():
    # ENGINEERING
    # server = '10.0.1.120\E2SQL'
    # server = '10.0.1.224\E2SQLSERVER'

    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    # db = 'MONARCH'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, R.EstimQty, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, D.QuoteNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='101 ENGIN' AND O.User_Text3!='UNCONFIRMED'"""
    # sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3,\
    #                D.DueDate, O.CustCode, D.QuoteNo, Q.QuotedBy, O.PurchContact, C.Contact, C.Email \
    #                FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN QUOTE Q ON D.QuoteNo=Q.QuoteNo \
    #                INNER JOIN Contacts C ON O.CustCode=C.CODE \
    #                WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='101 ENGIN' AND O.User_Text3!='UNCONFIRMED'"""
    sql1 = """SELECT R.JobNo, R.WorkCntr \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='203 LASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='211 TLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='201 SHEAR') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='202 PUNCH') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='212 FLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='213 SLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='301 SAW') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='402 WELD') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='702 ASSEM')"""
    sql2 ="""SELECT P.PartNo, P.DocNumber, R.JobNo \
                       FROM PartFiles P INNER JOIN OrderDet D ON P.PartNo=D.PartNo INNER JOIN OrderRouting R ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                       WHERE D.Status='Open' AND D.User_Text3='Repeat' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='101 ENGIN' AND O.User_Text3!='UNCONFIRMED'"""

    df1 = pd.read_sql(sql, con=cnxn)
    dflsr = pd.read_sql(sql1, con=cnxn)
    dfnoprnt = pd.read_sql(sql2, con=cnxn)

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM jobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model', 'nest']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')
    df3lsr = pd.merge(left=df3, right=dflsr, left_on='JobNo', right_on='JobNo')
    if not df3lsr.empty:
        df3lsr['DueDate'] = df3lsr['DueDate'].dt.strftime('%y/%m/%d')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'EstimQty', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'StepNo', 'qcn', 'model', 'QuoteNo']]
    if not df4.empty:
        df4['DueDate'] = df4['DueDate'].dt.strftime('%y/%m/%d')

    # DF5 IS FOR ALL JOBS IN ENGINEERING
    df5 = df4.sort_values(by=['JobNo'], ascending = True)
    if not df5.empty:
        dfm = df5['DueDate'].str.split(pat = '/').str[1]
        dfd = df5['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df5['ShowDate'] = dfn

    # DF6 IS FOR ONLY TBR JOBS IN ENGINEERING
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS IN ENGINEERING (NO REPEATS)
    df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df7.loc[df7['User_Text3'] != 'REPEAT']
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY REPEAT JOBS IN ENGINEERING (SORT TOWER IN ROUTES.PY)
    df8 = df3lsr
    df8 = df8.loc[df8['User_Text2'] != '7. ON HOLD']
    df8 = df8.sort_values(by=['DueDate'], ascending = True)
    if not df8.empty:
        dfm = df8['DueDate'].str.split(pat = '/').str[1]
        dfd = df8['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df8['ShowDate'] = dfn
    # df8 = pd.merge(left=df8, right=dfnoprnt, left_on='JobNo', right_on='JobNo', how='outer')
    # df8 = df8.fillna(0)

    # DF9 IS FOR JOBS THAT ARE READY TO BE CHECKED BY QC
    df9 = df4.loc[df4['qc'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))
    if not df9.empty:
        dfm = df9['DueDate'].str.split(pat = '/').str[1]
        dfd = df9['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df9['ShowDate'] = dfn

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD IN ENGINEERING
    df10 = df4.loc[df4['hold'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))
    if not df3lsr.empty:
        dfm = df10['DueDate'].str.split(pat = '/').str[1]
        dfd = df10['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df10['ShowDate'] = dfn

    # DF11 IS FOR ONLY JOBS THAT HAVE NO CUSTOMER MODELS
    df11a = df4.loc[df4['User_Text3'] == 'NEW']
    df11b = df4.loc[df4['User_Text3'] == 'REVISION']
    df11c = pd.concat([df11a, df11b])
    df11 = df11c.loc[df11c['model'] != 'on']
    df11 = df11.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF12 IS FOR ONLY REPEAT JOBS THAT ARE MISSING PRINTS
    df12a = df3lsr
    df12a1 = df12a.sort_values(by=['WorkCntr_y'])
    df12a2 = df12a1.drop_duplicates(subset = ['JobNo'])
    df12a3 = df12a2.sort_values(by = ['JobNo'])
    df12a = df12a3
    df12b = dfnoprnt
    df12bl = df12b.values.tolist()
    for d in df12bl:
        df12a = df12a.loc[df12a['JobNo'] != d[2]]
    df12 = df12a

    return [df5, df6, df7, df8, df9, df10, df11, df12]





def dbmach():
    # MACHINING
    # server = '10.0.1.120\E2SQL'
    # server = '10.0.1.224\E2SQLSERVER'

    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    # db = 'MONARCH'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, D.QtyOrdered, D.QtyToStock \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='104 MACH' AND O.User_Text3!='UNCONFIRMED'"""
    sql1 = """SELECT R.JobNo, R.WorkCntr \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='301 SAW') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='302 MILL') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='303 LATHE') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='306 TAP')"""
    sql2 ="""SELECT P.PartNo, P.DocNumber, R.JobNo \
                       FROM PartFiles P INNER JOIN OrderDet D ON P.PartNo=D.PartNo INNER JOIN OrderRouting R ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                       WHERE D.Status='Open' AND D.User_Text3='Repeat' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='104 MACH' AND O.User_Text3!='UNCONFIRMED'"""

    df1 = pd.read_sql(sql, con=cnxn)
    df1['QtyOpen'] = df1['QtyOrdered'] + df1['QtyToStock']
    dflsr = pd.read_sql(sql1, con=cnxn)
    dfnoprnt = pd.read_sql(sql2, con=cnxn)

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM mjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')
    df3lsr = pd.merge(left=df3, right=dflsr, left_on='JobNo', right_on='JobNo')
    df3lsr['DueDate'] = df3lsr['DueDate'].dt.strftime('%m/%d')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'StepNo', 'QtyOrdered', 'QtyToStock']]
    if not df4.empty:
        df4['DueDate'] = df4['DueDate'].dt.strftime('%m/%d')

    # DF5 IS FOR ALL JOBS IN MACHINING
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS IN MACHINING
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)

    # DF7 IS FOR ONLY FUTURE JOBS IN MACHINING (NO REPEATS)
    df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df7.loc[df7['User_Text3'] != 'REPEAT']
    df7 = df7.sort_values(by=['DueDate'], ascending = True)

    # DF8 IS FOR ONLY REPEAT JOBS IN MACHINING (SORT TOWER IN ROUTES.PY)
    df8 = df3lsr
    df8 = df8.sort_values(by=['DueDate'], ascending = True)

    # DF9 IS FOR JOBS THAT ARE READY TO BE CHECKED BY QC
    # df9 = df4.loc[df4['qc'] == 'on']
    # df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD IN MACHINING
    df10 = df4.loc[df4['hold'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF12 IS FOR ONLY REPEAT JOBS THAT ARE MISSING PRINTS
    df12a = df3lsr
    df12a1 = df12a.sort_values(by=['WorkCntr_y'])
    df12a2 = df12a1.drop_duplicates(subset = ['JobNo'])
    df12a3 = df12a2.sort_values(by = ['JobNo'])
    df12a = df12a3
    df12b = dfnoprnt
    df12bl = df12b.values.tolist()
    for d in df12bl:
        df12a = df12a.loc[df12a['JobNo'] != d[2]]
    df12 = df12a

    return [df5, df6, df7, df8, df10, df12]





def dbsl():
    # STATIC LASER
    # server = '10.0.1.120\E2SQL'
    # server = '10.0.1.224\E2SQLSERVER'

    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    # db = 'MONARCH'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.JobNo, R.WorkCntr, R.Status, D.PartNo, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.DueDate, O.CustCode \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='213 SLASER'"""
    df1 = pd.read_sql(sql, con=cnxn)
    dfl = df1.values.tolist()

    # ACTIVE STATIC JOBS
    jn = []
    for f in dfl:
        jn.append(f[0])

    folder = '00000.1 TIME'
    nc = 'NC'
    pul = 'PULSAR'
    mit = 'MITSUBISHI'
    server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
    # puls = os.listdir(server+'/'+folder+'/'+nc+'/'+pul)
    puls = os.listdir(server+'/'+folder+'/'+pul)
    # mits = os.listdir(server+'/'+folder+'/'+nc+'/'+mit)
    mits = os.listdir(server+'/'+folder+'/'+mit)

    # PULSAR
    pl = []
    for fil in puls:
        f = fil[:6]
        if f.isnumeric():
            pl.append(f)
    pl = list(dict.fromkeys(pl))
    rmp = [x for x in pl if x not in jn]
    rmp.sort()

    # MITSUBISHI
    mt = []
    for fil in mits:
        f = fil[:6]
        if f.isnumeric():
            mt.append(f)
    mt = list(dict.fromkeys(mt))
    rmm = [x for x in mt if x not in jn]
    rmm.sort()

    return [rmp, rmm]





def dbfl():
    # FIXTURE LASER
    # server = '10.0.1.120\E2SQL'
    # server = '10.0.1.224\E2SQLSERVER'

    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    # db = 'MONARCH'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.JobNo, R.WorkCntr, R.Status, D.PartNo, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.DueDate, O.CustCode \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='212 FLASER'"""
    df1 = pd.read_sql(sql, con=cnxn)
    dfl = df1.values.tolist()

    # ACTIVE FIXTURE JOBS
    jn = []
    for f in dfl:
        jn.append(f[3])
    jn = list(dict.fromkeys(jn))

    folder = '00000.1 TIME'
    nc = 'NC'
    pul = 'PULSAR'
    fix = 'FLASER'
    server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
    # puls = os.listdir(server+'/'+folder+'/'+nc+'/'+pul+'/'+fix)
    puls = os.listdir(server+'/'+folder+'/'+pul+'/'+fix)

    pl = []
    for fil in puls:
        f = fil.split()[0]
        pl.append(f)
    pl = list(dict.fromkeys(pl))
    rmfl = [x for x in pl if x not in jn]
    rmfl.sort()

    return rmfl





def dbpp():
    # PUNCH PROGRAMS
    # server = '10.0.1.120\E2SQL'
    # server = '10.0.1.224\E2SQLSERVER'

    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    # db = 'MONARCH'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.JobNo, R.WorkCntr, R.Status, D.PartNo, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.DueDate, O.CustCode \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='202 PUNCH'"""
    df1 = pd.read_sql(sql, con=cnxn)
    dfl = df1.values.tolist()

    # ACTIVE PUNCH JOBS
    jn = []
    for f in dfl:
        jn.append(f[0])

    folder = '00000.1 TIME'
    nc = 'NC'
    mur = 'MURATA'
    vip = 'VIPROS'
    server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
    # murs = os.listdir(server+'/'+folder+'/'+nc+'/'+mur)
    murs = os.listdir(server+'/'+folder+'/'+mur)
    # vips = os.listdir(server+'/'+folder+'/'+nc+'/'+vip)
    vips = os.listdir(server+'/'+folder+'/'+vip)

    # MURATA
    mp = []
    for fil in murs:
        f = fil[:6]
        if f.isnumeric():
            mp.append(f)
    mp = list(dict.fromkeys(mp))
    rmr = [x for x in mp if x not in jn]
    rmr.sort()

    # VIPROS
    vp = []
    for fil in vips:
        f = fil[:6]
        if f.isnumeric():
            vp.append(f)
    vp = list(dict.fromkeys(vp))
    rmv = [x for x in vp if x not in jn]
    rmv.sort()

    return [rmr, rmv]





def dbemail():
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3,\
                   D.DueDate, O.CustCode, D.QuoteNo, Q.QuotedBy, O.PurchContact, C.Contact, C.Email, D.MasterJobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN QUOTE Q ON D.QuoteNo=Q.QuoteNo \
                   INNER JOIN Contacts C ON O.CustCode=C.CODE \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='101 ENGIN' AND O.User_Text3!='UNCONFIRMED'"""
    sql1 = """SELECT R.JobNo, R.WorkCntr \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='203 LASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='211 TLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='201 SHEAR') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='202 PUNCH') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='212 FLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='213 SLASER') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='301 SAW') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='402 WELD') or \
                   (D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND D.User_Text3='REPEAT' AND R.WorkCntr='702 ASSEM')"""
    sql2 ="""SELECT P.PartNo, P.DocNumber, R.JobNo \
                       FROM PartFiles P INNER JOIN OrderDet D ON P.PartNo=D.PartNo INNER JOIN OrderRouting R ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                       WHERE D.Status='Open' AND D.User_Text3='Repeat' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='101 ENGIN' AND O.User_Text3!='UNCONFIRMED'"""

    df1 = pd.read_sql(sql, con=cnxn)
    dflsr = pd.read_sql(sql1, con=cnxn)
    dfnoprnt = pd.read_sql(sql2, con=cnxn)

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM jobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model', 'nest']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')
    df3lsr = pd.merge(left=df3, right=dflsr, left_on='JobNo', right_on='JobNo')
    df3lsr['DueDate'] = df3lsr['DueDate'].dt.strftime('%m/%d')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'StepNo', 'qcn', \
               'model', 'QuoteNo', 'QuotedBy', 'PurchContact', 'Contact', 'Email', 'MasterJobNo']]
    # df4['DueDate'] = df4['DueDate'].dt.strftime('%m/%d')
    df4 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS IN ENGINEERING
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)

    # DF7 IS FOR ONLY FUTURE JOBS IN ENGINEERING (NO REPEATS)
    df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df7.loc[df7['User_Text3'] != 'REPEAT']
    df7 = df7.sort_values(by=['DueDate'], ascending = True)

    # DETERMINE IF WE HAVE A MODEL IN QUOTE FOLDER FOR EACH JOB IN FUTURE / TBR
    df8 = df6[['CustCode', 'QuoteNo', 'JobNo', 'PartNo', 'QuotedBy', 'PurchContact', 'Contact', 'Email', 'MasterJobNo']]
    df9 = df7[['CustCode', 'QuoteNo', 'JobNo', 'PartNo', 'QuotedBy', 'PurchContact', 'Contact', 'Email', 'MasterJobNo']]
    dfe = df8.append(df9)

    le = dfe.values.tolist()
    # print(le)
    ve = []
    for l in le:
        cust = l[0]
        quote = l[1]
        job = l[2]
        part = l[3]
        quotedby = l[4]
        pcontact = l[5]
        contact = l[6]
        email = l[7]
        master = l[8]

        # if master != None:
        #     sqlm = """SELECT QuoteNo FROM OrderDet WHERE JobNo="""+master+""" """
        #     dfm = pd.read_sql(sqlm, con=cnxn)

        if quote == None:
            quote = '0'

        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=estimation/Quotes'
        path = server+'/'+cust+'/'+quote
        d = os.path.exists(server+'/'+cust+'/'+quote)
        if d == True:
            r = []
            r += [each for each in os.listdir(path) if each.lower().endswith(('.stp', '.dxf', '.dwg', '.step', '.igs', '.iges', '.sldprt'))]
            z = []
            z += [each for each in os.listdir(path) if each.lower().endswith('.txt')]
            if z:
                ve.append([job, 3, cust, quote, part, quotedby, pcontact, contact, email, master])
            else:
                if not r:
                    ve.append([job, 0, cust, quote, part, quotedby, pcontact, contact, email, master])
                else:
                    ve.append([job, 1, cust, quote, part, quotedby, pcontact, contact, email, master])
        else:
            ve.append([job, 2, cust, quote, part, quotedby, pcontact, contact, email, master])

    ge=[]
    for v in ve:
        if v[6] == v[7]:
            ge.append(v)

    # REMOVE JOBS WITH NO MODEL.TXT
    xe=[]
    for g in ge:
        if g[1] != 3:
            xe.append(g)

    # IF WE HAVE A MODEL IN THE FOLDER UPDATE THE WEBSITE AUTOMATICALLY
    for x in xe:
        if x[1] == 1:
            j = 'on'
            k = x[0]
            db = "database.db"
            conn = None
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("""UPDATE jobs SET model == ? WHERE job = ?""",(j,k))
            conn.commit()

    return xe





def ships():
    # SHIPMENT SUMMARY
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT T.DelTicketNo, T.OrderNo, T.CustCode, T.CustDesc, T.ShipDate, T.DTPrinted, T.CustPONum, D.JobNo, D.PartNo, D.ContactName, D.Qty2Ship, C.Contact, C.Email, O.DueDate \
                   FROM DelTicket T INNER JOIN DelTicketDet D ON T.DelTicketNo=D.DelTicketNo INNER JOIN Contacts C ON D.ContactName=C.Contact INNER JOIN OrderDet O ON D.JobNo=O.JobNo \
                   WHERE T.ShipDate >= cast(GETDATE() as date) AND T.DTPrinted = 'Y'"""
    df = pd.read_sql(sql, con=cnxn)
    print(df)
    return df





def dbpb():
    # PRESS BRAKE
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.JobNo, R.WorkCntr, R.Status, D.PartNo, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.DueDate, O.CustCode, D.User_Number1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.Status!='Pending' AND R.WorkCntr='204 BRAKE' AND D.User_Text2='3. WIP'"""
    df1 = pd.read_sql(sql, con=cnxn)
    dff = df1.values.tolist()

    fe = []
    se = []
    xe = []
    ye = []
    ze = []
    r = []
    for f in dff:
        job = f[0]
        wip = f[10]
        part = f[3]
        rev = f[4]
        qty = f[5]
        jtype = f[7]
        due = f[8]
        cust = f[9]
        # SOLIDWORKS FILE
        cad = 'CAD'
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        path = server+'/'+cust+'/'+part+'/'+cad
        d = os.path.exists(path)
        r = []
        if d == True:
            r += [each for each in os.listdir(path) if each.lower().endswith(('.stp', '.step', '.sldprt'))]
            if not r:
                fe.append([wip, job, 0, cust, part, rev, qty, jtype, due])
            else:
                fe.append([wip, job, 1, cust, part, rev, qty, jtype, due])
        # FORMING PROGRAM
        form = 'FORMING'
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        path = server+'/'+cust+'/'+part+'/'+form
        e = os.path.exists(path)
        if e == True:
            print('true')
            s = []
            s += [each for each in os.listdir(path) if each.lower().endswith(('.pbpp'))]
            if not s:
                se.append([job, 0])
            else:
                se.append([job, 1])
                for x in s:
                    if x.startswith('S2'):
                        xe.append([job, 1])
                    else:
                        xe.append([job, 0])
                for y in s:
                    if y.startswith('S3'):
                        ye.append([job, 1])
                    else:
                        ye.append([job, 0])
                for z in s:
                    if z.startswith('AP'):
                        ze.append([job, 1])
                    else:
                        ze.append([job, 0])
        else:
            print('false')
            print(part)
    xee = []
    for x in xe:
        if x[1] == 1:
            xee.append(x[0])
    xxe = []
    for c in xee:
        if c not in xxe:
            xxe.append(c)

    yee = []
    for y in ye:
        if y[1] == 1:
            yee.append(y[0])
    yye = []
    for c in yee:
        if c not in yye:
            yye.append(c)

    zee = []
    for z in ze:
        if z[1] == 1:
            zee.append(z[0])
    zze = []
    for c in zee:
        if c not in zze:
            zze.append(c)

    for s in se:
        if s[0] in xxe:
            s.append(1)
        else:
            s.append(0)
        if s[0] in yye:
            s.append(1)
        else:
            s.append(0)
        if s[0] in zze:
            s.append(1)
        else:
            s.append(0)
    fe.sort(key = lambda i : i[1])
    # print('fe')
    # print(len(fe))
    # for f in fe:
    #     print(f)
    se.sort(key = lambda i : i[0])
    # print('se')
    # print(len(se))
    # for s in se:
    #     print(s)
    xx = [a + [b[2]] + [b[3]] + [b[4]] for (a,b) in zip(fe, se)]
    xx.sort(key = lambda i : i[1])
    xx.sort(reverse = True, key = lambda i : i[0])
    return xx





def dbsaw():
    # SAW SCHEDULER
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='301 SAW'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                    FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                    WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='301 SAW' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='104 MACH') \
                   OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='104 MACH')"""
    df1 = pd.read_sql(sql, con=cnxn)
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    df4['User_Date1'] = df4['User_Date1'].fillna('-')

    # DF5 IS FOR ALL JOBS ON SAW
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON SAW
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON SAW
    # df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON SAW
    # df8 = df4.loc[df4['mtl'] == 'on']
    df8 = df4.loc[(df4['mtl'] == 'on') & (df4['pgm'] != 'on')]
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON SAW
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER SAW
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))


    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': '      '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)


    return [df5, df6, df7, df8, df9, df10, df11, df12]





def shipdeliv():
    # SHIPPING
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT T.DelTicketNo, T.OrderNo, T.CustCode, T.ShipDate, T.DTPrinted, T.CustPONum, D.JobNo, D.PartNo, D.Qty2Ship, O.DueDate, P.Status, P.User_Text2, P.ShipVia, P.User_Currency1, D.MasterJobNo, T.AutoBill \
                   FROM DelTicket T INNER JOIN DelTicketDet D ON T.DelTicketNo=D.DelTicketNo INNER JOIN OrderDet O ON D.JobNo=O.JobNo INNER JOIN Orders P ON T.OrderNo=P.OrderNo \
                   WHERE T.DTPrinted = 'Y' AND T.DelTicketNo >= '73050' AND D.MasterJobNo = ''"""
    df = pd.read_sql(sql, con=cnxn)

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM ship;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'date', 'track', 'delv']

    df3 = pd.merge(left=df, right=df2, left_on='JobNo', right_on='job')
    df3l = df3.values.tolist()
    for d in df3l:
        if d[15] == 'Y':
            d[20] = 'on'
    df3 = DataFrame(df3l, columns=['DelTicketNo', 'OrderNo', 'CustCode', 'ShipDate', 'DTPrinted', 'CustPONum', 'JobNo', 'PartNo', 'Qty2Ship', 'DueDate', 'Status', 'User_Text2', 'ShipVia', 'User_Currency1', \
                                   'MasterJobNo', 'AutoBill', 'id', 'job', 'date', 'track', 'delv'])
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df4)

    # NOT IDENTIFIED SHIPPING
    dfn = df3.loc[(df3['User_Text2'] != 'PARTIAL') & (df3['User_Text2'] != 'FULL') & (df3['delv'] != 'on')]

    # PARTIAL SHIPPING
    dfp = df3.loc[(df3['User_Text2'] == 'PARTIAL') & (df3['delv'] != 'on')]

    # FULL SHIPPING - NOT SENT
    dff = df3.loc[(df3['User_Text2'] == 'FULL') & (df3['delv'] != 'on') & (df3['Status'] == 'O')]

    # FULL SHIPPING - SENT
    dfs = df3.loc[(df3['User_Text2'] == 'FULL') & (df3['delv'] != 'on') & (df3['Status'] == 'C')]

    # DELIVERED
    dfd = df3.loc[df3['delv'] == 'on']

    return [dfn, dfp, dff, dfs, dfd]





def dblp():
    # LASER - FOR PROGRAMS NEEDED TO BE NESTED
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, R.EstimQty, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='203 LASER'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN'"""
    df1 = pd.read_sql(sql, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # d2 = cur.execute("SELECT * FROM tjobs;")
    # df2 = DataFrame(d2.fetchall())
    # df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']
    d2 = cur.execute("SELECT * FROM jobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model', 'nest']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'EstimQty', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'nest']]

    # DFN IF FOR JOBS THAT NEED TO BE NESTED
    dfn = df4.loc[(df4['User_Text2'] == '2. TBR') & (df4['nest'] != 'on')]
    dfn = dfn.sort_values(by=['User_Number3'], ascending = True)

    # DFD IS FOR JOBS THAT HAVE BEEN NESTED
    dfd = df4.loc[(df4['User_Text2'] == '2. TBR') & (df4['nest'] == 'on')]
    dfd = dfd.sort_values(by=['User_Number3'], ascending = True)

    return [dfn, dfd]





def dbshear():
    # SHEAR
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='201 SHEAR'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='201 SHEAR' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENG') \
                   OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENG')"""
    df1 = pd.read_sql(sql, con=cnxn)
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    # df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'StepNo', 'qcn', 'model']]
    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    df4['User_Date1'] = df4['User_Date1'].fillna('-')

    # DF5 IS FOR ALL JOBS ON SHEAR
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON SHEAR
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON SHEAR
    # df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON SHEAR
    # df8 = df4.loc[df4['mtl'] == 'on']
    df8 = df4.loc[(df4['mtl'] == 'on') & (df4['pgm'] != 'on')]
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON SHEAR
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER SHEAR
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))

    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': '      '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)

    return [df5, df6, df7, df8, df9, df10, df11, df12]





def dbslaser():
    # SLASER
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='213 SLASER'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='213 SLASER' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENG') \
                   OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENG')"""
    df1 = pd.read_sql(sql, con=cnxn)
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # d2 = cur.execute("SELECT * FROM jobs;")
    # df2 = DataFrame(d2.fetchall())
    # df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model', 'nest']
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    # df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'StepNo', 'qcn', 'model']]
    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].fillna('-')

    # DF5 IS FOR ALL JOBS ON SLASER
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON SLASER
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON SLASER
    # df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON SLASER
    # df8 = df4.loc[df4['mtl'] == 'on']
    df8 = df4.loc[(df4['mtl'] == 'on') & (df4['pgm'] != 'on')]
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON SLASER
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER SLASER
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))

    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': ' '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)

    return [df5, df6, df7, df8, df9, df10, df11, df12]





def dbpunch():
    # PUNCH
    server = '10.0.1.130\E2SQLSERVER'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='202 PUNCH'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='202 PUNCH' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENG') \
                   OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENG')"""
    df1 = pd.read_sql(sql, con=cnxn)
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')

    # DF5 IS FOR ALL JOBS ON PUNCH
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON PUNCH
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON PUNCH
    # df7 = df4.loc[df4['User_Text2'] != '2. TBR']
    # df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON PUNCH
    df8 = df4.loc[(df4['mtl'] == 'on') & (df4['pgm'] != 'on')]
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON PUNCH
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER PUNCH
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))

    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': ' '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)

    return [df5, df6, df7, df8, df9, df10, df11, df12]





def dbflaser():
    # FLASER
    server = '10.0.1.130\E2SQLSERVER'
    # server = '10.0.1.130\E2SQLSERVER, 1433'
    db = 'MONARCH_SHOP'
    un = 'sa'
    pw = 'Mon@rch09'

    cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    # cnxn = p.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
    sql = """SELECT R.OrderNo, R.JobNo, R.StepNo, R.WorkCntr, R.Status, D.PartNo, D.PartDesc, D.Revision, D.QtyToMake, D.User_Text2, D.User_Text3, D.User_Number3, D.DueDate, O.CustCode, E.User_Memo1, D.User_Date1 \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo INNER JOIN Estim E ON D.PartNo=E.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='212 FLASER'"""
    sql2 = """SELECT R.JobNo, D.PartNo, M.SubPartNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN Materials M ON D.PartNo=M.PartNo\
                   WHERE D.Status='Open' AND R.Status!='Finished' AND R.Status!='Closed' AND R.WorkCntr='212 FLASER' AND M.Purchased='1'"""
    sql11 = """SELECT R.JobNo \
                   FROM OrderRouting R INNER JOIN OrderDet D ON R.JobNo=D.JobNo INNER JOIN ORDERS O ON D.OrderNo=O.OrderNo \
                   WHERE (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Finished' AND R.WorkCntr='101 ENG') \
                   OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENGIN') OR (D.Status='Open' AND R.Status='Closed' AND R.WorkCntr='101 ENG')"""
    df1 = pd.read_sql(sql, con=cnxn)
    df2n = pd.read_sql(sql2, con=cnxn)
    df11 = pd.read_sql(sql11, con=cnxn)
    df12 = pd.merge(left=df1, right=df11, left_on='JobNo', right_on='JobNo')
    df32 = pd.merge(left=df2n, right=df11, left_on='JobNo', right_on='JobNo')

    df1 = df12

    db = "database.db"
    conn = None
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # d2 = cur.execute("SELECT * FROM jobs;")
    # df2 = DataFrame(d2.fetchall())
    # df2.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model', 'nest']
    d2 = cur.execute("SELECT * FROM tjobs;")
    df2 = DataFrame(d2.fetchall())
    df2.columns = ['id', 'job', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']

    df3 = pd.merge(left=df1, right=df2, left_on='JobNo', right_on='job')

    # df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'StepNo', 'qcn', 'model']]
    df4 = df3[['JobNo', 'PartNo', 'Revision', 'QtyToMake', 'DueDate', 'CustCode', 'User_Text3', 'User_Text2', 'User_Number3', 'OrderNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn', 'User_Memo1', 'StepNo', 'User_Date1']]
    df4['DueDate'] = df4['DueDate'].dt.strftime('%Y/%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].dt.strftime('%m/%d')
    # df4['User_Date1'] = df4['User_Date1'].fillna('-')

    # DF5 IS FOR ALL JOBS ON FLASER
    df5 = df4.sort_values(by=['JobNo'], ascending = True)

    # DF6 IS FOR ONLY TBR JOBS ON FLASER
    df6 = df4.loc[df4['User_Text2'] == '2. TBR']
    df6 = df6.sort_values(by=['User_Number3'], ascending = True)
    if not df6.empty:
        dfm = df6['DueDate'].str.split(pat = '/').str[1]
        dfd = df6['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df6['ShowDate'] = dfn

    # DF7 IS FOR ONLY FUTURE JOBS ON FLASER
    # df7 = df4.loc[df4['User_Text2'] == '1. OFFICE']
    df7 = df4.loc[(df4['User_Text2'] == '1. OFFICE') | (df4['User_Text2'] == '3. WIP')]
    df7 = df7.sort_values(by=['DueDate'], ascending = True)
    if not df7.empty:
        dfm = df7['DueDate'].str.split(pat = '/').str[1]
        dfd = df7['DueDate'].str.split(pat = '/').str[2]
        dfn = dfm +'/'+ dfd
        df7['ShowDate'] = dfn

    # DF8 IS FOR ONLY JOBS THAT NEED MATERIAL ON FLASER
    # df8 = df4.loc[df4['mtl'] == 'on']
    df8 = df4.loc[(df4['mtl'] == 'on') & (df4['pgm'] != 'on')]
    df8 = df8.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF9 IS FOR ONLY JOBS THAT ARE PROGRAMMED ON FLASER
    df9 = df4.loc[df4['pgm'] == 'on']
    df9 = df9.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF10 IS FOR ONLY JOBS THAT ARE ON HOLD
    df10 = df4.loc[df4['tlh'] == 'on']
    df10 = df10.sort_values(by=['User_Text2', 'DueDate'], ascending = (False, True))

    # DF11 IS FOR ONLY JOBS THAT HAVE MATERIAL ON ORDER FLASER
    df11 = df4.loc[df4['pgm'] == 'on']
    df11 = df11.sort_values(by=['pgmn', 'User_Text2', 'DueDate'], ascending = (True, False, True))

    #df12 IS TO SHOW ALL MATERIALS BEING USED AND THEIR JOB NUMBERS
    df3n = pd.merge(left=df32, right=df2, left_on='JobNo', right_on='job')
    df4n = df3n[['JobNo', 'PartNo', 'SubPartNo', 'id', 'mtl', 'mtln', 'pgm', 'pgmn', 'tlh', 'tlhn']]
    df4n['Verify'] = np.where(df4n['tlh']=='on', df4n['JobNo'], '')
    df4n['Check'] = np.where((df4n['tlh']!='on') & (df4n['mtl']!='on') & (df4n['pgm']!='on'), df4n['JobNo'], '')
    df4n['Need'] = np.where(df4n['mtl']=='on', df4n['JobNo'], '')
    df4n['Order'] = np.where(df4n['pgm']=='on', df4n['JobNo'], '')
    df12n = df4n.groupby(["SubPartNo"]).agg({'Verify': ' '.join, 'Check': ' '.join, 'Need': ' '.join, 'Order': ' '.join})
    df12n['index'] = df12n.index
    df12 = df12n.sort_values(by=['index'], ascending = True)

    return [df5, df6, df7, df8, df9, df10, df11, df12]
