# Flyte ML Orchestration Platform Demo

This repository demonstrates the deployment and usage of Flyte, a powerful workflow automation platform designed for machine learning and data processing pipelines. The setup leverages Chameleon Cloud infrastructure and uses Kubernetes for orchestration.

## Overview

Flyte is an open-source workflow automation platform that simplifies the process of building and maintaining scalable and reproducible machine learning workflows. This demo showcases:

- Setting up a Kubernetes cluster on Chameleon Cloud
- Deploying Flyte using Helm charts
- Configuring storage and dependencies
- Running a sample ML workflow

## Prerequisites

-  [Hello, Chameleon](https://teaching-on-testbeds.github.io/blog/hello-chameleon) : **Chameleon Cloud account with an active project**
- SSH keys configured in your Chameleon account
- Basic understanding of Kubernetes and container orchestration
- Familiarity with Python and ML workflows

## Infrastructure Setup

### Chameleon Cloud Resources

The `reserve_chameleon.ipynb` notebook provided in this repository helps you set up the required infrastructure:

1. Creates a single VM node with the following specifications:
   - Flavor: m1.large (4 VCPUs, 8GB RAM, 40GB disk)
   - Image: CC-Ubuntu22.04
   - Network configuration with proper security groups

2. Configures the necessary networking components:
   - Public network for SSH access
   - Private network for internal communication
   - Security groups for required ports (22, 8088, 8089, 9000)

### Kubernetes Cluster Setup

The notebook automatically sets up a Kubernetes cluster using Kubespray with the following components:

1. Base Kubernetes installation
2. Container runtime (Docker)
3. Network plugins
4. Storage configuration using hostpath-provisioner

## File Structure

```
flyte-artifact/
├── config/                   # Configuration files
│   ├── local_secret.yaml
│   └── onprem-flyte-binary-values.yaml
├── scripts/                  # Sample workflows
│   ├── hello_world.py
│   └── house_price_predictor.py
├── reserve_kvm/             # Chameleon setup
│   └── reserve_chameleon.ipynb
└── README.md
```

## Sample Workflows

The repository includes sample workflows in the `scripts` directory:

- `hello_world.py`: Basic workflow demonstration
- `house_price_predictor.py`: ML workflow example

To run a workflow:
```bash
pyflyte run --remote scripts/hello_world.py my_wf
```



## Cleanup

To remove all created resources:

1. Uninstall Flyte:
```bash
helm uninstall flyte-binary -n flyte
```

2. Delete dependencies:
```bash
kubectl delete -f config/local_secret.yaml
kubectl delete -f config/onprem-flyte-dependencies.yaml
kubectl delete namespace flyte
```

## Contributing

Feel free to contribute to this repository by:
- Reporting issues
- Suggesting improvements
- Adding more example workflows
- Enhancing documentation

