# Image tag : epm_db_migration

FROM python:3

RUN mkdir -p /opt/src/epm_db_migration
WORKDIR /opt/src/epm_db_migration

COPY election_process_management/db_migration/migrate.py ./migrate.py
COPY election_process_management/db_migration/requirements.txt ./requirements.txt
COPY election_process_management/db_migration/conf.py ./conf.py
COPY election_process_management/db_migration/db_models.py ./db_models.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/epm_db_migration"
ENTRYPOINT ["python", "./migrate.py"]