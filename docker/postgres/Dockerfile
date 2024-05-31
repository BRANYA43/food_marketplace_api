FROM postgres:16.0-alpine

COPY init.sh /docker-entrypoint-initdb.d/
COPY healthcheck.sh /usr/src/

RUN chmod +x /usr/src/healthcheck.sh