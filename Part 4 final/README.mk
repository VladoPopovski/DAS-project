This folder contains the codes for the microservices, the dockerfiles for all microservises and the docker-compose.

Since the port 5000 for main_service is mapped to 5000,if the Docker containers are running successfully, we should be able to access it via:
http://localhost:5000

Since the port 8050 for visualization_service is mapped to 8050, if the Docker containers are running successfully, we should be able to access it via:
http://localhost:8050

This project also includes Azure integration for deploying services to the cloud. The code is designed to be deployed on Microsoft Azure, allowing seamless scalability and cloud accessibility.


Deployment:
Open to see main_service: https://main-service.gentledune-429612a1.westeurope.azurecontainerapps.io
Open to see visualization_service: https://visualization-service.gentledune-429612a1.westeurope.azurecontainerapps.io

