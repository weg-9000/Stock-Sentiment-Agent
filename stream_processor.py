"""
Kafka ⟶ Flink (or Spark Structured Streaming)  
실시간 집계 Job 의 **개요 코드** (자세한 Job DSL 은 Flink SQL 혹은 PyFlink 로 작성)
"""
FLINK_SCRIPT = """
CREATE TABLE social_raw(
    symbol STRING,
    sentiment_score DOUBLE,
    `ts` TIMESTAMP(3),
    WATERMARK FOR `ts` AS `ts` - INTERVAL '5' SECOND
) WITH (... Kafka connector ...);

CREATE TABLE sentiment_agg(...) WITH (... Postgres sink ...);

INSERT INTO sentiment_agg
SELECT
  symbol,
  AVG(sentiment_score) AS score,
  TUMBLE_START(`ts`, INTERVAL '5' MINUTE) AS window_start
FROM social_raw
GROUP BY
  symbol,
  TUMBLE(`ts`, INTERVAL '5' MINUTE);
"""
# 실제 배포는 .sql / pyflink job 파일로 관리
