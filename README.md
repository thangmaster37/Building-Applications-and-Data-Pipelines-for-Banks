# Building-Applications-and-Data-Pipelines-for-Banks

## 🚀 1.INTRODUCTION
In this project, I built a website that serves some basic banking functions. My purpose of building this website is mainly to serve the purpose of collecting data to build a data pipeline. In this website, I have integrated some Machine Learning models to serve two problems: Credit Scoring and Fraudulent Transaction Prediction. Building a data pipeline helps me collect data from many sources and store it in a data warehouse to serve data analysis.

## 🧐 2.ABOUT DATA 
The HMEQ dataset reports characteristics and default information for 5,960 home equity loans. A home equity loan is a loan in which the borrower uses the equity value of the home as
collateral. The dataset has the following characteristics:

- **BAD**: 1 = the applicant is in default or seriously delinquent; 0 = the applicant has paid the loan
- **LOAN**: Amount of loan requested
- **MORTDUE**: Amount of outstanding debt on the current mortgage
- **VALUE**: Current value of the property.
- **REASON**: Reason for the loan DebtCon = debt consolidation; HomeImp = home improvement.
- **JOB**: job type, including the groups “Office”, “Sales”, “Mananger”, “Professional Executive”, “Self business” and other jobs.
- **YOJ**: Number of years at current job
- **DEROG**: Number of reported defaults.
- **DELINQ**: Number of delinquent credit lines
- **CLAGE**: Age of oldest credit line in months
- **NINQ**: Number of recent credit requests
- **CLNO**: Number of credit lines
- **DEBTINC**: Debt-to-income ratio

## 🛠️ 3.BUILD DOCKER AND CONNECTION

In the airflow-pipeline directory run: <strong>docker-compose up -d --build</strong>
![UI](docker.png)

To connect Apache Airlfow with Apache Spark, in the Airflow transaction select Admin, then select Connections and create a connection as shown below.
![UI](conn_airflow_spark.png)

## 🔥 4.HOW TO RUN

To process data from the website, just activate it on the Apache Airflow interface.

To process data from logs collected from monitoring APIs, you need to install ELK Stack and run as follows:

- Move to elasticsearch directory and run: <strong>bin\elasticsearch.bat</strong>
- Move to kibana directory and run: <strong>bin\kibana.bat</strong>
- Move to logstash directory and run: <strong>bin/logstash -f /path/to/your/logstash.conf</strong>

To use kafka for real time fraud transaction alert run as follows:

- .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties  <!-- Start the Zookeeper server -->

- .\bin\windows\kafka-server-start.bat .\config\server.properties <!-- Start the Kafka server -->

- .\bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --replication-factor 1 --partition 1 --topic “test” 

- .\bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --replication-factor 1 --partition 1 --topic “test”

- .\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic “test”

- .\bin\windows\kafka-console-consumer.bat --topic “test” --bootstrap-server localhost:9092 --from-beginning

- streamlit run consumer.py

- python consumer.py

- python producer.py

## ✅ 5.Workflow

![UI](data_pipeline.png)

## 📝 6.RESULT

Model for Credit Scoring Problem

![UI](svc_max.png)

Data Pipeline

![UI](dag.png)

Run Dag

![UI](run_dag.png)









## 🛠️ 3.INSTALLATION LIBRARIES

|ID  |     Command Prompt            |     Jupyter Notebook                        |
|----|-------------------------------|---------------------------------------------|
|1   |pip install numpy              |conda install numpy                          |
|2   |pip install pandas             |conda install pandas                         |
|3   |pip install matplotlib         |conda install -c conda-forge matplotlib      |
|4   |pip install seaborn            |conda install -c anaconda seaborn            |
|5   |pip install plotly             |conda install -c plotly plotly               |
|6   |pip install -U scikit-learn    |conda install -c conda-forge scikit-learn    |
|7   |pip install -U imbalanced-learn|conda install -c conda-forge imbalanced-learn|
|8   |pip install tk                 |conda install -c anaconda tk                 |
|9   |pip install joblib             |conda install -c anaconda joblib             |
