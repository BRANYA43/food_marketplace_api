install:
	curl -fsSL https://get.docker.com -o get-docker.sh
	sudo sh get-docker.sh
	rm get-docker.sh

up:
	sudo docker compose up

up-build:
	sudo docker compose up --build

down:
	sudo docker compose down

down-volume:
	sudo docker compose down -v

reup:
	sudo docker compose down; sudo docker compose up

start:
	sudo docker compose start

stop:
	sudo docker compose stop

restart:
	sudo docker compose stop; sudo docker compose start

shell-api:
	sudo docker exec -it api /bin/bash

shell-nginx:
	sudo docker exec -it nginx /bin/bash

shell-db:
	sudo docker exec -it db /bin/bash

rmi:
	sudo docker rmi -f $(sudo docker images -q)

imgs:
	sudo docker images -a

ps:
	sudo docker ps -a

