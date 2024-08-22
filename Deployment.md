# FastAPI Application Deployment Guide

This guide will help you deploy the FastAPI application to an AWS EC2 instance.

## Supported Cloud Platform
**Amazon EC2 Instance** - Config - m7g.xlarge (minimum)

## Prerequisites

- An AWS account with access to launch an EC2 instance.
- An SSH key pair to connect to the EC2 instance.
- A FastAPI application ready to deploy.

## 1. Launch an EC2 Instance
Follow the docs here for launching your ec2 Instance on aws
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

## 2. Connect to Your EC2 Instance
1. In your terminal, connect to your EC2 instance using SSH:

    ```bash
    ssh -i <path-to-your-key-pair.pem> ubuntu@<ec2-public-ip>
    ```

2. Once connected, update the package manager and install necessary packages:

    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

## 3. Install Python, Pip, and Git

1. Install Python 3 and Pip:

    ```bash
    sudo apt install python3-pip python3-dev git -y
    ```

2. Clone your FastAPI application from GitHub:

    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd C4GTDMP/fastapi
    ```

3. Install your project's dependencies:

    ```bash
    pip3 install -r requirements.txt
    ```

## 4. Test the FastAPI Application

1. Run your FastAPI application using Uvicorn:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers <based on your machine config>
    ```

2. Visit `http://<ec2-public-ip>:8000` in your browser to see if the application is running.


