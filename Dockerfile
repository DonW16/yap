# Use an official Python runtime as the base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the command to run when the container starts
CMD ["python3", "app.py"]