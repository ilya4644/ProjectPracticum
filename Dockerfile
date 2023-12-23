FROM ubuntu:jammy

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./project /usr/src/app

COPY ./tmp* /tmp/

RUN chmod +x install_dependencies.sh && ./install_dependencies.sh

RUN cd pointcloudtools-main && chmod +x && pip3 install ./ && ./install.sh

#CMD ["python3", "main.py"]