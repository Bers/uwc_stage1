sudo apt-get update
sudo apt-get install -y python-dev python-setuptools python-virtualenv git
sudo apt-get install -y redis-server
sudo apt-get install -y python-software-properties python g++ make

# uwsgi
sudo apt-get install -y libpcre3 libpcre3-dev

# lxml
sudo apt-get install -y libxslt1.1 libxslt1-dev python-libxml2 python-libxslt1 libxml2-dev libxslt-dev python-dev lib32z1-dev

# deploy
sudo apt-get install -y nginx supervisor

sudo locale-gen UTF-8

# default 500mb memory not enough for lxml compiling
sudo dd if=/dev/zero of=/swapfile bs=1024 count=524288
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# virtualenv
cd /vagrant/
./build/buildenv.sh

# deploy
sudo cp /vagrant/build/nginx_uwc1.conf /etc/nginx/sites-enabled
sudo /etc/init.d/nginx reload

sudo cp /vagrant/build/sprvsr_uwc1.conf /etc/supervisor/conf.d
sudo supervisorctl update
