from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Vela, Oracion, Categoria

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    return render_template('home.html')


@public_bp.route('/catalog')
def catalog():
    q = request.args.get('q', '').strip()
    categoria_id = request.args.get('categoria', type=int)
    tipo = request.args.get('tipo', '').strip()
    per_page = 12

    velas_query = Vela.query
    oraciones_query = Oracion.query

    if q:
        like = f'%{q}%'
        velas_query = velas_query.filter(Vela.nombre.ilike(like))
        oraciones_query = oraciones_query.filter(Oracion.nombre.ilike(like))

    if categoria_id:
        velas_query = velas_query.filter(Vela.categorias.any(id=categoria_id))
        oraciones_query = oraciones_query.filter(Oracion.categorias.any(id=categoria_id))

    if tipo == 'velas':
        page = request.args.get('page', 1, type=int)
        velas_pagination = velas_query.order_by(Vela.nombre).paginate(page=page, per_page=per_page, error_out=False)
        oraciones_pagination = None
        velas = velas_pagination.items
        oraciones = []
    elif tipo == 'oraciones':
        page = request.args.get('page', 1, type=int)
        oraciones_pagination = oraciones_query.order_by(Oracion.nombre).paginate(page=page, per_page=per_page, error_out=False)
        velas_pagination = None
        velas = []
        oraciones = oraciones_pagination.items
    else:
        page_velas = request.args.get('page_velas', 1, type=int)
        page_oraciones = request.args.get('page_oraciones', 1, type=int)
        velas_pagination = velas_query.order_by(Vela.nombre).paginate(page=page_velas, per_page=per_page, error_out=False)
        oraciones_pagination = oraciones_query.order_by(Oracion.nombre).paginate(page=page_oraciones, per_page=per_page, error_out=False)
        velas = velas_pagination.items
        oraciones = oraciones_pagination.items

    categorias = Categoria.query.order_by(Categoria.id.desc()).all()

    return render_template('catalog.html', velas=velas, oraciones=oraciones,
                           categorias=categorias, q=q, categoria_id=categoria_id, tipo=tipo,
                           velas_pagination=velas_pagination, oraciones_pagination=oraciones_pagination)


@public_bp.route('/api/velas/<int:id>')
def api_vela(id):
    vela = Vela.query.get_or_404(id)
    cat_ids = [c.id for c in vela.categorias]
    if cat_ids:
        oraciones_rel = Oracion.query.filter(
            Oracion.categorias.any(Categoria.id.in_(cat_ids))
        ).limit(4).all()
    else:
        oraciones_rel = []
    return jsonify({
        'id': vela.id,
        'nombre': vela.nombre,
        'imagen': vela.imagen,
        'descripcion': vela.descripcion,
        'categorias': [{'id': c.id, 'nombre': c.nombre, 'color': c.color} for c in vela.categorias],
        'created_at': vela.created_at.isoformat() if vela.created_at else None,
        'updated_at': vela.updated_at.isoformat() if vela.updated_at else None,
        'oraciones_relacionadas': [
            {'id': o.id, 'nombre': o.nombre,
             'categorias': [c.nombre for c in o.categorias]}
            for o in oraciones_rel
        ],
    })


@public_bp.route('/api/oraciones/<int:id>')
def api_oracion(id):
    oracion = Oracion.query.get_or_404(id)
    cat_ids = [c.id for c in oracion.categorias]
    if cat_ids:
        velas_rel = Vela.query.filter(
            Vela.categorias.any(Categoria.id.in_(cat_ids))
        ).limit(4).all()
    else:
        velas_rel = []
    return jsonify({
        'id': oracion.id,
        'nombre': oracion.nombre,
        'contenido': oracion.contenido,
        'proposito': oracion.proposito,
        'imagen': oracion.imagen,
        'categorias': [{'id': c.id, 'nombre': c.nombre, 'color': c.color} for c in oracion.categorias],
        'created_at': oracion.created_at.isoformat() if oracion.created_at else None,
        'velas_relacionadas': [
            {'id': v.id, 'nombre': v.nombre, 'imagen': v.imagen,
             'categorias': [c.nombre for c in v.categorias]}
            for v in velas_rel
        ],
    })


@public_bp.route('/dashboard')
@login_required
def dashboard():
    tab = request.args.get('tab', 'velas')
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    per_page = 15

    velas_query = Vela.query
    oraciones_query = Oracion.query

    if q:
        like = f'%{q}%'
        velas_query = velas_query.filter(Vela.nombre.ilike(like))
        oraciones_query = oraciones_query.filter(Oracion.nombre.ilike(like))

    velas_pagination = velas_query.order_by(Vela.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    oraciones_pagination = oraciones_query.order_by(Oracion.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('dashboard.html',
                           velas=velas_pagination.items, oraciones=oraciones_pagination.items,
                           velas_pagination=velas_pagination, oraciones_pagination=oraciones_pagination,
                           tab=tab, q=q)
