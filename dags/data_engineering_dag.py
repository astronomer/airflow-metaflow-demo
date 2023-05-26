from datetime import datetime
from airflow.decorators import dag, task, task_group
from astro import sql as aql 
from astro.sql.operators.load_file import LoadFileOperator as LoadFile
from astro.files import File, get_file_list
from astro.sql.table import Table 
import pandas as pd

_POSTGRES_CONN_ID = 'postgres_default'

@dag(dag_id='data_engineering_dag', 
     schedule_interval=None, 
	 start_date=datetime(2023, 4, 1))
def data_engineering_dag():

	# ingest_files=[File('include/data/yellow_tripdata_sample_2019_01.csv'), File('include/data/yellow_tripdata_sample_2019_02.csv')]
	raw_table = Table(name='TAXI_RAW', conn_id=_POSTGRES_CONN_ID, metadata={'schema':'public', 'database':'postgres'})

	raw_data = LoadFile.partial(task_id="load_data", 
		  						output_table=raw_table,
		  						use_native_support=True,
								if_exists='append')\
						.expand(input_file=get_file_list(path='include/data/yellow*', conn_id=_POSTGRES_CONN_ID))
	
	# @task_group()
	# def load():
	# 	for file in ingest_files:
	# 		aql.load_file(task_id=f'load_data{file.name}',
	# 			input_file = file, 
	# 			output_table = raw_table,
	# 			if_exists='append'
	# 		)
		
	@aql.transform()
	def transform(raw_table:Table) -> Table:
		return """
		select 
			pickup_location_id::text,
			dropoff_location_id::text,
			extract(hour from (pickup_datetime::timestamp)) as hour,
			trip_distance,
			extract(epoch from (dropoff_datetime::timestamp - pickup_datetime::timestamp)) as trip_duration_seconds
		from {{raw_table}};
		
		"""

		# raw_table.with_column('TRIP_DURATION_SEC',
		#   					F.datediff('seconds', F.col('PICKUP_DATETIME'), F.col('DROPOFF_DATETIME')))\
		# 			.with_column('HOUR', F.date_part('hour', F.col('PICKUP_DATETIME').cast(T.TimestampType())))\
		# 			.select(\
		# 				F.col('PICKUP_LOCATION_ID').cast(T.StringType()).alias('PICKUP_LOCATION_ID'), \
		# 				F.col('DROPOFF_LOCATION_ID').cast(T.StringType()).alias('DROPOFF_LOCATION_ID'), \
		# 				F.col('HOUR'), \
		# 				F.col('TRIP_DISTANCE'), \
		# 				F.col('TRIP_DURATION_SEC'))\
		# 				.write.mode('overwrite').save_as_table(transformed_table.name)
		# transformed_table = Table(name='TAXI_DATA') 
		
	@aql.dataframe(task_id="feature_eng")
	def feature_engineering(taxidf:pd.DataFrame) -> Table:
		from sklearn.preprocessing import MaxAbsScaler
		import pandas as pd

		# taxidf = taxidf.with_column('HOUR_OF_DAY', F.col('HOUR').cast(T.StringType())).to_pandas()

		# cat_cols = pd.get_dummies(taxidf[['PICKUP_LOCATION_ID', 'DROPOFF_LOCATION_ID', 'HOUR_OF_DAY']])

		# num_cols = pd.DataFrame(
		# 			MaxAbsScaler().fit_transform(taxidf[['TRIP_DISTANCE']]), 
		# 			columns=['TRIP_DISTANCE_SCALED']
		# 		)

		# taxidf = pd.concat([taxidf, cat_cols, num_cols], axis=1)

		# snowpark_session.write_pandas(
		# 	df=taxidf, 
		# 	table_name=feature_table.name,
		# 	auto_create_table=True,
		# 	overwrite=True
		# )
		
		return Table(name='TAXI_FEATURE')
	
	# load() >> 
	raw_data >> feature_engineering(taxidf=transform(raw_table=raw_table))

data_engineering_dag()