import requests
import pydantic
from typing import Optional
import string
import typing as t
from datetime import datetime
import json
import pprint
import os
from dotenv import load_dotenv
load_dotenv()
FILENAME = "chicken.json"


class User(pydantic.BaseModel):
    username: str
    password: str

    @pydantic.validator("username")
    def username_valid(cls, value):
        if any(item in value for item in string.punctuation):
            raise ValueError("try again")
        else:

            return value

    @pydantic.root_validator()
    def check_password(cls, values):

        if os.getenv(values.get("username")) != values.get("password"):

            raise ValueError("Your password is incorrect")
        else:
            print("login succesful")
            return values


class Eat(pydantic.BaseModel):

    username: list
    eat_chicken: list
    eat_rice: list
    total_chicken: float
    total_rice: float
    date: datetime = datetime.utcnow()

    @pydantic.root_validator()
    def check_values(cls, values):
        eat_rice = values.get("eat_rice")
        eat_chicken = values.get("eat_chicken")

        for rice in eat_rice:
            if rice < 0.0:
                raise ValueError("You cannot enter a negative value for rice.")
            elif rice == 0.0 and all(chicken == 0.0 for chicken in eat_chicken):
                raise ValueError("Both rice and chicken cannot be zero.")

        for chicken in eat_chicken:
            if chicken < 0.0:
                raise ValueError(
                    "You cannot enter a negative value for chicken.")

        return values


class Buy(pydantic.BaseModel):

    username: str
    buy_rice: float
    buy_chicken: float
    eaten_chicken: float
    eaten_rice: float
    per_chicken: float
    per_rice: float
    date: datetime = datetime.utcnow()

    @pydantic.root_validator()
    def check_values(cls, values):
        if (float(values.get("buy_rice")) > 0.0 and float(values.get("buy_chicken")) >= 0.0) or (float(values.get("buy_rice")) >= 0.0 and float(values.get("buy_chicken")) > 0.0):
            return values
        else:
            raise ValueError(
                "You cannot enter a negative value or double zero!!!!")


class Debt(pydantic.BaseModel):
    buyer: str
    creditor: str
    amount: float
    date: Optional[datetime] = datetime.utcnow()


class Database(pydantic.BaseModel):
    buy: t.List[Buy]
    eat: t.List[Eat]
    debt: t.List[Debt]
    version = "1.0"


def write_database(database: Database):
    with open(FILENAME, "w") as f:
        f.write(database.json(indent=2))


def read_database():
    try:
        with open(FILENAME, "r") as f:
            if not (data := f.read()):
                return None
            database = pydantic.parse_raw_as(Database, data)

        return database
    except FileNotFoundError:
        print("Error : File not found !!! ")


def total(db: Database):
    total_chicken = 0
    total_rice = 0
    for buy in db.buy:
        total_chicken += buy.buy_chicken
        total_rice += buy.buy_rice
    for eat in db.eat:
        total_chicken -= eat.total_chicken
        total_rice -= eat.total_rice
    return total_chicken, total_rice


def user_buy_history(user: User, all: t.List["Buy"]):
    user_special: t.List["Buy"] = []
    for buy in all:
        if buy.username == user.username:
            user_special.append(buy)
    return user_special


# TODO: İLKERİN aldığı TAVUK BİTTİ

# NOTE: True -> Chicken
# NOTE: False -> Rice


def algorithm_of_chicken(db: Database):

    id = find_chicken(db)
    chicken_debt = []
    total_eat_chicken = db.eat[-1].total_chicken
    for fucking in range(len(list(item.username for item in db.buy))):
        rem_chicken = (db.buy[id].buy_chicken - db.buy[id].eaten_chicken)
        if total_eat_chicken <= rem_chicken:
            procces_amount = total_eat_chicken
            total_eat_chicken -= rem_chicken
            chicken_debt.append(debt_proccesser(db, procces_amount, id, True))
        if total_eat_chicken > rem_chicken:
            procces_amount = rem_chicken
            total_eat_chicken -= rem_chicken
            chicken_debt.append(debt_proccesser(db, procces_amount, id, True))
            id += 1
        if total_eat_chicken <= 0:
            break

    return chicken_debt, id, total_eat_chicken


def algorithm_of_rice(db: Database):
    id = find_rice(db)

    rice_debt = []
    total_eat_rice = db.eat[-1].total_rice
    for fucking in range(len(list(item.username for item in db.buy))):

        rem_rice = (db.buy[id].buy_rice - db.buy[id].eaten_rice)
        if total_eat_rice <= rem_rice:
            procces_amount = total_eat_rice
            total_eat_rice -= rem_rice
            rice_debt.append(debt_proccesser(db, procces_amount, id, False))
        if total_eat_rice > rem_rice:
            procces_amount = rem_rice
            total_eat_rice -= rem_rice
            rice_debt.append(debt_proccesser(db, procces_amount, id, False))
            id += 1
        if total_eat_rice <= 0:
            break

    return rice_debt, id, total_eat_rice


def find_chicken(db: Database):
    id = 0
    _, chicken = total(db)
    if chicken == 0:
        return id
    for i in db.buy:
        if i.buy_chicken != i.eaten_chicken and not (i.buy_chicken == 0 and i.eaten_chicken == 0):
            break
        else:
            id += 1

    return id


def find_rice(db: Database):
    id = 0
    _, rice = total(db)
    if rice == 0:
        return id
    for i in db.buy:

        if i.buy_rice != i.eaten_rice and not (i.buy_rice == 0 and i.eaten_rice == 0):
            break
        else:
            id += 1

    return id


def debt_proccesser(db: Database, procces_amount: float, id: int, chicken_or_rice: bool):
    chicken_or_rice__debt = []
    for i in range(len(db.eat[-1].eat_chicken)):
        if chicken_or_rice is True and db.eat[-1].total_chicken != 0:
            chicken_or_rice__debt.append(float(
                (db.eat[-1].eat_chicken[i] / db.eat[-1].total_chicken) * (db.buy[id].per_chicken * procces_amount)))
        if chicken_or_rice is False and db.eat[-1].total_rice != 0:
            chicken_or_rice__debt.append(float(
                (db.eat[-1].eat_rice[i] / db.eat[-1].total_rice) * (db.buy[id].per_rice * procces_amount)))

    return chicken_or_rice__debt


def debt_printer(db: Database, chicken_or_rice_debt_list: list, id: int, rice_or_chicken: bool):
    item = 0

    while item != len(chicken_or_rice_debt_list[0]):
        debt_list = debt_user_elements(chicken_or_rice_debt_list, item)
        if rice_or_chicken is True:
            i = find_chicken(db)
        else:
            i = find_rice(db)
        for username in range(len(debt_list)):
            if item < len(db.eat[-1].username) and db.buy[i].username != db.eat[-1].username[item]:
                debt = Debt(
                    buyer=db.buy[i].username,
                    creditor=db.eat[-1].username[item],
                    amount=debt_list[username]
                )

                db.debt.append(debt)

            if i != id:
                i += 1
        item += 1
    return db


def debt_user_elements(lst: list, i: int):
    total = []
    for sublist in lst:
        if i < len(sublist):
            total.append(sublist[i])
    return total


def eaten_chicken_printer(db: Database, id: int, total_eat_chicken: float):
    i = find_chicken(db)
    while i != id:
        db.buy[i].eaten_chicken = db.buy[i].buy_chicken
        print(f"The chicken that {db.buy[i].username} bought is finished ")
        i += 1
    if id == i:
        db.buy[i].eaten_chicken = db.buy[i].buy_chicken + total_eat_chicken
        if db.buy[i].eaten_chicken == db.buy[i].buy_chicken :
            print(f"The chicken that {db.buy[i].username} bought is finished ")
            
    return db


def eaten_rice_printer(db: Database, id: int, total_eat_rice: float):
    i = find_rice(db)
    while i != id:
        db.buy[i].eaten_rice = db.buy[i].buy_rice
        i += 1
    if id == i:
        db.buy[i].eaten_rice = db.buy[i].buy_rice + total_eat_rice
    return db


def pay_off(db: Database, username: str, buyer: str, amount: float):
    debt = Debt(
        buyer=buyer,
        creditor=username,
        amount=-1 * (amount)
    )
    db.debt.append(debt)
    return db


def sum_debts(db: Database):
    debt_totals = {}
    for debt in db.debt:
        buyer = debt.buyer
        creditor = debt.creditor
        amount = debt.amount
        key = f"{buyer}-{creditor}"
        if key in debt_totals:
            debt_totals[key] += amount
        else:
            debt_totals[key] = amount
    return debt_totals


def exchange_api(amount: float, from_currency: str, to_currency: str):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    amount = amount
    response = requests.get(
        f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

    return float(response.json()['rates'][to_currency])
