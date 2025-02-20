# This Dockerfile is to build an image that host the python script to avoid installing python on the host machine
# The python scripts purpose is to offer an admin tool for managing the demo system
# See the README.md for more information
# To launch the container, run the following command:
# docker run -it -v "$(pwd)/assets:/app/assets" -v "$(pwd)/templates:/app/templates" milvue-admin-tool


FROM python:3.11.10-slim

RUN echo "alias ll='ls -alh'" >> /root/.bashrc

# Accept a build argument for the version (default to "1.0")
ARG VERSION="1.0"
# Set an environment variable with the version that will be used in the app
ENV APP_VERSION=$VERSION

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

CMD ["python", "main.curses.py"]
