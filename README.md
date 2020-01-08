# SQLalchemy database

playbook for sqlalchemy

## docker pgsql database
```
## start container with link to host machine db files
docker-compose up --build

## connect to database
psql -h localhost -U postgres -d postgres
## password `docker`

```


## alternative directly with docker
```
docker run --rm \
	--name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 \
	-v $HOME/docker/volumes/postgres:/var/lib/postgresql/data \
	postgres
	```