Overview
========

Welcome to Astronomer! This demo provides an example of using (Metaflow)[https://metaflow.org/] with Apache Airflow.  The demo shows how to build a local development using the Metaflow API and developer experience with the ability to schedule and run the steps in an Airflow DAG.  After testing locally the DAG can be pushed to a production Airflow environment.  
  
Project Services
================

This demo includes the following services running in local Docker containers.

- (Airflow)[https://airflow.apache.org/]:  This includes containers for the webserver, scheduler and triggerer.
- (Metaflow)[https://metaflow.org/]: This includes containers for the metadata service, UI and UI backend.
- (Minio)[https://min.io/]:  A local object storage to provide object versioning for Metaflow.  
- (Postgres)[https://www.postgresql.org/]: A database to hold state for Airflow and Metaflow.
  
NOTE: This demo uses containers from (Outerbounds)[https://outerbounds.com/] for the Metaflow service and UI backend.  At the current time these containers are only built for x86 platform architectures.  The Metaflow service and UI backend containers will run on non-x86 systems like Apple M1/M2.  However, the (Metaflow UI)[https://gallery.ecr.aws/outerbounds/metaflow_ui] container is based on the nginx image which has platform dependencies. A multi-architecture image for Metaflow UI has been made available at `mpgregor/metaflow-ui:latest` based on `https://github.com/Netflix/metaflow-ui`.

Project Directory Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. 
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains a sample Metaflow and the Minio data repository.
- requirements.txt: Contains Python packages to be installed in Airflow at startup.
- .env: This environment file provides variables for the Airflow, Metaflow and Minio services listed above.

Deploy Your Project Locally
===========================

Requirements:
- Docker and __Kubernetes__ services enabled.

Note: The Metaflow steps run as (KubernetesPodOperator)[https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html] tasks in Airflow.  Therefore a Kubernetes service is needed.  This demo was built using (Docker Desktop)[https://www.docker.com/products/docker-desktop/] which optionally includes Kubernetes services.  To enable Kubernetes:
    - Open the Docker Desktop Dashboard
    - Click on the Settings (wheel) in the top right
    - Select Kubernetes
    - Select __Enable Kubernetes__
    - Click on __Apply & Restart__ 

Networking: Docker Desktop automatically creates a local network using `host.docker.internal` and maps it in each container.  The `.env` file has been setup with this hostname.  If using a different Docker service these names may need to be updated.

1. Setup the project directory:
```sh
git clone https://github.com/astronomer/airflow-metaflow-demo
cd airflow-metaflow-demo
cp ~/.kube/config include/kube_config
```
  
2. Start Airflow, Metaflow and Minio on your local machine by running 
```sh
astro dev start
```
  
This command will spin up 8 Docker containers on your machine including:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks
- Metaflow-ui: The Metaflow frontend UI.
- Metaflow-ui-backend: The Metaflow UI backend service.
- Metaflow-metadata-service: The metadata service for Metaflow
- Minio: An S3 compatible object storage service.

3. Verify that all 8 Docker containers were created by running 'docker ps'.

4. Create an Airflow DAG.
    
    Metaflow has the ability to (export a flow as an Airflow DAG)[https://docs.metaflow.org/production/scheduling-metaflow-flows/scheduling-with-airflow]. This demo environment has already been (configured)[https://outerbounds.com/engineering/operations/airflow/#configuring-metaflow-for-airflow] for this process. 
    
    For this demo we will use a sample from (Outerbounds' fantastic set of tutorials)[https://outerbounds.com/docs/cv-tutorial-S1E3/]

    The demo includes a sample machine learning workflow for computer vision copied with ❤️ from https://github.com/outerbounds/tutorials/tree/main/cv

    To run this demo you can install metaflow python libraries in a local python environment or connect to the Airflow scheduler container.  

```sh
astro dev bash -s
```
```sh
cd dags
python ../include/cv/model_comparison_flow.py airflow create model_comparison_dag.py 
python ../include/cv/tuning_flow.py airflow create tuning_dag.py 
```

When adding new DAGs to Airflow it may take up to 30 seconds for the DAG to appear in the UI.

  
4. Access the UIs for your local project. 
- Airflow: http://localhost:8080/ login is `admin` password is `admin`
- Metaflow: http://localhost:3000/
- Minio: http://localhost:9001/ login is `admin` password is `adminadmin`

