##########
# dev
##########
FROM debian:stable-slim as dev

# Install Java and python
RUN apt-get update \
    && apt-get install -y openjdk-17-jdk python3 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment var
ENV JAVA_HOME="/usr/lib/jvm/jre-openjdk"

# jdepend
COPY jdepend-2.10.jar /app/jdepend-2.10.jar

# python requirements
COPY requirements.txt /app/jdepend_enhanced/requirements.txt
RUN pip3 install --break-system-packages -r /app/jdepend_enhanced/requirements.txt

# python package
COPY jdepend_enhanced /app/jdepend_enhanced/jdepend_enhanced
COPY setup.py /app/jdepend_enhanced/setup.py
WORKDIR /app/jdepend_enhanced
RUN pip3 install --break-system-packages -e .

CMD ["bash"]

##########
# build
##########
FROM python:3.11.7-slim as build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY setup.py .
COPY jdepend_enhanced ./jdepend_enhanced
RUN python setup.py sdist bdist_wheel

##########
# prod
##########
FROM debian:stable-slim as prod

# Install Java and python
RUN apt-get update \
    && apt-get install -y openjdk-17-jdk python3 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment var
ENV JAVA_HOME="/usr/lib/jvm/jre-openjdk"

# jdepend
COPY jdepend-2.10.jar /app/jdepend-2.10.jar

# jdepend_enhanced
COPY --from=build /app/dist/*.whl /app/
RUN pip install --break-system-packages --no-cache-dir /app/*.whl && \
    rm -rf /app/*.whl

ENTRYPOINT ["jdepend-enhanced"]