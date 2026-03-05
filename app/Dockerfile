# syntax=docker/dockerfile:1

# Bad practice to use mutable tag
# Alpine 3.21 Python 3.11.11
# docker pull python:3.11.11-alpine3.21
FROM docker.io/library/python@sha256:d5e2fc72296647869f5eeb09e7741088a1841195059de842b05b94cb9d3771bb


USER root

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && apk upgrade && apk add --no-cache \
  bash \
  git \
  openssh \
  curl \
  nginx \
  && rm -rf /var/cache/apk/*

# Remove bash permissions from executables
RUN find / -perm +6000 -type f -exec chmod a-s {} \; || true 

# Download dependencies as a separate step to take advantage of Docker's caching.
# RUN python -m pip install --upgrade pip
# COPY requirements.txt requirements.txt
# RUN python -m pip install -r requirements.txt


# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
# CMD uvicorn 'app:app' --host=0.0.0.0 --port=8000
CMD ["/bin/sh","start-app.sh"]
