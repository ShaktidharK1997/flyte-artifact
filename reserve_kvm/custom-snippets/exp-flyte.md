
::: {.cell .markdown}
### Deploy Flyte on Kubernetes

Now that we have our Kubernetes cluster ready, we'll deploy Flyte using the following steps:
1. Setup storage using hostpath-provisioner
2. Deploy Flyte dependencies (PostgreSQL and MinIO)
3. Create Kubernetes secrets
4. Deploy Flyte using Helm
5. Configure and test the deployment
:::

::: {.cell .code}
```python
#Cloning repo
remote.run("git clone https://github.com/ShaktidharK1997/flyte-artifact.git")
```
:::

::: {.cell .markdown}
### Namespaces
Namespaces in Kubernetes provide a mechanism to organize and isolate a set of resources under a common identifier. 
In our case, we will keep all the created resources for the flyte deployment under a common namespace *flyte*. This will help us keep track of all the infrastructure that we have created for the flyte deployment. 
:::

::: {.cell .code}
```python
remote.run("kubectl get namespace")
remote.run("kubectl create namespace flyte")
remote.run("kubectl get namespace")
```
:::

::: {.cell .markdown}
### Setup Storage Architecture
Storage Classes provide a way to define different types of storage in Kubernetes. We'll use the hostpath-provisioner which:
- Creates a basic storage class for development environments
- Provisions storage from the host machine's filesystem
- Automates PV creation when PVCs request storage

The storage system consists of three main components:
- PersistentVolumeClaims (PVCs): Acts as a request for storage
- PersistentVolumes (PVs): Represents the actual storage resource
- StorageClass: Automates PV creation

PVC Request → StorageClass → PV Creation → Storage Available
:::

::: {.cell .code}
```python
#check for storage class in our K8s setup
remote.run("kubectl get storageclass")
```
:::

::: {.cell .code}
```python
#installing helm
remote.run("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
#installing hostpath provisioner
remote.run("helm repo add rimusz https://charts.rimusz.net")
remote.run("helm repo update")
remote.run("helm upgrade --install hostpath-provisioner --namespace flyte rimusz/hostpath-provisioner")
remote.run("kubectl get storageclass -n flyte")
```
:::

::: {.cell .code}
```python
#running the dependencies yaml in master node 
remote.run("kubectl apply -f flyte-artifact/config/onprem-flyte-dependencies.yaml")
```
:::

::: {.cell .code}
```python
#checking pod and service status ( Object store MinIO and PgSQL database containers must be created)
remote.run("kubectl get pods -n flyte")
```
:::

::: {.cell .markdown}
### Understanding Helm
- Helm is like a package manager for Kubernetes, similar to how pip is for python
- It helps you install and manage applications in your Kubernetes Cluster
- Applications are packaged as"charts" that contains all the Kubernetes manifests and configurations needed

### Helm Repositories 
- It is a catalog of available charts 
- It's a locatio where packaged charts are stored and can be shared 
- Just like how PyPI is a repository for Python packages
:::

::: {.cell .code}
```python
#add flyte through helm repo
remote.run("helm repo add flyteorg https://flyteorg.github.io/flyte")
```
:::


::: {.cell .markdown}
At this point the dependencies required by Flyte are ready. You can now choose which form factor to deploy:

Single binary: all Flyte components (flyteadmin,flytepropeller, flyteconsole, etc) packaged into a single Pod. This is useful for environments with limited resources and a need for quick setup.

Core: all components as standalone Pods, and potentially different number of replicas. This is required for multi-K8s-cluster environments.

Since we are having a single-node setup, we will install a single binary flyte deployment
:::

::: {.cell .markdown}
### Kubernetes Secret
A Kubernetes Secret is an object that helps store and manage sensitive information like passwords, OAuth tokens, or SSH keys.

In our specific case, the secret is needed because:
- It stores the PostgreSQL database password that Flyte needs to connect to its backend database

- Instead of putting the password directly in the Helm values file (onprem-flyte-binary-values.yaml), which would be less secure, we're creating a separate secret

- The name flyte-binary-inline-config-secret is specifically looked for by the Flyte binary chart to inject these configuration values

- The file 202-database-secrets.yaml inside the secret contains the database configuration with the password
:::

::: {.cell .code}
```python
remote.run("kubectl create -f flyte-artifact/config/local_secret.yaml")
remote.run("kubectl describe secret flyte-binary-inline-config-secret -n flyte")
```
:::

::: {.cell .markdown}
### Install Flyte:
:::

::: {.cell .code}
```python
remote.run("helm install flyte-binary flyteorg/flyte-binary  --values flyte-artifact/config/onprem-flyte-binary-values.yaml -n flyte")
remote.run("kubectl get pods -n flyte")
```
:::

::: {.cell .markdown}
### Configuration setup to connect to Flyte

### Flytectl command-line interface (CLI) tool for Flyte.

It allows you to:
1. Manage and interact with Flyte deployments
2. Create and update workflows
3. Monitor executions
4. Manage cluster resources
5. Handle authentication and configuration

`flytectl config init` : Initializes the basic Flytectl configuration and creates a default config file at `$HOME/.flyte/config.yaml`
:::

::: {.cell .code}
```python
# Installing and configuring flytectl

remote.run("curl -sL https://ctl.flyte.org/install | sudo bash -s -- -b /usr/local/bin")
remote.run("flytectl config init")
```
:::

::: {.cell .code}
```python
#copying contents of config.yaml into the flyte config file
remote.run("cp flyte-artifact/config/config.yaml $HOME/.flyte/config.yaml")
```
:::

::: {.cell .code}
```python
#Creating DNS Service for minio yaml 
remote.run("""echo "127.0.0.1 minio.flyte.svc.cluster.local" | sudo tee -a /etc/hosts""")
remote.run("cat /etc/hosts")
```
:::

::: {.cell .code}
```python
remote.run("source myenv/bin/activate; pip install flytekit")
```
:::

::: {.cell .code}
```python
# Start three port forwarding sessions for Http/grpc/minio
remote.run("""
# Start port forwards in the background using &
nohup kubectl -n flyte port-forward --address 0.0.0.0 service/minio 9000:9000 > /tmp/minio.log 2>&1 &
nohup kubectl -n flyte port-forward --address 0.0.0.0 service/flyte-binary-grpc 8089:8089 > /tmp/grpc.log 2>&1 &
nohup kubectl -n flyte port-forward --address 0.0.0.0 service/flyte-binary-http 8088:8088 > /tmp/http.log 2>&1 &

# Store the process IDs so we can terminate them later if needed
echo $! > /tmp/flyte-portforward.pid

# Print the running port forwards
echo "Port forwards running:"
ps aux | grep "port-forward" | grep -v grep

""")
```
:::
::: {.cell .markdown}

### Running a sample "Hello World!" script in Flyte

:::
::: {.cell .code}
```python
remote.run("source myenv/bin/activate; pyflyte run --remote flyte-artifact/scripts/rm hello_world.py my_wf")
```
:::

::: {.cell .markdown}

### Running a house price predictor workflow in Flyte
 Go to the dashboard at {Node-1's public IP}:8088 after running house_predictor workflow to see Flyte Workflow in action!
:::

::: {.cell .code}

```python
remote.run("source myenv/bin/activate; pyflyte run --image sk10945/house-price-predictor:latest scripts/house_price_predictor.py house_price_wf")
```

:::

::: {.cell .markdown}

### Deleting created resources

:::

::: {.cell .code}
```python
remote.run("""
# Kill all port-forward processes
pkill -f "port-forward"
""")
```
:::

::: {.cell .code}
```python
remote.run("helm uninstall flyte-binary -n flyte")
remote.run("kubectl delete -f flyte-artifact/config/local_secret.yaml")
remote.run("kubectl delete -f flyte-artifact/config/onprem-flyte-dependencies.yaml")
remote.run("kubectl delete namespace flyte")
```
:::