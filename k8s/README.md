# Deploying Apps with Kubernetes
This guide provides concise instructions on how to deploy and manage apps in your project using Kubernetes.

# Prerequisites
Make sure you have kubectl installed and configured to interact with your Kubernetes cluster.

# Deploying a Single App
Navigate to the app's folder on the host machine.
**cd /path/to/repository/kubernetes**

Deploy the app using the following command:
**kubectl apply -k .**

# Deploying Multiple Apps
To deploy all apps at once, execute the following command from the kubernetes/base folder:
**kubectl apply -k .**

# Deploying Apps with Data Retriever Job
To deploy all apps along with the job that downloads sample data, execute the following command from the kubernetes/overlays/data-retriever folder:
**kubectl apply -k .**

# Removing an App or Apps
To remove an app or multiple apps, execute the following command:
**kubectl delete -k .**
Make sure to run this command from the appropriate folder (the app's folder, kubernetes/base, or kubernetes/overlays/data-retriever) depending on which app(s) you want to remove.
