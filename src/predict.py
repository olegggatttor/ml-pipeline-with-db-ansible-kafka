import argparse
import pickle
import numpy as np
from ansible_vault import Vault

from db import get_connection, store_predictions, DB_HOST_NAME, DB_NAME
from kafka_utils import get_producer
from trainer import Trainer

DATABASE_ROOT_CREDENTIALS = 'db.credentials'


def main():
    parser = argparse.ArgumentParser(prog='BikeSharingDemandRegressionPredict')
    parser.add_argument("--data", default="tests/func_samples.csv")
    parser.add_argument("--from_pretrained", default="data/r_forest.pickle")
    parser.add_argument("--ansible_password")
    parser.add_argument("--db_port")
    args = parser.parse_args()

    with open(args.from_pretrained, 'rb') as f:
        trainer = Trainer.from_pretrained(pickle.load(f), args.data, args.data)
        test_predictions = trainer.predict(trainer.get_train())

        assert np.allclose(test_predictions, trainer.get_train()['count'], rtol=0, atol=35), \
            (test_predictions, trainer.get_train()['count'])

    vault = Vault(args.ansible_password)
    with open(DATABASE_ROOT_CREDENTIALS) as vault_data:
        [login, password, kafka_host, kafka_port] = vault.load(vault_data.read()).split()

    db = get_connection(login, password, DB_HOST_NAME, args.db_port, DB_NAME)
    producer = get_producer(kafka_host, kafka_port)
    store_predictions(db, producer, trainer, test_predictions)


if __name__ == '__main__':
    main()
