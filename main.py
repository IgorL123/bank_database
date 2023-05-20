import random

import psycopg2
import configparser
import pandas as pd
from time import time
from datetime import date

config = configparser.ConfigParser()
config.read("config.ini")


class Etl:
    def __init__(self, path, verbose=False):
        self.filepath = path
        self.verbose = verbose

    def extract(self) -> pd.DataFrame:
        return pd.read_csv(self.filepath)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        start = time()

        pd.options.mode.copy_on_write = True
        labels2drop = ['CustGender', 'CustAccountBalance', 'TransactionTime', 'CustomerDOB', "TransactionID"]
        data.drop(labels2drop, axis=1, inplace=True)

        id2id = {}
        row2drop = []
        for i in range(len(data)):
            id = data["CustomerID"][i]
            if id not in id2id:
                if len(id2id) < 1000:
                    id2id[id] = len(id2id) + 1
                else:
                    row2drop.append(i)
            if id in id2id:
                data.loc[i, 'CustomerID'] = id2id[id]
                dat = data["TransactionDate"][i]
                dat = list(map(int, dat.split("/")))
                data.loc[i, "TransactionDate"] = date(dat[-1] + 2000, dat[1], dat[0])

        data.drop(row2drop, axis=0, inplace=True)
        data.rename(columns={"CustomerID": "id", "CustLocation": "place", "TransactionDate": "date",
                             "TransactionAmount (INR)": "amount"}, inplace=True)
        if self.verbose:
            print("Completed")
            print(f"Transform time: {time() - start} sec", )
        return data

    def load(self, data: pd.DataFrame) -> None:
        start = time()

        conn = psycopg2.connect(
            dbname=config["Database"]["dbname"],
            user=config["Database"]["user"],
            password=config["Database"]["password"],
            host=config["Database"]["host"],
            port=config["Database"]["port"]
        )
        cur = conn.cursor()
        id_currency = 20  # IRN
        blocked = False
        for i in range(len(data)):

            place = data.loc[i, "place"]
            amount = data.loc[i, "amount"]
            date = data.loc[i, "date"]
            id = data.loc[i, "id"]
            card = random.randint(1, 999)
            cur.execute(""" INSERT INTO operation (id_account, id_card, id_currency, amount, place, date, blocked) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (id, card, id_currency, amount, place, date, blocked))

        conn.commit()
        cur.close()
        conn.close()

        if self.verbose:
            print("Completed")
            print(f"Load time: {time() - start} sec", )


if __name__ == '__main__':
    etl = Etl('data_csv/' + config['File_csv']['filename'], verbose=True)
    data = etl.extract()
    data = data[:1000]
    data = etl.transform(data)
    etl.load(data)
