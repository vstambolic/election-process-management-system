# Image tag : ac_db_migration

FROM python:3

RUN mkdir -p /opt/src/ac_db_migration
WORKDIR /opt/src/ac_db_migration

COPY access_control/migrate.py ./migrate.py
COPY access_control/conf.py ./conf.py
COPY access_control/db_models.py ./db_models.py
COPY access_control/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]

