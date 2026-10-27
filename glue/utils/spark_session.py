
from pyspark.sql import SparkSession
import os
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

def create_spark_session():

    spark = (
        SparkSession.builder
        .appName("Rohith ETL_Project")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.jars.packages","org.apache.hadoop:hadoop-aws:3.3.4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark