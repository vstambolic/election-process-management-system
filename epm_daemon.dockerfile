# Image tag : epm_daemon

FROM python:3

RUN mkdir -p /opt/src/epm_daemon
WORKDIR /opt/src/epm_daemon

COPY election_process_management/daemon/app.py ./app.py
COPY election_process_management/daemon/requirements.txt ./requirements.txt
COPY election_process_management/daemon/conf.py ./conf.py
COPY election_process_management/daemon/db_models.py ./db_models.py

RUN pip install -r ./requirements.txt
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Belgrade /etc/localtime
# Syncrhonize container and host time
 # Other solutions:
 # -> create volume localtime_path:/etc/localtime
 # -> from python: datetime.now(tz=pytz.timezone('Europe/Belgrade'))
 # -> create environment variable TZ and use it in python

ENV PYTHONPATH="/opt/src/epm_daemon"
ENTRYPOINT ["python", "./app.py"]