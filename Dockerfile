FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3.10-full python3-pip

RUN python3 -m pip install --upgrade pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN chmod +x install_dependencies.sh && ./install_dependencies.sh

RUN cd pointcloudtools-main && chmod +x install.sh && pip install ./ && ./install.sh

CMD ["python3", "main.py"]
