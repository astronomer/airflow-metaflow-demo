def predict(featuredf:SnowparkTable, run_id:str) -> Table:
		import mlflow 
		
		pred_table = SnowparkTable(name='TAXI_PRED')

		run = mlflow.get_run(run_id=run_id)

		lr = mlflow.sklearn.load_model('runs:/'+run_id+'/model')
		
		df = featuredf.to_pandas()
		X = df.drop(df[['PICKUP_LOCATION_ID', 'DROPOFF_LOCATION_ID', 'HOUR_OF_DAY', 'HOUR', 'TRIP_DURATION_SEC', 'TRIP_DISTANCE']], axis=1)
				
		#look for drift 
		drifts={}
		for feature in ['HOUR', 'TRIP_DURATION_SEC', 'TRIP_DISTANCE']:
			drifts[feature] = df[feature].std() - run.data.metrics[feature+'_std']

		df['PREDICTED_DURATION'] = lr.predict(X).astype(int)

		write_columns = ['PICKUP_LOCATION_ID', 'DROPOFF_LOCATION_ID', 'HOUR_OF_DAY', 'PREDICTED_DURATION', 'TRIP_DURATION_SEC']

		snowpark_session.write_pandas(
			df[write_columns], 
			table_name=pred_table.name,
			auto_create_table=True,
			overwrite=True
		)

		return pred_table