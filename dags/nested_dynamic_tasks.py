import json
from pendulum import datetime

from airflow.operators.python import PythonOperator
from airflow.decorators import (
    dag,
    task,
    task_group,
)

@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args={
        "retries": 2,  
    },
    tags=["metaflow example"],
)
def nested_dynamic_tasks():

    _I_RANGE = list(range(1,4))
    _J_RANGE = list(range(10,40,10))
    _K_RANGE = list(range(100,400,100))

    @task()
    def enter():
       return 'success'
    
    @task_group()
    def nested_for_loop_sums():
       for i in _I_RANGE:
           for j in _J_RANGE:
                 for k in _K_RANGE:
                    @task(task_id=f'task{i}{j}{k}')
                    def mytask(i, j, k):
                        return i+j+k
                    mytask(i=i, j=j, k=k)


    zipped_arguments = list(zip(_I_RANGE, _J_RANGE, _K_RANGE))

    @task
    def zip_sum(zipped_x_y_z):
        return zipped_x_y_z[0] + zipped_x_y_z[1] + zipped_x_y_z[2]

    @task
    def multiply_by_2(num):
        return num * 2
    @task
    def add_10(num):
        return num + 10
    @task
    def multiply_by_100(num):
        return num * 100

    multiply_by_100.expand(
        num=add_10.expand(
            num=multiply_by_2.expand(
                num=[1, 2, 3]
            )
        )
    )

    @task()
    def exit():
       return 'success'
    
    enter() >> nested_for_loop_sums() >> zip_sum.expand(zipped_x_y_z=zipped_arguments) >> exit()

nested_dynamic_tasks()
