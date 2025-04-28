import pandas as pd
import sklearn
from sklearn.datasets import fetch_openml

test = pd.DataFrame()

bike_sharing = fetch_openml("Bike_Sharing_Demand", version=2, as_frame=True)

print("Hello world")