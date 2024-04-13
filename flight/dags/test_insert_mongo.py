from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
from pymongo import MongoClient
from airflow.hooks.base import BaseHook


def try_():
    return_json = {"hi":8}
    collection = insert_mongodb_atlas()
    collection.insert_one(return_json)
    print("Document inserted successfully.")

def insert_mongodb_atlas():
    conn = BaseHook.get_connection('MONGODB_DEFAULT')
    uri = conn.get_uri()
    client = MongoClient(uri)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client['flying_high']
    collection = db['insurance_guotai']

    mongo_dblist = client.list_database_names()
    if "flying_high" in mongo_dblist:
        print("flying_high database 已存在！")
    else:
        print('flying_high database 不存在')
    
    return collection

with DAG(
    dag_id="hellow_dag",
    schedule= '@daily',
    start_date=pendulum.datetime(2024, 4, 6, tz="UTC"),
    catchup=False,
    tags=["example"],
) as dag:
    operator = PythonOperator(
        task_id='print_hi',
        python_callable=try_,
        dag=dag,
    )