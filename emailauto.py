import os
import pyodbc as p
import pandas as pd
from pandas import DataFrame
import sqlite3
from sqlite3 import Error
from os import listdir
from os.path import isfile, join
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tabulate import tabulate

    # SHIPMENT SUMMARY
print('running')
server = '10.0.1.130\E2SQLSERVER'
db = 'MONARCH_SHOP'
un = 'sa'
pw = 'Mon@rch09'

cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
sql = """SELECT T.DelTicketNo, T.OrderNo, T.CustCode, T.CustDesc, T.ShipDate, T.DTPrinted, T.CustPONum, D.JobNo, D.PartNo, D.ContactName, D.Qty2Ship, C.Contact, C.Email, O.DueDate \
                FROM DelTicket T INNER JOIN DelTicketDet D ON T.DelTicketNo=D.DelTicketNo INNER JOIN Contacts C ON D.ContactName=C.Contact INNER JOIN OrderDet O ON D.JobNo=O.JobNo \
                WHERE T.ShipDate >= cast(GETDATE() as date) AND T.DTPrinted = 'Y'"""
df = pd.read_sql(sql, con=cnxn)
print(df)

df = df[['CustPONum', 'DelTicketNo', 'PartNo', 'Qty2Ship','DueDate', 'JobNo', 'CustCode', 'Contact', 'Email']]
df = df.rename(columns={'CustPONum': 'PO Number', 'DelTicketNo': 'Packing Slip', 'PartNo': 'Part Number', 'Qty2Ship': 'Qty', 'DueDate': 'Due Date', 'JobNo': 'Job Number', 'CustCode': 'Customer'})
cont = df.Contact.unique()

    # EMAIL SETUP
port = 465
smtp_server = "mail.monarchmetalmfg.com"
sender_email = "shipschedule@monarchmetalmfg.com"
pw = 'Xm@*c;ej9N~g'
context = ssl.create_default_context()

df = df.drop_duplicates()
df = df[(df != 0).all(1)]
dfl = df.values.tolist()

for x in cont:
    lem = []
    for y in dfl:
        if x == y[7]:
            lem.append(y)
            email = y[8]
            contact = y[7]
            cust = y[6]
    df = DataFrame(lem, columns=['PO Number', 'Packing Slip', 'Part Number', 'Qty', 'Due Date', 'Job Number', 'Customer', 'Contact', 'Email'])
    df =df.drop(['Due Date', 'Customer', 'Contact', 'Email'], axis = 1)
    print(email)

    if cust == 'STO':
        html = """\
        <html>
            <head>
            </head>
            <body><p>Dear Stacey Ricketts,</p>
                <p>Today the following items had packing slips created in our system:</p>
                <style>
                    table, th, td {{ text-align: center; border: 1px solid black; border-collapse: collapse; }}
                    th, td {{ padding: 5px; }}
                </style>
                    {0}
                <p>If we deliver to your location or ship UPS or FedEx they will be on their way shortly <br> If you are setup for will call or arrange freight they will be ready in our shipping department</p>
                <p>*This is an automated email, do not respond. Please contact your sales representation if you have any questions or concerns</p>
            </body>
        </html>
        """.format(df.to_html(index=False))

        part1 = MIMEText(html, 'html')

        # rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com", "stacey.ricketts@stollemachinery.com"]
        # rec_email = ["cjs@monarchmetalmfg.com"]
        rec_email = ["stacey.ricketts@stollemachinery.com"]

        message = MIMEMultipart("alternative")
        message["Subject"] = 'Advanced Shipment Notice'
        message["From"] = sender_email
        message["To"] = ", ".join(rec_email)
        message.attach(part1)

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())
            print('Email Sent')
    else:
        html = """\
        <html>
            <head>
            </head>
            <body><p>Dear """ +str(contact)+ """,</p>
                <p>Today the following items had packing slips created in our system:</p>
                <style>
                    table, th, td {{ text-align: center; border: 1px solid black; border-collapse: collapse; }}
                    th, td {{ padding: 5px; }}
                </style>
                    {0}
                <p>If we deliver to your location or ship UPS or FedEx they will be on their way shortly <br> If you are setup for will call or arrange freight they will be ready in our shipping department</p>
                <p>*This is an automated email, do not respond. Please contact your sales representation if you have any questions or concerns</p>
            </body>
        </html>
        """.format(df.to_html(index=False))

        part1 = MIMEText(html, 'html')

    # nqt=[]
    # for d in dfl:
    #     txt = "Customer: "+d[5]+""
    #     nqt.append(txt)

    # if nqt:
    # nqts = "\n".join(nqt)
    # rec_email = "brentw@monarchmetalmfg.com"
        # rec_email = "cjsand03@gmail.com"
    # rec_email = "zechariah.williams@stollemachinery.com"
        # rec_email = "cjs@monarchmetalmfg.com"
        rec_email = email
        # rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com"]

        message = MIMEMultipart("alternative")
    # message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])
        message["Subject"] = 'Advanced Shipment Notice'
        message["From"] = sender_email
    # message["To"] = rec_email
        message["To"] = ", ".join(rec_email)
        message.attach(part1)

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())
            print('Email Sent')



df = DataFrame(dfl, columns=['PO Number', 'Packing Slip', 'Part Number', 'Qty', 'Due Date', 'Job Number', 'Customer', 'Contact', 'Email'])
df =df.drop(['Due Date', 'Contact', 'Email'], axis = 1)

html = """\
<html>
    <head>
    </head>
    <body><p>Monarch Staff,</p>
        <p>Today the following items had packing slips created in our system:</p>
        <style>
            table, th, td {{ text-align: center; border: 1px solid black; border-collapse: collapse; }}
            th, td {{ padding: 5px; }}
        </style>
            {0}
        <p>*This is an automated email, do not respond.</p>
    </body>
</html>
""".format(df.to_html(index=False))

part1 = MIMEText(html, 'html')

# rec_email = ["cjs@monarchmetalmfg.com"]
# rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com", "shipping@monarchmetalmfg.com", "customerservice@monarchmetalmfg.com"]
rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com", "shipping@monarchmetalmfg.com"]

message = MIMEMultiparta"alternative")
message["Subject"] = 'Combined Advanced Shipment Notice'
message["From"] = sender_email
message["To"] = ", ".join(rec_email)
message.attach(part1)

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, pw)
    server.sendmail(sender_email, rec_email, message.as_string())
    print('Email Sent')
