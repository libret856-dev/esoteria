#!/bin/bash
set -e
python -c "
from app import create_app
from config import Config
import os, time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.models import db
from seed import seed_data

app = create_app()
with app.app_context():
    url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(url)
    for i in range(30):
        try:
            conn = engine.connect()
            conn.close()
            break
        except OperationalError:
            if i < 29:
                time.sleep(1)
    else:
        raise RuntimeError('No se pudo conectar a la base de datos')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()
    seed_data()
"
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} run:app
