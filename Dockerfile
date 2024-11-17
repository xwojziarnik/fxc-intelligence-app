# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary Python packages
RUN pip install --no-cache-dir psycopg2-binary pika

RUN chmod +x main.py

ENTRYPOINT ["python", "-u", "./main.py"]

