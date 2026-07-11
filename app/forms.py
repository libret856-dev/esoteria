from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectMultipleField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('new_password', message='Las contraseñas no coinciden')])
    submit = SubmitField('Cambiar contraseña')


class VelaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    imagen = FileField('Imagen', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes (jpg, jpeg, png, gif, webp)')])
    descripcion = TextAreaField('Descripción', description='Características físicas: color, tamaño, peso, aroma, etc.')
    categorias = SelectMultipleField('Categorías', coerce=int)
    submit = SubmitField('Guardar')


class OracionForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    proposito = TextAreaField('Propósito', description='¿Para qué sirve esta oración? Beneficios, intención, etc.')
    imagen = FileField('Imagen', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes (jpg, jpeg, png, gif, webp)')])
    categorias = SelectMultipleField('Categorías', coerce=int)
    submit = SubmitField('Guardar')


class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    color = StringField('Color', render_kw={'type': 'color'})
    submit = SubmitField('Guardar')
