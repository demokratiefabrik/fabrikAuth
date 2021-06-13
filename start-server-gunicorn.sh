#!/usr/bin/env bash
# PREPARE DOCKER SECRETS (Workaround, since we are not in swarm mode)
# remove symbolic link => create real directory
rm -Rf /var/run
mkdir /var/run
cp -R /run/secrets /var/run/secrets
chmod -Rf 555 /var/run/secrets
# TODO: hmm why everybody requires execution permission.?? gunicorn user is www-data, right?
#chown -Rf root:www-data /var/run/secrets

# TODO: only for DJANGO MODE....
# RUN celery worker

echo "STARTING SERVER"
cd ./fabrikAuth
# FIND SITE package PATH and write it to extpath file.
chmod -R 777 ./

# CELERY: Python Massmailer => Batch email sending job... (ONLY FOR MODE=DJANGO)
# GUNICORN - A LIGHTWIGHT PYTHON SERVER

if [ "$MODE" == "OAUTH" ] 
then
  sudo -u www-data gunicorn fabrikAuth.wsgi:application --pythonpath ./fabrikAuth --timeout 60 --user www-data --bind 0.0.0.0:8010 --workers 4
else
  sudo -u www-data /usr/local/bin/celery -A fabrikAuth worker &
  (gunicorn fabrikAuth.wsgi:application --pythonpath ./fabrikAuth --timeout 60 --user www-data --bind 0.0.0.0:8010 --workers 1 )
fi

# NOTES:
# Gunicorn relies on the operating system to provide all of the load balancing when handling requests. 
# Generally we recommend (2 x $num_cores) + 1 as the number of workers to start off with. 
# While not overly scientific, the formula is based on the assumption that for a given core, one worker will be reading or writing from the socket
# while the other worker is processing a request.
