# Project Overview  
This project demonstrates my software development skills through a **FastAPI web application**.  
The application supports **user registration and authentication**, **project management**, and **file attachment handling**.  

## Tech Stack  
- **FastAPI** – Web framework  
- **SQLAlchemy** & **Pydantic** – ORM & validation  
- **Alembic** – Database migrations  
- **Pytest** – Unit and end-to-end testing  
- **Docker** – Containerization  

## Database Schema  
- **users** – Registered application users  
- **projects** – User-created projects  
- **user_project** – Pivot table for assigning users to projects and managing roles  
- **documents** – Metadata for project-related documents  

## Architecture  
### Routing  
- Implemented with FastAPI routers  
- Handles dependency injection  
- Delegates request processing to service classes  
- Converts service responses into HTTP responses  

### Services  
- Contain business logic  
- Process and validate input  
- Enforce authorization  
- Utilize repositories for data access and modification  

### Repositories  
- Handle database and file system interactions  
- Responsible for data retrieval and persistence  

## Installation  
1. Create a `.env` file based on `.env.example`  
2. Build and start the services:  
   ```bash
   docker-compose up --build
   ```
3. Run database migrations inside the FastAPI container:
   ```bash
   alembic upgrade head
   ```
