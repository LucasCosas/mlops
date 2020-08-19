# MLOPS 

### Clone Repository & Create Environment Library  
Start cloning this repo in the Azure DevOps Repo blade. 

Create a variables library called "trainmodel" in the Pipelines label with the following:

- RESOURCE_GROUP : "resource group name"
- WORKSPACE_NAME : "AML workspace name"
- SUBSCRIPTION_ID : "Azure subscription ID"
### Data and Storage Account

Create a storage account, take the csv in the link below and upload into a new container

https://storagemlops.blob.core.windows.net/fraud/creditcard.csv?sp=r&st=2020-08-19T12:03:02Z&se=2020-08-26T20:03:02Z&spr=https&sv=2019-12-12&sr=b&sig=i7jHw5ZgYEJVJXxgcVX4dU4iGZFu3732Z%2BsuWW5SvCM%3D

Take note of the Storage Account name, container name and key

### Create Connected Services

> You'll need two different connections. One for the Azure Subscription and the other for the Azure Machine Learning workspace:

Go to project settings on the left corner and look for Service Connections

- Create a new one for Azure Resource Manager specifing a manual Service Principal if you already have one or an autommatic one. Name it "MLOpsServiceConnection"

- Create one more for Azure Resource Manager, manual and check Azure Machine Learning workspace. Name it "AzureMLServiceConnection"

### Create first Pipeline

Head to pipelines blade and create your first build/training pipeline:
Click new pipeline and choose Azure Repos Git and Existing Azure Pipelines YAML File
/pipeline/azure-pipelines.yml
Run the pipeline

### Training and Registering pipeline

The pipeline above did a few things:
Registered a datastore pointing to a BLOB
Registered a dataset
Trained a model
Registered the model in AML and created an Azure DevOps Artifact

### AML Extension

Install the following extension to your organization:
> https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml

### First CD

Change Agent pool to ubuntu

Open the Releases in the Pipelines blade and click create release, chose empty job.

Create an Artifact from AzureML Model Artifact type, chosing the Service Endpoint AzureMLServiceConnection and Model name fraud_model. Click on the lightning icon on top of the artifact and enable CD trigger

Add another artifact for the build, specifying the build pipeline previously ran.

In the pipeline, click in "1 job, 1 task". Right after Agent Job, click on the plus sign

Look for AzureML Model Deploy, specify the AzureML Connection, inference config file and deployment config file, both from the build artifact (Build)/config

Finally, hit create release

This Release will be beased on the deployment config file, this case, an Azure Container Instance. This is not the ideal scenario and we will get into it now.



### Continuos Deployment Pipeline

Import the json in /pipeline/Deploy Webservice.json
Make sure to chose the default agent pools and an approver to deploy the model to production, after testing the ACI.


# Contents:

## Config:
   - Deploymentconfig
   - Inference Config
   - Myenv
   - Score.py

## Model:
>Endpoint:
   - Inference_test.py
>Scripts:
   - Register.py
   - Setup.py
   - train.py

## Pipeline:
   - azure-pipelines.yml
   - Deploy Webservice.json

## Data:
   - creditcard.cvs