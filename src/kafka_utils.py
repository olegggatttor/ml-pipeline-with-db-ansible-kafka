from kafka import KafkaProducer


def get_producer(kafka_host: str, kafka_port: int):
    producer = KafkaProducer(bootstrap_servers=f'{kafka_host}:{kafka_port}')
    return producer


KAFKA_PREDICTIONS_TOPIC = "kafka-predictions"
