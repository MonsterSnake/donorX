# Use the official Python image as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    libpq-dev

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django project files into the container
COPY . /app/

# Expose the port on which Django runs (change 8000 if your project uses a different port)
EXPOSE 8000

# Run Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
