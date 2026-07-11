from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Categoria
from app.forms import CategoriaForm

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')


@categorias_bp.route('', methods=['GET', 'POST'])
@login_required
def list_create():
    form = CategoriaForm()
    if form.validate_on_submit():
        cat = Categoria(nombre=form.nombre.data, descripcion=form.descripcion.data,
                        color=form.color.data or None)
        db.session.add(cat)
        db.session.commit()
        flash('Categoría creada con éxito', 'success')
        return redirect(url_for('categorias.list_create'))
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('categorias.html', form=form, categorias=categorias)


@categorias_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    cat = db.session.get(Categoria, id)
    if not cat:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('categorias.list_create'))
    form = CategoriaForm(obj=cat)
    if form.validate_on_submit():
        cat.nombre = form.nombre.data
        cat.descripcion = form.descripcion.data
        cat.color = form.color.data or None
        db.session.commit()
        flash('Categoría actualizada con éxito', 'success')
        return redirect(url_for('categorias.list_create'))
    return render_template('categoria-form.html', form=form, categoria=cat)


@categorias_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    cat = db.session.get(Categoria, id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
        flash('Categoría eliminada con éxito', 'success')
    else:
        flash('Categoría no encontrada', 'error')
    return redirect(url_for('categorias.list_create'))
