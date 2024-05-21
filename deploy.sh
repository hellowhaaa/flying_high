#!/bin/bash

echo "deleting old app"
sudo rm -rf /home/ec2-user/production

echo "creating app folder"
sudo mkdir -p /home/ec2-user/production

echo "moving files to app folder"
sudo mv ./deploy.sh ./.env ./server ./map ./dashboard /home/ec2-user/production

# Navigate to the app directory
cd /home/ec2-user/production
sudo cp .env /home/ec2-user/production/server
sudo cp .env /home/ec2-user/production/map
sudo cp .env /home/ec2-user/production/dashboard
cd /home/ec2-user/production/server


# sudo yum update
# echo "installing python and pip"
# sudo yum install -y python3 python3-pip

# # Install application dependencies from requirements.txt
# echo "Install application dependencies from requirements.txt"
# pip3 install -r requirements.txt

echo "Activating the 'myenv_py310' environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate myenv_py310

# Confirm which Python is being used
echo "Using Python at $(which python3)"


# kill the gunicorn process
sudo pkill gunicorn

echo "starting gunicorn"

# run the gunicorn server in the background
gunicorn --workers 2 --bind localhost:5000 'app:create_app()' --daemon

echo "started gunicorn"

