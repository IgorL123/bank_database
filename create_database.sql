CREATE TABLE Users (
    id serial not null primary key,
    name varchar(30),
    email varchar(50),
    verified bool,
    phone_number char(11),
    date_birth date,
    passport_number char(10)
);
CREATE TABLE Account (
    id serial not null primary key,
    number char(22) unique,
    value bigint,
    credit_limit int,
    blocked bool,
    bank_name varchar(20),
    INN char(10),
    BIK char(9)
);

CREATE TABLE AccountUsers (
    id serial not null primary key,
    account_id integer references account(id),
    user_id integer references users(id)
);

CREATE TABLE Card (
    id serial not null primary key,
    card_type varchar(12),
    card_number char(16) unique ,
    date date,
    pin char(4),
    cvv char(3),
    percent float
);

CREATE TABLE AccountCard (
    id serial not null primary key,
    account_id integer references account(id),
    card_id integer references card(id)
);

CREATE TABLE Currency (
    id serial not null primary key,
    name varchar(5),
    exchange_ration2rub float,
    available int
);

CREATE TABLE CurrencyCard (
    id serial not null primary key,
    currency_id integer references currency(id),
    card_id integer references card(id)
);

CREATE TABLE Transaction (
    id serial not null primary key,
    account_id int references account(id),
    card_id int references card(id),
    currency_id int references currency(id),
    value int,
    place varchar(100),
    date date,
    blocked bool
);