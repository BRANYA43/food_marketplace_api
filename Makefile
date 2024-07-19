fs ?=
up_fs ?=
down_fs ?=
start_fs ?=
stop_fs ?=

shell=/bin/sh

up:
	sudo docker compose up $(fs)

down:
	sudo docker compose down $(fs)

reup:
	sudo docker compose down $(down_fs); sudo docker compose up $(up_f)

start:
	sudo docker compose start $(fs)

stop:
	sudo docker compose stop $(fs)

restart:
	sudo docker compose stop $(stop_fs); sudo docker compose start $(start_fs)

images:
	sudo docker images -a $(fs)

ps:
	sudo docker ps -a $(fs)

image-prune:
	sudo docker image prune -af $(fs)

push:
	sudo docker compose build; sudo docker compose push;

shell-api:
	sudo docker exec -it api $(shell)

shell-db:
	sudo docker exec -it db $(shell)

shell-nginx:
	sudo docker exec -it nginx $(shell)

logs-api:
	sudo docker logs api $(fs)

logs-db:
	sudo docker logs db $(fs)

logs-nginx:
	sudo docker logs nginx $(fs)

