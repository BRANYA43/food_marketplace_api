![Static Badge](https://img.shields.io/badge/Python-%23?style=for-the-badge&logo=python&logoColor=white&labelColor=%230a0a0a&color=%233776AB)
![Static Badge](https://img.shields.io/badge/Django-%23?style=for-the-badge&logo=django&logoColor=white&labelColor=%230a0a0a&color=%23092E20)
![Static Badge](https://img.shields.io/badge/Django%20REST%20Framework-%23?style=for-the-badge&logo=django&logoColor=white&labelColor=%230a0a0a&color=b81414)
![Static Badge](https://img.shields.io/badge/Swagger-%23?style=for-the-badge&logo=swagger&logoColor=white&labelColor=%230a0a0a&color=%2385EA2D)
![Static Badge](https://img.shields.io/badge/Postgres-%23?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=%230a0a0a&color=%234169E1)
![Static Badge](https://img.shields.io/badge/Docker-%23?style=for-the-badge&logo=docker&logoColor=white&labelColor=%230a0a0a&color=%232496ED)
![Static Badge](https://img.shields.io/badge/%20pre%20commit-%23?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=%230a0a0a&color=%23FAB040)
![Static Badge](https://img.shields.io/badge/Ruff-%23?style=for-the-badge&logo=ruff&logoColor=white&labelColor=%230a0a0a&color=%23D7FF64)
![Static Badge](https://img.shields.io/badge/nginx-%23?style=for-the-badge&logo=nginx&logoColor=white&labelColor=%230a0a0a&color=%23009639)
![Static Badge](https://img.shields.io/badge/poetry-%23?style=for-the-badge&logo=poetry&logoColor=white&labelColor=%230a0a0a&color=%2360A5FA)
![Static Badge](https://img.shields.io/badge/gunicorn-%23?style=for-the-badge&logo=gunicorn&logoColor=white&labelColor=%230a0a0a&color=%23499848)
![Static Badge](https://img.shields.io/badge/JWT-%23?style=for-the-badge&logo=jsonwebtokens&labelColor=0a0a0a&color=%23662D91)

***

# Food Marketplace API

### All Environment values
#### Django environment values
* **DJANGO_SECRET_KEY** - secret key of django app.
* **DJANGO_SETTINGS_ENV** - load production or development settings
of django app. It's `production`, by default.
* **DJANGO_ALLOWED_HOSTS** - list of allowed hosts for django app.
Add needed your hosts to list django app allow you to enter on site 
by these hosts. It's `localhost [::1] 127.0.0.1 0.0.0.0` by default.
* **DJANGO_SUPERUSER_EMAIL** - email of superuser for django admin site.
It's `admin@admin.com` by default.
* **DJANGO_SUPERUSER_PASSWORD** - password of superuser for django admin site.
It's `123` by default.

#### Postgres environment values
- **POSTGRES_DB** - database name for Postgres. It's `postgres` by default.
- **POSTGRES_USER** - user to enter to database. It's `postgres` by default.
- **POSTGRES_PASSWORD** - user password to enter to database. 
It's `postgres` by default.
- **POSTGRES_HOST** - host for postgres. Host must be similarly 
name of docker compose service for Postgres. 
- **POSTGRES_PORT** - port for Postgres listening. It's `5432` by default.

### Template of .env file with required environment values
```dotenv
DJANGO_SECRET_KEY=<secret key>
DJANGO_ALLOWED_HOSTS='localhost [::1] 127.0.0.1 0.0.0.0'
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=123

POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=<host>
```

***

### Django admin site credential by default
- Username: admin@admin.com
- Password: 123

***
### Docker commands
#### Run steck of containers
```commandline
docker compose up
```

#### Stop steck of container
```
ctrl + C
```
OR
```commandline
docker compose stop
```
#### Delete steck of containers
```commandline
docker compose down
```
with volumes
```commandline
docker compose down -v
```

If you installed docker compose as application to your OS that command must start with 
`docker-compose` instead `docker compose`.

***

### Links
#### Admin Site
- http://localhost/admin/

#### Swagger
- http://localhost/api/schema/swagger-ui/

#### Redoc
- http://localhost/api/schema/redoc/

#### API
- http://localhost/api/schema/redoc/

***

### Example of access token header

| Header        | Value                 |
|---------------|-----------------------|
| Authorization | Bearer <access_token> |

