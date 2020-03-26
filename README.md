# Course Catalogue Project

The Course Catalogue Project is a full stack web application that allows users to perform CRUD actions on course items, after signing in through the Google API:

## Tools
Excluding minor modules, the key tools used for this project include the following:
- Virtual Box: https://www.virtualbox.org/wiki/Downloads
- Vagrant: https://www.vagrantup.com/downloads.html 
- Vagrant File by Udacity: https://github.com/udacity/fullstack-nanodegree-vm/blob/master/vagrant/Vagrantfile
- SQLite
- Python3
- Visual Studio Code
- SQLAlchemy
- Git
- Create a project on Google Console to get oAuth credentials: https://console.developers.google.com/
- Make sure your authorised Javascript origins and redirect URIs are set to https://localhost:8000 and https://localhost:8000/oauthcallback respectively. Follow the instructions and download the necessary files.

Finally, Check requirements.txt and install dependencies to avoid any errors. You can automatically download all dependencies using pip3 install --upgrade -r requirements.txt

You might encounter a similar problem to me when installing dependencies due to Vagrant. Try adding --user in fron of your install, e.g pip3 install --upgrade --user -r requirements.txt

## SetUp
The easiest to get started with the right environment is to clone the Udacity full stack vm repo: https://github.com/udacity/fullstack-nanodegree-vm 
- Make sure you have the tools identified above installed (or your favourite alternatives) and set up. Some require a pip3 or sudo -apt install.  
- Make sure you're in the /vagrant directory based on the Udacity repo you cloned earlier. 
- Enter 'vagrant up' into your terminal to get vagrant started up
- Enter 'vagrant ssh' to ssh into your linux instance
- Clone this repository or download the files in it.
- In your terminal, whilst in vagrant, enter 'python3 application.py' to run the app

## SetUp
Navigate the app by going to https://localhost:8000

## Ackowledgement:

I'd like to acknowledge Udacity as most of the processes I followed are based on the lectures. And also the friends and mentors who were always eager to help and support!

I also made use of Bootstrap for the CSS

