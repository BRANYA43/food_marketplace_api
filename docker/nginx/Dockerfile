FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY default.conf /etc/nginx/conf.d/
COPY healthcheck.sh /usr/src/

RUN chmod +x /usr/src/healthcheck.sh