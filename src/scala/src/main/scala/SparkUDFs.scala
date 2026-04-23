package io.lakehouse

import java.security.MessageDigest
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.udf

/** Registers custom UDFs used by the PySpark silver transformation.
  *
  * Currently:
  *   - normalizePhone: E.164 projection
  *   - maskEmail: preserves the domain but hashes the local-part
  *   - gdprTokenize: deterministic tokeniser for PII columns
  */
object SparkUDFs {

  private def sha256(s: String): String = {
    val md = MessageDigest.getInstance("SHA-256")
    md.digest(s.getBytes("UTF-8")).map("%02x".format(_)).mkString
  }

  val normalizePhone = udf { (raw: String) =>
    if (raw == null) null
    else {
      val digits = raw.replaceAll("[^0-9]", "")
      if (digits.startsWith("1") && digits.length == 11) "+" + digits
      else if (digits.length == 10) "+1" + digits
      else "+" + digits
    }
  }

  val maskEmail = udf { (email: String) =>
    if (email == null) null
    else {
      email.split("@", 2) match {
        case Array(local, domain) => s"${sha256(local).take(10)}@$domain"
        case _ => null
      }
    }
  }

  val gdprTokenize = udf { (value: String) =>
    if (value == null) null else sha256(value).take(32)
  }

  def register(spark: SparkSession): Unit = {
    spark.udf.register("normalize_phone", normalizePhone)
    spark.udf.register("mask_email",      maskEmail)
    spark.udf.register("gdpr_tokenize",   gdprTokenize)
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("SparkUDFsRegistrar")
      .getOrCreate()
    register(spark)
    println("Registered UDFs: normalize_phone, mask_email, gdpr_tokenize")
    spark.stop()
  }
}
