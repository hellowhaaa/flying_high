# 基于 Apache Airflow 的基础镜像
FROM apache/airflow:2.7.1
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# USER root

# # -# 安装 MongoDB provider
# # RUN pip install apache-airflow-providers-mongo
# # RUN pip install --no-cache-dir selenium webdriver-manager


# # 安装必要的工具
# RUN apt-get update && apt-get install -y wget software-properties-common


# RUN apt-get update && apt-get install -y unzip wget curl
# # 安装 ChromeDriver
# RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#     wget -N http://chromedriver.storage.googleapis.com/114.0.5735.16/chromedriver_linux64.zip -P ~/ && \
#     unzip ~/chromedriver_linux64.zip -d ~/ && \
#     rm ~/chromedriver_linux64.zip && \
#     mv -f ~/chromedriver /usr/local/bin/chromedriver && \
#     chmod 0755 /usr/local/bin/chromedriver

# # # 安裝 selenium 和 webdriver-manager
# # RUN pip install selenium webdriver-manager
# # 切换回默认用户
# USER airflow

