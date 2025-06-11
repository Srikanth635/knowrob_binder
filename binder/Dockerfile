FROM intel4coro/base-notebook:20.04-noetic-vnc

# Path to the default ROS workspace
ENV ROS_WS=${HOME}/workspace/ros

USER root
RUN apt update && \
    apt install -y \
        gdb g++ clang cmake make doxygen \
        libeigen3-dev \
        libspdlog-dev \
        libraptor2-dev \
        librdf0 \
        librdf0-dev \
        libmongoc-1.0-0 \
        libmongoc-dev \
        libgtest-dev \
        libfmt-dev \
        software-properties-common \
        git \
        wget \
        curl \
        gnupg \
        sudo \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools

# # Ensure NB_USER has sudo privileges
# RUN usermod -aG sudo ${NB_USER} && \
#     echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install SWI Prolog
RUN apt-add-repository -y ppa:swi-prolog/stable && \
    apt update && \
    apt install -y swi-prolog*
ENV SWI_HOME_DIR=/usr/lib/swi-prolog
ENV LD_LIBRARY_PATH=/usr/lib/swi-prolog/lib/x86_64-linux:$LD_LIBRARY_PATH

# Install MongoDB Community Edition
ARG MONGODEB_VERSION=4.4
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-${MONGODEB_VERSION}.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-${MONGODEB_VERSION}.gpg --dearmor && \
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGODEB_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/${MONGODEB_VERSION} multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-${MONGODEB_VERSION}.list && \
    apt update && apt install -y mongodb-org && \
    mkdir -p /data/db && \
    chown -R ${NB_USER}:users /data/db

# Install MongoDB-Compass
RUN wget -O /tmp/mongodb-compass.deb https://downloads.mongodb.com/compass/mongodb-compass_1.43.0_amd64.deb && \
    dpkg -i /tmp/mongodb-compass.deb && \
    rm /tmp/mongodb-compass.deb


# Install Knowrob as root (recommended)
WORKDIR /home/${NB_USER}
RUN git clone https://github.com/Srikanth635/knowrob_binder.git && \
    cd knowrob_binder && \
    rm -rf build && \
    mkdir -p build && \
    cd build && \
    cmake -DCATKIN=OFF \
          -DPYTHON_MODULE_LIBDIR="dist-packages" \
          -DPython3_EXECUTABLE=/usr/bin/python3 \
          -DPython3_INCLUDE_DIR=/usr/include/python3.8 \
          -DPython3_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.8.so \
          .. && \
    make && \
    make install && \
    chown -R ${NB_USER}:users /home/${NB_USER}/knowrob_binder

# Switch to non-root user for final setup
USER ${NB_USER}

COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

USER root

RUN conda create -n agentic_ai311 python=3.11 -y && \
    echo "source /opt/conda/etc/profile.d/conda.sh" >> /home/${NB_USER}/.bashrc && \
    echo "conda activate agentic_ai311" >> /home/${NB_USER}/.bashrc && \
    chown ${NB_USER}:users /home/${NB_USER}/.bashrc

WORKDIR /home/${NB_USER}

# Add a volatile resource that changes on every build
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /dev/null

# Install LLM Reasoner Framework
RUN rm -rf /home/jovyan/LLM_Reasoner && \
    git clone --branch ownarch --single-branch https://github.com/Srikanth635/LLM_Reasoner.git && \
    chown -R ${NB_USER}:users /home/${NB_USER}/LLM_Reasoner

# Switch to non-root user and install Python packages in the conda environment
USER ${NB_USER}

# Install requirements in the conda environment
RUN cd LLM_Reasoner && \
    /opt/conda/envs/agentic_ai311/bin/pip install -r requirements.txt

WORKDIR /home/${NB_USER}/knowrob_binder

EXPOSE 8081

ENV FLASK_APP=flask_graph.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8081

ENTRYPOINT []
# # Run the startup script
CMD ["bash", "/entrypoint.sh"]
# ENTRYPOINT ["/entrypoint.sh"]