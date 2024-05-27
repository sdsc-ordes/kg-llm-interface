# Deploying Apps with Kubernetes
This guide provides concise instructions on how to deploy and manage apps in your project using Kubernetes.

## Prerequisites
Make sure you have kubectl installed and configured to interact with your Kubernetes cluster.

Then create a `kg-llm` namespace, this is the default namespace used to deploy apps in this repository.
```sh
kubectl create ns kg-llm
```

## Deploy example config
We provide an example config using a kustomize overlay, located under `overlays/custom-config`.
This config downloads example data from the web and injects it into the graphdb and chroma services using init containers, providing a ready-to-use knowledge graph interface with pre-loaded data.

To deploy it, simply run:

```sh
kubectl apply -k overlays/custom-config
```

> [!TIP]
> The easiest way to get started with custom data is to copy the provided config into a separate folder (e.g. `overlays/my-config`) and edit it.


## Deploy a Single App

kubectl apply -k <app-folder>

For example, to deploy only graphdb in this repository:

```sh
kubectl apply -k ./base/graphdb
```

## Deploying Multiple Apps
To deploy all apps at once, execute the following command from the kubernetes/base folder:

```sh
kubectl apply -k ./base
```

## Removing an App or Apps
To remove an app or multiple apps, execute the following command:

```sh
kubectl delete -k <app-folder>
```
