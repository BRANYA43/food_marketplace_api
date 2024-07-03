#!/bin/bash
if [ "$NGINX_STAGING" = "1" ] || [ "$NGINX_STAGING" = "True" ] || [ "$NGINX_STAGING" = "true" ]; then
    echo "Setting default.dev.conf as default config."
    cp /user/src/nginx/conf/default.dev.conf /etc/nginx/conf.d/default.conf
    echo "Setting is done."
else
    echo "Setting default.prod.conf as default config."
    cp /user/src/nginx/conf/default.prod.conf /etc/nginx/conf.d/default.conf
    echo "Setting is done."
fi

if command -v nginx &> /dev/null; then
    echo "nginx found, starting nginx..."
    nginx -g 'daemon off;'
else
    echo >&2 "Error: nginx not found. Aborting."
    exit 1
fi