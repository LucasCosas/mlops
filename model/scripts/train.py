from azureml.core import Run
import argparse
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import roc_auc_score, f1_score
import shutil
import os

# Get parameters
parser = argparse.ArgumentParser()
parser.add_argument('--output_folder', type=str, dest='output_folder', default="fraud_model", help='output folder')
parser.add_argument('--data_dir', dest='data_dir')
args = parser.parse_args()
output_folder = args.output_folder
data_dir = args.data_dir #.data_dir 


# Get the experiment run context
run = Run.get_context()

# load the diabetes data (passed as an input dataset)
print("Loading Data...")
fraud = run.input_datasets['fraud_train'].to_pandas_dataframe()



# Cleaning dataset

fraud = fraud.dropna(axis=0,how='any')

# Separate features and labels
X, y = fraud.drop(['Class'],axis=1).values, fraud['Class'].values

# Split data into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

print(fraud.head())


# Train a decision tree model

model = RandomForestClassifier(n_estimators=2,random_state=42)
model.fit(X_train, y_train)

print('Training a decision tree model')

# calculate accuracy
y_hat = model.predict(X_test)
acc = np.average(y_hat == y_test)
print('Accuracy:', acc)
run.log('Accuracy', np.float(acc))

#calculate F1-score
f1score = f1_score(y_test, y_hat)
print('F1-score: ', f1score)
run.log('F1-score', f1score)


# calculate AUC
y_scores = model.predict_proba(X_test)
auc = roc_auc_score(y_test,y_scores[:,1])
print('AUC: ' + str(auc))
run.log('AUC', np.float(auc))

# Save the trained model
os.makedirs(output_folder, exist_ok=True)
output_path = output_folder + "/model.pkl"
joblib.dump(value=model, filename=output_path)


files = ['deploymentconfig.json', 'inferenceconfig.json', 'myenv.yml']



for f in files:
    with open(data_dir + f, 'r') as file:
        fs = file.read()
        joblib.dump(value=fs, filename=output_folder + "/" +f )


run.complete()





