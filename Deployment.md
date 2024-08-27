# FastAPI Application Deployment Guide

This guide will help you deploy the FastAPI application to an AWS EC2 instance using an automated deployment script.

## Supported Cloud Platform
**Amazon EC2 Instance** - Config - m7g.xlarge (minimum)

## Prerequisites

- An AWS account with access to launch an EC2 instance.
- An SSH key pair (`.pem` file) to connect to the EC2 instance.
- A FastAPI application repository on GitHub (this repository).
- Ensure that you have configured the security group for your EC2 instance to allow inbound access on port `8000`.

## Steps to Deploy the FastAPI Application

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/vandit98/C4GTDMP
cd C4GTDMP
```

### 2. Make the deploy.sh Script Executable
```bash
chmod +x deploy.sh
```

### 3. Run the Deployment Script
<ec2-username>: The username for your EC2 instance (e.g., ubuntu for Ubuntu instances).
<path-to-your-key-pair.pem>: The path to your SSH key pair file (.pem file).
<ec2-public-ip>: The public IP address of your EC2 instance.

```bash
# example
./deploy.sh ubuntu ~/my-key.pem 54.123.45.67
```

### 5. Access Your Application

```bash
http://<ec2-public-ip>:8000
```