# MLOPS 

### Clone Repository & Create Environment Library  

First task is creating a new blank project in Azure DevOps

Start cloning this repo in the Azure DevOps Repo blade.

> Import Repo https://github.com/LucasCosas/mlops

Create a variable library called "trainmodel" in the Pipelines blade with the following:

- RESOURCE_GROUP : "resource group name"
- WORKSPACE_NAME : "AML workspace name"
- SUBSCRIPTION_ID : "Azure subscription ID"

### Data and Storage Account

Create a storage account, download the csv in the link below and upload into a new container

https://storagemlops.blob.core.windows.net/fraud/creditcard.csv?sp=r&st=2020-08-19T12:03:02Z&se=2020-08-26T20:03:02Z&spr=https&sv=2019-12-12&sr=b&sig=i7jHw5ZgYEJVJXxgcVX4dU4iGZFu3732Z%2BsuWW5SvCM%3D

Take note of the Storage Account name, container name and key

In the file setup.py make sure to use the Storage Account name, container and key in lines 32-34

### Create Connected Services

> You'll need two different connections. One for the Azure Subscription and the other for the Azure Machine Learning workspace:

Go to project settings on the left corner and look for Service Connections

- Create a new one for Azure Resource Manager specifing a manual Service Principal if you already have one or an autommatic one. Name it "MLOpsServiceConnection". If manual chosen here, make sure to put the Service Principal as a contributor to the Resource Group where the AML workspace is

- Create one more for Azure Resource Manager, manual/automatic and check Azure Machine Learning workspace. Name it "AzureMLServiceConnection"

### Create first Pipeline

Head to the pipelines blade and create your first build/training pipeline:
Click new pipeline and chose Azure Repos Git and Existing Azure Pipelines YAML File
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

### Continuos Deployment

Import the json from this repo /pipeline/Deploy Webservice.json

Make sure to chose the default agent pools pointing to ubuntu and an approver to deploy the model to production, after testing the ACI.

In the artifacts blade, you'll need two different artifacts:

Create an Artifact from AzureML Model Artifact type, chosing the Service Endpoint AzureMLServiceConnection and Model named fraud_model (or your own model). Click on the lightning icon on top of the artifact and enable CD trigger

Add another artifact for the git repo, specifying the git repo you cloned.

In the Variables blade of the pipeline, change the values as they fit in your scenario. 

Model_name could be different, if we deploy another model and reuse the pipeline.

Resource group is probably different, as well as the AML workspace for both QA and prod.

Working Directory is the artifact name you created for the git repo and the folder for the config files.

Finally, run the CD 

# Contents:

## Config:
   - Deploymentconfig for both ACI and AKS
   - Inference Config for Prod and QA
   - Myenv 
   - Score.py for both Prod and QA

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