import io
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required

from PIL import Image
import cloudinary.uploader
from app.models import db, Oracion, Categoria
from app.forms import OracionForm

oraciones_bp = Blueprint('oraciones', __name__, url_prefix='/oraciones')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@oraciones_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OracionForm()
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.id.desc()).all()]
    if form.validate_on_submit():
        oracion = Oracion(nombre=form.nombre.data, contenido=form.contenido.data, proposito=form.proposito.data)
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
                    return render_template('oracion-form.html', form=form, titulo='Nueva Oración', categorias=categorias)
                img.thumbnail((800, 800), Image.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffer = io.BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                buffer.seek(0)
                result = cloudinary.uploader.upload(buffer, folder='esoteria', resource_type='image')
                oracion.imagen = result['secure_url']
        for cat_id in form.categorias.data:
            cat = db.session.get(Categoria, cat_id)
            if cat:
                oracion.categorias.append(cat)
        db.session.add(oracion)
        db.session.commit()
        flash('Oración creada con éxito', 'success')
        return redirect(url_for('public.dashboard'))
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('oracion-form.html', form=form, titulo='Nueva Oración', categorias=categorias)


@oraciones_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    oracion = db.session.get(Oracion, id)
    if not oracion:
        flash('Oración no encontrada', 'error')
        return redirect(url_for('public.dashboard'))
    form = OracionForm(obj=oracion)
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.id.desc()).all()]
    if form.validate_on_submit():
        oracion.nombre = form.nombre.data
        oracion.contenido = form.contenido.data
        oracion.proposito = form.proposito.data
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
                    form.categorias.data = [c.id for c in oracion.categorias]
                    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
                    return render_template('oracion-form.html', form=form, titulo='Editar Oración', categorias=categorias)
                img.thumbnail((800, 800), Image.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffer = io.BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                buffer.seek(0)
                result = cloudinary.uploader.upload(buffer, folder='esoteria', resource_type='image')
                oracion.imagen = result['secure_url']
        oracion.categorias = []
        for cat_id in form.categorias.data:
            cat = db.session.get(Categoria, cat_id)
            if cat:
                oracion.categorias.append(cat)
        db.session.commit()
        flash('Oración actualizada con éxito', 'success')
        return redirect(url_for('public.dashboard'))
    form.categorias.data = [c.id for c in oracion.categorias]
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('oracion-form.html', form=form, titulo='Editar Oración', categorias=categorias)


@oraciones_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    oracion = db.session.get(Oracion, id)
    if oracion:
        db.session.delete(oracion)
        db.session.commit()
        flash('Oración eliminada con éxito', 'success')
    else:
        flash('Oración no encontrada', 'error')
    return redirect(url_for('public.dashboard'))
