FROM python:3.13-slim-bullseye

FROM node:lts-bullseye

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Install Node.js and npm (if not already installed)
RUN apt-get update && apt-get install -y nodejs npm

# Install Prettier globally (so it's available in your PATH)
RUN npm install -g prettier

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

RUN mkdir -p /data

COPY app.py /app/app.py

CMD ["uv", "run", "app.py"]