# alternative to start from empty df:

import pyspark.sql.functions as f
from pyspark.sql.types import StructField, StructType, StringType, DateType

schema = StructType([
  StructField("PatientUid", StringType(), True),
  StructField("ReferenceDate",DateType(), True),
  StructField("Note", StringType(), True),
  StructField("groups1234", StringType(), False)
])

empty = spark.createDataFrame([], schema)

