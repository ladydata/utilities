import pyspark.sql.functions as f
from pyspark.sql.types import StructField, StructType, StringType, ArrayType, IntegerType
# from pyspark.sql.window import Window


def calc_tf_idf(df, id_col="doc_id", tokens_col="array_of_tokens", df_num=1):

    # Calculate number of documents
    num_docs = df.count() * 1.

    # Calculate Term Frequency * Inverse Document Frequency
    tf_idf = df.\
        .withColumn("token", f.explode(f.col(tokens_col)))\
        .groupBy(id_col, "token").agg(f.count(tokens_col).alias("tf"))\
        .groupBy("token").agg(f.count(id_col).alias("df"), f.sum("tf").alias("tf"))\
        .where(f.col("df") >= df_num)\
        .withColumn("tf_idf", f.col("tf") * f.log((num_docs + 1)/(f.col("df") + 1)))\
        .drop("tf", "df")

    return tf_idf

# Note: if keeping doc_id, then replace the line:
# .groupBy("token").agg(f.count(id_col).alias("df"), f.sum("tf").alias("tf"))\
# by the line:
# .withColumn("df", f.count(f.col(id_col)).over(Window.partitionBy("token")))\


# Test

sentences = ["one green one white and one pink", "no green is blue", "no dark blue no light blue and no pink"]

data = enumerate(s.split() for s in sentences)

schema = StructType([
    StructField("doc_id", IntegerType(), True),
    StructField("document", ArrayType(StringType()), True)])

df = spark.createDataFrame(data, schema)

test = calc_tf_idf(df, id_col="doc_id", tokens_col="document")

test.show(20, False)


# # Easy way to scrap HTML, XML, RTF, HL7 markup from notes (by A Koshta):
# def scrap(s):
#    s = re.sub(" +", " ",
#        re.sub("~|\||\^", " ",
#        re.sub("<.*?>", " ",
#        re.sub("&gt;", ">",
#        re.sub("&lt;", "<",
#        re.sub("&amp;", "&",
#        re.sub("\\\\\w+|\{.*?\}|}", " ",
#        re.sub("<!\[CDATA\[|\]\]>", " ", s)
#    )))))))
#    return s
