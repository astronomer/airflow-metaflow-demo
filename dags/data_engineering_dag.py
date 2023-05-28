from datetime import datetime
from airflow.decorators import dag, task
from astro import sql as aql 
from astro.files import File
from astro.sql.operators.export_to_file import ExportToFileOperator, export_to_file
from astro.sql.table import Table 
import pandas as pd

_POSTGRES_CONN_ID = 'postgres_default'
_S3_CONN_ID = 'minio_default'

@dag(dag_id='data_engineering_dag', 
     schedule_interval=None, 
	 start_date=datetime(2023, 4, 1))
def data_engineering_dag():

	raw_sources = ['include/data/yellow_tripdata_sample_2019_01.csv', 'include/data/yellow_tripdata_sample_2019_02.csv']
	raw_table = Table(name='taxi_raw', conn_id=_POSTGRES_CONN_ID, metadata={'schema':'public', 'database':'postgres'})
	taxi_data = Table(name='taxi_data', conn_id=_POSTGRES_CONN_ID, metadata={'schema':'public', 'database':'postgres'})
			
	_raw_table = aql.load_file(
		task_id=f'load_{raw_sources[0].split("/")[-1]}',
		input_file=File(path=raw_sources[0]), 
		output_table=raw_table,
		use_native_support=True,
		if_exists='replace'
	)

	_raw_table = aql.load_file(
		task_id=f'load_{raw_sources[1].split("/")[-1]}',
		input_file=File(path=raw_sources[1]), 
		output_table=_raw_table,
		use_native_support=True,
		if_exists='append'
	)
						
	@aql.transform()
	def transform(raw_table:Table) -> Table:
		return """
		select 
			pickup_location_id::text,
			dropoff_location_id::text,
			extract(hour from (pickup_datetime::timestamp))::text as hour_of_day,
			trip_distance,
			extract(epoch from (dropoff_datetime::timestamp - pickup_datetime::timestamp)) as trip_duration_seconds
		from {{raw_table}};
		
		"""
		
	@aql.dataframe(task_id="feature_eng")
	def feature_engineering(taxidf:pd.DataFrame):
		from sklearn.preprocessing import MaxAbsScaler
		import pandas as pd

		cat_cols = pd.get_dummies(taxidf[['pickup_location_id', 'dropoff_location_id', 'hour_of_day']])

		num_cols = pd.DataFrame(
					MaxAbsScaler().fit_transform(taxidf[['trip_distance']]), 
					columns=['trip_distance_scaled']
				)

		taxidf = pd.concat([taxidf, cat_cols, num_cols], axis=1)
		
		return taxidf
	
	_transformed_data = transform(raw_table=_raw_table)
	_feature_table = feature_engineering(taxidf=_transformed_data, output_table=taxi_data) 
	_feature_file = aql.export_file(
		task_id='export', 
		input_data=_feature_table, 
		output_file=File(path='S3://metaflow-test/taxi_data.parquet', conn_id=_S3_CONN_ID), 
		if_exists='replace') >> aql.cleanup()

data_engineering_dag()