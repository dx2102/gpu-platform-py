# 使用官方 Python 镜像作为基础镜像
FROM python:3.8

# 安装 SSH
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd

# 安装 NumPy 和 Matplotlib
RUN pip install numpy matplotlib

# 安装 Jupyter Notebook
RUN pip install jupyter

# 设置 root 用户的密码（请根据实际情况更改密码）
RUN echo 'root:password' | chpasswd

# 暴露 SSH 和 Jupyter Notebook 的端口
EXPOSE 22
EXPOSE 8888

# 启动 SSH 服务和 Jupyter Notebook
CMD ["/usr/sbin/sshd", "-D"] && jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
