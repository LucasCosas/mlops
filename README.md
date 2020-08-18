# MLOPS 

### Clone Repository & Create Environment Library  
Start cloning this repo in the Azure DevOps Repo blade. 

Create a variables library called "trainmodel" in the Pipelines label with the following:

- RESOURCE_GROUP : "resource group name"
- WORKSPACE_NAME : "AML workspace name"

### Create first Pipeline

Head to pipelines blade and create your first build/training pipeline:
Click new pipeline and choose Azure Repos Git and Existing Azure Pipelines YAML File
/pipeline/azure-pipelines.yml
Run the pipeline

### CD Pipeline

Open the Releases in the Pipelines blade and click create release


# Contents:

## Config:
   - Deploymentconfig
   - Inference Config
   - Myenv
   - Score.py

## Model:
>Data:
   - Register_data.py
>Endpoint:
   - Inference_test.py
>Scripts:
   - Register.py
   - Setup.py
   - train.py

## Pipeline:
   - azure-pipelines.yml