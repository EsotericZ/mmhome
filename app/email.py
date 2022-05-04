from app.dbcn import dbemail
import sqlite3
from sqlite3 import Error
from pandas import DataFrame
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email():
    xe = dbemail()

    # CHECK TO SEE IF THE MODEL WAS ADDED MANUALLY AND UPDATE XE IF SO
    for x in xe:
        job = x[0]
        db = "database.db"
        conn = None
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        d = cur.execute("SELECT * FROM jobs WHERE job = "+job+";")
        df = DataFrame(d.fetchall())
        df.columns = ['id', 'job', 'eng', 'wip', 'hold', 'hrsn', 'qc', 'apr', 'qcn', 'model']

        le = df.values.tolist()
        if le[0][9] == 'on':
            x[1] = 1



    # EMAIL SETUP
    port = 465
    smtp_server = "mail.monarchmetalmfg.com"
    sender_email = "model@monarchmetalmfg.com"
    pw = 'fV;+$%BkjY{8'
    context = ssl.create_default_context()

    bwq=[]
    csq=[]
    brq=[]
    ssq=[]
    swq=[]
    for x in xe:

        # BRENT W (12)
        if x[5] == '12' or x[5] == '0':
            bwq.append(x)

        # CJ (206)
        if x[5] == '206':
            csq.append(x)

        # # BRANDON W (120)
        # if x[5] == '120':
        #     brq.append(x)

        # # SAM S (137)
        # if x[5] == '137':
        #     ssq.append(x)

        # # STAN W (13)
        # if x[5] == '13':
        #     swq.append(x)



# # # # # BRENT # # # # #

    # PARTS WITH NO QUOTE FOLDER
    nq = []
    for x in bwq:
        if x[1] == 2:
            nq.append(x)
    nqt = []
    for n in nq:
        txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+""
        nqt.append(txt)

    if nqt:
        nqts = "\n".join(nqt)
        # rec_email = "brentw@monarchmetalmfg.com"
        rec_email = "cjs@monarchmetalmfg.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = 'No Quote Folder'
        message["From"] = sender_email
        message["To"] = rec_email

        text = "The following do not have a quote folder in TOWER: \n\n"+nqts+"\n\nThis is an automated email"
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())

    # PARTS WITH NO MODEL
    nm = []
    for x in bwq:
        if x[1] == 0:
            nm.append(x)
    nmt = []
    for n in nm:
        txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+"\nContact: "+n[6]+"     Email: "+n[8]+""
        nmt.append(txt)

    if nmt:
        nmts = "\n".join(nmt)
        # rec_email = "brentw@monarchmetalmfg.com"
        rec_email = "cjs@monarchmetalmfg.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = 'No Model'
        message["From"] = sender_email
        message["To"] = rec_email

        text = "The following jobs do not have customer supplied models: \n\n"+nmts+"\n\nThis is an automated email"
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())



# # # # # CJ # # # # #

    # PARTS WITH NO QUOTE FOLDER
    nq = []
    for x in csq:
        if x[1] == 2:
            nq.append(x)
    nqt = []
    for n in nq:
        txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+""
        nqt.append(txt)

    if nqt:
        nqts = "\n".join(nqt)
        rec_email = "cjs@monarchmetalmfg.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = 'No Quote Folder'
        message["From"] = sender_email
        message["To"] = rec_email

        text = "The following do not have a quote folder in TOWER: \n\n"+nqts+"\n\nThis is an automated email"
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())

    # PARTS WITH NO MODEL
    nm = []
    for x in csq:
        if x[1] == 0:
            nm.append(x)
    nmt = []
    for n in nm:
        txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+"\nContact: "+n[6]+"     Email: "+n[8]+""
        nmt.append(txt)

    if nmt:
        nmts = "\n".join(nmt)
        rec_email = "cjs@monarchmetalmfg.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = 'No Model'
        message["From"] = sender_email
        message["To"] = rec_email

        text = "The following jobs do not have customer supplied models: \n\n"+nmts+"\n\nThis is an automated email"
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, rec_email, message.as_string())



# # # # # # BRANDON # # # # #

#     # PARTS WITH NO QUOTE FOLDER
#     nq = []
#     for x in brq:
#         if x[1] == 2:
#             nq.append(x)
#     nqt = []
#     for n in nq:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+""
#         nqt.append(txt)

#     if nqt:
#         nqts = "\n".join(nqt)
#         rec_email = "brandonw@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Quote Folder'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following do not have a quote folder in TOWER: \n\n"+nqts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())

#     # PARTS WITH NO MODEL
#     nm = []
#     for x in brq:
#         if x[1] == 0:
#             nm.append(x)
#     nmt = []
#     for n in nm:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+"\nContact: "+n[6]+"     Email: "+n[8]+""
#         nmt.append(txt)

#     if nmt:
#         nmts = "\n".join(nmt)
#         rec_email = "brandonw@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Model'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following jobs do not have customer supplied models: \n\n"+nmts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())



# # # # # # SAM # # # # #

#     # PARTS WITH NO QUOTE FOLDER
#     nq = []
#     for x in ssq:
#         if x[1] == 2:
#             nq.append(x)
#     nqt = []
#     for n in nq:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+""
#         nqt.append(txt)

#     if nqt:
#         nqts = "\n".join(nqt)
#         rec_email = "sams@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Quote Folder'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following do not have a quote folder in TOWER: \n\n"+nqts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())

#     # PARTS WITH NO MODEL
#     nm = []
#     for x in ssq:
#         if x[1] == 0:
#             nm.append(x)
#     nmt = []
#     for n in nm:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+"\nContact: "+n[6]+"     Email: "+n[8]+""
#         nmt.append(txt)

#     if nmt:
#         nmts = "\n".join(nmt)
#         rec_email = "sams@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Model'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following jobs do not have customer supplied models: \n\n"+nmts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())



# # # # # # STAN # # # # #

#     # PARTS WITH NO QUOTE FOLDER
#     nq = []
#     for x in swq:
#         if x[1] == 2:
#             nq.append(x)
#     nqt = []
#     for n in nq:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+""
#         nqt.append(txt)

#     if nqt:
#         nqts = "\n".join(nqt)
#         rec_email = "stanw@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Quote Folder'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following do not have a quote folder in TOWER: \n\n"+nqts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())

#     # PARTS WITH NO MODEL
#     nm = []
#     for x in swq:
#         if x[1] == 0:
#             nm.append(x)
#     nmt = []
#     for n in nm:
#         txt = "Customer: "+n[2]+"     Quote No: "+n[3]+"     Job No: "+n[0]+"     Part No: "+n[4]+"\nContact: "+n[6]+"     Email: "+n[8]+""
#         nmt.append(txt)

#     if nmt:
#         nmts = "\n".join(nmt)
#         rec_email = "stanw@monarchmetalmfg.com"

#         message = MIMEMultipart("alternative")
#         message["Subject"] = 'No Model'
#         message["From"] = sender_email
#         message["To"] = rec_email

#         text = "The following jobs do not have customer supplied models: \n\n"+nmts+"\n\nThis is an automated email"
#         part1 = MIMEText(text, "plain")
#         message.attach(part1)
#         with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#             server.login(sender_email, pw)
#             server.sendmail(sender_email, rec_email, message.as_string())
