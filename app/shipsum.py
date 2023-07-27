from app.dbcn import ships
# from dbcn import ships
import sqlite3
from sqlite3 import Error
from pandas import DataFrame
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tabulate import tabulate

def shipsum():
    df = ships()
    df = df[['CustPONum', 'DelTicketNo', 'PartNo', 'Qty2Ship','DueDate', 'JobNo', 'CustCode', 'Contact', 'Email']]
    df = df.rename(columns={'CustPONum': 'PO Number', 'DelTicketNo': 'Packing Slip', 'PartNo': 'Part Number', 'Qty2Ship': 'Qty', 'DueDate': 'Due Date', 'JobNo': 'Job Number', 'CustCode': 'Customer'})
    cont = df.Contact.unique()

    # EMAIL SETUP
    port = 465
    smtp_server = "mail.monarchmetalmfg.com"
    sender_email = "model@monarchmetalmfg.com"
    pw = '+4{-VUG!HcPQ'
    context = ssl.create_default_context()

    dfl = df.values.tolist()

    for x in cont:
        # print(x)
        lem = []
        for y in dfl:
            if x == y[7]:
                lem.append(y)
                email = y[8]
                contact = y[7]
                cust = y[6]
        # print(lem)
        # print(contact)
        # print(email)
        # print(cust)
        df = DataFrame(lem, columns=['PO Number', 'Packing Slip', 'Part Number', 'Qty', 'Due Date', 'Job Number', 'Customer', 'Contact', 'Email'])
        df =df.drop(['Due Date', 'Customer', 'Contact', 'Email'], axis = 1)

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

        # html = """\
        # <html>
        #     <head>
        #     </head>
        #     <body><p>Dear Stacey Ricketts,</p>
        #         <p>Today the following items had packing slips created in our system:</p>
        #         <style>
        #             table, th, td {{ text-align: center; border: 1px solid black; border-collapse: collapse; }}
        #             th, td {{ padding: 5px; }}
        #         </style>
        #             {0}
        #         <p>If we deliver to your location or ship UPS or FedEx they will be on their way shortly <br> If you are setup for will call or arrange freight they will be ready in our shipping department</p>
        #         <p>*This is an automated email, do not respond. Please contact your sales representation if you have any questions or concerns</p>
        #     </body>
        # </html>
        # """.format(df.to_html(index=False))

        part1 = MIMEText(html, 'html')

        # nqt=[]
        # for d in dfl:
        #     txt = "Customer: "+d[5]+""
        #     nqt.append(txt)

        # if nqt:
        # nqts = "\n".join(nqt)
        # rec_email = "brentw@monarchmetalmfg.com"
        rec_email = "cjs@monarchmetalmfg.com"
        # rec_email = "zechariah.williams@stollemachinery.com"
        # rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com", "zechariah.williams@stollemachinery.com"]
        # rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com", "stacey.ricketts@stollemachinery.com"]
        # rec_email = ["cjs@monarchmetalmfg.com", "brentw@monarchmetalmfg.com"]

        message = MIMEMultipart("alternative")
        # message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])
        message["Subject"] = 'Advanced Shipment Notice'
        message["From"] = sender_email
        message["To"] = rec_email
        # message["To"] = ", ".join(rec_email)
        message.attach(part1)

        # text = "The following are **********: \n\n"+html+"\n\nThis is an automated email"
        # part1 = MIMEText(text, "plain")
        # message.attach(part1)
        # if cust == 'STO':
        #     with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        #         server.login(sender_email, pw)
        #         server.sendmail(sender_email, rec_email, message.as_string())
        #         print('Email Sent')

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())
            print('Email Sent')
