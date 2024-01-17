FROM python:3.11

RUN apt update && \
    apt install -y openssh-server && \
    mkdir /var/run/sshd

RUN pip install numpy matplotlib
RUN pip install jupyter





RUN echo 'root:password' | chpasswd
COPY sshd_config.txt /etc/ssh/sshd_config
CMD /usr/sbin/sshd -D \
 && jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
