import time
import mimesis
import psycopg2
import datetime
from mimesis import Person
import random
import configparser

currency_list = ['AUD', 'EUR', 'DZD', 'USD', 'GBP', 'CNY', 'MXN', 'NOK', 'PLN', 'RUB', 'TRY', 'CHF', 'JPY',
                 'DZD', 'ARS', 'AMD', 'BYN', 'BRL', 'ILS', 'INR', 'IDR']

config = configparser.ConfigParser()
config.read("config.ini")


def generate_users(users):

    bank_list = ['СберБанк', 'ВТБ', 'Газпромбанк', 'Альфа-Банк', 'Россельхозбанк',
                 'Банк «Открытие»', 'Совкомбанк', 'Райффайзенбанк', 'Росбанк', 'Тинькофф Банк']
    card_list = ['Кредитная', 'Дебетовая', 'Виртуальная']

    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()

    person = Person('ru')
    cur.execute("""SELECT count(id) FROM users """)
    last_user_id = cur.fetchone()[0]
    cur.execute("""SELECT count(id) FROM account """)
    last_account_id = cur.fetchone()[0]
    cur.execute("""SELECT count(id) FROM card """)
    last_card_id = cur.fetchone()[0]

    for i in range(users):
        print("Generated user number ", i + 1)
        name = person.full_name()
        email = person.email()
        if random.randint(0, 10) > 8:
            verified = False
        else:
            verified = True
        phone_number = person.telephone().replace('-', "")[1:].replace('(', '').replace(')', '')
        start = datetime.date(1930, 1, 1)
        end = datetime.date.today()
        date_birth = start + datetime.timedelta(
            seconds=random.randint(0, int((end - start).total_seconds())),
        )
        passport_number = random.randint(10**9, 10**10 - 1)

        cur.execute("""
        INSERT INTO users (name, email, verified, phone_number, date_birth, passport_number)
        VALUES (%s, %s, %s, %s, %s, %s );
        """, (name, email, verified, phone_number, date_birth, passport_number, ))
        last_user_id += 1
        conn.commit()

        if verified:
            amount_accounts = random.randint(0, 4)
            if not amount_accounts:
                amount_cards = 0
            else:
                amount_cards = random.randint(1, 4)
            for j in range(amount_accounts):
                number = random.randint(10 ** 21, 10 ** 22 - 1)
                value = random.randint(0, 4 * 10 ** 6 + 1)
                bank_name = random.randint(0, 9)
                if random.randint(0, 10) > 8:
                    credit_limit = random.randint(10 * 4, 3 * 10 ** 6 + 1)
                else:
                    credit_limit = 0
                if random.randint(0, 20) > 18:
                    blocked = True
                else:
                    blocked = False
                inn = random.randint(10 ** 9, 10 ** 10 - 1)
                bik = random.randint(10 ** 8, 10 ** 9 - 1)

                cur.execute("""
                 INSERT INTO account (number, value, credit_limit, bank_name, blocked, inn, bik)
                 VALUES (%s, %s, %s, %s, %s, %s, %s );
                """, (number, value, credit_limit, bank_list[bank_name], blocked, inn, bik))
                last_account_id += 1
                conn.commit()
                cur.execute("""
                    INSERT INTO accountusers (account_id, user_id) 
                    VALUES (%s, %s);
                """, (last_account_id, last_user_id))

                if not blocked:
                    for k in range(amount_cards):
                        if not credit_limit:
                            card_type = random.randint(1, 2)
                        else:
                            card_type = 0
                        card_number = random.randint(10 ** 11, 10 ** 12 - 1)
                        start = datetime.date.today()
                        end = datetime.date(2040, 12, 1)
                        card_date = start + datetime.timedelta(
                            seconds=random.randint(0, int((end - start).total_seconds())),
                        )
                        pin = random.randint(10 ** 3, 10 ** 4 - 1)
                        cvv = random.randint(10 ** 2, 10 ** 3 - 1)
                        percent = random.random()
                        if percent > 0.21:
                            percent = 0.21
                        cur.execute("""
                            INSERT INTO card (card_type, card_number, date, pin, cvv, percent)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (card_list[card_type], card_number, card_date, pin, cvv, percent))
                        last_card_id += 1
                        conn.commit()
                        cur.execute("""
                            INSERT INTO accountcard (account_id, card_id) 
                            VALUES (%s, %s);
                        """, (last_account_id, last_card_id))

                        amount_cur = random.randint(1, 4)
                        names = random.sample(range(1, len(currency_list)), 10)
                        for n in range(amount_cur):
                            cur.execute("""
                                INSERT INTO currencycard (currency_id, card_id) 
                                VALUES (%s, %s);
                            """, (names[n], last_card_id))

    conn.commit()
    cur.close()
    conn.close()


def make_currencies():
    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()

    for i in range(len(currency_list)):

        ratio = random.uniform(0.001, 200)
        if not currency_list[i] == 'RUB':
            available = random.randint(0, 2 ** 27)
            cur.execute("""
                INSERT INTO currency (name, exchange_ration2rub, available)
                VALUES (%s, %s, %s);
            """, (currency_list[i], ratio, available))
        else:
            available = random.randint(2 ** 26 + 1, 2 ** 31 - 1)
            cur.execute("""
                INSERT INTO currency (name, exchange_ration2rub, available)
                VALUES (%s, %s, %s);
            """, (currency_list[i], 1, available))

    conn.commit()
    cur.close()
    conn.close()


def generate_transactions(start, end):

    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()
    cur.execute("""SELECT count(id) FROM users WHERE verified = True""")
    users = cur.fetchone()[0]
    omega = random.randint(1, 9)  # Mean amount transactions per user
    transactions = users * omega
    address = mimesis.Address('ru')
    cur.execute("""SELECT id FROM account WHERE blocked = False""")
    account_list = cur.fetchall()
    cur.execute("""SELECT id FROM card """)
    card_list = cur.fetchall()

    diff = end - start
    for j in range(diff.days + 1):
        date = start + datetime.timedelta(days=j)
        print("Transactions of ", date)
        for i in range(transactions):
            if random.randint(0, 10) < 8:
                value = random.randint(1, 10 ** 4)
            else:
                value = random.randint(1, 10 ** 6)

            if random.randint(0, 10) == 10:
                blocked = True
            else:
                blocked = False
            place = address.city() + ", " + address.address()
            currency_id = random.sample(range(1, len(currency_list)), 1)[0]
            card_id = random.sample(card_list, 1)[0]
            account_id = random.sample(account_list, 1)[0]

            cur.execute(""" 
                INSERT INTO transaction (account_id, card_id, currency_id, value, place, date, blocked) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (account_id, card_id, currency_id, value, place, date, blocked))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    start = time.time()

    make_currencies()
    generate_users(users=2000)
    today = datetime.date.today()
    delta = datetime.timedelta(days=3)
    generate_transactions(today - delta, today)
    # generate_transactions(today, today + datetime.timedelta(days=1))
    print("Time:", time.time() - start)


