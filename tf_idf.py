import pyspark.sql.functions as f
from pyspark.sql.types import StructField, StructType, StringType, ArrayType, IntegerType


def calc_tf_idf(df, id_col="doc_id", tokens_col="document"):

    # Calculate number of documents
    num_docs = df.count() * 1.

    # Turn array of tokens into rows of tokens
    unfolded_df = df.withColumn("token", f.explode(f.col(tokens_col)))
    # unfolded_df.cache()

    # Calculate Term Frequency
    df_TF = unfolded_df\
        .groupBy(id_col, "token").agg(f.count(tokens_col).alias("tf"))

    # Calculate Inverse Document Frequency
    df_IDF = unfolded_df\
        .groupBy("token").agg(f.countDistinct(id_col).alias("df"))\
        .withColumn("idf", f.log((num_docs + 1) / (f.col("df") + 1)))

    # Calculate TF.IDF
    TF_IDF = df_TF\
        .join(df_IDF, "token", "left")\
        .withColumn("tf_idf", f.col("tf") * f.col("idf"))

    return TF_IDF.select(id_col, "token", "tf_idf")


# Test

sentences = ["one green one white and one pink", "no green is blue", "no dark blue no light blue and no pink"]

data = enumerate(s.split() for s in sentences)

schema = StructType([
    StructField("doc_id", IntegerType(), True),
    StructField("document", ArrayType(StringType()), True)])

df = spark.createDataFrame(data, schema)

test = calc_tf_idf(df, id_col="doc_id", tokens_col="document")

test.show(20, False)
