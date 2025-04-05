# Credrails

[![Pipeline](https://github.com/ajharry69/credrails/actions/workflows/pipeline.yml/badge.svg)](https://github.com/ajharry69/credrails/actions/workflows/pipeline.yml)
[![Supported Python Versions](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![Supported Django Versions](https://img.shields.io/badge/Django-5.2-purple)](https://www.djangoproject.com/download/)

### Running with Manual Installation

The following guidelines assume presence of an active python virtual environment. In the absence of virtual
environment, please visit [here](https://fastapi.tiangolo.com/virtual-environments/#create-a-project) to set one up.

#### Install dependencies

```bash
pip install --upgrade --upgrade-strategy=eager pip
pip install --upgrade --upgrade-strategy=eager -r requirements-dev.txt
```

#### Running tests

```bash
py.test .
```

#### Start server

```bash
python manage.py runserver
```

### Running with Docker

To run this project using Docker, follow the steps below:

#### Prerequisites

Ensure you have Docker and Docker Compose installed on your system. Refer to
the [Docker installation guide](https://docs.docker.com/get-docker/) for assistance.

#### Build and Run the Application

1. Build the Docker images and start the services:

   ```bash
   docker compose up --build
   ```

2. Access the application at http://localhost:8000/api/reconciliation/reconcile/.

    ```bash
   curl --location --request POST 'http://localhost:8000/api/reconciliation/reconcile/' \
   --form "source=@tests/source.csv;type=text/csv" \
   --form "target=@tests/target.csv;type=text/csv" | jq .
    ```

![Test output](screenshots/test.png)
