#############################################################################
# project: Reusable code snippets
# version: 0.1
# release: 2019-06
# author: Paula Alves
#############################################################################

# PRESTO: encrypt NPI number
to_hex(xxhash64(to_utf8(phys_npi))) AS npi


# ATHENA: create table via Spark
df = spark.read.parquet("s3://source_loc/myparquetfile/*")
df.write.parquet("path", "s3://dest_loc/").saveAsTable("athenadb.tablename")


# JUPYTER

# List all magic commands
%lsmagic

# Header template (Python 3)
%matplotlib inline
# import datetime
# import time
import re
import sys
print(sys.version)


import numpy as np
print('Numpy version:', np.__version__)

import pandas as pd
print('Pandas version:', pd.__version__)

import matplotlib as mpl
import matplotlib.pyplot as plt
print('Matplotlib version:', mpl.__version__)

import seaborn as sns
print('Seaborn version:', sns.__version__)
sns.set()
pal = sns.hls_palette(10, h=.5)
sns.set_palette(pal)

# #Avoid display of scientific notation and show precision of 4 decimals:
# pd.set_option('display.float_format', lambda x: '%.4f' % x)


# Reconfigure EMR Spark cluster within Jupyter notebook

%%configure -f
{"conf":{"spark.executor.memory":"24G",
         "spark.executor.cores":"4",
         "spark.executor.instances":"1000",
         "spark.sql.shuffle.partitions":"640",
         "spark.dynamicAllocation.enabled": "False"}}
#
# For EMR cluster, set executor (task node with largest EBS storage) to
# minimum of 20 instances instead of 0 (i.e. min and max as 20 instances).
# REMEMBER TO SHUT DOWN THE SPARK SESSION AND RESIZE DOWN CLUSTER WHEN DONE!


# SPARK

# Display all dataframes in the current Spark Session
def list_dataframes():
    return [k for (k, v) in globals().items() if isinstance(v, DataFrame)]

list_dataframes()


# Make Hive data catalog available if necessary
spark = spark\
    .builder\
    .enableHiveSupport()\
    .getOrCreate()


# SQL queries
tablename.createOrReplaceTempView('table_name')

df = spark.sql("""
SELECT *
FROM table_name
""")


# Create an empty dataframe
import pyspark.sql.functions as f
from pyspark.sql.types import StructField, StructType, StringType, DateType

## Define schema (may also pass existing table schema)
df_schema = StructType([
    StructField("id", StringType(), True),
    StructField("record_date", DateType(), True),
    StructField("notes", StringType(), True),
    StructField("numchars", IntegerType(), True)])

df = spark.createDataFrame([], df_schema)


# Read csv data (complete option)
## Pass header
h = ['id', 'code', 'description', 'comment']

## Create schema where all fields are nullable strings
fields = [StructField(field_name, StringType(), True) for field_name in h]
schema = StructType(fields)

# Read data
diag = spark.read\
            .format("csv")\
            .schema(schema)\
            .option("header", "false")\
            .option("sep", "\001")\
            .option("nullValue", "null")\
            .load("s3://loc-data/")


# Output csv file not partitioned
df.repartition(1).write.csv("s3_loc")


# Create md5 keys
list_of_columns = ["first", "last", "dob", "gender"]

spark.read.parquet("s3://loc")\
    .select(md5(concat_ws("|", *list_of_columns)).alias("id"))

# Cast parameter from string to date
first_date = f.to_date(f.lit(start_date), "yyyy-MM-dd")


# Map taxonomy codes in NPPES data
@f.udf(ArrayType(StringType()))
def map_taxonomy(arr):
    """
    Function to map NPPES taxonomy codes to their description.

    This function takes a column with an array of taxonomy strings and returns
    an array of taxonomy description strings if the taxonomy exists as a key
    in a dictionary with the codes of interest, otherwise it returns "N/A"

    Parameters
    ----------
    arr : array<string>
        Array of NPPES taxonomy strings

    Returns
    -------
    arr : array<string>
        Array with taxonomy description strings

    """
    # taxonomy codes mapping
    codes = {
        "207W": "Ophthalmology",
        "152W": "Optometry",
        "1932": "Multi-Specialty Individual Group",
        "1934": "Single Specialty Individual Group",
        "207K": "Allergy & Immunology",
        "207L": "Anesthesiology",
        "208U": "Clinical Pharmacology",
        "208C": "Colon & Rectal Surgery",
        "207N": "Dermatology",
        "204R": "Electrodiagnostic Medicine",
        "207P": "Emergency Medicine",
        "207Q": "Family Medicine",
        "208D": "General Practice",
        "208M": "Hospitalist",
        "202C": "Independent Medical Examiner",
        "207R": "Internal Medicine",
        "2098": "Legal Medicine",
        "207S": "Medical Genetics",
        "207T": "Neurological Surgery",
        "204D": "Neuromusculoskeletal Medicine & OMM",
        "204C": "Neuromusculoskeletal Medicine, Sports Medicine",
        "207U": "Nuclear Medicine",
        "207V": "Obstetrics & Gynecology",
        "207W": "Ophthalmology",
        "204E": "Oral & Maxillofacial Surgery",
        "207X": "Orthopaedic Surgery",
        "207Y": "Otolaryngology",
        "208V": "Pain Medicine",
        "207Z": "Pathology",
        "2080": "Pediatrics",
        "202K": "Phlebology",
        "2081": "Physical Medicine & Rehabilitation",
        "2082": "Plastic Surgery",
        "2083": "Preventive Medicine",
        "2084": "Psychiatry & Neurology",
        "2085": "Radiology",
        "2086": "Surgery",
        "208G": "Thoracic Surgery",
        "204F": "Transplant Surgery",
        "2088": "Urology",
        "103T": "Psychologist",
        "152W": "Optometrist",
        "163W": "Registered Nurse",
        "1835": "Pharmacist",
        "364S": "Clinical Nurse Specialist",
        "363L": "Nurse Practitioner",
        "363A": "Physician Assistant",
        "213E": "Podiatrist",
        "225X": "Occupational Therapist",
        "2251": "Physical Therapist",
        "225C": "Rehabilitation Counselor",
        "2278": "Respiratory Therapist, Certified",
        "2279": "Respiratory Therapist, Registered",
        "231H": "Speech, Language and Hearing Service Providers",
        "261Q": "Clinic/Center - Non-individual",
        "281P": "Hospital - Chronic Disease",
        "282N": "Hospital - General Acute Care",
        "282E": "Hospital - Longe Term Care",
        "2865": "Hospital - Military",
        "283Q": "Hospital - Psychiatric",
        "283X": "Hospital - Rehabilitation",
        "385H": "Respite Care Facility",
        "3336": "Pharmacy"}

    return [codes.get(k, "N/A") for k in arr]


# UDF: remove dups from an array of strings
remove_dup = f.udf(lambda x: list(set(x)), ArrayType(StringType()))


# UDF: flatten array (no longer needed from 2.4)
from itertools import chain
flatten_udf = udf(lambda x: list(set(chain.from_iterable(x))), ArrayType(IntegerType()))


# data aggregation
pts.join(rx, "id")\
    .groupBy("id", "index_date")\
    .agg(flatten_udf(collect_set(when((col("rx_date") > date_sub(col("index_date"), 365)) & (col("rx_date") <= col("index_date")), col("classes")))).alias("pre_12mo"),
         flatten_udf(collect_set(when((col("rx_date") > col("index_date")) & (col("rx_date") <= date_add(col("index_date"), 365)), col("classes")))).alias("post_12mo"))\
    .show()
