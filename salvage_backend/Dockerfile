# Dockerfile (for Django)
FROM python:3.11.2-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including git
RUN apk update && \
    apk add --no-cache build-base gcc musl-dev git

# Copy the requirements file into the container
COPY ./requirements.txt /usr/src/app/requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container
COPY . /usr/src/app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
