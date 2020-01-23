## About

Microservice that handles users and stuff related to users

## Dependencies

    sudo apt-get install build-essential libffi-dev python-dev
	
## How to start the server

Run the server using uvicorn 

	uvicorn server:app --reload

## How to run tests

	pytests tests
