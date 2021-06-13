# Dockerfile
# https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application
# FROM python:3.7-buster

# Dockerfile
# https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application

# FROM python:3.7-buster

# DEFAULT ALPINE SETUP (SYNC WITH fabrikApi)
FROM python:3.8-alpine

# install nginx
# RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
# COPY nginx.default /etc/nginx/sites-available/default
# RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#     && ln -sf /dev/stderr /var/log/nginx/error.log
# copy source and install dependencies
# COPY .pip_cache /opt/app/pip_cache/
#COPY . /opt/app/fabrikApi/
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
# RUN mkdir -p /opt/app/fabrikAuth
WORKDIR /opt/app

# OnlY NEEDED FOR ALPINE
# TODO: we do not have to install the full mysql client, right?
RUN set -e; \
  apk add --no-cache --virtual .build-deps \
  bash \
  nano \
  gcc \
  libc-dev \
  linux-headers \
  mariadb-dev \
  python3-dev; \
  set -x ; \
  addgroup -g 82 -S www-data ; \
  adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1 ;

# fabrikAuth specifications
# for cryptography python module...
RUN apk add --no-cache \
  libressl-dev \
  musl-dev \
  libffi-dev

# TEMPORARY, I BELIEVE
#RUN apk add --no-cache ssmtp sudo

# COPY requirements.txt start-server-gunicorn.sh ./
# crypto: https://stackoverflow.com/questions/50619166/docker-installing-python-cryptography-on-alpine-linux-distribution/50651322
# RUN apk update && apk add libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev
RUN mkdir -p /opt/app/fabrikAuth
COPY requirements.txt ./
RUN pip install -Ur requirements.txt --cache-dir /opt/app/pip_cache; \
  rm -Rf /opt/app/pip_cache; \
  rm -Rf /opt/app/.pytest_cache; \
  rm -Rf /opt/app/.vscode; \
  rm -Rf /opt/app/.coveragerc; \
  chown -R www-data:www-data /opt/app
RUN apk del libressl-dev musl-dev libffi-dev
COPY start-server-gunicorn.sh ./
COPY . ./fabrikAuth/
RUN apk add --no-cache sudo
RUN pip install --upgrade importlib-metadata
RUN pip install celery 
# putt celery module packages folder first in path

# > sys.path.insert(0,celery.__file__)
# >>> import celery

# start server
EXPOSE 8010 
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server-gunicorn.sh"]

# COPY start-server-gunicorn.sh ./
# COPY . ./fabrikAuth/
# RUN chown -R root:www-data ./
