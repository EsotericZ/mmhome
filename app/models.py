from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import Column, Integer, String, DateTime
# from app.database import Base
from database import Base
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# ENGINEERING JOBS
class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job = Column(String(10))
    eng = Column(String(120))
    wip = Column(Integer())
    hold = Column(Integer())
    hrsn = Column(String(120))
    qc = Column(Integer())
    apr = Column(Integer())
    qcn = Column(String(120))
    model = Column(Integer())
    nest = Column(Integer())

    def __init__(self, job=None, eng=None, wip=None, hold=None, hrsn=None, qc=None, apr=None, qcn=None, model=None, nest=None):
        self.job = job
        self.eng = eng
        self.wip = wip
        self.hold = hold
        self.hrsn = hrsn
        self.qc = qc
        self.apr = apr
        self.qcn = qcn
        self.model = model
        self.nest = nest

    def __repr__(self):
        return '<Job %r>' % (self.job)



# MACHINING JOBS
class MJob(Base):
    __tablename__ = 'mjobs'

    id = Column(Integer, primary_key=True)
    job = Column(String(10))
    eng = Column(String(120))
    wip = Column(Integer())
    hold = Column(Integer())
    hrsn = Column(String(120))

    def __init__(self, job=None, eng=None, wip=None, hold=None, hrsn=None):
        self.job = job
        self.eng = eng
        self.wip = wip
        self.hold = hold
        self.hrsn = hrsn

    def __repr__(self):
        return '<MJob %r>' % (self.job)



# TUBE LASER JOBS
class TJob(Base):
    __tablename__ = 'tjobs'

    id = Column(Integer, primary_key=True)
    job = Column(String(10))
    mtl = Column(Integer())
    mtln = Column(String(120))
    pgm = Column(Integer())
    pgmn = Column(String(120))
    tlh = Column(Integer())
    tlhn = Column(String(120))

    def __init__(self, job=None, mtl=None, mtln=None, pgm=None, pgmn=None, tlh=None, tlhn=None):
        self.job = job
        self.mtl = mtl
        self.mtln = mtln
        self.pgm = pgm
        self.pgmn = pgmn
        self.tlh = tlh
        self.tlhn = tlhn

    def __repr__(self):
        return '<Job %r>' % (self.job)



# BEND DEDUCTION
class Bendd(Base):
    __tablename__ = 'bendd'

    id = Column(Integer, primary_key=True)
    matl = Column(String(10))
    desc = Column(String(25))
    gauge = Column(String(10))
    thick = Column(String(50))
    rad = Column(String(50))
    bd = Column(String(50))
    pt = Column(String(120))
    dt = Column(String(120))
    notes = Column(String(120))

    def __init__(self, matl=None, desc=None, gauge=None, thick=None, rad=None, bd=None, pt=None, dt=None, notes=None):
        self.matl = matl
        self.desc = desc
        self.gauge = gauge
        self.thick = thick
        self.rad = rad
        self.bd = bd
        self.pt = pt
        self.dt = dt
        self.notes = notes

    def __repr__(self):
        return '<Job %r>' % (self.matl)



# SHIPPING
class Ship(Base):
    __tablename__ = 'ship'

    id = Column(Integer, primary_key=True)
    job = Column(String(10))
    date = Column(String(25))
    track = Column(String(120))
    delv = Column(Integer())

    def __init__(self, job=None, date=None, track=None, delv=None):
        self.job = job
        self.date = date
        self.track = track
        self.delv = delv

    def __repr__(self):
        return '<Job %r>' % (self.job)



# TUBE LASER NOTES
class PageNotes(Base):
    __tablename__ = 'pnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# SAW NOTES
class SawNotes(Base):
    __tablename__ = 'sawnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# SHEAR NOTES
class ShearNotes(Base):
    __tablename__ = 'shearnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# PUNCH NOTES
class PunchNotes(Base):
    __tablename__ = 'punchnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# SLASER NOTES
class SLaserNotes(Base):
    __tablename__ = 'slasernotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# FLASER NOTES
class FLaserNotes(Base):
    __tablename__ = 'flasernotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# FORMING NOTES
class FormingNotes(Base):
    __tablename__ = 'formingnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# MACHINING NOTES
class MachiningNotes(Base):
    __tablename__ = 'machiningnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# ENGINEERING NOTES
class EngNotes(Base):
    __tablename__ = 'engnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# PURCHASING NOTES
class PurchNotes(Base):
    __tablename__ = 'purchnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# ENTERPRISE NOTES
class EntNotes(Base):
    __tablename__ = 'entnotes'

    id = Column(Integer, primary_key=True)
    area = Column(String(50))
    notes = Column(String(1000))

    def __init__(self, area=None, notes=None):
        self.area = area
        self.notes = notes

    def __repr__(self):
        return '<Notes %r>' % (self.area)



# ENTERPRISE
class Ent(Base):
    __tablename__ = 'ent'

    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    need = Column(Integer())
    needn = Column(String(120))
    ordr = Column(Integer())
    ordrn = Column(String(120))
    verf = Column(Integer())
    verfn = Column(String(120))
    done = Column(Integer())

    def __init__(self, name=None, need=None, needn=None, ordr=None, ordrn=None, verf=None, verfn=None, done=None):
        self.name = name
        self.need = need
        self.needn = needn
        self.ordr = ordr
        self.ordrn = ordrn
        self.verf = verf
        self.verfn = verfn
        self.done = done

    def __repr__(self):
        return '<Job %r>' % (self.name)



# SUPPLIES
class Supplies(Base):
    __tablename__ = 'supplies'

    id = Column(Integer, primary_key=True)
    dept = Column(String(120))
    need = Column(Integer())
    desc = Column(String(120))
    ordr = Column(Integer())
    ordrn = Column(String(120))
    done = Column(Integer())

    def __init__(self, dept=None, need=None, desc=None, ordr=None, ordrn=None, done=None):
        self.dept = dept
        self.need = need
        self.desc = desc
        self.ordr = ordr
        self.ordrn = ordrn
        self.done = done

    def __repr__(self):
        return '<Job %r>' % (self.dept)



# TODO LIST
class Todo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True)
    rtype = Column(String(120))
    area = Column(String(120))
    desc = Column(String(120))
    name = Column(String(120))
    done = Column(Integer())

    def __init__(self, rtype=None, area=None, desc=None, name=None, done=None):
        self.rtype = rtype
        self.area = area
        self.desc = desc
        self.name = name
        self.done = done

    def __repr__(self):
        return '<Job %r>' % (self.desc)



# MAINTENANCE TODO
class MTodo(Base):
    __tablename__ = 'mtodo'

    id = Column(Integer, primary_key=True)
    rtype = Column(String(120))
    area = Column(String(120))
    desc = Column(String(120))
    name = Column(String(120))
    done = Column(Integer())

    def __init__(self, rtype=None, area=None, desc=None, name=None, done=None):
        self.rtype = rtype
        self.area = area
        self.desc = desc
        self.name = name
        self.done = done

    def __repr__(self):
        return '<Job %r>' % (self.desc)
