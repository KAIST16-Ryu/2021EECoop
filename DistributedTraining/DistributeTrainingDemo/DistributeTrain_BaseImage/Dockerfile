# Description.
# Made by Ryu Eojin, Institue of Technology, Platform Department.

# If you don't want "Horovod", and other Distribute Training frameworks,
# You can remove related part of the Dockerfile and add requirements.


# Base Image - nvidia/cuda + ubuntu image. => nvidia/cuda is needed for gpu usage.
FROM nvidia/cuda:10.1-devel-ubuntu18.04

# TensorFlow, Pytorch version is tightly coupled to CUDA and cuDNN so it's version should be selected carefully.
ENV TENSORFLOW_VERSION=2.3.0
ENV PYTORCH_VERSION=1.6.0
ENV TORCHVISION_VERSION=0.7.0
ENV CUDNN_VERSION=7.6.5.32-1+cuda10.1

# NCCL is an NVIDA library used to transfer various parameter in distribute training.
# It may used for other distribute training framework which is not "Horovod".
ENV NCCL_VERSION=2.7.8-1+cuda10.1

# Python 3.7 is supported by Ubuntu Bionic out of the box
ARG python=3.7
ENV PYTHON_VERSION=${python}

# Set default shell to /bin/bash
SHELL ["/bin/bash", "-cu"]

# Make requirements tools for the image.
RUN mkdir /examples && apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
        build-essential \
        cmake \
        g++-7 \
        git \
        curl \
        vim \
        wget \
        ca-certificates \
        libcudnn7=${CUDNN_VERSION} \
        libnccl2=${NCCL_VERSION} \
        libnccl-dev=${NCCL_VERSION} \
#        libjpeg-dev \  # This one can be used after. Please leave it for future usage.
#        libpng-dev \   # This one can be used after. Please leave it for future usage.
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-distutils
#        librdmacm1 \   # This one can be used after. Please leave it for future usage.
#        libibverbs1 \  # This one can be used after. Please leave it for future usage.
#        ibverbs-providers  # This one can be used after. Please leave it for future usage.

# Base Ubuntu provides both python2.7 and 3.
# Make python interpreter to indicate python3.7 ($ python  => python 3.7, not 2.7).
RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# Install pip command for "pip install" command below.
RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Some Needed python module. Don't understand exactly.
RUN pip install future typing packaging

# Install Tensorflow, Keras.
RUN pip install tensorflow==${TENSORFLOW_VERSION} \
                keras \
                h5py

# Install Pytorch.
RUN PYTAGS=$(python -c "from packaging import tags; tag = list(tags.sys_tags())[0]; print(f'{tag.interpreter}-{tag.abi}')") && \
    pip install https://download.pytorch.org/whl/cu101/torch-${PYTORCH_VERSION}%2Bcu101-${PYTAGS}-linux_x86_64.whl \
        https://download.pytorch.org/whl/cu101/torchvision-${TORCHVISION_VERSION}%2Bcu101-${PYTAGS}-linux_x86_64.whl

# Install Open MPI. It is necessary for "Horovod".
RUN mkdir /tmp/openmpi && \
    cd /tmp/openmpi && \
    wget https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-4.0.0.tar.gz && \
    tar zxf openmpi-4.0.0.tar.gz && \
    cd openmpi-4.0.0 && \
    ./configure --enable-orterun-prefix-by-default && \
    make -j $(nproc) all && \
    make install && \
    ldconfig && \
    rm -rf /tmp/openmpi

# Install Horovod.
RUN ldconfig /usr/local/cuda/targets/x86_64-linux/lib/stubs && \
    HOROVOD_GPU_OPERATIONS=NCCL HOROVOD_WITH_TENSORFLOW=1 HOROVOD_WITH_PYTORCH=1 \
    pip install --no-cache-dir horovod[tensorflow,pytorch] && \
    ldconfig

# Install OpenSSH for Open MPI to communicate between containers.
RUN apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd

# Change OpenSSH configuration for each containers to communicate each other without asking for confirmation or password.
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config

# Add Additional public (=authorized_keys) & private(=.pem file) keys to the container.
# You can make your own "Public & Private Key pairs" for protection.
ADD authorized_keys /root/.ssh/authorized_keys
ADD lifelog-lab-t3q.pem /root/.ssh/lifelog-lab-t3q.pem

# Train.py
# !!!It must be changed as a way to use persistent volume and mount it. !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ADD Train.py /examples/Train.py
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Make base directory as /examples.
WORKDIR "/examples"

# Restart ssh server of the container for updating changes.
RUN service ssh restart
