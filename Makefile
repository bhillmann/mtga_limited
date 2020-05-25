build :
	scripts/docker-build.sh

env :
	rm -f ./.env && ln -s ./config/.env ./.env

up : env
	docker-compose up -d

update-env :
	pip install --no-cache-dir -r ./requirements.txt --upgrade
