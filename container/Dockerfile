FROM python:3.11

RUN pip install numpy matplotlib
RUN pip install jupyter jupyterlab 

RUN apt update && \
    apt install -y openssh-server && \
    apt clean





RUN mkdir /var/run/sshd
RUN echo 'root:password' | chpasswd
COPY sshd_config.txt /etc/ssh/sshd_config
CMD /usr/sbin/sshd -D \
 && jupyter lab --ip=0.0.0.0 --port=8888 --allow-root
