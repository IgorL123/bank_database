

/*
    Вывести всех клиентов, имеющих хотя бы один заблокированный счет, и количество заблокированных счетов.
*/

SELECT client.id, client.name, count(ac.id) as blocked_accounts
FROM client
    JOIN accountclient a on client.id = a.id_client
    JOIN account ac on a.id_account = ac.id
WHERE ac.blocked = true
GROUP BY client.id
ORDER BY blocked_accounts DESC;

/*
    Вывести всех клиентов с максимальным количеством переводов и сумму их переводов.
*/

SELECT client.id, client.name, count(operation.id) as count_operation,
       round(sum(operation.amount * currency.exchange2_rub)) as sum_operation
FROM operation
    JOIN account a on operation.id_account = a.id
    JOIN accountclient ac on a.id = ac.id_account
    JOIN currency on operation.id_currency = currency.id
    JOIN client on ac.id_client = client.id
GROUP BY client.id
ORDER BY count_operation DESC
LIMIT 1;

/*
    Найти валюты с наибольшей суммой операций за сегодня, выраженной в рублях.
*/

SELECT currency.id, currency.name, round(sum(o.amount * currency.exchange2_rub)) as sum_operations
FROM currency
    JOIN operation o on currency.id = o.id_currency
GROUP BY currency.id
ORDER BY sum_operations;

/*
    Вывести все транзакции с суммой меньшей 1000 руб за вчера.
*/

SELECT c.name, round(amount * c.exchange2_rub) AS sum
FROM operation
         JOIN currency c on operation.id_currency = c.id
WHERE amount * c.exchange2_rub < 1000 AND date = MAKE_DATE(2023, 5, 16);

/*
    Вывести имена пользователей с наибольшим совокупным состоянием,
    то есть суммой всех средств на всех счетах, посчитать в рублях.
*/

SELECT client.id, client.name, round(sum(ac.balance * c.exchange2_rub)) as balance_in_rub
FROM client
    JOIN accountclient a on client.id = a.id_client
    JOIN account ac on a.id_account = ac.id
    JOIN currency c on c.id = ac.id_currency
GROUP BY client.id
ORDER BY balance_in_rub DESC;
/*
    Посчитать среднюю сумму операций в различных городах.
*/

SELECT substr(place, 0, position(',' in place)), round(avg(amount)) as avg_operations
FROM operation
GROUP BY substr(place, 0, position(',' in place))
ORDER BY avg_operations DESC;

/*
    Подсчитать для каждого дня в году среднюю сумму операций (покупок) в рублях.
*/

SELECT date, round(avg(amount * c.exchange2_rub)) as sum
FROM operation
    JOIN currency c on operation.id_currency = c.id
GROUP BY date
ORDER BY sum DESC;

/*
    Вывести средний расход за месяц для клиентов банка, имеющих более 3 вкладов .
*/

SELECT client.id, client.name, round(avg(o.amount)) as mean_spending
FROM client
    JOIN accountclient a on client.id = a.id_client
    JOIN account a2 on a.id_account = a2.id
    JOIN operation o on a2.id = o.id_account
    JOIN deposit c on a2.id = c.id_account
WHERE o.amount < 0 and o.date > make_date(2023, 04, 1)
GROUP BY client.id
HAVING count(c.id) > 3
ORDER BY mean_spending ASC;

/*
    Вывести таблицу ранжированных клиентов банка по кредитной истории: чем больше закрыто
    кредитов в срок и чем больше их сумма, тем выше ранг.
 */
SELECT client.id, client.name, rank() OVER (ORDER BY sum(c.sum) DESC) as credit_rank
 FROM client
    JOIN accountclient a on client.id = a.id_client
    JOIN account a2 on a.id_account = a2.id
    JOIN credit c on a2.id = c.id_account
 GROUP BY client.id;
