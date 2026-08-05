# File-storage

Service for downloading and uploading files.

**JIRA TICKET [RSEGDSSEAC-1158](https://jiraeu.epam.com/plugins/servlet/mobile#issue/RSEGDSSEAC-1158)**

#### TODO:
1. Ability to add new engines:
    * GCP;
    * Azure;
    * AWS.
2. Covered by unit and integrational tests;
3. Documentation
4. Logging

## How to run project

```bash
# Setup environment variables for run
make install

# Fill required variables in .env file. 
# Actual information about variables could be found at KB onboarding page

# Build application containers
make build

# Up services
docker-compose up -d
```

## Usage 

```bash
# run mypy:
make mypy

# run lint:
make lint

# run code formatters (will change source code):
make format

# run code formatter check
make format-check

# run all static checks (mypy, lint, formatter-check):
make static-check

Logs are available in output folder

# run tests:
make tests

# Upload file
curl --location --request POST 'http://localhost:8003/api/storage/v1/file/<optional_path>' \
--header 'content-type: multipart/form-data' \
--form 'file=@/path/to/uploaded/file' \

# Download file
curl --location --request GET 'http://localhost:8003/api/storage/v1/<optional_path>/<filename>' \
--header 'content-type: multipart/related'

# Cause internal server error to check sentry
curl --location --request GET 'http://localhost:8003/api/storage/v1/debug/500'
```

## Environment variables

| name | type | required | default |
|------|------|----------|---------|
| MEDIA_ROOT | str | false | "media/files" |
| FILE_STORAGE_LOGGER_LEVEL | int | false | 30 (logging.WARNING) |
## Useful links

- [Docker](https://docs.docker.com/)
- [Flask](http://flask.pocoo.org/docs/1.0/)
- [PyTest](https://docs.pytest.org/en/latest/)
- [HTTPie](https://httpie.org/)

### Run locally using skaffold 
 Make sure that deps-infra (postgres, redis, rabbitmq is up) is up and running

# !Note make sure that context is rancher-desktop
```bash 
kubectl config current-context 
```

Do the following commands

```bash
make skaffold
```

## Enabling/Disabling vault usage
You can enable or disable vault secret usage without modifying kubernetes yaml files. By default vault usage is set to false inside value.yaml file but we override this value with VAULT_ENABLE_DEV, VAULT_ENABLE_QA, VAULT_ENABLE_INS, VAULT_ENABLE_DEMO, VAULT_ENABLE_DS variables from Settings >> CI/CD for each environment. If you change variable value from Settings >> CI/CD you need to manually start new pipline from CI/CD >> Pipelines.
