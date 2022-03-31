# data challenge

### Necessary to run the project
To run this project is necessary to have docker and docker-compose

Links to install:
* Docker: https://docs.docker.com/install/linux/docker-ce/ubuntu/
* Docker-compose: https://docs.docker.com/compose/install/

### Running the project
The docker will create the DB and up the project

* Command to run: docker-compose up

As all is executed the DB will be created and the project will be running

### How do you recomment to set local enviroment?
```sh
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### How do I test this project?
If your enviroment is set, you can use **pytest -v** alter **docker-compose up**

There are a lot of UTs.

### Executing the endpoints
To execute the endpoints is possible to use the documentation of swagger.
For that with the project running access: http://localhost:5000/apidocs/
