[![cheuklau](https://circleci.com/gh/cheuklau/trading-post.svg?style=svg)](https://circleci.com/gh/cheuklau/trading-post)

# Trading Post

Trading post is a simple platform to help people in the same location find each other and make trades.

## Dependencies

The project can be run locally using [Vagrant](https://www.vagrantup.com/downloads) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads). The `VagrantFile` contains all of the dependencies.

## To test locally

Follow the following steps to test locally:

- Start Vagrant: `vagrant up`
- SSH into the Vagrant virtual machine: `vagrant ssh`
- Change to the Vagrant directory: `cd ../../vagrant`
- Create the database: `python database_setup.py`
- Populate the database: `python populate_db.py`
- Run the platform: `python project.py`
- Visit `http://0.0.0.0.xip.io:5000/` from your browser

Note that [xip](xip.io) is a domain name that provides wildcard DNS for any IP. This allows testing on the local network.
