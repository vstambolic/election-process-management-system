# Image tag : epm_admin

FROM python:3

RUN mkdir -p /opt/src/epm_admin
RUN mkdir -p /opt/src/epm_admin/utils
WORKDIR /opt/src/epm_admin

COPY election_process_management/admin/app.py ./app.py
COPY election_process_management/admin/requirements.txt ./requirements.txt
COPY election_process_management/admin/conf.py ./conf.py
COPY election_process_management/admin/db_models.py ./db_models.py

COPY utils/__init__.py ./utils/__init__.py
COPY utils/permission_control.py ./utils/permission_control.py

RUN pip install -r ./requirements.txt
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Belgrade /etc/localtime
# Syncrhonize container and host time
 # Other solutions:
 # -> create volume localtime_path:/etc/localtime
 # -> from python: datetime.now(tz=pytz.timezone('Europe/Belgrade'))
 # -> create environment variable TZ and use it in python
ENV PYTHONPATH="/opt/src/epm_admin"
ENTRYPOINT ["python", "./app.py"]