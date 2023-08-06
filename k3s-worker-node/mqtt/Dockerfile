# Use the official Python image as the base image
FROM python:3.7

# Set the working directory inside the container
WORKDIR /script

COPY ./requirements.txt /script/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /script/requirements.txt
# Copy the Python script into the container
COPY . /script

# Run the script when the container starts
CMD ["python3", "api_to_mqtt.py"]
