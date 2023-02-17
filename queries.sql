

/*
    Посчитать средний процент на остаток по дебетовой карте для всех счетов.
*/

SELECT AVG(percent) AS mean_percent
FROM card
WHERE card_type = 'Дебетовая';

/*
    Вывести всех пользователей, имеющих хотя бы один заблокированный счет, и количество заблокированных счетов.
 */
SELECT users.name, COUNT(a2.number) AS amount
FROM users
    JOIN accountusers a on users.id = a.user_id
    JOIN account a2 on a.account_id = a2.id
WHERE blocked = True
GROUP BY users.name
ORDER BY amount DESC, name;


/*
    Посчитать средний долг по кредитам всех пользовательей.
*/
SELECT AVG(aad.debt) AS mean_dept
FROM (
    SELECT SUM(credit_limit) AS debt
FROM account
    JOIN accountusers a on account.id = a.account_id
GROUP BY user_id
     ) as aad;

/*
    Вывести всех пользователей, имеющих на счету больше, чем 1 млн. Отсоритровать по убыванию счета.
*/
SELECT users.name, SUM(account.value) AS money
FROM users
    JOIN accountusers a on users.id = a.user_id
    JOIN account on a.account_id = account.id
WHERE account.value > 1000000
GROUP BY users.name
ORDER BY money DESC;

/*
    Вывести всех пользователей с максимальным количеством переводов и сумму их переводов.
*/
SELECT users.name, SUM(value) AS sum
FROM users
    JOIN accountusers au ON users.id = au.user_id
    JOIN transaction tr ON au.account_id = tr.account_id
GROUP BY users.name
HAVING COUNT(users.name) = (
        SELECT COUNT(transaction.value)
        FROM transaction
            JOIN account a on transaction.account_id = a.id
            JOIN accountusers a2 on a.id = a2.account_id
            JOIN users u on a2.user_id = u.id
        GROUP BY u.id
        ORDER BY COUNT(transaction.value) DESC
        LIMIT 1
    )
ORDER BY sum DESC;

/*
    Найти самую популярную валюту переводов среди пользователей, имеющих кредит.
 */

SELECT currency.name, COUNT(t.id) AS amount_t
FROM currency
    JOIN transaction t on currency.id = t.currency_id
    JOIN account a on t.account_id = a.id
    JOIN accountusers a2 on a.id = a2.account_id
WHERE a2.user_id IN (
        SELECT users.id
        FROM users
            JOIN accountusers a on users.id = a.user_id
            JOIN account a2 on a.account_id = a2.id
        WHERE credit_limit != 0
    )
GROUP BY currency.name
ORDER BY amount_t DESC
LIMIT 1;

/*
    Найти валюты с наибольшей суммой операций за сегодня, выраженной в рублях.
 */


SELECT name, SUM(value * exchange_ration2rub) AS max_sum_rub
FROM transaction
    JOIN currency c on transaction.currency_id = c.id
WHERE date = CURRENT_DATE
GROUP BY name
HAVING SUM(value * exchange_ration2rub) = (
    SELECT SUM(value * exchange_ration2rub)
    FROM transaction
        JOIN currency c2 on transaction.currency_id = c2.id
    WHERE date = CURRENT_DATE
    GROUP BY currency_id
    ORDER BY SUM(value * exchange_ration2rub) DESC
    LIMIT 1 );

/*
    Вывести имена пользователей с наибольшим совокупным состоянием.
 */
SELECT users.name, SUM(value) AS sum
FROM users
    JOIN accountusers a on users.id = a.user_id
    JOIN account a2 on a.account_id = a2.id
GROUP BY users.name
HAVING SUM(value) = (
    SELECT SUM(value)
        FROM users
    JOIN accountusers a on users.id = a.user_id
    JOIN account a2 on a.account_id = a2.id
    GROUP BY users.name
    ORDER BY SUM(value) DESC
    LIMIT 1 );


/*
    Вывести все транзакции с суммой меньшей 1000 руб за вчера
 */

SELECT *, value * c.exchange_ration2rub AS rub_value FROM transaction
         JOIN currency c on transaction.currency_id = c.id
    WHERE value * c.exchange_ration2rub < 1000 AND date=MAKE_DATE(2022, 12, 18)
