# Image tag : epm_election_official

FROM python:3

RUN mkdir -p /opt/src/epm_eo
RUN mkdir -p /opt/src/epm_eo/utils
WORKDIR /opt/src/epm_eo

COPY election_process_management/election_official/app.py ./app.py
COPY election_process_management/election_official/requirements.txt ./requirements.txt
COPY election_process_management/election_official/conf.py ./conf.py

COPY utils/__init__.py ./utils/__init__.py
COPY utils/permission_control.py ./utils/permission_control.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/epm_eo"
ENTRYPOINT ["python", "./app.py"]