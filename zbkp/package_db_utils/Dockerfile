FROM public.ecr.aws/sam/build-python3.12
ENTRYPOINT []

# Install general tools
RUN dnf install -y "dnf-command(download)"
RUN dnf install -y tar
RUN dnf group install -y "Development Tools"

# Install unixODBC
WORKDIR /root
RUN dnf download --source unixODBC
RUN rpm -ivh unixODBC*.src.rpm
WORKDIR /root/rpmbuild/SOURCES
RUN mkdir /root/rpmbuild/SOURCES/unixODBC
RUN tar -xvf unixODBC*.tar.gz -C unixODBC --strip-components=1
WORKDIR /root/rpmbuild/SOURCES/unixODBC
RUN ./configure --build=aarch64-unknown-linux-gnu --sysconfdir=/opt/python --disable-gui --disable-drivers --enable-iconv --with-iconv-char-enc=UTF8 --with-iconv-ucode-enc=UTF16LE --prefix=/root/unixODBC-install
RUN make install
RUN mv /root/unixODBC-install/bin /opt/bin
RUN mv /root/unixODBC-install/lib /opt/lib

# Install msodbcsql
RUN curl https://packages.microsoft.com/config/rhel/9/prod.repo | tee /etc/yum.repos.d/mssql-release.repo
RUN ACCEPT_EULA=Y dnf install -y msodbcsql18

# Install pyodbc
RUN dnf -y install unixODBC-devel
RUN export CFLAGS="-I/opt/microsoft/msodbcsql18/include"
RUN export LDFLAGS="-L/opt/microsoft/msodbcsql18/lib"
RUN pip3 install pyodbc --upgrade --target /opt/python

# Create odbc.ini and odbcinst.ini
RUN echo $'[ODBC Driver 18 for SQL Server]\nDriver = ODBC Driver 18 for SQL Server\nDescription = My ODBC Driver 18 for SQL Server\nTrace = No' > /opt/python/odbc.ini
RUN so_file=$(ls /opt/microsoft/**/lib64/libmsodbcsql-*.so.* | grep msodbcsql18) && echo $'[ODBC Driver 18 for SQL Server]\nDescription = Microsoft ODBC Driver 17 for SQL Server\nDriver = '"$so_file"$'\nUsageCount = 1' > /opt/python/odbcinst.ini

# Install Python 3.12, pip, and required build tools
RUN dnf -y install \
    python3.12 \
    python3.12-pip \
    python3.12-devel \
    gcc \
    gcc-c++ \
    zip \
    unixODBC \
    unixODBC-devel \
    libffi-devel \
    openssl-devel

# Upgrade pip and setuptools
RUN python3.12 -m pip install --upgrade pip setuptools wheel

# Create layer directory structure
RUN mkdir -p /opt/python/layer_db_utils/services

# Create __init__.py files
RUN touch /opt/python/layer_db_utils/__init__.py
RUN touch /opt/python/layer_db_utils/services/__init__.py

# Copy requirements file
COPY requirements.txt /opt/requirements.txt

# Install Python packages into the layer folder
RUN python3.12 -m pip install --only-binary=:all: -r /opt/requirements.txt -t /opt/python

# Copy Python code
COPY services/ /opt/python/layer_db_utils/services/
COPY config.py /opt/python/layer_db_utils/

# Package the layer zip
WORKDIR /opt
RUN zip -r9 layer_db_utils.zip python

# docker build -t layer-db-utils .
# docker run -d --name layer-container layer-db-utils
# docker cp layer-container:/opt/layer_db_utils.zip .
# docker stop layer-container
# docker rm layer-container
