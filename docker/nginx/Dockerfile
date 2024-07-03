FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY default.dev.conf /user/src/nginx/conf/
COPY default.prod.conf /user/src/nginx/conf/


COPY healthcheck.sh /usr/src/
COPY entrypoint.sh /usr/src/

RUN chmod +x /usr/src/healthcheck.sh; chmod +x /usr/src/entrypoint.sh

ENTRYPOINT ["usr/src/entrypoint.sh"]
