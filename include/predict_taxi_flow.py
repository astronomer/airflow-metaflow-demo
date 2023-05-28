from metaflow import FlowSpec, step, namespace

namespace('user:astro')
class PredictTripDurationFlow(FlowSpec):

	@step
	def start(self):
		from metaflow import Flow, S3
		import pandas as pd

		with S3() as s3:
			data=s3.get('s3://metaflow-data/taxi_data.parquet')
			self.taxi_data = pd.read_parquet(data.path)

		self.X = self.taxi_data.drop(self.taxi_data[['pickup_location_id', 'dropoff_location_id', 'hour_of_day', 'trip_duration_seconds', 'trip_distance']], axis=1)
		
		flow = Flow('TrainTripDurationFlow')
		self.train_run = flow.latest_successful_run

		self.next(self.predict)

	@step
	def predict(self):
		from sklearn.linear_model import LinearRegression
		
		self.y_pred = self.train_run['train_model'].task.data.lr.predict(self.X).reshape(-1)

		self.next(self.eval)

	@step
	def eval(self):

		train_distribution = self.train_run['end'].task.data._artifacts['pred_distribution'].data

		feature_distributions = self.train_run['end'].task.data._artifacts['feature_distributions'].data
		
		self.concept_drift = {
			'std': self.y_pred.std() - train_distribution['pred_std'],
			'mean': self.y_pred.mean() - train_distribution['pred_mean']
		}
		
		self.data_drifts={}
		for feature in ['hour_of_day', 'trip_distance']:
			self.data_drifts[feature] = self.taxi_data[feature].astype('float').std() - feature_distributions[feature+'_std']
		
		self.next(self.end)

	@step
	def end(self):
		import pandas as pd
		from metaflow import S3
		import tempfile

		with tempfile.TemporaryFile() as tf, S3() as s3:
			pd.concat([self.taxi_data[['pickup_location_id', 
			 					  	   'dropoff_location_id', 
									   'hour_of_day',  
									   'trip_distance']], 
						pd.DataFrame(self.y_pred, columns=['trip_duration_pred'])],
						axis=1)\
			  .to_parquet(tf)
			s3.put('s3://metaflow-data/taxi_pred.parquet', tf, overwrite=True)

if __name__ == '__main__':
    PredictTripDurationFlow()