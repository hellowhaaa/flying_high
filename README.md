## airflow

> 得到官方 yaml 檔

- curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.0/docker-compose.yaml'

> 建立四個 folder

- mkdir -p ./dags ./logs ./plugins ./config

> 啟動環境

`docker compose up airflow-init`
`docker compose up`
