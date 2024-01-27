FROM python:3.11

RUN pip install numpy matplotlib jupyter jupyterlab 

RUN apt update && \
    apt install -y openssh-server && \
    apt clean

RUN mkdir /var/run/sshd
COPY sshd_config.txt /etc/ssh/sshd_config


CMD \
    echo "root:"${PASSWORD} | chpasswd && \
    /usr/sbin/sshd -D & \
    curl ipconfig.io && \
    jupyter lab --allow-root --ip=0.0.0.0 --port=8888 & \ 
    echo done && \
    sleep infinity


