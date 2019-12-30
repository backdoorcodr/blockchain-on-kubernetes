# blockchain-on-kubernetes
Kubernetes can address a number of concerns of Blockchain infrastructure as mentioned in  '[Orchestrating Blockchain on Kubernetes]' article (https://thesendlessloop.wordpress.com/2019/12/30/orchestrating-blockchain-on-kubernetes/). This project orchestrates a simple blockchain on a locally running Kubernetes based on minikube. 

[The article] (https://thesendlessloop.wordpress.com/2019/12/30/orchestrating-blockchain-on-kubernetes/) also refers to some of the monitoring tools that can help us monitor our blockchain resources running on Kubernetes. 

# Requirements
1. [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) 
2. Helm
3. Python [Python 3.6+](https://www.python.org/downloads/)
4. Tiller (to be able to use Helm, tiller needs to be installed on your cluster)

# Deployment steps:
1. Start minikube on your machine:
	* ``` minikube start ```
2. Start helm and install tiller once your cluster is running:
	* ``` helm init ```
3. Start the deployment of blockchain container:
	* ``` helm install blockchain-charts/ ```

4. Check if the pods are running: 
	* ``` kubectl get pods ```

5. Once the pods gets to running state, this is when it start serving the traffic. For that, we need to do port forwarding so the service can get our requests:
	* ``` kubectl port-forward <pod-name-for-example-blockchain-chart> 8080:5000 ```
	
6. Now you can start sending requests to: 
``` http://localhost:8080/ ```

	
	
 
 