## Requirement 1
This folder contains the refactored code, using the singleton design pattern. 

## Requirement 2 and 3
Here are also the codes for the microservices, the dockerfiles for all microservises and the docker-compose. 

Since the port 5000 for main_service is mapped to 5000, if the Docker containers are running successfully, we should be able to access it via:
http://localhost:5000

Since the port 8050 for visualization_service is mapped to 8050, if the Docker containers are running successfully, we should be able to access it via:
http://localhost:8050


This project also includes Azure integration for deploying services to the cloud. The code is designed to be deployed on Microsoft Azure, allowing seamless scalability and cloud accessibility.

Deployment (it takes a while):
Open to see main_service: https://main-service.gentledune-429612a1.westeurope.azurecontainerapps.io
Open to see visualization_service: https://visualization-service.gentledune-429612a1.westeurope.azurecontainerapps.io


### Video link demonstrating docker operation

https://drive.google.com/file/d/1EK6f3k8sJ23TzzSlIKe35GzFmL5jWj1l/view?usp=sharing

##Summary
All requirements were satisfied from homework 4 short of initiating connection between the microservice for visualization and the database.
The refactored code complies with software design patterns, ensuring clarity, consistency, meaningful naming, and proper documentation for improved readability and understanding. It is modular, reusable, efficient, making it easy to maintain and extend.

The application has been refactored by transforming specific functions into independent microservices that communicate via APIs. Each microservice is implemented as a standalone project, ensuring they operate independently while seamlessly interacting with the main application through API communication, short of the visualization-database connection.

The application has been prepared for deployment by containerizing it using Docker, ensuring it includes all dependencies for consistency across environments. The containerized application is deployed to the cloud using Azure.
