import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app import create_app
from app.models import db
from seed import seed_data

app = create_app()


def wait_for_db():
    url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(url)
    for i in range(30):
        try:
            conn = engine.connect()
            conn.close()
            return True
        except OperationalError:
            if i < 29:
                time.sleep(1)
    raise RuntimeError('No se pudo conectar a la base de datos')


if __name__ == '__main__':
    with app.app_context():
        wait_for_db()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
