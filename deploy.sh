#!/bin/bash

echo "deleting old app"
sudo rm -rf /home/ec2-user/production

echo "creating app folder"
sudo mkdir -p /home/ec2-user/production

echo "moving files to app folder"
sudo mv ./server ./map ./dashboard /home/ec2-user/production

# Navigate to the app directory
cd /home/ec2-user/production/server
sudo mv env .env 
sudo cp .env /home/ec2-user/production/map
sudo cp .env /home/ec2-user/production/dashboard

sudo apt-get update
echo "installing python and pip"
sudo apt-get install -y python3 python3-pip

# Install application dependencies from requirements.txt
echo "Install application dependencies from requirements.txt"
sudo pip install -r requirements.txt

# Update and install Nginx if not already installed
# if ! command -v nginx > /dev/null; then
#     echo "Installing Nginx"
#     sudo apt-get update
#     sudo apt-get install -y nginx
# fi 

# # Configure Nginx to act as a reverse proxy if not already configured
# if [ ! -f /etc/nginx/sites-available/myapp ]; then
#     sudo rm -f /etc/nginx/sites-enabled/default
#     sudo bash -c 'cat > /etc/nginx/sites-available/myapp <<EOF
# server {
#     listen 80;
#     server_name _;

#     location / {
#         include proxy_params;
#         proxy_pass http://unix:/var/www/langchain-app/myapp.sock;
#     }
# }
# EOF'

#     sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled
#     sudo systemctl restart nginx
# else
#     echo "Nginx reverse proxy configuration already exists."
# fi

# Stop any existing Gunicorn process
sudo pkill gunicorn
# sudo rm -rf myapp.sock

# # Start Gunicorn with the Flask application
# # Replace 'server:app' with 'yourfile:app' if your Flask instance is named differently.
# # gunicorn --workers 3 --bind 0.0.0.0:8000 server:app &
echo "starting gunicorn"
sudo gunicorn --workers 2 --bind localhost:5000 app:app  server:app --daemon
echo "started gunicorn 🚀"
echo "start streamlit"
cd /home/ec2-user/production/dashboard
sudo streamlit run dashboard.py --server.port 8501