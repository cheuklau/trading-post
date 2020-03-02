# Catalog App

Author: Cheuk Lau

Date: 6/10/2018

In this project, we are creating a catalog app which stores items belonging to different pre-defined categories. Users are allowed to create, read, update and delete (CRUD) items from different pre-defined categories. Note that users are only allowed to modify items that they have created. This project uses Python Flask with an SQL backend.

## Dependencies

The project was tested using VirtualBox running a Vagrant virtual machine (VM). The VM will run a web server and the catalog app that uses it. Please download and install VirtualBox and Vagrant using the following links:

- `https://www.virtualbox.org/wiki/Downloads`
- `https://www.vagrantup.com/downloads`

The provided `VagrantFile` contains all of the dependencies needed to run the catalog app.

## Running the Catalog App

Follow the following steps to run the catalog app:

- Change to the `Catalog_App` directory: `cd Catalog_App`
- Start the Vagrant VM: `vagrant up`
- SSH into the Vagrant VM: `vagrant ssh`
- Change to the Vagrant directory shared between the VM and your machine: `cd ../../vagrant`
- Create the database: `python database_setup.py`
- (Optional) populate the database: `python populate_db.py`
- Run the catalog app: `python project.py`
- Visit `http://0.0.0.0.xip.io:5000/` from your browser to view the catalog app

Note that xip is a domain name that provides wildcard DNS for any IP address. This allows testing of apps on other devices on the local network. Visit `xip.io` for more details.
