FROM apache/airflow:2.9.1-python3.11

USER root

# Install OpenJDK-17
RUN apt update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

# ENV PYSPARK_SUBMIT_ARGS --master spark://spark-master_1:7077 pyspark-shell
ENV PYSPARK_SUBMIT_ARGS --master spark://172.18.0.3:7077 pyspark-shell
RUN export PYSPARK_SUBMIT_ARGS

USER airflow

COPY ./dags /opt/airflow/dags
COPY ./logs /opt/airflow/logs
COPY ./plugins /opt/airflow/plugins
COPY ./dataCollection /opt/airflow/dataCollection

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt