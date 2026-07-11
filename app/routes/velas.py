import os
import io
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image
import cloudinary.uploader
from app.models import db, Vela, Categoria
from app.forms import VelaForm

velas_bp = Blueprint('velas', __name__, url_prefix='/velas')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@velas_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = VelaForm()
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.id.desc()).all()]
    if form.validate_on_submit():
        vela = Vela(nombre=form.nombre.data, descripcion=form.descripcion.data)
        file = form.imagen.data
        if file and hasattr(file, 'filename') and file.filename:
            if allowed_file(file.filename):
                file.stream.seek(0)
                try:
                    img = Image.open(io.BytesIO(file.stream.read()))
                    img.verify()
                    file.stream.seek(0)
                    img = Image.open(io.BytesIO(file.stream.read()))
                except Exception:
                    flash('El archivo no es una imagen válida.', 'error')
                    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
                    return render_template('vela-form.html', form=form, titulo='Nueva Vela', categorias=categorias)
                filename = secure_filename(file.filename)
                img.thumbnail((800, 800), Image.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                result = cloudinary.uploader.upload(file.stream, folder='esoteria')
                vela.imagen = result['secure_url']
        for cat_id in form.categorias.data:
            cat = db.session.get(Categoria, cat_id)
            if cat:
                vela.categorias.append(cat)
        db.session.add(vela)
        db.session.commit()
        flash('Vela creada con éxito', 'success')
        return redirect(url_for('public.dashboard'))
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('vela-form.html', form=form, titulo='Nueva Vela', categorias=categorias)


@velas_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    vela = db.session.get(Vela, id)
    if not vela:
        flash('Vela no encontrada', 'error')
        return redirect(url_for('public.dashboard'))
    form = VelaForm(obj=vela)
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.id.desc()).all()]
    if form.validate_on_submit():
        vela.nombre = form.nombre.data
        vela.descripcion = form.descripcion.data
        file = form.imagen.data
        if file and hasattr(file, 'filename') and file.filename:
            if allowed_file(file.filename):
                file.stream.seek(0)
                try:
                    img = Image.open(io.BytesIO(file.stream.read()))
                    img.verify()
                    file.stream.seek(0)
                    img = Image.open(io.BytesIO(file.stream.read()))
                except Exception:
                    flash('El archivo no es una imagen válida.', 'error')
                    form.categorias.data = [c.id for c in vela.categorias]
                    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
                    return render_template('vela-form.html', form=form, titulo='Editar Vela', categorias=categorias)
                filename = secure_filename(file.filename)
                img.thumbnail((800, 800), Image.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                result = cloudinary.uploader.upload(file.stream, folder='esoteria')
                vela.imagen = result['secure_url']
        vela.categorias = []
        for cat_id in form.categorias.data:
            cat = db.session.get(Categoria, cat_id)
            if cat:
                vela.categorias.append(cat)
        db.session.commit()
        flash('Vela actualizada con éxito', 'success')
        return redirect(url_for('public.dashboard'))
    form.categorias.data = [c.id for c in vela.categorias]
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('vela-form.html', form=form, titulo='Editar Vela', categorias=categorias)


@velas_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    vela = db.session.get(Vela, id)
    if vela:
        db.session.delete(vela)
        db.session.commit()
        flash('Vela eliminada con éxito', 'success')
    else:
        flash('Vela no encontrada', 'error')
    return redirect(url_for('public.dashboard'))
