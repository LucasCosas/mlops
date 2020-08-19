from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core import Environment, Experiment, Workspace, Dataset
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import PipelineData, Pipeline
from azureml.pipeline.steps import PythonScriptStep, EstimatorStep
from azureml.train.estimator import Estimator
from azureml.core.datastore import Datastore
from azureml.data.data_reference import DataReference

import os

cluster_name = "azuremlscluster"
#
# Get Azure machine learning workspace
ws = Workspace.get(
    name=os.environ.get("WORKSPACE_NAME"),
    subscription_id=os.environ.get("SUBSCRIPTION_ID"), 
    resource_group=os.environ.get("RESOURCE_GROUP")
)

# Set default Datastore
ws.set_default_datastore('workspaceblobstore')

# if creditcard is not registered

if 'creditcard' not in ws.datasets:
    
    #Set blobdatastore
    blob_datastore_name='MyBlobDatastore'
    account_name=os.getenv("BLOB_ACCOUNTNAME_62", "") # Storage account name
    container_name=os.getenv("BLOB_CONTAINER_62", "") # Name of Azure blob container
    account_key=os.getenv("BLOB_ACCOUNT_KEY_62", "") # Storage account 
    

    try:
        blob_datastore = Datastore.get(ws, blob_datastore_name)
        print("Found Blob Datastore with name: %s" % blob_datastore_name)
    except HttpOperationError:
        blob_datastore = Datastore.register_azure_blob_container(
        workspace=ws,
        datastore_name=blob_datastore_name,
        account_name=account_name, # Storage account name
        container_name=container_name, # Name of Azure blob container
        account_key=account_key) # Storage account key
        print("Registered blob datastore with name: %s" % blob_datastore_name)

    blob_data_ref = DataReference(
        datastore=blob_datastore,
        data_reference_name="blob_test_data",
        path_on_datastore="testdata")
    csv_path = (blob_datastore, '/creditcard.csv')
    


    try:
        tab_ds = Dataset.Tabular.from_delimited_files(path=csv_path)
        tab_ds = tab_ds.register(workspace=ws, name='creditcard')
    except Exception as ex:
        print(ex)
else:
    print('Dataset already registered.')




creditds = ws.datasets['creditcard']
df = creditds.to_pandas_dataframe() 


default_ds = ws.get_default_datastore()

default_ds.upload_files(files=['./config/deploymentconfigaci.json', './config/inferenceconfig.json', './config/myenv.yml'], # Upload the configs
                        target_path='config/', # Put it in a folder path in the datastore
                        overwrite=True, # Replace existing files of the same name
                        show_progress=True)


experiment_folder = './model/scripts'

# Verify that cluster exists
try:
    pipeline_cluster = ComputeTarget(workspace=ws, name=cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    # If not, create it
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           max_nodes=4,
                                                           idle_seconds_before_scaledown=1800)
    pipeline_cluster = ComputeTarget.create(ws, cluster_name, compute_config)

pipeline_cluster.wait_for_completion(show_output=True)


# Create a Python environment for the experiment
fraud_env = Environment("fraud-pipeline-env")
fraud_env.python.user_managed_dependencies = False # Let Azure ML manage dependencies
fraud_env.docker.enabled = True # Use a docker container

# Create a set of package dependencies
fraud_packages = CondaDependencies.create(conda_packages=['scikit-learn','pandas'],
                                             pip_packages=['azureml-sdk'])

# Add the dependencies to the environment
fraud_env.python.conda_dependencies = fraud_packages

# Register the environment (just in case you want to use it again)
fraud_env.register(workspace=ws)
registered_env = Environment.get(ws, 'fraud-pipeline-env')

# Create a new runconfig object for the pipeline
pipeline_run_config = RunConfiguration()

# Use the compute you created above. 
pipeline_run_config.target = pipeline_cluster

# Assign the environment to the run configuration
pipeline_run_config.environment = registered_env

print ("Run configuration created.")


# Get the training dataset
fraud_ds = ws.datasets.get("creditcard")

# Create a PipelineData (temporary Data Reference) for the model folder
model_folder = PipelineData("model_folder", datastore=ws.get_default_datastore())
#pipeline_data = PipelineData('pipeline_data',  datastore=default_ds)

data_ref = DataReference(datastore=default_ds, data_reference_name = 'data_ref', path_on_datastore="config/")

estimator = Estimator(source_directory=experiment_folder,
                        compute_target = pipeline_cluster,
                        environment_definition=pipeline_run_config.environment,
                        entry_script='train.py')

# Step 1, run the estimator to train the model
train_step = EstimatorStep(name = "Train Model",
                           estimator=estimator,
                           estimator_entry_script_arguments=['--output_folder', model_folder, '--data_dir', data_ref],
                           inputs=[fraud_ds.as_named_input('fraud_train'), data_ref],
                           outputs=[model_folder],
                           compute_target = pipeline_cluster,
                           allow_reuse = True)

# Step 2, run the model registration script
register_step = PythonScriptStep(name = "Register Model",
                                source_directory = experiment_folder,
                                script_name = "register.py",
                                arguments = ['--model_folder', model_folder],
                                inputs=[model_folder],
                                compute_target = pipeline_cluster,
                                runconfig = pipeline_run_config,
                                allow_reuse = True)

print("Pipeline steps defined")

# Construct the pipeline
pipeline_steps = [train_step, register_step]
pipeline = Pipeline(workspace = ws, steps=pipeline_steps)
print("Pipeline is built.")

# Create an experiment and run the pipeline
experiment = Experiment(workspace = ws, name = 'fraud-training-pipeline')
pipeline_run = experiment.submit(pipeline, regenerate_outputs=True)
print("Pipeline submitted for execution.")

# RunDetails(pipeline_run).show()
pipeline_run.wait_for_completion()

published_pipeline = pipeline.publish(name="fraud_Training_Pipeline",
                                      description="Trains fraud model",
                                      version="1.0")
rest_endpoint = published_pipeline.endpoint
print(rest_endpoint)