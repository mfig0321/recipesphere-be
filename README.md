# Demo
Demo Backend using Django REST

## Getting Started

- Install Docker
1. https://docs.docker.com/engine/install/
2. Run command `docker-compose up` or `sudo docker-compose up` if on linux.

## Making requests via api docs.
1. go to browser address http:localhost:8000/api/docs/
2. go to /api/createuser/ and fill out json request body
- authenticate api
1. click on /api/token/ tab and enter password and login from user createuser
2. copy response token 
3. click on Authorize button on top right corner of page.
4. scroll down to thrid option of tokenAuth and type `Token [token_from_response]`
5. click Authorize.