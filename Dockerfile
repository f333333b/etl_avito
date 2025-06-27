FROM apache/airflow:2.8.1

USER root

RUN mkdir -p /opt/airflow/etl/data \
    && chown -R airflow: /opt/airflow/etl/data

USER airflow

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./etl /opt/airflow/etl
COPY ./dags /opt/airflow/dags