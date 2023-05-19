import os
import psycopg2
import configparser


def load():
    config = configparser.ConfigParser()
    config.read("config.ini")

    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()

    # DO NOT WORKING DUE TO FOREIGN KEYS AND __enter__
    # files = os.listdir(os.getcwd() + '/data_csv')
    files = ['client.csv', 'currency.csv', 'account.csv', 'credit.csv', 'deposit.csv',
             'card.csv', 'accountclient.csv', 'accountcard.csv', 'currencycard.csv']
    for i in files:
        with open(os.getcwd() + '/data_csv/' + i, 'r') as f:
            with cur.copy_from(f, i[:-4], sep=',') as copy:
                while data := f.read(100):
                    copy.write(data)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    load()

