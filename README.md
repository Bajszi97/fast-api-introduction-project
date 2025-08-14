# Project
The goal of this project is to demonstrate my software developing skills. It contains a Fast Api web application that can handle user registration and authentication, 
managing user's projects and attaching files for them.

## Tools used in the project:
- Fast Api framework
- SQLAlchemy & Pydantic for ORM & validation
- Alembic for migrations
- Docker

# Instalation
1. Create a `.env` file based on `.env.example`
2. run `docker-compose up --build`
3. run `alembic upgrade head` inside the fast api container
