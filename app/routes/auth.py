from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Usuario
from app.forms import LoginForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    form = LoginForm()

    attempts = session.get('login_attempts', 0)
    lockout = session.get('lockout_until')

    if lockout:
        if datetime.utcnow() < datetime.fromisoformat(lockout):
            remaining = int((datetime.fromisoformat(lockout) - datetime.utcnow()).total_seconds() // 60)
            flash(f'Demasiados intentos. Intenta de nuevo en {remaining} minutos.', 'error')
            return render_template('login.html', form=form)
        else:
            session.pop('lockout_until', None)
            session['login_attempts'] = 0

    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session.pop('login_attempts', None)
            session.pop('lockout_until', None)
            login_user(user)
            return redirect(url_for('public.dashboard'))
        else:
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            if attempts >= 5:
                session['lockout_until'] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
                flash('Demasiados intentos fallidos. Intenta de nuevo en 15 minutos.', 'error')
            else:
                flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Contraseña actual incorrecta', 'error')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Contraseña actualizada con éxito', 'success')
            return redirect(url_for('public.dashboard'))
    return render_template('change_password.html', form=form)
