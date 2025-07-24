"""
Kafka Producer / Consumer (NAVER Cloud Data Streaming API 호환)
"""
import json, logging, asyncio
from kafka import KafkaProducer
from config import settings

class Streamer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode(),
            key_serializer=lambda k: k.encode() if k else None
            # TODO: security_protocol, sasl_mechanism 등 설정
        )

    async def send(self, topic: str, key: str | None, value: dict):
        try:
            fut = self.producer.send(topic, key=key, value=value)
            await asyncio.get_event_loop().run_in_executor(None, fut.get, 10)
            logging.debug("→ Kafka %s", topic)
        except Exception as e:
            logging.error("Kafka send error %s", e)