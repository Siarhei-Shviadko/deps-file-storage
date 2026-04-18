-include .env
-include vendors/deps-pipelines/shared/Makefile
-include Makefile.local

APP_NAME=file-storage
PROJECT_DIRECTORY_NAME=deps_file_storage/
CURRENT_UID := $(shell id -u):$(shell id -g)
HASH := $(shell git rev-parse HEAD)
DATE := $(shell date)
TAG = $(shell git describe || echo "latest")
INJECT_VAULT_SECRETS := $(shell [[ -z "$$INJECT_VAULT_SECRETS" ]] && echo false || echo $$INJECT_VAULT_SECRETS)
commit_short_sha := "$(CI_COMMIT_SHORT_SHA)"
commit_short_sha_migrator := "tag$(CI_COMMIT_SHORT_SHA)"


NO_DEV_DOCKER_IMAGE = file-storage
DEV_DOCKER_IMAGE = file-storage-dev

.PHONY: config
## Show current docker compose config
config:
	docker compose -f docker-compose.yml config

.PHONY: config-test
## Show docker compose test config
config-test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml config

.PHONY: install
## Install default environment settings
install:
	cp .env.example .env

.PHONY: login
## Login in docker registry
login:
	docker login $(repository)

.PHONY: prereq
prereq:
	test -f .env || echo >> .env
	docker network create deps-network || true

.PHONY: prereq-tests
prereq-tests: | prereq
	docker compose -f docker-compose.yml -f docker-compose.test.yml down -v

.PHONY: run
## Run service
run: | prereq
	docker compose up -d

.PHONY: logs
## Open service logs
logs:
	docker compose logs -f

.PHONY: status
## Get running status information
status:
	docker compose ps

.PHONY: stop
## Stop runned services
stop:
	docker compose stop

.PHONY: build
## Build containers
build:
	docker compose build \
	--build-arg BUILD_HASH=$(HASH) \
	--build-arg BUILD_TAG=$(TAG) \
	--build-arg BUILD_DATE="$(DATE)"

.PHONY: migrate
## Apply database migrations
migrate:
	docker compose run --rm migrator update

.PHONY: shell-app
## Open shell in Corleone API container
shell-app:
	docker compose exec -u root $(APP_NAME) /bin/sh

.PHONY: format
## Apply black & isort code formatting
format:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path setup.cfg .

.PHONY: format-check
## Check for correct code format
format-check:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml --check .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path setup.cfg --check-only .

.PHONY: lint
## Check code using linters
lint:
	docker compose run --rm --no-deps $(APP_NAME) flake8 .

.PHONY: mypy
## Check code using mypy
mypy:
	docker compose run --rm --no-deps $(APP_NAME) mypy .

.PHONY: tests-unit
## Run unit tests
tests-unit:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps $(APP_NAME) coverage run -a -m pytest -vv -x tests/unit

.PHONY: tests-integration
## Run integration tests
tests-integration:
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d test-database
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm migrator update
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm $(APP_NAME) coverage run -a -m pytest -vv -x tests/integration
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f

.PHONY: tests
## Run unit & integration tests
tests:
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d test-database
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm migrator update
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm $(APP_NAME) coverage run	-a -m pytest -vv -x --junitxml=junit-report.xml tests
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f

.PHONY: coverage
## Get code coverage report
coverage:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm $(APP_NAME) coverage report -i --rcfile=/app/setup.cfg

.PHONY: coverage-xml
## Generate xml coverage report
coverage-xml:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm $(APP_NAME) coverage xml -i --rcfile=/app/setup.cfg -o /app/tests/coverage.xml

.PHONY: ci
## Run CI checks
ci: | prereq-tests format-check lint mypy tests coverage prereq-tests
	@if [ "$(version)" == "ci" ]; then \
		make coverage-xml;\
	else \
	  	make requirements-lock; \
	fi

.PHONY: build-prod
## Build images for production
build-prod:
	$(call build_service,file-storage-dev,./etc/deps-file-storage/Dockerfile,,develop)
	$(call build_service,file-storage,./etc/deps-file-storage/Dockerfile,,,file-storage-dev)
	$(call build_service,file-storage-nginx,./etc/deps-file-storage-nginx/Dockerfile,./etc/deps-file-storage-nginx)
	$(call build_service,file-storage-migrator,./etc/migrator/Dockerfile)

.PHONY: push
## Push images to registry
push:
	$(call push_service,file-storage)
	$(call push_service,file-storage-dev)
	$(call push_service,file-storage-nginx)
	$(call push_service,file-storage-migrator)

.PHONY: deliver
## Build prod images and push to registry
deliver: | build-prod push

.PHONY: tag
## Retag built services
tag:
	$(call tag_service,file-storage)
	$(call tag_service,file-storage-dev)
	$(call tag_service,file-storage-nginx)
	$(call tag_service,file-storage-migrator)

.PHONY: pull
## Pull service images from docker registry
pull:
	$(call pull_service,file-storage)
	$(call pull_service,file-storage-dev)
	$(call pull_service,file-storage-nginx)
	$(call pull_service,file-storage-migrator)

.PHONY: helm-upgrade-service
helm-upgrade-service:
	helm upgrade --install $(CI_PROJECT_NAME) .helm/services \
        --values .helm/services/values.yaml $(ADDITIONAL_VALUES) \
        --set registry=$(REPOSITORY_URL) \
        --set file_storage.image.tag=$(commit_short_sha) \
        --set file_storage_consumer.image.tag=$(commit_short_sha) \
        --set file_storage_nginx.image.tag=$(commit_short_sha) \
        --set vault_settings.enabled=$(VAULT_ENABLE) \
        --set file_storage_settings.DATABASE_REQUIRE_SECURE_TRANSPORT=$(DATABASE_REQUIRE_SECURE_TRANSPORT) \
		--timeout 300s \
        --atomic \
        --wait \
        --debug \
        --namespace $(NAMESPACE)

.PHONY: helm-apply-migrations
helm-apply-migrations:
	helm upgrade --install $(CI_PROJECT_NAME)-migrator .helm/migrator \
        --values .helm/migrator/values.yaml $(ADDITIONAL_VALUES) \
        --set registry=$(REPOSITORY_URL) \
        --set migrator_update.image.tag=$(commit_short_sha) \
        --set migrator.args="$(migration_command)" \
        --set vault_settings.enabled=$(VAULT_ENABLE) \
        --set migration_settings.DATABASE_REQUIRE_SECURE_TRANSPORT=$(DATABASE_REQUIRE_SECURE_TRANSPORT) \
		--timeout 300s \
        --atomic \
        --wait \
        --debug \
        --namespace $(NAMESPACE)

.PHONY: helm-migration-rollback
helm-migration-rollback:
	make migration_command="rollback $(commit_short_sha_migrator)" helm-apply-migrations

.PHONY: helm-deployment-rollback
helm-deployment-rollback:
	helm rollback --namespace $(NAMESPACE) $(CI_PROJECT_NAME) 0

.PHONY: helm-rollback
helm-rollback:
	make helm-migration-rollback
	make helm-deployment-rollback

.PHONY: helm-upgrade
helm-upgrade:
	make migration_command="tag $(commit_short_sha_migrator)" helm-apply-migrations
	make helm-apply-migrations
	make helm-upgrade-service

testdkube := $(shell kubectl config current-context)
ifeq ($(testdkube), rancher-desktop)
.PHONY: skaffold
skaffold:
	cd skaffold && skaffold run -f skaffold.yaml
endif

.PHONY: build-no-dev
build-no-dev:
	$(call build_service,$(NO_DEV_DOCKER_IMAGE),./etc/deps-file-storage/Dockerfile,,build,$(DEV_DOCKER_IMAGE))
