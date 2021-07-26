# Image tag : ac

FROM python:3

RUN mkdir -p /opt/src/access_control
RUN mkdir -p /opt/src/access_control/utils
WORKDIR /opt/src/access_control

COPY access_control/app.py ./app.py
COPY access_control/conf.py ./conf.py
COPY access_control/data_validator.py ./data_validator.py
COPY access_control/db_models.py ./db_models.py
COPY access_control/requirements.txt ./requirements.txt
COPY utils/__init__.py ./utils/__init__.py
COPY utils/permission_control.py ./utils/permission_control.py

RUN pip install -r ./requirements.txt
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Belgrade /etc/localtime

ENV PYTHONPATH="/opt/src/access_control"
ENTRYPOINT ["python", "./app.py"]