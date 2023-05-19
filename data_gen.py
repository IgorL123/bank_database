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
    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()

    person = Person('ru')
    cur.execute("""SELECT count(id) FROM client """)
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
        passport_number = str(random.randint(10**9, 10**10 - 1))
        pass_hash = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))
        sec_q = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))
        cur.execute("""
        INSERT INTO client (name, email, confirmed, phone_number, date_birth, passport_num, password_hash
        , secret_q_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s );
        """, (name, email, verified, phone_number, date_birth, passport_number, pass_hash, sec_q))
        last_user_id += 1
        conn.commit()

        if verified:
            # GEN ACCOUNTS
            amount_accounts = random.randint(0, 4)
            if not amount_accounts:
                amount_cards = 0
            else:
                amount_cards = random.randint(1, 4)
            for j in range(amount_accounts):
                number = random.randint(10 ** 21, 10 ** 22 - 1)
                value = random.randint(0, 4 * 10 ** 6 + 1)
                if random.randint(0, 20) > 18:
                    blocked = True
                else:
                    blocked = False
                inn = random.randint(10 ** 9, 10 ** 10 - 1)
                bik = random.randint(10 ** 8, 10 ** 9 - 1)
                currency_id = random.sample(range(1, len(currency_list)), 1)[0]
                cur.execute("""
                 INSERT INTO account (number, balance, blocked, inn, bik, id_currency)
                 VALUES (%s, %s, %s, %s, %s, %s);
                """, (number, value, blocked, inn, bik, currency_id))
                last_account_id += 1
                conn.commit()
                cur.execute("""
                    INSERT INTO accountclient (id_account, id_client) 
                    VALUES (%s, %s);
                """, (last_account_id, last_user_id))

                if not blocked:
                    # GEN CREDIT & DEPOSIT

                    amount_credit = random.randint(0, 2)
                    amount_deposit = random.randint(0, 1)

                    for credit in range(amount_credit):
                        start = datetime.date.today()
                        end = datetime.date(2070, 12, 1)
                        date_e_credit = start + datetime.timedelta(
                            seconds=random.randint(0, int((end - start).total_seconds())),
                        )
                        start = datetime.date(1991, 12, 1)
                        end = datetime.date.today()
                        date_s_credit = start + datetime.timedelta(
                            seconds=random.randint(0, int((end - start).total_seconds())),
                        )
                        in_rate_credit = min(0.1, random.random())
                        payment = random.randint(10**2, 10**4)
                        sum_credit = random.randint(10**3, 10**6)
                        cur.execute("""INSERT INTO credit (sum, interest_rate, payment_month, date_start, date_end, id_account)
                                                   VALUES (%s, %s, %s, %s, %s, %s); """,
                                (sum_credit, in_rate_credit, payment, date_s_credit, date_e_credit, last_account_id))
                        conn.commit()

                    for depo in range(amount_deposit):
                        start = datetime.date.today()
                        end = datetime.date(2070, 12, 1)
                        date_e_depo = start + datetime.timedelta(
                            seconds=random.randint(0, int((end - start).total_seconds())),
                        )
                        start = datetime.date(1991, 12, 1)
                        end = datetime.date(2070, 12, 1)
                        date_s_depo = start + datetime.timedelta(
                            seconds=random.randint(0, int((end - start).total_seconds())),
                        )
                        in_rate_deposit = max(0.2, random.random())
                        sum_deposit = random.randint(10**3, 10**6)

                        cur.execute("""INSERT INTO deposit (sum, interest_rate, date_start, date_end, id_account)
                                   VALUES (%s, %s, %s, %s, %s);""",
                                (sum_deposit, in_rate_deposit, date_s_depo, date_e_depo, last_account_id))
                        conn.commit()

                    for k in range(amount_cards):
                        card_type = random.randint(0, 2)
                        card_number = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))
                        card_date = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))
                        pin = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))
                        cvv = ''.join(random.choices([chr(i) for i in range(65, 90)], k=25))

                        cur.execute("""
                            INSERT INTO card (type, number_hash, date_hash, pin_hash, code_hash)
                            VALUES (%s, %s, %s, %s, %s);
                        """, (card_type, card_number, card_date, pin, cvv))
                        last_card_id += 1
                        conn.commit()
                        cur.execute("""
                            INSERT INTO accountcard (id_account, id_card) 
                            VALUES (%s, %s);
                        """, (last_account_id, last_card_id))

                        amount_cur = random.randint(1, 4)
                        names = random.sample(range(1, len(currency_list)), 10)
                        for n in range(amount_cur):
                            cur.execute("""
                                INSERT INTO currencycard (id_currency, id_card) 
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

        ratio = round(random.uniform(0.001, 200), 2)
        if not currency_list[i] == 'RUB':
            available = random.randint(0, 2 ** 27)
            cur.execute("""
                INSERT INTO currency (name, exchange2_rub, available)
                VALUES (%s, %s, %s);
            """, (currency_list[i], ratio, available))
        else:
            available = random.randint(2 ** 26 + 1, 2 ** 31 - 1)
            cur.execute("""
                INSERT INTO currency (name, exchange2_rub, available)
                VALUES (%s, %s, %s);
            """, (currency_list[i], 1, available))

    conn.commit()
    cur.close()
    conn.close()


def generate_operations(start, end):

    conn = psycopg2.connect(
        dbname=config["Database"]["dbname"],
        user=config["Database"]["user"],
        password=config["Database"]["password"],
        host=config["Database"]["host"],
        port=config["Database"]["port"]
    )
    cur = conn.cursor()
    cur.execute("""SELECT count(id) FROM client WHERE confirmed = True""")
    users = cur.fetchone()[0]
    omega = random.randint(1, 9)  # Mean amount operations per user
    transactions = users * omega
    address = mimesis.Address('ru')
    cur.execute("""SELECT id FROM account WHERE blocked = False""")
    account_list = cur.fetchall()
    cur.execute("""SELECT id FROM card """)
    card_list = cur.fetchall()

    diff = end - start
    for j in range(diff.days + 1):
        date = start + datetime.timedelta(days=j)
        print("Operations of ", date)
        for i in range(transactions):
            if random.randint(0, 10) < 8:
                value = random.randint(-10**4, 10 ** 4)
            else:
                value = random.randint(-10**4, 10 ** 6)

            if random.randint(0, 10) == 10:
                blocked = True
            else:
                blocked = False
            place = address.city() + ", " + address.address()
            currency_id = random.sample(range(1, len(currency_list)), 1)[0]
            card_id = random.sample(card_list, 1)[0]
            account_id = random.sample(account_list, 1)[0]

            cur.execute("""
                INSERT INTO operation (id_account, id_card, id_currency, amount, place, date, blocked) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (account_id, card_id, currency_id, value, place, date, blocked))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    start = time.time()

    make_currencies()
    generate_users(users=1000)
    today = datetime.date.today()
    delta = datetime.timedelta(days=3)
    generate_operations(today - delta, today)
    # generate_transactions(today, today + datetime.timedelta(days=1))
    print("Time:", time.time() - start)