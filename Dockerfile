FROM python:3.7-slim-stretch

RUN apt-get update && \
apt-get upgrade -y && \
apt-get -y install git libspatialindex-dev &&  \
rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --no-cache-dir --compile --upgrade pip

COPY ./scripts .
COPY . .

RUN pip3 install --no-cache-dir --compile -e . && pip cache purge
ENV PYTHONPATH=./scripts:${PYTHONPATH}

ENTRYPOINT ["osmox", "run"]