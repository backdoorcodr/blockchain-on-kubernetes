# blockchain-on-kubernetes
Kubernetes can address a number of concerns of Blockchain infrastructure. This project executes Kubernetes for Blockchain. 

# Aim
When deploying blockchain on classical machines, several concerns arise such as :
1. Availability: Should always be available
2. Resiliency: Should be able to recover from a failure induced by load, attacks and failures. 
3. Elasticity: It should be able to spin up new blockchain network
4. Isolation: Should be able to isolate multiple blockchain infrastructures 
5. Logging, Debugging, Tracing: Should have the ability to trace the performance of blockchain components running within the infrastructure. If something goes wrong, developers should be able to debug.
6. Health checking and alerting: Should be able to generate alerts and perform health checks. 
7. Management: Should be able to provide overview of the underlying infrastructure with different stats and status of components running. 

Hence, in order to address these points; I am setting up a basic blockchain on kubernetes running on minikube. This basic blockchain has already implemented [here](https://github.com/backdoorcodr/blockchain/blob/master/py-blockchain-api/blockchain.py) 

Obviously, if you get access to EKS/AKS; please feel free to make changes accordingly. 

# Requirements
1. [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) 
2. Helm
3. Python [Python 3.6+](https://www.python.org/downloads/)
4. Tiller (to be able to use Helm, tiller needs to be installed on your cluster)

# Steps to execute:
1. Start minikube on your machine:
	* ``` minikube start ```
2. Start helm and install tiller once your cluster is running:
	* ``` helm init ```
3. Start the deployment of blockchain container:
	* ``` helm install blockchain-charts/ ```

4. Check if the pods are running: 
	* ``` kubectl get pods ```

5. Once the pods gets to running state, this is when it start serving the traffic. For that, we need to do port forwarding so the service can get our requests:
	* ``` kubectl port-forward kubectl port-forward <pod-name-for-example-blockchain-chart> 8080:5000 ```
	
6. Now you can start sending requests to: 
``` http://localhost:8080/ ```
