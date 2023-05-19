CREATE TABLE Client (
    id serial not null primary key,
    name varchar(30),
    email varchar(50),
    confirmed bool,
    phone_number char(11),
    date_birth date,
    passport_num varchar(11),
    password_hash varchar(50),
    secret_q_hash varchar(90)
);


CREATE TABLE Currency (
    id serial not null primary key,
    name varchar(5),
    exchange2_rub float,
    available bigint
);

CREATE TABLE Account (
    id serial not null primary key,
    number char(22) unique,
    balance bigint,
    blocked bool,
    INN char(10),
    BIK char(9),
    id_currency integer references currency(id)
);

CREATE TABLE Credit(
    id serial not null primary key,
    sum integer,
    interest_rate float,
    payment_month integer,
    date_start date,
    date_end date,
    id_account integer references account(id)
);

CREATE TABLE Deposit(
    id serial not null primary key,
    sum integer,
    interest_rate float,
    date_start date,
    date_end date,
    id_account integer references account(id)
);

CREATE TABLE AccountClient (
    id serial not null primary key,
    id_account integer references account(id),
    id_client integer references client(id)
);

CREATE TABLE Card (
    id serial not null primary key,
    type smallint,
    number_hash varchar(30),
    pin_hash varchar(30),
    code_hash varchar(30),
    date_hash varchar(30)
);

CREATE TABLE AccountCard (
    id serial not null primary key,
    id_account integer references account(id),
    id_card integer references card(id)
);

CREATE TABLE CurrencyCard (
    id serial not null primary key,
    id_currency integer references currency(id),
    id_card integer references card(id)
);

CREATE TABLE Operation (
    id serial not null primary key,
    amount integer,
    place varchar(100),
    date date,
    blocked bool,
    id_currency integer references currency(id),
    id_account integer references account(id),
    id_card integer references card(id)
);