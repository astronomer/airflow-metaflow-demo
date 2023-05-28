from metaflow import FlowSpec, step, namespace

namespace('user:astro')
class TrainTripDurationFlow(FlowSpec):

	@step
	def start(self):
		from metaflow import S3
		import pandas as pd

		with S3() as s3:
			data=s3.get('s3://metaflow-test/taxi_data.parquet')
			self.taxi_data = pd.read_parquet(data.path)

		self.X = self.taxi_data.drop(self.taxi_data[['pickup_location_id', 'dropoff_location_id', 'hour_of_day', 'trip_duration_seconds', 'trip_distance']], axis=1)
		self.y = self.taxi_data[['trip_duration_seconds']]
		self.next(self.train_model)

	@step
	def train_model(self):
		from sklearn.model_selection import train_test_split
		from sklearn.linear_model import LinearRegression
		from sklearn.metrics import mean_squared_error

		X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.33, random_state=42)
		
		self.lr = LinearRegression().fit(X_train, y_train)

		self.y_pred = self.lr.predict(self.X).reshape(-1)

		self.mse = mean_squared_error(y_true = y_test, y_pred=self.lr.predict(X_test).reshape(-1))
		self.next(self.end)

	@step
	def end(self):

		self.pred_distribution = {
			'pred_std': self.y_pred.std(),
			'pred_mean': self.y_pred.mean()
		}
		
		self.feature_distributions = {}
		for feature in ['hour_of_day', 'trip_distance']:
			self.feature_distributions.update({
				feature+'_std': self.taxi_data[feature].astype('float').std(),
				feature+'_mean': self.taxi_data[feature].astype('float').mean()
				      })

if __name__ == '__main__':
    TrainTripDurationFlow()