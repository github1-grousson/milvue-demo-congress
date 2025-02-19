# This Dockerfile is to build an image that host the python script to avoid installing python on the host machine
# The python scripts purpose is to offer an admin tool for managing the demo system
# See the README.md for more information
# To launch the container, run the following command:
# docker run -it -v "$(pwd)/assets:/app/assets" -v "$(pwd)/templates:/app/templates" milvue-admin-tool


FROM python:3.11.10-slim

RUN echo "alias ll='ls -alh'" >> /root/.bashrc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

CMD ["python", "main.py"]