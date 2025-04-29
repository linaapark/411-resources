# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the env file to the container
COPY .env /app/.env

# Make port 5002 available to the world outside this container
ENV PORT=5002

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3

# Add a shell script that loads the .env file and handles database creation
COPY ./sql/create_db.sh /app/sql/create_db.sh
COPY ./sql/init_db.sql /app/sql/init_db.sql
RUN chmod +x /app/sql/create_db.sh

# Define a volume for persisting the database
VOLUME ["/app/db"]

EXPOSE $PORT

#  Add this line to ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]


