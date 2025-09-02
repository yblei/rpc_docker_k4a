# Ubuntu 20.04 is the path of least resistance with official packages
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Optional: force software OpenGL if you ever run k4aviewer inside the container
ENV LIBGL_ALWAYS_SOFTWARE=1

RUN apt-get update && apt-get install -y \
    curl gnupg2 ca-certificates apt-transport-https software-properties-common \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && add-apt-repository 'deb [arch=amd64] https://packages.microsoft.com/ubuntu/20.04/prod focal main' \
    && apt-get update && apt-get install -y \
       libk4a1.4 libk4a1.4-dev k4a-tools \
    && rm -rf /var/lib/apt/lists/*

# Your app here (example copies a simple capture script)
WORKDIR /app
COPY . /app

# Default command shows devices
CMD ["bash", "-lc", "k4aviewer --help || true; k4arecorder --list || true"]

