	def train(featuredf:SnowparkTable, experiment_id:str) -> str:
		from sklearn.linear_model import LinearRegression
		from sklearn.model_selection import train_test_split
		from sklearn.metrics import mean_squared_error
		import mlflow

		mlflow.sklearn.autolog(exclusive=False)

		with mlflow.start_run(experiment_id=experiment_id, run_name='trip_duration_estimator') as run:
			run_id=run.info.run_id

			df = featuredf.to_pandas()
			X = df.drop(df[['PICKUP_LOCATION_ID', 'DROPOFF_LOCATION_ID', 'HOUR_OF_DAY', 'HOUR', 'TRIP_DURATION_SEC', 'TRIP_DISTANCE']], axis=1)
			y = df[['TRIP_DURATION_SEC']]

			X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
			
			lr = LinearRegression().fit(X_train, y_train)

			test_pred = lr.predict(X_test).reshape(-1)

			feature_distributions = {}
			for feature in ['HOUR', 'TRIP_DURATION_SEC', 'TRIP_DISTANCE']:
				feature_distributions.update({feature+'_std': df[feature].std()})

			mlflow.log_metrics(feature_distributions)

			return run_id