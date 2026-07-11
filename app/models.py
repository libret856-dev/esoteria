from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

vela_categorias = db.Table('vela_categorias',
    db.Column('vela_id', db.Integer, db.ForeignKey('velas.id', ondelete='CASCADE'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categorias.id', ondelete='CASCADE'), primary_key=True)
)

oracion_categorias = db.Table('oracion_categorias',
    db.Column('oracion_id', db.Integer, db.ForeignKey('oraciones.id', ondelete='CASCADE'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categorias.id', ondelete='CASCADE'), primary_key=True)
)


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7))


class Vela(db.Model):
    __tablename__ = 'velas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    imagen = db.Column(db.String(256))
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    categorias = db.relationship('Categoria', secondary=vela_categorias,
                                  backref=db.backref('velas', lazy='dynamic'))


class Oracion(db.Model):
    __tablename__ = 'oraciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    proposito = db.Column(db.Text)
    imagen = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=db.func.now())

    categorias = db.relationship('Categoria', secondary=oracion_categorias,
                                  backref=db.backref('oraciones', lazy='dynamic'))
