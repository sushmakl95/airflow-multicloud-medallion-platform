ThisBuild / scalaVersion := "2.12.18"
ThisBuild / version      := "0.1.0"
ThisBuild / organization := "io.lakehouse"

lazy val sparkVersion = "3.5.1"
lazy val deltaVersion = "3.1.0"

lazy val root = (project in file("."))
  .settings(
    name := "scala-spark-udfs",
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-sql"        % sparkVersion % Provided,
      "org.apache.spark" %% "spark-streaming"  % sparkVersion % Provided,
      "io.delta"         %% "delta-spark"      % deltaVersion % Provided,
      "org.scalatest"    %% "scalatest"        % "3.2.18"     % Test
    ),
    Compile / mainClass := Some("io.lakehouse.SparkUDFs")
  )
