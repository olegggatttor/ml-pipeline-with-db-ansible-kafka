import argparse
import pickle
import numpy as np
import logging
from ansible_vault import Vault

from db import get_connection, INSERT_PREDICTIONS, HOST_NAME, DB_NAME, SELECT_ALL_PREDICTS
from trainer import Trainer

DATABASE_ROOT_CREDENTIALS = 'db.credentials'


def main():
    parser = argparse.ArgumentParser(prog='BikeSharingDemandRegressionPredict')
    parser.add_argument("--data", default="tests/func_samples.csv")
    parser.add_argument("--from_pretrained", default="data/r_forest.pickle")
    parser.add_argument("--ansible_password")
    parser.add_argument("--port")
    args = parser.parse_args()

    with open(args.from_pretrained, 'rb') as f:
        trainer = Trainer.from_pretrained(pickle.load(f), args.data, args.data)
        test_predictions = trainer.predict(trainer.get_train())

        assert np.allclose(test_predictions, trainer.get_train()['count'], rtol=0, atol=35), \
            (test_predictions, trainer.get_train()['count'])

    vault = Vault(args.ansible_password)
    with open(DATABASE_ROOT_CREDENTIALS) as vault_data:
        [login, password] = vault.load(vault_data.read()).split()
    db = get_connection(login, password, HOST_NAME, args.port, 'ml_pipe_db')
    try:
        cursor = db.cursor()

        cursor.execute("DESCRIBE Predicts")

        logging.info(cursor.fetchall())

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

        cursor.execute(SELECT_ALL_PREDICTS)

        list(map(logging.info, cursor.fetchall()))
    finally:
        db.close()


if __name__ == '__main__':
    main()
