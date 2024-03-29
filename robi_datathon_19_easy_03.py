# -*- coding: utf-8 -*-
"""robi-datathon-19-easy-03

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MOndGqiNNYOH3qDbYHjl615NFRYilZX3

#Step 01. Install All Dependencies

This installs Apache Spark 2.3.3, Java 8, Findspark library that makes it easy for Python to work on the given Big Data.
"""

import os
#OpenJDK Dependencies for Spark
os.system('apt-get install openjdk-8-jdk-headless -qq > /dev/null')

#Download Apache Spark
os.system('wget -q http://apache.osuosl.org/spark/spark-2.3.3/spark-2.3.3-bin-hadoop2.7.tgz') 

#Apache Spark and Hadoop Unzip
os.system('tar xf spark-2.3.3-bin-hadoop2.7.tgz')

#FindSpark Install
os.system('pip install -q findspark')

"""# Step 02. Set Environment Variables
Set the locations where Spark and Java are installed based on your installation configuration. Double check before you proceed.
"""

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-2.3.3-bin-hadoop2.7"

"""# Step 03. ELT - Load the Data: Mega Cloud Access
This is an alternative approach to load datasets from already stored in [**Mega Cloud**](https://mega.nz) cloud repository. You need to install the necessary packages and put the link URL of cloud to load the file from cloud directly.
"""

import os
os.system('git clone https://github.com/jeroenmeulenaar/python3-mega.git')
os.chdir('python3-mega')
os.system('pip install -r requirements.txt')

"""# Step 04. ELT - Load the Data: Read Uploaded Dataset
In this approach you can directly load the uploaded dataset downloaded fro Mega Cloud Infrastructure
"""

from mega import Mega
os.chdir('../')
m_prepaid = Mega.from_ephemeral()
m_prepaid.download_from_url('https://mega.nz/#!kwRG2YyC!8TU2aoENtn98M9FHvGEjbk4iIsxBDBERw_H_wFzUchA')

m_postpaid = Mega.from_ephemeral()
m_postpaid.download_from_url('https://mega.nz/#!R0RWwAKA!4HK8qDfIxCFo40mS7hnYjo5XiBYmGhUcB23rN5uSQQk')

m_crm = Mega.from_ephemeral()
m_crm.download_from_url('https://mega.nz/#!soBChSAY!gnyBRDrglAgkQffIAOqHDGGoOViYywT6eXc2DYZlz5E')

"""# Step 05. Start a Spark Session
This basic code will prepare to start a Spark session.
"""

import findspark
findspark.init()
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('ml-datathon19-easy03').master("local[*]").getOrCreate()

"""# Step 06. Data Cleaning - Phase 01 Data Schema View
Now let's load the DataFrame and see the schema view of the Spark dataset and start cleaning our datasets
"""

df_crm = spark.read.csv('crm.csv', header = False, inferSchema = True)
df_crm.dtypes

"""# Step 07. Data Cleaning - Phase 02 Header Update
Now let's load the DataFrame and we can see that there is no header for this dataset. So we need to update the header columns and verify
"""

df_crm =df_crm.withColumnRenamed('_c0', 'msisdn')

df_crm =df_crm.withColumnRenamed('_c1', 'gender')

df_crm =df_crm.withColumnRenamed('_c2', 'year_of_birth')

df_crm =df_crm.withColumnRenamed('_c3', 'system_status')

df_crm =df_crm.withColumnRenamed('_c4', 'mobile_type')

df_crm =df_crm.withColumnRenamed('_c5', 'value_segment')

df_crm.head()

"""# Step 08. Data Cleaning - Phase 03 Row Count and Unique Row Count
We need to know the number of rows. We'll grab total number of entries to have an overview of all data and grab total number of unique entries or unique row count of the Spark dataset to have an overview of duplicate data
"""

print("Total Rows: ")
df_crm.count()

print("Unique Rows: ")
df_crm.distinct().count()

"""# Step 09. Data Cleaning - Phase 04 Removing duplicate rows

Roughly `0.017%` data are `DUPLICATE` values from the table. Since this is neglitible compare to the original row count, we will now filter the dataset to remove all `DUPLICATE` values
"""

df_crm = df_crm.dropDuplicates()

"""# Step 10. Data Cleaning - Phase 05 Review NULL values in each column
Since the total row count and unique row count are now same, it means there is no duplicate rows in the table. Now we'll grab the count of NULL values per column to check whether any missing values is there or not.
"""

import pyspark.sql.functions as F
df_agg = df_crm.agg(*[F.count(F.when(F.isnull(c), c)).alias(c) for c in df_crm.columns])
df_agg.show()

"""# Step 11. Data Cleaning - Advanced Data Filling
Roughly `19.5%` `gender` data, `3%` `year_of_birth` data and `8.5%` `value_segment` data are `NULL` values from the table. Since this is a large chunk of data, we will now do some advanced techniques to fill the required columns so that we can do our operations fruitfully
"""

df_crm.groupBy("year_of_birth").count().sort("count", ascending=False).show()

df_crm_year_10 = df_crm.filter(df_crm["year_of_birth"]<2001)
df_crm_year_10_75 = df_crm_year_10.filter(df_crm_year_10["year_of_birth"]>1944)
df_crm_year_10_75.groupBy("year_of_birth").count().sort("year_of_birth", ascending=False).show()

df_crm_year_10_75.groupBy("gender").count().sort("count", ascending=False).show()

"""#Test From Here"""

df_crm_year_10_75_x = df_crm_year_10_75.replace(['M', 'm', 'MALE', 'male','Male.'], ['Male', 'Male', 'Male', 'Male', 'Male'], 'gender')
df_crm_year_10_75_xy = df_crm_year_10_75_x.replace(['F', 'f', 'FEMALE', 'female', 'Female.', 'Female]', 'FEMELE', 'FE', 'Not Available', 'Female3'], ['Female', 'Female', 'Female', 'Female', 'Female', 'Female', 'Female', 'Female', 'Female', 'Female'], 'gender')

df_crm_year_10_75_xy = df_crm_year_10_75_xy.fillna({'gender':'Female'})
df_crm_year_10_75_xy.groupBy("gender").count().sort("count", ascending=False).show()

df_prepaid = spark.read.csv('prepaid.csv', header = True, inferSchema = True)
df_prepaid.dtypes

df_postpaid = spark.read.csv('postpaid.csv', header = True, inferSchema = True)
df_postpaid.dtypes

ta = df_crm_year_10_75_xy.alias('ta')
tb = df_prepaid.alias('tb')
tc = df_postpaid.alias('tc')
inner_join_pre = ta.join(tb, ta.msisdn == tb.msisdn)
inner_join_post = ta.join(tc, ta.msisdn == tc.msisdn)

from pyspark.sql.functions import desc
Easy02 = inner_join_pre.groupBy('gender').agg({'total_volume_mb':'sum'}).sort(desc("sum(total_volume_mb)"))
Easy02 = Easy02.withColumnRenamed("sum(total_volume_mb)", "Total Data Consumed (Prepaid)")
Easy02 = Easy02.withColumnRenamed("gender", "Gender")
Easy02.show(n=2, truncate=False)

from pyspark.sql.functions import desc
Easy03 = inner_join_post.groupBy('gender').agg({'total_volume_mb':'sum'}).sort(desc("sum(total_volume_mb)"))
Easy03 = Easy03.withColumnRenamed("sum(total_volume_mb)", "Total Data Consumed (Postpaid)")
Easy03 = Easy03.withColumnRenamed("gender", "Gender")
Easy03.show(n=2, truncate=False)

"""#Stop Here

# Step 06. Exploration - Data Schema View
Now let's load the DataFrame and see the schema view of the Spark dataset

# Step 07. Exploration - Row Count
Now since all the rows are here string/text formatted there is no meaning of running statistical method over the values of these columns. But we need to know the number of rows. We'll grab total number of entries to have an overview of data

# Step 08. Exploration - Total Unique Row Count
Now we'll grab total number of unique entries or unique row count of the Spark dataset to have an overview of duplicate data

# Step 09. Exploration - Reviewing the NULL values in each column
Since the total row count and unique row count are same, it means there is no duplicate rows in the table. Now we'll grab the count of NULL values per column to check whether any missing values is there or not.

# Step 10. Exploration - Filtering the NULL values rows of Model entries
Roughly `1.25%` data are `NULL` values from the table. Since this is neglitible compare to the original row count, we will now filter the dataset to remove all `NULL` values of `model_name` column.

# Step 11. Implementation - Run the SQL Command
Now since we got the idea that there is no NULL values and we optimises the dual SIM enabled mobile set rows, we can straightly go for executing SQL command to get the desired outcome. As a part of optimisation, we can drop of the column week_number as this is not relevant to this problem.
"""