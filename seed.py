import os
from app.models import db, Usuario, Categoria, Vela, Oracion


def seed_data():
    if Usuario.query.first() is not None:
        return

    admin = Usuario(username='admin')
    admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
    db.session.add(admin)

    categorias_data = [
        ('Salud', '#4CAF50', 'Velas y oraciones para la salud y el bienestar físico y espiritual'),
        ('Buena Suerte', '#26A69A', 'Para atraer la buena fortuna y el azar positivo'),
        ('Protección', '#42A5F5', 'Protección contra energías negativas y mal de ojo'),
        ('Amor', '#E91E63', 'Para el amor propio, de pareja y la armonía familiar'),
        ('Prosperidad', '#FFB300', 'Para la abundancia económica y el crecimiento profesional'),
        ('Limpieza Espiritual', '#7E57C2', 'Limpieza de energías estancadas y renovación espiritual'),
    ]

    categorias = {}
    for nombre, color, desc in categorias_data:
        cat = Categoria(nombre=nombre, color=color, descripcion=desc)
        db.session.add(cat)
        categorias[nombre] = cat

    db.session.flush()

    velas_data = [
        ('Vela de Protección Blanca', 'proteccion_blanca.jpg',
         'Vela de cera vegetal blanca de 20 cm de altura. Aroma a incienso y mirra. Ideal para rituales de protección y limpieza energética. Se presenta en envase de vidrio transparente.',
         ['Protección', 'Limpieza Espiritual']),
        ('Vela de la Abundancia', 'abundancia_verde.jpg',
         'Vela color verde esmeralda de 15 cm, elaborada con cera de soja. Aceites esenciales de menta, canela y pino. Decorada con hojas de laurel secas en la superficie.',
         ['Prosperidad', 'Buena Suerte']),
        ('Vela del Amor Eterno', 'amor_roja.jpg',
         'Vela roja pasión de 18 cm de cera de palma. Aroma a rosas y vainilla con pétalos de rosa secos incrustados. Base decorada con un lazo de satén rojo.',
         ['Amor']),
        ('Vela de la Salud Radiante', 'salud_azul.jpg',
         'Vela azul celeste de 12 cm de cera de abejas. Aroma a eucalipto, lavanda y menta. Formato cilíndrico compacto ideal para espacios pequeños.',
         ['Salud']),
        ('Vela de la Buena Fortuna', 'fortuna_dorada.jpg',
         'Vela dorada de 10 cm con purpurina biodegradable. Aroma cítrico a naranja y jengibre. Decorada con símbolos de fortuna grabados en la superficie.',
         ['Buena Suerte', 'Prosperidad']),
    ]

    for nombre, img, desc, cats in velas_data:
        vela = Vela(nombre=nombre, imagen=img, descripcion=desc)
        for cat_name in cats:
            vela.categorias.append(categorias[cat_name])
        db.session.add(vela)

    oraciones_data = [
        ('Oración de Sanación',
         'Señor, concede salud y bienestar a mi cuerpo y espíritu. Que la luz divina fluya a través de mí, restaurando cada célula y renovando mi energía vital. Amén.',
         'Ideal para momentos de enfermedad, recuperación o cuando necesitas fortalecer tu energía vital. Ayuda a armonizar el cuerpo y el espíritu.',
         ['Salud']),
        ('Oración para la Buena Suerte',
         'Que la luz divina ilumine mi camino y atraiga la buena fortuna. Abro mi corazón a las oportunidades y confío en que el universo conspira a mi favor.',
         'Recomendada para abrir caminos, atraer oportunidades laborales y comenzar nuevos proyectos con buen pie.',
         ['Buena Suerte', 'Prosperidad']),
        ('Oración de Protección',
         'Con tu escudo divino, protégeme de todo mal y negatividad. Que ninguna energía oscura me alcance y que tu luz me envuelva siempre.',
         'Perfecta para realizar al inicio del día, antes de viajar o cuando sientes que necesitas resguardarte de energías externas.',
         ['Protección']),
        ('Oración para el Amor',
         'Abre mi corazón al amor sincero y verdadero. Que pueda dar y recibir amor en abundancia, y que la armonía reine en mis relaciones.',
         'Para fortalecer la relación de pareja, atraer el amor verdadero o cultivar el amor propio y la autoestima.',
         ['Amor']),
        ('Oración de Prosperidad',
          'Bendice mi trabajo y mis finanzas con abundancia. Que el flujo de la prosperidad llegue a mí y pueda compartirlo con quienes lo necesitan.',
          'Indicada para épocas de cosecha, inicio de mes, o cuando buscas mejorar tu situación económica y atraer abundancia.',
          ['Prosperidad', 'Buena Suerte']),
    ]

    for nombre, contenido, proposito, cats in oraciones_data:
        oracion = Oracion(nombre=nombre, contenido=contenido, proposito=proposito)
        for cat_name in cats:
            oracion.categorias.append(categorias[cat_name])
        db.session.add(oracion)

    db.session.commit()
