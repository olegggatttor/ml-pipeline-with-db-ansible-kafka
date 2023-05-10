import mysql.connector
import logging

from kafka_utils import KAFKA_PREDICTIONS_TOPIC


def get_connection(user, password, host, port, database):
    return mysql.connector.connect(user=user, password=password,
                                   host=host, database=database, port=port)


def store_predictions(db, kafka_producer, trainer, test_predictions):
    try:
        cursor = db.cursor()

        to_store = trainer.get_train()
        to_store_data = to_store.drop('count', axis=1).to_numpy()
        to_store_target = to_store['count']

        to_insert = [
            ('root', features.tobytes(), float(target), float(pred))
            for features, target, pred in zip(to_store_data, to_store_target, test_predictions)
        ]

        cursor.executemany(
            INSERT_PREDICTIONS,
            to_insert
        )
        db.commit()

        logging.info(f"{cursor.rowcount} rows was inserted.")

        for log in to_insert:
            kafka_producer.send(KAFKA_PREDICTIONS_TOPIC, bytearray(str(log), 'utf-8'))
    finally:
        db.close()
        kafka_producer.close()


DB_HOST_NAME = "mldb"
DB_NAME = "ml_pipe_db"
INSERT_PREDICTIONS = "INSERT INTO Predicts (login, features, target, predict) VALUES (%s, %s, %s, %s)"
