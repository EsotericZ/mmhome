from __future__ import unicode_literals
from xlwt import Workbook
import io
from werkzeug.utils import secure_filename

from flask import Flask, render_template, flash, redirect, request, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.scaleModels import Scale
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Job, TJob, MJob, Bendd, Ship, PageNotes, SawNotes, ShearNotes, PunchNotes, SLaserNotes, FLaserNotes, FormingNotes, MachiningNotes, EngNotes, Ent, EntNotes, PurchNotes, SupNotes, Todo, MTodo, Supplies, Taps, Directory, Hardware, MatlTL, TlmNotes
from werkzeug.urls import url_parse
from database import db_session
from datetime import datetime
from datetime import date as dt
from app.dbcn import dbtl, dbeng, dbmach, dbsl, dbfl, dbpp, dbemail, dbpb, dbsaw, shipdeliv, dblp, dbshear, dbslaser, dbpunch, dbflaser
# from app.ship import dbship
from app.shipsum import shipsum
# from app.invman import invman
from app.email import email
from app.scaleApi import *
from app.e2db import equip
import json
import pusher
import os
import pandas as pd
import numpy as np
import xlrd
import pyodbc as p
# import var

pusher_client = pusher.Pusher(
    app_id='807301',
    key='32d695007f6b78ffea0d',
    secret='a8f64240ccb736372743',
    cluster='us3',
    ssl=True)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
@app.route('/index')
def index():
    todos = Todo.query.order_by('id').all()
    return render_template('index.html', title='Monarch Home', todos=todos)

@app.route('/backend_todo', methods=["POST", "GET"])
def backend_todo():
    if request.method == "POST":
        rtype = request.form["rtype"]
        area = request.form["area"]
        desc = request.form["desc"]
        name = request.form["name"]
        done = request.form["done"]

        new_todo = Todo(rtype, area, desc, name, done)
        db_session.add(new_todo)
        db_session.commit()

        data = {
            "id": new_todo.id,
            "rtype": rtype,
            "area": area,
            "desc": desc,
            "name": name,
            "done": done
        }

        pusher_client.trigger('table', 'new-record-todo', {'data': data })

        return redirect("/index", code=302)
    else:
        todos = Todo.query.all()
        return render_template('backend_todo.html', todos=todos)

@app.route('/edit_todo/<int:id>', methods=["POST", "GET"])
def update_record_todo(id):
    if request.method == "POST":
        rtype = request.form["rtype"]
        area = request.form["area"]
        desc = request.form["desc"]
        name = request.form["name"]
        done = request.form["done"]

        update_todo = Todo.query.get(id)
        update_todo.rtype = rtype
        update_todo.area = area
        update_todo.desc = desc
        update_todo.name = name
        update_todo.done = done

        db_session.commit()

        data = {
            "id": id,
            "rtype": rtype,
            "area": area,
            "desc": desc,
            "name": name,
            "done": done
        }

        pusher_client.trigger('table', 'update-record-todo', {'data': data })

        return redirect("/index", code=302)
    else:
        new_todo = Todo.query.get(id)

        return render_template('update_todo.html', data=new_todo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/test')
@login_required
def test():
    return render_template('test.html')





# CHECK INTO THESE

# @app.route('/jobs')
# def jobs():
#     jobs = Job.query.all()
#     return render_template('jobs.html', jobs=jobs)

# @app.route('/review')
# def review():
#     jobs = Job.query.all()
#     return render_template('review.html', jobs=jobs)

# @app.route('/engineering')
# def engineering():
#     jobs = Job.query.all()
#     return render_template('engineering.html', jobs=jobs)

# @app.route('/production')
# def production():
#     jobs = Job.query.all()
#     return render_template('production.html', jobs=jobs)

# @app.route('/completed')
# def completed():
#     jobs = Job.query.all()
#     return render_template('completed.html', jobs=jobs)

@app.route('/construction')
def construction():
    return render_template('construction.html', title="Under Construction")





# # # ENGINEERING # # #

@app.route('/enghome')
def enghome():
    dbeng()
    shipdeliv()
    dbsl()
    return render_template('enghome.html')

@app.route('/tbr_eng')
def tbr_eng():
    df6 = dbeng()[1]
    eng = df6.values.tolist()
    return render_template('tbr_eng.html', eng=eng)

@app.route('/future_eng')
def future_eng():
    df7 = dbeng()[2]
    df7 = df7.sort_values(by = ['DueDate', 'JobNo'])
    eng = df7.values.tolist()
    # for i in reversed(range(len(eng))):
    #     if eng[i][5] == 'WESTERN':
    #         del eng[i]
    return render_template('future_eng.html', eng=eng)

@app.route('/repeat')
def repeat():
    df8 = dbeng()[3]
    df81 = df8.sort_values(by=['WorkCntr_y'])
    df82 = df81.drop_duplicates(subset = ['JobNo'])
    df83 = df82.sort_values(by = ['DueDate', 'JobNo'])
    en = df83.values.tolist()
    eng = []
    for e in en:
        cust = e[13]
        part = e[5]
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        d = os.path.exists(server+'/'+cust+'/'+part)
        if d == True:
            eng.append(e)
    df12 = dbeng()[7]
    df121 = df12.sort_values(by=['JobNo'])
    df122 = df121.drop_duplicates(subset = ['JobNo'])
    df123 = df122['JobNo']
    pr = df123.values.tolist()
    eng = [x + [0] for x in eng]
    for e in eng:
        if e[1] in pr:
            e[28] = 'x'
    return render_template('repeat.html', eng=eng)

@app.route('/repeat_add')
def repeat_add():
    df8 = dbeng()[3]
    df81 = df8.sort_values(by=['WorkCntr_y'])
    df82 = df81.drop_duplicates(subset = ['JobNo'])
    df83 = df82.sort_values(by = ['DueDate', 'JobNo'])
    en = df83.values.tolist()
    eng = []
    for e in en:
        cust = e[13]
        part = e[5]
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        d = os.path.exists(server+'/'+cust+'/'+part)
        if d == False:
            eng.append(e)
    df12 = dbeng()[7]
    df121 = df12.sort_values(by=['JobNo'])
    df122 = df121.drop_duplicates(subset = ['JobNo'])
    df123 = df122['JobNo']
    pr = df123.values.tolist()
    eng = [x + [0] for x in eng]
    for e in eng:
        if e[1] in pr:
            e[28] = 'x'
    return render_template('repeat_add.html', eng=eng)

@app.route('/quality')
def quality():
    df9 = dbeng()[4]
    df9 = df9.sort_values(by = ['DueDate', 'JobNo'])
    en = df9.values.tolist()
    eng = []
    for e in en:
        if e[16] != 'on':
            eng.append(e)
    return render_template('quality.html', eng=eng)

@app.route('/hold_eng')
def hold_eng():
    df10 = dbeng()[5]
    df10 = df10.sort_values(by = ['DueDate', 'JobNo'])
    eng = df10.values.tolist()
    return render_template('hold_eng.html', eng=eng)

@app.route('/engform')
def engform():
    eng = dbpb()
    return render_template('engform.html', eng=eng)

@app.route('/mmodels')
def mmodels():
    df11 = dbeng()[6]
    df11 = df11.sort_values(by = ['DueDate', 'JobNo'])
    eng = df11.values.tolist()
    return render_template('mmodels.html', eng=eng)

@app.route('/addprint')
def addprint():
    df12 = dbeng()[7]
    df12 = df12.sort_values(by = ['DueDate', 'JobNo'])
    eng = df12.values.tolist()
    return render_template('addprint.html', eng=eng)

@app.route('/active')
def active():
    df5 = dbeng()[0]
    eng = df5.values.tolist()
    return render_template('active.html', eng=eng)

@app.route('/backend', methods=["POST", "GET"])
def backend():
    if request.method == "POST":
        job = request.form["job"]
        eng = request.form["eng"]
        wip = request.form["wip"]
        hold = request.form["hold"]
        hrsn = request.form["hrsn"]
        qc = request.form["qc"]
        apr = request.form["apr"]
        qcn = request.form["qcn"]
        model = request.form["model"]

        new_job = Job(job, eng, wip, hold, hrsn, qc, apr, qcn, model)
        db_session.add(new_job)
        db_session.commit()

        data = {
            "id": new_job.id,
            "job": job,
            "eng": eng,
            "wip": wip,
            "hold": hold,
            "hrsn": hrsn,
            "qc": qc,
            "apr": apr,
            "qcn": qcn,
            "model": model
        }

        pusher_client.trigger('table', 'new-record', {'data': data })

        return redirect("/backend", code=302)
    else:
        jobs = Job.query.all()
        return render_template('backend.html', jobs=jobs)

@app.route('/edit/<int:id>', methods=["POST", "GET"])
def update_record(id):
    if request.method == "POST":
        job = request.form["job"]
        eng = request.form["eng"]
        wip = request.form["wip"]
        hold = request.form["hold"]
        hrsn = request.form["hrsn"]
        qc = request.form["qc"]
        apr = request.form["apr"]
        qcn = request.form["qcn"]
        model = request.form["model"]

        update_job = Job.query.get(id)
        update_job.job = job
        update_job.eng = eng
        update_job.wip = wip
        update_job.hold = hold
        update_job.hrsn = hrsn
        update_job.qc = qc
        update_job.apr = apr
        update_job.qcn = qcn
        update_job.model = model

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "eng": eng,
            "wip": wip,
            "hold": hold,
            "hrsn": hrsn,
            "qc": qc,
            "apr": apr,
            "qcn": qcn,
            "model": model
        }

        pusher_client.trigger('table', 'update-record', {'data': data })

        return redirect("/active", code=302)
    else:
        new_job = Job.query.get(id)

        return render_template('update_job.html', data=new_job)





# # # FORMING SCHEDULER # # #

@app.route('/forminghome')
def forminghome():
    note = FormingNotes.query.all()
    return render_template('forminghome.html', note=note)

@app.route('/forming')
def forming():
    eng = dbpb()
    return render_template('forming.html', eng=eng)





# # # MACHINING # # #

@app.route('/machhome')
def machhome():
    dbeng()
    note = MachiningNotes.query.all()
    return render_template('machhome.html', note=note)

@app.route('/tbr_mach')
def tbr_mach():
    df6 = dbmach()[1]
    mach = df6.values.tolist()
    return render_template('tbr_mach.html', mach=mach)

@app.route('/future_mach')
def future_mach():
    df7 = dbmach()[2]
    df7 = df7.sort_values(by = ['DueDate', 'JobNo'])
    mach = df7.values.tolist()
    return render_template('future_mach.html', mach=mach)

@app.route('/repeat_mach')
def repeat_mach():
    df8 = dbmach()[3]
    df81 = df8.sort_values(by=['WorkCntr_y'])
    df82 = df81.drop_duplicates(subset = ['JobNo'])
    df83 = df82.sort_values(by = ['DueDate', 'JobNo'])
    en = df83.values.tolist()
    mach = []
    for e in en:
        cust = e[13]
        part = e[5]
        # server = '/run/user/1000/gvfs/smb-share:server=tower,share=production/'
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        d = os.path.exists(server+'/'+cust+'/'+part)
        if d == True:
            mach.append(e)
    df12 = dbmach()[5]
    df121 = df12.sort_values(by=['JobNo'])
    df122 = df121.drop_duplicates(subset = ['JobNo'])
    df123 = df122['JobNo']
    pr = df123.values.tolist()
    mach = [x + [0] for x in mach]
    for e in mach:
        if e[1] in pr:
            e[24] = 'x'
    return render_template('repeat_mach.html', mach=mach)

@app.route('/repeat_madd')
def repeat_madd():
    df8 = dbmach()[3]
    df81 = df8.sort_values(by=['WorkCntr_y'])
    df82 = df81.drop_duplicates(subset = ['JobNo'])
    df83 = df82.sort_values(by = ['DueDate', 'JobNo'])
    en = df83.values.tolist()
    mach = []
    for e in en:
        cust = e[13]
        part = e[5]
        # server = '/run/user/1000/gvfs/smb-share:server=tower,share=production/'
        server = '/run/user/1000/gvfs/smb-share:server=tower.local,share=production/'
        d = os.path.exists(server+'/'+cust+'/'+part)
        if d == False:
            mach.append(e)
    df12 = dbmach()[5]
    df121 = df12.sort_values(by=['JobNo'])
    df122 = df121.drop_duplicates(subset = ['JobNo'])
    df123 = df122['JobNo']
    pr = df123.values.tolist()
    mach = [x + [0] for x in mach]
    for e in mach:
        if e[1] in pr:
            e[24] = 'x'
    return render_template('repeat_madd.html', mach=mach)

# @app.route('/quality')
# def quality():
#     df9 = dbeng()[4]
#     en = df9.values.tolist()
#     eng = []
#     for e in en:
#         if e[16] != 'on':
#             eng.append(e)
#     return render_template('quality.html', eng=eng)

@app.route('/hold_mach')
def hold_mach():
    df10 = dbmach()[4]
    df10 = df10.sort_values(by = ['DueDate', 'JobNo'])
    mach = df10.values.tolist()
    return render_template('hold_mach.html', mach=mach)

@app.route('/active_mach')
def active_mach():
    df5 = dbmach()[0]
    mach = df5.values.tolist()
    return render_template('active_mach.html', mach=mach)

# @app.route('/backend', methods=["POST", "GET"])
# def backend():
#     if request.method == "POST":
#         job = request.form["job"]
#         eng = request.form["eng"]
#         wip = request.form["wip"]
#         hold = request.form["hold"]
#         hrsn = request.form["hrsn"]
#         qc = request.form["qc"]
#         apr = request.form["apr"]
#         qcn = request.form["qcn"]

#         new_job = Job(job, eng, wip, hold, hrsn, qc, apr, qcn)
#         db_session.add(new_job)
#         db_session.commit()

#         data = {
#             "id": new_job.id,
#             "job": job,
#             "eng": eng,
#             "wip": wip,
#             "hold": hold,
#             "hrsn": hrsn,
#             "qc": qc,
#             "apr": apr,
#             "qcn": qcn
#         }

#         pusher_client.trigger('table', 'new-record', {'data': data })

#         return redirect("/backend", code=302)
#     else:
#         jobs = Job.query.all()
#         return render_template('backend.html', jobs=jobs)

@app.route('/edit_mach/<int:id>', methods=["POST", "GET"])
def update_record_mach(id):
    if request.method == "POST":
        job = request.form["job"]
        eng = request.form["eng"]
        wip = request.form["wip"]
        hold = request.form["hold"]
        hrsn = request.form["hrsn"]

        update_mjob = MJob.query.get(id)
        update_mjob.job = job
        update_mjob.eng = eng
        update_mjob.wip = wip
        update_mjob.hold = hold
        update_mjob.hrsn = hrsn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "eng": eng,
            "wip": wip,
            "hold": hold,
            "hrsn": hrsn
        }

        pusher_client.trigger('table', 'update-record_mach', {'data': data })

        return redirect("/active_mach", code=302)
    else:
        new_mjob = MJob.query.get(id)

        return render_template('update_mjob.html', data=new_mjob)





# # # TUBE LASER SCHEDULER # # #

@app.route('/tlhome')
def tlhome():
    note = PageNotes.query.all()
    return render_template('tlhome.html', note=note)

@app.route('/jobs_tl')
def jobs_tl():
    df6 = dbtl()[1]
    st = df6.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbtl()[2]

    sf = df7.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_tl.html', st=st, sf=sf)

@app.route('/tl_nest')
def tl_nest():
    df13 = dbtl()[8]
    st = df13.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df14 = dbtl()[9]

    sf = df14.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('tl_nest.html', st=st, sf=sf)

@app.route('/tbr_tl')
def tbr_tl():
    df6 = dbtl()[1]
    tl = df6.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)
    return render_template('tbr_tl.html', tl=tl)

@app.route('/future_tl')
def future_tl():
    df7 = dbtl()[2]
    tl = df7.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)
    return render_template('future_tl.html', tl=tl)

@app.route('/material_tl')
def material_tl():
    df8 = dbtl()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_tl.html', tl=tl)

@app.route('/onorder_tl')
def onorder_tl():
    df11 = dbtl()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_tl.html', tl=tl)

# @app.route('/production_tl')
# def production_tl():
#     df9 = dbtl()[4]
#     tl = df9.values.tolist()
#     return render_template('production_tl.html', tl=tl)

# @app.route('/hold_tl')
# def hold_tl():
#     df10 = dbtl()[5]
#     tl = df10.values.tolist()
#     return render_template('hold_tl.html', tl=tl)

@app.route('/common_tl')
def common_tl():
    df12 = dbtl()[7]
    tl = df12.values.tolist()
    return render_template('common_tl.html', tl=tl)

@app.route('/active_tl')
def active_tl():
    df5 = dbtl()[0]
    tl = df5.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('active_tl.html', tl=tl)

@app.route('/backend_tl', methods=["POST", "GET"])
def backend_tl():
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        new_tjob = TJob(job, mtl, mtln, pgm, pgmn, tlh, tlhn)
        db_session.add(new_tjob)
        db_session.commit()

        data = {
            "id": new_tjob.id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'new-record_tl', {'data': data })

        return redirect("/backend_tl", code=302)
    else:
        tjobs = TJob.query.all()
        return render_template('backend_tl.html', tjobs=tjobs)

@app.route('/edit_tl/<int:id>', methods=["POST", "GET"])
def update_record_tl(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/active_tl", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_tjob.html', data=new_tjob)





# # # SAW SCHEDULER # # #

@app.route('/sawhome')
def sawhome():
    note = SawNotes.query.all()
    return render_template('sawhome.html', note=note)
    # return render_template('sawhome.html')

@app.route('/jobs_saw')
def jobs_saw():
    df6 = dbsaw()[1]

    st = df6.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbsaw()[2]

    sf = df7.values.tolist()
    print('check!!!!!!!!!!!!!!', sf)
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_saw.html', st=st, sf=sf)

@app.route('/tbr_saw')
def tbr_saw():
    df6 = dbsaw()[1]

    tl = df6.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    # df6 = df6.drop_duplicates()
    # tl = df6.values.tolist()
    return render_template('tbr_saw.html', tl=tl)

@app.route('/future_saw')
def future_saw():
    df7 = dbsaw()[2]

    tl = df7.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    # df7 = df7.drop_duplicates()
    # tl = df7.values.tolist()
    return render_template('future_saw.html', tl=tl)

@app.route('/material_saw')
def material_saw():
    df8 = dbsaw()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_saw.html', tl=tl)

@app.route('/onorder_saw')
def onorder_saw():
    df11 = dbsaw()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_saw.html', tl=tl)

@app.route('/active_saw')
def active_saw():
    df5 = dbsaw()[0]
    tl = df5.values.tolist()
    for t in tl:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)
    # df5 = dbsaw()[0]
    # df5 = df5.drop_duplicates()
    # tl = df5.values.tolist()
    return render_template('active_saw.html', tl=tl)

@app.route('/common_saw')
def common_saw():
    df12 = dbsaw()[7]
    tl = df12.values.tolist()
    return render_template('common_saw.html', tl=tl)

@app.route('/backend_saw', methods=["POST", "GET"])
def backend_saw():
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        new_tjob = TJob(job, mtl, mtln, pgm, pgmn, tlh, tlhn)
        db_session.add(new_tjob)
        db_session.commit()

        data = {
            "id": new_tjob.id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'new-record_tl', {'data': data })

        return redirect("/backend_saw", code=302)
    else:
        tjobs = TJob.query.all()
        return render_template('backend_saw.html', tjobs=tjobs)

@app.route('/edit_saw/<int:id>', methods=["POST", "GET"])
def update_record_saw(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/active_saw", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_saw.html', data=new_tjob)





# # # INVENTORY # # #

uploads_dir = os.path.join(app.instance_path, 'uploads')

@app.route('/invhome', methods = ['GET', 'POST'])
def invhome():
    eng = []
    if request.method == 'POST':
        cwd = os.getcwd()
        f = request.files['user_file']
        cust = request.values.get('cust', None)
        f.save(os.path.join(uploads_dir, secure_filename('INV.XLS')))
        filename = r'INV.XLS'

        df = pd.read_excel(r'/home/monarchhome/Projects/mmhome/instance/uploads/INV.XLS', header=None, names=['Part', 'Rev', 'Qty', 'Pallet'])
        df = df[df['Pallet'].notna()]
        df1 = df.groupby('Part').Pallet.apply(list).reset_index()
        aggf = {'Qty': 'sum'}
        df2 = df.groupby(df['Part']).aggregate(aggf)
        dfe = df2.merge(df1, on='Part', how='inner')

        server = '10.0.1.130\E2SQLSERVER'
        db = 'MONARCH_SHOP'
        un = 'sa'
        pw = 'Mon@rch09'

        cnxn = p.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1};SERVER='+server+';DATABASE='+db+';UID='+un+';PWD='+pw)
        # QTY ON HAND
        sqlh = "SELECT B.PartNo, B.QtyOnHand \
                        FROM BinLocations B INNER JOIN Estim E ON B.PartNo=E.PartNo \
                        WHERE B.QtyOnHand > 0 AND E.CustCode = '"""+cust+"'"
        dfh = pd.read_sql(sqlh, con=cnxn)
        # QTY RESERVED
        sqlr = """SELECT B.PartNo, J.QtyPosted1 \
                        FROM BinLocations B INNER JOIN Estim E ON B.PartNo=E.PartNo INNER JOIN JobMaterials J ON J.PartNo=E.PartNo INNER JOIN OrderDet D ON J.JobNo=D.JobNo \
                        WHERE B.QtyOnHand > 0 AND D.Status = 'Open' AND E.CustCode = '"""+cust+"'"
        dfr = pd.read_sql(sqlr, con=cnxn)

        dfh = dfh.groupby(['PartNo'],as_index=False).agg({'QtyOnHand': 'sum'})
        dfr = dfr.drop_duplicates()

        dfc = pd.merge(left=dfh, right=dfr, how='left', left_on='PartNo', right_on='PartNo')
        dfc['QtyPosted1'] = dfc['QtyPosted1'].fillna(0)
        dfc['TotalQty'] = dfc['QtyOnHand'] + dfc['QtyPosted1']

        dfi = dfc
        dfi['PartNo'] = dfi['PartNo'].astype('str')
        dfe['Part'] = dfe['Part'].astype('str')
        pd.set_option("max_rows", None)
        dff = pd.merge(left=dfi, right=dfe, how="outer", left_on='PartNo', right_on='Part')
        dff['PartNo'] = dff['PartNo'].fillna(dff['Part'])
        dff['TotalQty'] = dff['TotalQty'].fillna(0)
        dff['Qty'] = dff['Qty'].fillna(0)
        dff['Pallet'] = dff['Pallet'].fillna('-')
        dff['Diff'] = dff['TotalQty'] - dff['Qty']
        dff['Action'] = np.where(dff['Diff']==0, 'Good', 'Adjust')
        dff = dff.sort_values(by=['Action', 'PartNo'])
        eng = dff.values.tolist()
    return render_template('invhome.html', eng=eng)





# # # BEND DEDUCTION # # #

@app.route('/bdhome')
def bdhome():
    return render_template('bdhome.html')

@app.route('/bdcrs')
def bdcrs():
    bds = Bendd.query.order_by('thick', 'rad').all()
    return render_template('bdcrs.html', bds=bds)

@app.route('/bdsss')
def bdsss():
    bds = Bendd.query.order_by('thick', 'rad').all()
    return render_template('bdsss.html', bds=bds)

@app.route('/bdals')
def bdals():
    bds = Bendd.query.order_by('thick', 'rad').all()
    return render_template('bdals.html', bds=bds)

@app.route('/bdcust')
def bdcust():
    bds = Bendd.query.order_by('thick', 'rad').all()
    return render_template('bdcust.html', bds=bds)

@app.route('/bdarchive')
def bdarchive():
    bds = Bendd.query.order_by('thick', 'rad').all()
    return render_template('bdarchive.html', bds=bds)

# @app.route('/future_tl')
# def future_tl():
#     df7 = dbtl()[2]
#     tl = df7.values.tolist()
#     return render_template('future_tl.html', tl=tl)

@app.route('/backend_bd', methods=["POST", "GET"])
def backend_bd():
    if request.method == "POST":
        matl = request.form["matl"]
        desc = request.form["desc"]
        gauge = request.form["gauge"]
        thick = request.form["thick"]
        rad = request.form["rad"]
        bd = request.form["bd"]
        pt = request.form["pt"]
        dt = request.form["dt"]
        notes = request.form["notes"]

        new_bd = Bendd(matl, desc, gauge, thick, rad, bd, pt, dt, notes)
        print('new')
        print(new_bd)
        db_session.add(new_bd)
        db_session.commit()

        data = {
            "id": new_bd.id,
            "matl": matl,
            "desc": desc,
            "gauge": gauge,
            "thick": thick,
            "rad": rad,
            "bd": bd,
            "pt": pt,
            "dt": dt,
            "notes": notes
        }

        pusher_client.trigger('table', 'new-record_bd', {'data': data })

        return redirect("/bdhome", code=302)
    else:
        bds = Bendd.query.all()
        return render_template('backend_bd.html', bds=bds)

@app.route('/edit_bd/<int:id>', methods=["POST", "GET"])
def update_record_bd(id):
    if request.method == "POST":
        matl = request.form["matl"]
        desc = request.form["desc"]
        gauge = request.form["gauge"]
        thick = request.form["thick"]
        rad = request.form["rad"]
        bd = request.form["bd"]
        pt = request.form["pt"]
        dt = request.form["dt"]
        notes = request.form["notes"]

        update_bd = Bendd.query.get(id)
        update_bd.matl = matl
        update_bd.desc = desc
        update_bd.gauge = gauge
        update_bd.thick = thick
        update_bd.rad = rad
        update_bd.bd = bd
        update_bd.pt = pt
        update_bd.dt = dt
        update_bd.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "matl": matl,
            "desc": desc,
            "gauge": gauge,
            "thick": thick,
            "rad": rad,
            "bd": bd,
            "pt": pt,
            "dt": dt,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_bd', {'data': data })

        return redirect("/bdhome", code=302)
    else:
        new_bd = Bendd.query.get(id)

        return render_template('update_bd.html', data=new_bd)





# STATIC
@app.route('/remove')
def remove():
    rmfl = dbfl()
    rmp = dbsl()[0]
    rmm = dbsl()[1]
    rmr = dbpp()[0]
    rmv = dbpp()[1]
    return render_template('remove.html', rmp=rmp, rmm=rmm, rmfl=rmfl, rmr=rmr, rmv=rmv)


# EMAIL
@app.route('/esend')
def esend():
    shipsum()
    return render_template('esend.html')



@app.route('/shipping')
def shipping():
    df = shipdeliv()[0]
    df = df.sort_values(by = ['CustCode', 'OrderNo', 'JobNo'])
    ship = df.values.tolist()
    return render_template('shipping.html', ship=ship)

@app.route('/shippart')
def shippart():
    df = shipdeliv()[1]
    df = df.sort_values(by = ['CustCode', 'OrderNo', 'JobNo'])
    ship = df.values.tolist()
    return render_template('shippart.html', ship=ship)

@app.route('/shipfull')
def shipfull():
    df = shipdeliv()[2]
    df = df.sort_values(by = ['CustCode', 'OrderNo', 'JobNo'])
    ship = df.values.tolist()
    dfs = shipdeliv()[3]
    dfs = dfs.sort_values(by = ['CustCode', 'OrderNo', 'JobNo'])
    ships = dfs.values.tolist()
    return render_template('shipfull.html', ship=ship, ships=ships)

@app.route('/delivered')
def delivered():
    df = shipdeliv()[4]
    df = df.sort_values(by = ['date', 'CustCode', 'OrderNo', 'JobNo'])
    ship = df.values.tolist()
    return render_template('delivered.html', ship=ship)

@app.route('/shipcost')
def shipcost():
    df = shipdeliv()[4]
    df = df.sort_values(by = ['date', 'CustCode', 'OrderNo', 'JobNo'])
    ship = df.values.tolist()
    return render_template('shipcost.html', ship=ship)

@app.route('/edit_ship/<int:id>', methods=["POST", "GET"])
def update_record_ship(id):
    if request.method == "POST":
        job = request.form["job"]
        date = request.form["date"]
        track = request.form["track"]
        delv = request.form["delv"]

        update_ship = Ship.query.get(id)
        update_ship.job = job
        if delv == 'on':
            update_ship.date = (dt.today()).strftime("%x")
        else:
            update_ship.date = date
        update_ship.tack = track
        update_ship.delv = delv

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "date": date,
            "track": track,
            "delv": delv
        }

        pusher_client.trigger('table', 'update-record_ship', {'data': data })

        return redirect("/shipping", code=302)
    else:
        new_job = Ship.query.get(id)

        return render_template('update_ship.html', data=new_job)





@app.route('/sop')
def sop():
    return render_template('sop.html')


@app.route('/nest')
def nest():
    dfn = dblp()[0]
    nest = dfn.values.tolist()
    dfd = dblp()[1]
    nests = dfd.values.tolist()
    return render_template('nest.html', nest=nest, nests=nests)

@app.route('/edit_nest/<int:id>', methods=["POST", "GET"])
def update_record_nest(id):
    if request.method == "POST":
        job = request.form["job"]
        eng = request.form["eng"]
        wip = request.form["wip"]
        hold = request.form["hold"]
        hrsn = request.form["hrsn"]
        qc = request.form["qc"]
        apr = request.form["apr"]
        qcn = request.form["qcn"]
        model = request.form["model"]
        nest = request.form["nest"]

        update_nest = Job.query.get(id)
        update_nest.job = job
        update_nest.eng = eng
        update_nest.wip = wip
        update_nest.hold = hold
        update_nest.hrsn = hrsn
        update_nest.qc = qc
        update_nest.apr = apr
        update_nest.qcn = qcn
        update_nest.model = model
        update_nest.nest = nest

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "eng": eng,
            "wip": wip,
            "hold": hold,
            "hrsn": hrsn,
            "qc": qc,
            "apr": apr,
            "qcn": qcn,
            "model": model,
            "nest": nest
        }

        pusher_client.trigger('table', 'update-record_nest', {'data': data })

        return redirect("/nest", code=302)
    else:
        new_nest = Job.query.get(id)

        return render_template('update_nest.html', data=new_nest)





# # # TUBE CALCULATOR # # #

from app.forms import TubeCalcForm
def tcalc(tlma):
    # STARTING DATA
    b = []          # ALL LENGTH LIST - USED FOR 20' STICK
    c = []          # ALL LENGTH LIST - USED FOR 24' STICK
    gap = 0.25      # STANDARD GAP IN PARTS
    ends = 0.25     # GAP AT START/END OF STICK
    minh = 33       # MINIUMUM LENGHT OF LAST PART TO USE FULL STICK
    lost = 14       # INCHES LOST END OF STICK IF FULL STICK CAN'T BE USED

    # 20' LONG MATL
    lth20 = 240
    length20 = lth20 - (2*ends)
    # 24' LONG MATL
    lth24 = 288
    length24 = lth24 - (2*ends)

    for t in tlma:
        t[1] = int(t[1])

    # COMBINE ALL LENGTHS INTO ONE LIST
    for tl in tlma:
        if tl[0] != None:
            for i in range(tl[1]):
                if tl[2] == True and tl[3] == True:
                    ml = tl[0]
                elif tl[2] == False and tl[3] == False:
                    ml = tl[0] + gap
                else:
                    ml = tl[0] + (gap/2)
                b.append(ml)
                c.append(ml)

    # DETERMINE HOW MANY STICKS AND REMAINDER OF MATERIAL
    # 20 FOOT LONG MATL
    def maxsum20(values, *, k):
        tot = []
        rem = []
        wst = []
        stk = 0
        while len(values) > 0:
            if max(values) < minh:
                k = length20 - lost
            new = []
            current_sum = 0
            values_used = []
            values.sort(reverse=True)
            for value in values:
                if current_sum + value > k:
                    continue
                current_sum += value
                values_used.append(value)
                if current_sum == k:
                    break
            for i in values_used:
                if i in values:
                    values.remove(i)
                    new = values
            tot.append(sum(values_used))
            rem.append(k - current_sum)
            wst.append(((k - current_sum)/lth20)*100)
            stk += 1
            values = new
        twst = (sum(rem)/(lth24*stk))*100
        return tot, rem, stk, wst, twst

    result20 = maxsum20(b, k=length20)

    # DETERMINE HOW MANY STICKS AND REMAINDER OF MATERIAL
    # 24 FOOT LONG MATL
    def maxsum24(values, *, k):
        tot = []
        rem = []
        wst = []
        stk = 0
        while len(values) > 0:
            if max(values) < minh:
                k = length24 - lost
            new = []
            current_sum = 0
            values_used = []
            values.sort(reverse=True)
            for value in values:
                if current_sum + value > k:
                    continue
                current_sum += value
                values_used.append(value)
                if current_sum == k:
                    break
            for i in values_used:
                if i in values:
                    values.remove(i)
                    new = values
            tot.append(sum(values_used))
            rem.append(k - current_sum)
            wst.append(((k - current_sum)/lth24)*100)
            stk += 1
            values = new

        twst = (sum(rem)/(lth24*stk))*100
        return tot, rem, stk, wst, twst

    result24 = maxsum24(c, k=length24)

    r20 = ['20ft', result20[2], result20[0], round(result20[4], 1)]
    r24 = ['24ft', result24[2], result24[0], round(result24[4], 1)]
    tubes = [r20, r24]

    return tubes

@app.route('/tubecalc', methods=["GET", "POST"])
def tubecalc():
    form = TubeCalcForm()
    if form.validate_on_submit():
        lng1 = form.lng1.data
        qty1 = form.qty1.data
        ccl1 = form.ccl1.data
        ccr1 = form.ccr1.data
        t1 = [lng1, qty1, ccl1, ccr1]

        lng2 = form.lng2.data
        qty2 = form.qty2.data
        ccl2 = form.ccl2.data
        ccr2 = form.ccr2.data
        t2 = [lng2, qty2, ccl2, ccr2]

        lng3 = form.lng3.data
        qty3 = form.qty3.data
        ccl3 = form.ccl3.data
        ccr3 = form.ccr3.data
        t3 = [lng3, qty3, ccl3, ccr3]

        lng4 = form.lng4.data
        qty4 = form.qty4.data
        ccl4 = form.ccl4.data
        ccr4 = form.ccr4.data
        t4 = [lng4, qty4, ccl4, ccr4]

        lng5 = form.lng5.data
        qty5 = form.qty5.data
        ccl5 = form.ccl5.data
        ccr5 = form.ccr5.data
        t5 = [lng5, qty5, ccl5, ccr5]

        lng6 = form.lng6.data
        qty6 = form.qty6.data
        ccl6 = form.ccl6.data
        ccr6 = form.ccr6.data
        t6 = [lng6, qty6, ccl6, ccr6]

        lng7 = form.lng7.data
        qty7 = form.qty7.data
        ccl7 = form.ccl7.data
        ccr7 = form.ccr7.data
        t7 = [lng7, qty7, ccl7, ccr7]

        lng8 = form.lng8.data
        qty8 = form.qty8.data
        ccl8 = form.ccl8.data
        ccr8 = form.ccr8.data
        t8 = [lng8, qty8, ccl8, ccr8]

        lng9 = form.lng9.data
        qty9 = form.qty9.data
        ccl9 = form.ccl9.data
        ccr9 = form.ccr9.data
        t9 = [lng9, qty9, ccl9, ccr9]

        lng10 = form.lng10.data
        qty10 = form.qty10.data
        ccl10 = form.ccl10.data
        ccr10 = form.ccr10.data
        t10 = [lng10, qty10, ccl10, ccr10]

        tlma = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10]
        tubes = tcalc(tlma)
        return redirect(f"/tubedata?tubes={tubes}")

    return render_template('tubecalc.html', form=form)

@app.route('/tubecsvc', methods=["GET", "POST"])
def tubecsvc():
    if request.method == 'POST':
        cwd = os.getcwd()
        f = request.files['user_file']
        cust = request.values.get('cust', None)
        f.save(os.path.join(uploads_dir, secure_filename('TLC.XLS')))
        filename = r'TLC.XLS'

        df = pd.read_excel(r'/home/monarchhome/Projects/mmhome/instance/uploads/TLC.XLS', header=None, names=['Length', 'Qty', 'CCL', 'CCR'])
        tlma = df.values.tolist()
        for e in tlma:
            if str(e[2]) == 'nan':
                e[2] = False
            else:
                e[2] = True
            if str(e[3]) == 'nan':
                e[3] = False
            else:
                e[3] = True
        tubes = tcalc(tlma)
        return redirect(f"/tubedata?tubes={tubes}")

    return render_template('tubecsvc.html')

@app.route('/tubedata')
def tubedata():
    tubes = eval(request.args.get("tubes"))
    return render_template('tubedata.html', tubes=tubes)





# # # SLASER SCHEDULER # # #

@app.route('/slaserhome')
def slaserhome():
    note = SLaserNotes.query.all()
    return render_template('slaserhome.html', note=note)

@app.route('/jobs_slaser')
def jobs_slaser():
    df6 = dbslaser()[1]

    st = df6.values.tolist()
    print(st)
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbslaser()[2]

    sf = df7.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_slaser.html', st=st, sf=sf)

@app.route('/tbr_slaser')
def tbr_slaser():
    df6 = dbslaser()[1]
    df6 = df6.drop_duplicates()
    tl = df6.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('tbr_slaser.html', tl=tl)

@app.route('/future_slaser')
def future_slaser():
    df7 = dbslaser()[2]
    df7 = df7.drop_duplicates()
    tl = df7.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('future_slaser.html', tl=tl)

@app.route('/material_slaser')
def material_slaser():
    df8 = dbslaser()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_slaser.html', tl=tl)

@app.route('/onorder_slaser')
def onorder_slaser():
    df11 = dbslaser()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_slaser.html', tl=tl)

@app.route('/common_slaser')
def common_slaser():
    df12 = dbslaser()[7]
    tl = df12.values.tolist()
    return render_template('common_slaser.html', tl=tl)

@app.route('/active_slaser')
def active_slaser():
    df5 = dbslaser()[0]
    df5 = df5.drop_duplicates()
    tl = df5.values.tolist()
    return render_template('active_slaser.html', tl=tl)

@app.route('/edit_slaser/<int:id>', methods=["POST", "GET"])
def update_record_slaser(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/slaserhome", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_slaser.html', data=new_tjob)





# # # FLASER SCHEDULER # # #

@app.route('/flaserhome')
def flaserhome():
    note = FLaserNotes.query.all()
    return render_template('flaserhome.html', note=note)

@app.route('/jobs_flaser')
def jobs_flaser():
    df6 = dbflaser()[1]

    st = df6.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbflaser()[2]

    sf = df7.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_flaser.html', st=st, sf=sf)

@app.route('/tbr_flaser')
def tbr_flaser():
    df6 = dbflaser()[1]
    df6 = df6.drop_duplicates()
    tl = df6.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('tbr_flaser.html', tl=tl)

@app.route('/future_flaser')
def future_flaser():
    df7 = dbflaser()[2]
    df7 = df7.drop_duplicates()
    tl = df7.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('future_flaser.html', tl=tl)

@app.route('/material_flaser')
def material_flaser():
    df8 = dbflaser()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_flaser.html', tl=tl)

@app.route('/onorder_flaser')
def onorder_flaser():
    df11 = dbflaser()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_flaser.html', tl=tl)

@app.route('/common_flaser')
def common_flaser():
    df12 = dbflaser()[7]
    tl = df12.values.tolist()
    return render_template('common_flaser.html', tl=tl)

@app.route('/active_flaser')
def active_flaser():
    df5 = dbflaser()[0]
    df5 = df5.drop_duplicates()
    tl = df5.values.tolist()
    return render_template('active_flaser.html', tl=tl)

@app.route('/edit_flaser/<int:id>', methods=["POST", "GET"])
def update_record_flaser(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/flaserhome", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_flaser.html', data=new_tjob)





# # # PUNCH SCHEDULER # # #

@app.route('/punchhome')
def punchhome():
    note = PunchNotes.query.all()
    return render_template('punchhome.html', note=note)

@app.route('/jobs_punch')
def jobs_punch():
    df6 = dbpunch()[1]
    st = df6.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbpunch()[2]

    sf = df7.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_punch.html', st=st, sf=sf)

@app.route('/tbr_punch')
def tbr_punch():
    df6 = dbpunch()[1]
    df6 = df6.drop_duplicates()
    tl = df6.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('tbr_punch.html', tl=tl)

@app.route('/future_punch')
def future_punch():
    df7 = dbpunch()[2]
    df7 = df7.drop_duplicates()
    tl = df7.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            unCut = []
            cutRow = t[17].replace("\n", "     ").split("     ")
            if len(cutRow) > 3:
                onlyCut = cutRow[0::3]
                for i in onlyCut:
                    if i not in unCut:
                        unCut.append(i)
                finalCut = "\n".join(unCut)
            else:
                finalCut = cutRow[0]
            t.append(finalCut)
    return render_template('future_punch.html', tl=tl)

@app.route('/material_punch')
def material_punch():
    df8 = dbpunch()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_punch.html', tl=tl)

@app.route('/onorder_punch')
def onorder_punch():
    df11 = dbpunch()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_punch.html', tl=tl)

@app.route('/common_punch')
def common_punch():
    df12 = dbpunch()[7]
    tl = df12.values.tolist()
    return render_template('common_punch.html', tl=tl)

@app.route('/active_punch')
def active_punch():
    df5 = dbpunch()[0]
    df5 = df5.drop_duplicates()
    tl = df5.values.tolist()
    # return render_template('active_punch.html', tl=tl)

    # df5 = dbshear()[0]
    # df5 = df5.drop_duplicates()
    # tl = df5.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    # return render_template('active_shear.html', tl=tl)
    return render_template('active_punch.html', tl=tl)

@app.route('/edit_punch/<int:id>', methods=["POST", "GET"])
def update_record_punch(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/punchhome", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_punch.html', data=new_tjob)





# # # SHEAR SCHEDULER # # #

@app.route('/shearhome')
def shearhome():
    note = ShearNotes.query.all()
    return render_template('shearhome.html', note=note)

@app.route('/jobs_shear')
def jobs_shear():
    df6 = dbshear()[1]

    st = df6.values.tolist()
    for t in st:
        unCut = []
        if t[17]:
            cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    df7 = dbshear()[2]

    sf = df7.values.tolist()
    for t in sf:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('jobs_shear.html', st=st, sf=sf)

@app.route('/tbr_shear')
def tbr_shear():
    df6 = dbshear()[1]
    df6 = df6.drop_duplicates()
    tl = df6.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            for t in tl:
                unCut = []
                cutRow = t[17].replace("\n", "     ").split("     ")
                if len(cutRow) > 3:
                    onlyCut = cutRow[0::3]
                    for i in onlyCut:
                        if i not in unCut:
                            unCut.append(i)
                    finalCut = "\n".join(unCut)
                else:
                    finalCut = cutRow[0]
                t.append(finalCut)

    return render_template('tbr_shear.html', tl=tl)

@app.route('/future_shear')
def future_shear():
    df7 = dbshear()[2]
    df7 = df7.drop_duplicates()
    tl = df7.values.tolist()
    for t in tl:
        if t[17] == None:
            t.append('-')
        else:
            for t in tl:
                unCut = []
                cutRow = t[17].replace("\n", "     ").split("     ")
                if len(cutRow) > 3:
                    onlyCut = cutRow[0::3]
                    for i in onlyCut:
                        if i not in unCut:
                            unCut.append(i)
                    finalCut = "\n".join(unCut)
                else:
                    finalCut = cutRow[0]
                t.append(finalCut)

    return render_template('future_shear.html', tl=tl)

@app.route('/material_shear')
def material_shear():
    df8 = dbshear()[3]
    df8 = df8.drop_duplicates()
    df8 = df8.sort_values(by = ['DueDate', 'JobNo'])
    tl = df8.values.tolist()
    return render_template('material_shear.html', tl=tl)

@app.route('/onorder_shear')
def onorder_shear():
    df11 = dbshear()[6]
    df11 = df11.drop_duplicates()
    df11 = df11.sort_values(by = ['pgmn', 'DueDate', 'JobNo'])
    tl = df11.values.tolist()
    return render_template('onorder_shear.html', tl=tl)

@app.route('/common_shear')
def common_shear():
    df12 = dbshear()[7]
    tl = df12.values.tolist()
    return render_template('common_shear.html', tl=tl)


@app.route('/active_shear')
def active_shear():
    df5 = dbshear()[0]
    df5 = df5.drop_duplicates()
    tl = df5.values.tolist()
    for t in tl:
        unCut = []
        cutRow = t[17].replace("\n", "     ").split("     ")
        if len(cutRow) > 3:
            onlyCut = cutRow[0::3]
            for i in onlyCut:
                if i not in unCut:
                    unCut.append(i)
            finalCut = "\n".join(unCut)
        else:
            finalCut = cutRow[0]
        t.append(finalCut)

    return render_template('active_shear.html', tl=tl)

@app.route('/edit_shear/<int:id>', methods=["POST", "GET"])
def update_record_shear(id):
    if request.method == "POST":
        job = request.form["job"]
        mtl = request.form["mtl"]
        mtln = request.form["mtln"]
        pgm = request.form["pgm"]
        pgmn = request.form["pgmn"]
        tlh = request.form["tlh"]
        tlhn = request.form["tlhn"]

        update_tjob = TJob.query.get(id)
        update_tjob.job = job
        update_tjob.mtl = mtl
        update_tjob.mtln = mtln
        update_tjob.pgm = pgm
        update_tjob.pgmn = pgmn
        update_tjob.tlh = tlh
        update_tjob.tlhn = tlhn

        db_session.commit()

        data = {
            "id": id,
            "job": job,
            "mtl": mtl,
            "mtln": mtln,
            "pgm": pgm,
            "pgmn": pgmn,
            "tlh": tlh,
            "tlhn": tlhn
        }

        pusher_client.trigger('table', 'update-record_tl', {'data': data })

        return redirect("/shearhome", code=302)
    else:
        new_tjob = TJob.query.get(id)

        return render_template('update_shear.html', data=new_tjob)





# # # ENTERPRISE (LASER) # # #

@app.route('/enthome')
def enthome():
    note = EntNotes.query.all()
    return render_template('enthome.html', note=note)

@app.route('/material_ent')
def material_ent():
    ent = Ent.query.order_by('name').all()
    return render_template('material_ent.html', ent=ent)

@app.route('/onorder_ent')
def onorder_ent():
    ent = Ent.query.order_by('name').all()
    return render_template('onorder_ent.html', ent=ent)

@app.route('/common_ent')
def common_ent():
    ent = Ent.query.order_by('name').all()
    return render_template('common_ent.html', ent=ent)

@app.route('/verify_ent')
def verify_ent():
    ent = Ent.query.order_by('name').all()
    return render_template('verify_ent.html', ent=ent)

@app.route('/comp_ent')
def comp_ent():
    ent = Ent.query.order_by('name').all()
    return render_template('comp_ent.html', ent=ent)

@app.route('/backend_ent', methods=["POST", "GET"])
def backend_ent():
    if request.method == "POST":
        name = request.form["name"]
        need = request.form["need"]
        needn = request.form["needn"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        verf = request.form["verf"]
        verfn = request.form["verfn"]
        done = request.form["done"]

        new_ent = Ent(name, need, needn, ordr, ordrn, verf, verfn)
        db_session.add(new_ent)
        db_session.commit()

        data = {
            "id": new_ent.id,
            "name": name,
            "need": need,
            "needn": needn,
            "ordr": ordr,
            "ordrn": ordrn,
            "verf": verf,
            "verfn": verfn,
            "done": done
        }

        pusher_client.trigger('table', 'new-record-ent', {'data': data })

        return redirect("/common_ent", code=302)
    else:
        ent = Ent.query.all()
        return render_template('backend_ent.html', ent=ent)

@app.route('/edit_ent/<int:id>', methods=["POST", "GET"])
def update_record_ent(id):
    if request.method == "POST":
        name = request.form["name"]
        need = request.form["need"]
        needn = request.form["needn"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        verf = request.form["verf"]
        verfn = request.form["verfn"]
        done = request.form["done"]

        update_ent = Ent.query.get(id)
        update_ent.name = name
        update_ent.need = need
        update_ent.needn = needn
        update_ent.ordr = ordr
        update_ent.ordrn = ordrn
        update_ent.verf = verf
        update_ent.verfn = verfn
        update_ent.done = done

        db_session.commit()

        data = {
            "id": id,
            "name": name,
            "need": need,
            "needn": needn,
            "ordr": ordr,
            "ordrn": ordrn,
            "verf": verf,
            "verfn": verfn,
            "done": done
        }

        pusher_client.trigger('table', 'update-record-ent', {'data': data })

        return redirect("/enthome", code=302)
    else:
        new_ent = Ent.query.get(id)

        return render_template('update_ent.html', data=new_ent)





# # # TUBE LASER MATERIAL # # #

@app.route('/tlmatlhome')
def tlmatlhome():
    note = TlmNotes.query.all()
    return render_template('tlmatlhome.html', note=note)

@app.route('/material_tlmatl')
def material_tlmatl():
    tlm = MatlTL.query.order_by('name').all()
    return render_template('material_tlmatl.html', tlm=tlm)

@app.route('/onorder_tlmatl')
def onorder_tlmatl():
    tlm = MatlTL.query.order_by('name').all()
    return render_template('onorder_tlmatl.html', tlm=tlm)

@app.route('/common_tlmatl')
def common_tlmatl():
    tlm = MatlTL.query.order_by('name').all()
    return render_template('common_tlmatl.html', tlm=tlm)

@app.route('/verify_tlmatl')
def verify_tlmatl():
    tlm = MatlTL.query.order_by('name').all()
    return render_template('verify_tlmatl.html', tlm=tlm)

@app.route('/comp_tlmatl')
def comp_tlmatl():
    tlm = MatlTL.query.order_by('name').all()
    return render_template('comp_tlmatl.html', tlm=tlm)

@app.route('/backend_tlmatl', methods=["POST", "GET"])
def backend_tlmatl():
    if request.method == "POST":
        name = request.form["name"]
        need = request.form["need"]
        needn = request.form["needn"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        verf = request.form["verf"]
        verfn = request.form["verfn"]
        done = request.form["done"]

        new_tlm = MatlTL(name, need, needn, ordr, ordrn, verf, verfn)
        db_session.add(new_tlm)
        db_session.commit()

        data = {
            "id": new_tlm.id,
            "name": name,
            "need": need,
            "needn": needn,
            "ordr": ordr,
            "ordrn": ordrn,
            "verf": verf,
            "verfn": verfn,
            "done": done
        }

        pusher_client.trigger('table', 'new-record-tlmatl', {'data': data })

        return redirect("/common_tlmatl", code=302)
    else:
        tlm = MatlTL.query.all()
        return render_template('backend_tlmatl.html', tlm=tlm)

@app.route('/edit_tlm/<int:id>', methods=["POST", "GET"])
def update_record_tlmatl(id):
    if request.method == "POST":
        name = request.form["name"]
        need = request.form["need"]
        needn = request.form["needn"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        verf = request.form["verf"]
        verfn = request.form["verfn"]
        done = request.form["done"]

        update_tlm = MatlTL.query.get(id)
        update_tlm.name = name
        update_tlm.need = need
        update_tlm.needn = needn
        update_tlm.ordr = ordr
        update_tlm.ordrn = ordrn
        update_tlm.verf = verf
        update_tlm.verfn = verfn
        update_tlm.done = done

        db_session.commit()

        data = {
            "id": id,
            "name": name,
            "need": need,
            "needn": needn,
            "ordr": ordr,
            "ordrn": ordrn,
            "verf": verf,
            "verfn": verfn,
            "done": done
        }

        pusher_client.trigger('table', 'update-record-tlmatl', {'data': data })

        return redirect("/tlmatlhome", code=302)
    else:
        new_tlm = MatlTL.query.get(id)

        return render_template('update_tlmatl.html', data=new_tlm)





# # # SUPPLIES # # #

@app.route('/supplies')
def supplies():
    note = SupNotes.query.all()
    return render_template('supplies.html', note=note)

@app.route('/material_sup')
def material_sup():
    sup = Supplies.query.order_by('id').all()
    scales = GetScales()
    auto = []
    print(scales)
    for s in scales:
        print(s['Quantity'], s['AlertThreshold'])
        if s['Quantity'] < s['AlertThreshold']:
            if s['Quantity'] >= 0:
                print(s['Name'])
                add = [s['Name'], s['ScaleId'], s['Quantity'], s['AlertThreshold'], s['ItemPartNumber'], s['ItemDescription'], s['ItemId']]
                auto.append(add)
    print(auto)
    return render_template('material_sup.html', sup=sup, auto=auto)

@app.route('/onorder_sup')
def onorder_sup():
    sup = Supplies.query.order_by('id').all()
    return render_template('onorder_sup.html', sup=sup)

@app.route('/comp_sup')
def comp_sup():
    sup = Supplies.query.order_by('-id').all()
    return render_template('comp_sup.html', sup=sup)

@app.route('/scale_display')
@app.route('/scale_display/<editMode>')
def scale_display(editMode = False):
    scales = GetScales()
    return render_template('scale_display.html', scales=scales, edit=bool(editMode))

@app.route('/scale_logs')
def scale_logs():
    logs = GetLogs()
    return render_template('scale_quantitylog.html', logs = logs)

@app.route('/scale_create', methods=["POST", "GET"])
def scale_create():
    if request.method == "POST":
        channelIds = [int(x) for x in request.form.to_dict(flat=False)["channelIds"]]
        scale = Scale(request.form["name"],int(request.form["scaleWeightType"]), channelIds)
        CreateScale(scale)
        return redirect(url_for("scale_display"), code=302)
    else:
        sensors = GetSensors()
        sensors = [x for x in sensors if x['ScaleName']== 'Unused']
        if len(sensors) == 0:
            sensors = None
        return render_template('scale_create.html', sensors=sensors)

@app.route('/scale_itemcreate', methods=["POST", "GET"])
def scale_itemcreate():
    if request.method == "POST":
        scaleId = request.form["scaleId"]
        itemName = request.form["description"]
        quantity = request.form["quantity"]
        partNumber = request.form["partNumber"]
        alertThreshold = float(request.form["alertThreshold"])
        CreateItem({"ScaleId":int(scaleId), "Description": itemName, "Quantity": int(quantity), "PartNumber": partNumber, "AlertThreshold": alertThreshold})
        return redirect(url_for("scale_display"), code=302)
    else:
        scales = GetScales()
        scales = [x for x in scales if x['ItemId'] == None]
        if len(scales) == 0:
            scales = None
        return render_template('scale_itemcreate.html', scales=scales)


@app.route('/zeroScale/<scaleId>', methods=["GET"])
def zeroScale(scaleId):
    ZeroScale(int(scaleId))
    return redirect(url_for("scale_display"), code=302)

@app.route('/deleteScale/<scaleId>', methods=["GET"])
def deleteScale(scaleId):
    DeleteScale(int(scaleId))
    return redirect(url_for("scale_display"), code=302)

@app.route('/deleteItem/<itemId>', methods=["GET"])
def deleteItem(itemId):
    DeleteItem(int(itemId))
    return redirect(url_for("scale_display"), code=302)

@app.route('/backend_sup', methods=["POST", "GET"])
def backend_sup():
    if request.method == "POST":
        dept = request.form["dept"]
        need = request.form["need"]
        desc = request.form["desc"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        done = request.form["done"]
        requester = request.form["requester"]
        link = request.form["link"]
        jobno = request.form["jobno"]

        new_sup = Supplies(dept, need, desc, ordr, ordrn, done, requester, link, jobno)
        db_session.add(new_sup)
        db_session.commit()

        data = {
            "id": new_sup.id,
            "dept": dept,
            "need": need,
            "desc": desc,
            "ordr": ordr,
            "ordrn": ordrn,
            "done": done,
            "requester": requester,
            "link": link,
            "jobno": jobno
        }

        pusher_client.trigger('table', 'new-record-supplies', {'data': data })

        return redirect("/supplies", code=302)
    else:
        sup = Supplies.query.all()
        return render_template('backend_sup.html', sup=sup)

@app.route('/edit_sup/<int:id>', methods=["POST", "GET"])
def update_record_supplies(id):
    if request.method == "POST":
        dept = request.form["dept"]
        need = request.form["need"]
        desc = request.form["desc"]
        ordr = request.form["ordr"]
        ordrn = request.form["ordrn"]
        done = request.form["done"]
        requester = request.form["requester"]
        link = request.form["link"]
        jobno = request.form["jobno"]

        update_sup = Supplies.query.get(id)
        update_sup.dept = dept
        update_sup.need = need
        update_sup.desc = desc
        update_sup.ordr = ordr
        update_sup.ordrn = ordrn
        update_sup.done = done
        update_sup.requester = requester
        update_sup.link = link
        update_sup.jobno = jobno

        db_session.commit()

        data = {
            "id": id,
            "dept": dept,
            "need": need,
            "desc": desc,
            "ordr": ordr,
            "ordrn": ordrn,
            "done": done,
            "requester": requester,
            "link": link,
            "jobno": jobno
        }

        pusher_client.trigger('table', 'update-record-supplies', {'data': data })

        return redirect("/supplies", code=302)
    else:
        new_sup = Supplies.query.get(id)

        return render_template('update_sup.html', data=new_sup)





# # # PURCHASING # # #

@app.route('/purchhome')
def purchhome():
    note = PurchNotes.query.all()
    return render_template('purchhome.html', note=note)

@app.route('/common_purch')
def common_purch():
    # LASER / ENTERPRISE
    ent = Ent.query.order_by('name').all()

    # TLASER
    tlm = MatlTL.query.order_by('name').all()

    # TLASER
    # dftl = dbtl()[7]
    # dftl = dftl.drop_duplicates()
    # tl = dftl.values.tolist()

    # FLASER
    dffl = dbflaser()[7]
    dffl = dffl.drop_duplicates()
    fl = dffl.values.tolist()

    # SLASER
    dfsl = dbslaser()[7]
    dfsl = dfsl.drop_duplicates()
    sl = dfsl.values.tolist()

    # SAW
    dfs = dbsaw()[7]
    dfs = dfs.drop_duplicates()
    sa = dfs.values.tolist()

    # SHEAR
    dfsh = dbshear()[7]
    dfsh = dfsh.drop_duplicates()
    sh = dfsh.values.tolist()

    # PUNCH
    dfp = dbpunch()[7]
    dfp = dfp.drop_duplicates()
    pu = dfp.values.tolist()

    # LASER / ENTERPRISE
    sup = Supplies.query.order_by('id').all()

    # return render_template('common_purch.html', ent=ent, tl=tl, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)
    return render_template('common_purch.html', ent=ent, tlm=tlm, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)

@app.route('/material_purch')
def material_purch():
    # LASER / ENTERPRISE
    ent = Ent.query.order_by('name').all()

    # TLASER
    tlm = MatlTL.query.order_by('name').all()

    # TLASER
    # dftl = dbtl()[3]
    # dftl = dftl.drop_duplicates()
    # dftl = dftl.sort_values(by = ['DueDate', 'JobNo'])
    # tl = dftl.values.tolist()

    # FLASER
    dffl = dbflaser()[3]
    dffl = dffl.drop_duplicates()
    dffl = dffl.sort_values(by = ['DueDate', 'JobNo'])
    fl = dffl.values.tolist()

    # SLASER
    dfsl = dbslaser()[3]
    dfsl = dfsl.drop_duplicates()
    dfsl = dfsl.sort_values(by = ['DueDate', 'JobNo'])
    sl = dfsl.values.tolist()

    # SAW
    dfs = dbsaw()[3]
    dfs = dfs.drop_duplicates()
    dfs = dfs.sort_values(by = ['DueDate', 'JobNo'])
    sa = dfs.values.tolist()

    # SHEAR
    dfsh = dbshear()[3]
    dfsh = dfsh.drop_duplicates()
    dfsh = dfsh.sort_values(by = ['DueDate', 'JobNo'])
    sh = dfsh.values.tolist()

    # PUNCH
    dfp = dbpunch()[3]
    dfp = dfp.drop_duplicates()
    dfp = dfp.sort_values(by = ['DueDate', 'JobNo'])
    pu = dfp.values.tolist()

    # SUPPLIES
    sup = Supplies.query.order_by('id').all()

    # return render_template('material_purch.html', ent=ent, tl=tl, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)
    return render_template('material_purch.html', ent=ent, tlm=tlm, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)

@app.route('/onorder_purch')
def onorder_purch():
    # LASER / ENTERPRISE
    ent = Ent.query.order_by('name').all()

    # TLASER
    tlm = MatlTL.query.order_by('name').all()

    # TLASER
    # dftl = dbtl()[6]
    # dftl = dftl.drop_duplicates()
    # dftl = dftl.sort_values(by = ['DueDate', 'JobNo'])
    # tl = dftl.values.tolist()

    # FLASER
    dffl = dbflaser()[6]
    dffl = dffl.drop_duplicates()
    dffl = dffl.sort_values(by = ['DueDate', 'JobNo'])
    fl = dffl.values.tolist()

    # SLASER
    dfsl = dbslaser()[6]
    dfsl = dfsl.drop_duplicates()
    dfsl = dfsl.sort_values(by = ['DueDate', 'JobNo'])
    sl = dfsl.values.tolist()

    # SAW
    dfs = dbsaw()[6]
    dfs = dfs.drop_duplicates()
    dfs = dfs.sort_values(by = ['DueDate', 'JobNo'])
    sa = dfs.values.tolist()

    # SHEAR
    dfsh = dbshear()[6]
    dfsh = dfsh.drop_duplicates()
    dfsh = dfsh.sort_values(by = ['DueDate', 'JobNo'])
    sh = dfsh.values.tolist()

    # PUNCH
    dfp = dbpunch()[6]
    dfp = dfp.drop_duplicates()
    dfp = dfp.sort_values(by = ['DueDate', 'JobNo'])
    pu = dfp.values.tolist()

    # SUPPLIES
    sup = Supplies.query.order_by('id').all()

    # return render_template('onorder_purch.html', ent=ent, tl=tl, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)
    return render_template('onorder_purch.html', ent=ent, tlm=tlm, sl=sl, fl=fl, sa=sa, sh=sh, pu=pu, sup=sup)





# # # TAPS # # #

@app.route('/taps')
def taps():
    # note = PurchNotes.query.all()
    tap = Taps.query.order_by('size').all()
    return render_template('taps.html', tap=tap)

@app.route('/backend_taps', methods=["POST", "GET"])
def backend_taps():
    if request.method == "POST":
        tap = request.form["tap"]
        size = request.form["size"]
        note = request.form["note"]

        new_tap = Taps(tap, size, note)
        db_session.add(new_tap)
        db_session.commit()

        data = {
            "id": new_tap.id,
            "tap": tap,
            "size": size,
            "note": note
        }

        pusher_client.trigger('table', 'new-record-taps', {'data': data })

        return redirect("/taps", code=302)
    else:
        tap = Taps.query.all()
        return render_template('backend_taps.html', tap=tap)

@app.route('/edit_tap/<int:id>', methods=["POST", "GET"])
def update_record_taps(id):
    if request.method == "POST":
        tap = request.form["tap"]
        size = request.form["size"]
        note = request.form["note"]

        update_tap = Taps.query.get(id)
        update_tap.tap = tap
        update_tap.size = size
        update_tap.note = note

        db_session.commit()

        data = {
            "id": id,
            "tap": tap,
            "size": size,
            "note": note
        }

        pusher_client.trigger('table', 'update-record-taps', {'data': data })

        return redirect("/taps", code=302)
    else:
        new_tap = Taps.query.get(id)

        return render_template('update_tap.html', data=new_tap)





# # # DIRECTORY # # #

@app.route('/directory')
def directory():
    # note = PurchNotes.query.all()
    dic = Directory.query.order_by('ext').all()
    return render_template('directory.html', dic=dic)

@app.route('/backend_directory', methods=["POST", "GET"])
def backend_directory():
    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["dept"]
        ext = request.form["ext"]
        email = request.form["email"]
        phone = request.form["phone"]

        new_directory = Directory(name, dept, ext, email, phone)
        db_session.add(new_directory)
        db_session.commit()

        data = {
            "id": new_directory.id,
            "name": name,
            "dept": dept,
            "ext": ext,
            "email": email,
            "phone": phone
        }

        pusher_client.trigger('table', 'new-record-directory', {'data': data })

        return redirect("/directory", code=302)
    else:
        dic = Directory.query.all()
        return render_template('backend_directory.html', dic=dic)

@app.route('/edit_directory/<int:id>', methods=["POST", "GET"])
def update_record_directory(id):
    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["dept"]
        ext = request.form["ext"]
        email = request.form["email"]
        phone = request.form["phone"]

        update_directory = Directory.query.get(id)
        update_directory.name = name
        update_directory.dept = dept
        update_directory.ext = ext
        update_directory.email = email
        update_directory.phone = phone

        db_session.commit()

        data = {
            "id": id,
            "name": name,
            "dept": dept,
            "ext": ext,
            "email": email,
            "phone": phone
        }

        pusher_client.trigger('table', 'update-record-directory', {'data': data })

        return redirect("/directory", code=302)
    else:
        new_directory = Directory.query.get(id)

        return render_template('update_directory.html', data=new_directory)





# # # HARDWARE # # #

@app.route('/hardware')
def hardware():
    # note = PurchNotes.query.all()
    hw = Hardware.query.order_by('name').all()
    return render_template('hardware.html', hw=hw)

@app.route('/backend_hardware', methods=["POST", "GET"])
def backend_hardware():
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        hole = request.form["hole"]
        link = request.form["link"]

        new_hw = Hardware(name, desc, hole, link)
        db_session.add(new_hw)
        db_session.commit()

        data = {
            "id": new_hw.id,
            "name": name,
            "desc": desc,
            "hole": hole,
            "link": link
        }

        pusher_client.trigger('table', 'new-record-hardware', {'data': data })

        return redirect("/hardware", code=302)
    else:
        hw = Hardware.query.all()
        return render_template('backend_hardware.html', hw=hw)

@app.route('/edit_hardware/<int:id>', methods=["POST", "GET"])
def update_record_hardware(id):
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        hole = request.form["hole"]
        link = request.form["link"]

        update_hw = Hardware.query.get(id)
        update_hw.name = name
        update_hw.desc = desc
        update_hw.hole = hole
        update_hw.link = link

        db_session.commit()

        data = {
            "id": id,
            "name": name,
            "desc": desc,
            "hole": hole,
            "link": link
        }

        pusher_client.trigger('table', 'update-record-hardware', {'data': data })

        return redirect("/hardware", code=302)
    else:
        new_hw = Hardware.query.get(id)

        return render_template('update_hardware.html', data=new_hw)





#####################################################################################################################
############################################# NOTES ON HOMEPAGES ####################################################
#####################################################################################################################

# PAGE NOTES TLASER
@app.route('/edit_pn/<int:id>', methods=["POST", "GET"])
def update_record_pn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_pnotes = PageNotes.query.get(id)
        update_pnotes.area = area
        update_pnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_pn', {'data': data })

        return redirect("/tlhome", code=302)
    else:
        new_pn = PageNotes.query.get(id)

        return render_template('update_pnotes.html', data=new_pn)



# PAGE NOTES SAW
@app.route('/edit_sawn/<int:id>', methods=["POST", "GET"])
def update_record_sawn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_sawnotes = SawNotes.query.get(id)
        update_sawnotes.area = area
        update_sawnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_sawn', {'data': data })

        return redirect("/sawhome", code=302)
    else:
        new_sawn = SawNotes.query.get(id)

        return render_template('update_sawnotes.html', data=new_sawn)



# PAGE NOTES SHEAR
@app.route('/edit_shearn/<int:id>', methods=["POST", "GET"])
def update_record_shearn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_shearnotes = ShearNotes.query.get(id)
        update_shearnotes.area = area
        update_shearnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_shearn', {'data': data })

        return redirect("/shearhome", code=302)
    else:
        new_shearn = ShearNotes.query.get(id)

        return render_template('update_shearnotes.html', data=new_shearn)



# PAGE NOTES PUNCH
@app.route('/edit_punchn/<int:id>', methods=["POST", "GET"])
def update_record_punchn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_punchnotes = PunchNotes.query.get(id)
        update_punchnotes.area = area
        update_punchnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_punchn', {'data': data })

        return redirect("/punchhome", code=302)
    else:
        new_punchn = PunchNotes.query.get(id)

        return render_template('update_punchnotes.html', data=new_punchn)



# PAGE NOTES SLASER
@app.route('/edit_slasern/<int:id>', methods=["POST", "GET"])
def update_record_slasern(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_slasernotes = SLaserNotes.query.get(id)
        update_slasernotes.area = area
        update_slasernotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_slasern', {'data': data })

        return redirect("/slaserhome", code=302)
    else:
        new_slasern = SLaserNotes.query.get(id)

        return render_template('update_slasernotes.html', data=new_slasern)



# PAGE NOTES FLASER
@app.route('/edit_flasern/<int:id>', methods=["POST", "GET"])
def update_record_flasern(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_flasernotes = FLaserNotes.query.get(id)
        update_flasernotes.area = area
        update_flasernotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_flasern', {'data': data })

        return redirect("/flaserhome", code=302)
    else:
        new_flasern = FLaserNotes.query.get(id)

        return render_template('update_flasernotes.html', data=new_flasern)



# PAGE NOTES FORMING
@app.route('/edit_formingn/<int:id>', methods=["POST", "GET"])
def update_record_formingn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_formingnotes = FormingNotes.query.get(id)
        update_formingnotes.area = area
        update_formingnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_formingn', {'data': data })

        return redirect("/forminghome", code=302)
    else:
        new_formingn = FormingNotes.query.get(id)

        return render_template('update_formingnotes.html', data=new_formingn)



# PAGE NOTES MACHINING
@app.route('/edit_machiningn/<int:id>', methods=["POST", "GET"])
def update_record_machiningn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_machiningnotes = MachiningNotes.query.get(id)
        update_machiningnotes.area = area
        update_machiningnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_machiningn', {'data': data })

        return redirect("/machhome", code=302)
    else:
        new_machiningn = MachiningNotes.query.get(id)

        return render_template('update_machiningnotes.html', data=new_machiningn)



# PAGE NOTES ENGINEEING
@app.route('/edit_engn/<int:id>', methods=["POST", "GET"])
def update_record_engn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_engnotes = EngNotes.query.get(id)
        update_engnotes.area = area
        update_engnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_engn', {'data': data })

        return redirect("/enghome", code=302)
    else:
        new_engn = EngNotes.query.get(id)

        return render_template('update_engnotes.html', data=new_engn)



# PAGE NOTES PURCHASING
@app.route('/edit_purchn/<int:id>', methods=["POST", "GET"])
def update_record_purchn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_purchnotes = PurchNotes.query.get(id)
        update_purchnotes.area = area
        update_purchnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_purchn', {'data': data })

        return redirect("/purchhome", code=302)
    else:
        new_purchn = PurchNotes.query.get(id)

        return render_template('update_purchnotes.html', data=new_purchn)



# PAGE NOTES ENTERPRISE
@app.route('/edit_entn/<int:id>', methods=["POST", "GET"])
def update_record_entn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_entnotes = EntNotes.query.get(id)
        update_entnotes.area = area
        update_entnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_entn', {'data': data })

        return redirect("/enthome", code=302)
    else:
        new_entn = EntNotes.query.get(id)

        return render_template('update_entnotes.html', data=new_entn)



# PAGE NOTES TUBE LASER MATERIAL
@app.route('/edit_tlmn/<int:id>', methods=["POST", "GET"])
def update_record_tlmn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_tlmnotes = TlmNotes.query.get(id)
        update_tlmnotes.area = area
        update_tlmnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_tlmn', {'data': data })

        return redirect("/tlmatlhome", code=302)
    else:
        new_tlmn = TlmNotes.query.get(id)

        return render_template('update_tlmnotes.html', data=new_tlmn)



# PAGE NOTES SUPPLIES
@app.route('/edit_supn/<int:id>', methods=["POST", "GET"])
def update_record_supn(id):
    if request.method == "POST":
        area = request.form["area"]
        notes = request.form["notes"]

        update_supnotes = SupNotes.query.get(id)
        update_supnotes.area = area
        update_supnotes.notes = notes

        db_session.commit()

        data = {
            "id": id,
            "area": area,
            "notes": notes
        }

        pusher_client.trigger('table', 'update-record_supn', {'data': data })

        return redirect("/supplies", code=302)
    else:
        new_supn = SupNotes.query.get(id)

        return render_template('update_supnotes.html', data=new_supn)





# MAINTENANCE
@app.route('/maintenance')
def maintenance():
    mtodos = MTodo.query.order_by('id').all()
    return render_template('maintenance.html', title='Monarch Home', mtodos=mtodos)

@app.route('/completed_maint')
def completed_maint():
    mtodos = MTodo.query.order_by('id').all()
    return render_template('completed_maint.html', title='Monarch Home', mtodos=mtodos)

@app.route('/backend_maint', methods=["POST", "GET"])
def backend_maint():
    eq = equip()
    if request.method == "POST":
        rname = request.form["rname"]
        area = request.form["area"]
        rmach = request.form["rmach"]
        rdate = request.form["rdate"]
        rtype = request.form["rtype"]
        rdesc = request.form["rdesc"]
        aname = request.form["aname"]
        rpname = request.form["rpname"]
        rpdesc = request.form["rpdesc"]
        rptime = request.form["rptime"]
        rpdate = request.form["rpdate"]
        done = request.form["done"]
        comment = request.form["comment"]

        new_mtodo = MTodo(rname, area, rmach, rdate, rtype, rdesc, aname, rpname, rpdesc, rptime, rpdate, done, comment)
        db_session.add(new_mtodo)
        db_session.commit()

        data = {
            "id": new_mtodo.id,
            "rname": rname,
            "area": area,
            "rmach": rmach,
            "rdate": rdate,
            "rtype": rtype,
            "rdesc": rdesc,
            "aname": aname,
            "rpname": rpname,
            "rpdesc": rpdesc,
            "rptime": rptime,
            "rpdate": rpdate,
            "done": done,
            "comment": comment
        }

        pusher_client.trigger('table', 'new-record-mtodo', {'data': data })

        return redirect("/maintenance", code=302)
    else:
        mtodos = MTodo.query.all()
        return render_template('backend_maint.html', mtodos=mtodos, eq=eq)

@app.route('/edit_maint/<int:id>', methods=["POST", "GET"])
def update_record_mtodo(id):
    if request.method == "POST":
        rname = request.form["rname"]
        area = request.form["area"]
        rmach = request.form["rmach"]
        rdate = request.form["rdate"]
        rtype = request.form["rtype"]
        rdesc = request.form["rdesc"]
        aname = request.form["aname"]
        rpname = request.form["rpname"]
        rpdesc = request.form["rpdesc"]
        rptime = request.form["rptime"]
        rpdate = request.form["rpdate"]
        done = request.form["done"]
        comment = request.form["comment"]

        update_mtodo = MTodo.query.get(id)
        update_mtodo.rname = rname
        update_mtodo.area = area
        update_mtodo.rmach = rmach
        update_mtodo.rdate = rdate
        update_mtodo.rtype = rtype
        update_mtodo.rdesc = rdesc
        update_mtodo.aname = aname
        update_mtodo.rpname = rpname
        update_mtodo.rpdesc = rpdesc
        update_mtodo.rptime = rptime
        update_mtodo.rpdate = rpdate
        update_mtodo.done = done
        update_mtodo.comment = comment

        db_session.commit()

        data = {
            "id": id,
            "rname": rname,
            "area": area,
            "rmach": rmach,
            "rdate": rdate,
            "rtype": rtype,
            "rdesc": rdesc,
            "aname": aname,
            "rpname": rpname,
            "rpdesc": rpdesc,
            "rptime": rptime,
            "rpdate": rpdate,
            "done": done,
            "comment": comment
        }

        pusher_client.trigger('table', 'update-record-mtodo', {'data': data })

        return redirect("/maintenance", code=302)
    else:
        new_mtodo = MTodo.query.get(id)

        return render_template('update_mtodo.html', data=new_mtodo)
