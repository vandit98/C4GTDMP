if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <ec2-username> <path-to-your-key-pair.pem> <ec2-public-ip>"
    exit 1
fi

USERNAME=$1
PEM_PATH=$2
EC2_IP=$3
APP_REPO="https://github.com/vandit98/C4GTDMP"  
APP_DIR="C4GTDMP/fastapi" 
PORT=8000

echo "Starting deployment on EC2 instance $EC2_IP..."

ssh -o "StrictHostKeyChecking=no" -i $PEM_PATH $USERNAME@$EC2_IP << EOF
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3-pip nginx ffmpeg python3-dev git -y

    git clone $APP_REPO
    cd $APP_DIR

    pip3 install -r requirements.txt

    nohup uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4 &

    sudo cp -R fastapi_setup /etc/nginx/sites-enabled/
    sudo service nginx restart

    echo "FastAPI application is now running on port $PORT"
EOF

echo "Deployment complete! You can access your app at http://$EC2_IP:$PORT"
