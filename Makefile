build :
	scripts/docker-build.sh

env :
	rm -f ./.env && ln -s ./config/.env ./.env

up : env build
	docker-compose up -d --force-rebuild

update-env :
	pip install --no-cache-dir -r ./requirements.txt --upgrade
