# Description.
# Made by Ryu Eojin, Institue of Technology, Platform Department.

# Manager Image is used to create and delete related worker pods.
# The base image is used as ubuntu:18.04 image. But if you can make it
# lighter, you can change it.
# You can remove related part of the Dockerfile and add requirements.

# Base ubuntu 18.04 Bionic Beaver image.
FROM ubuntu:18.04

# Python 3.7 is supported by Ubuntu Bionic out of the box
ARG python=3.7
ENV PYTHON_VERSION=${python}

# Set default shell to /bin/bash.
SHELL ["/bin/bash", "-cu"]

# Make requirements tools for the image.
RUN mkdir /examples && apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-distutils

# Base Ubuntu provides both python2.7 and 3.
# Make python interpreter to indicate python3.7 ($ python  => python 3.7, not 2.7).
RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# Install pip command for "pip install" command below.
RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Install python kubernetes module to make enable for the manager
# to create worker pods.
RUN pip install future typing packaging
RUN pip install h5py \
                kubernetes

# Add python & shell scripts used to create & remove worker pods.
ADD DistributeTrain_PostTraining.py /examples/DistributeTrain_PostTraining.py
ADD DistributeTrain_PreTraining.py /examples/DistributeTrain_PreTraining.py
ADD Manager.sh /examples/Manager.sh

# Make base directory as /examples.
WORKDIR "/examples"

# Shell script should get a executable authorization.
RUN chmod +x /examples/Manager.sh


