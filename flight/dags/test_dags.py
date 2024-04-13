from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum


def print_array():
    my_array = [1, 2, 3]
    print(my_array)
    return my_array


with DAG(
    dag_id="lili_dag",
    schedule= '@daily',
    start_date=pendulum.datetime(2024, 4, 8, tz="UTC"),
    catchup=False,
    tags=["example"],
) as dag:
    operator = PythonOperator(
        task_id='print_array_task',
        python_callable=print_array,
        dag=dag,
    )