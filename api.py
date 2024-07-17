from fastapi import FastAPI, HTTPException, Request
from fastapi.params import Body
from pydantic import BaseModel
from data__mine import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response


app = FastAPI()


@app.middleware("http")
async def login(request: Request, call_next):
    try:
        username = request.headers["X-username"]
        password = request.headers["X-password"]
        User(username=username, password=password)
    except Exception:
        return Response(status_code=401, content="username or password is wrong")
    response = await call_next(request)

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login/")
async def checklogin(login: User):
    return True


@app.post("/eat/")
async def create_eat(eat: Eat) -> Eat:
    # TODO:CHANGE APPEND EAT
    db = read_database()
    if not db:
        db = Database(buy=[], eat=[], debt=[])

    chicken, rice = total(db)
    try:
        if eat.total_chicken <= chicken and eat.total_rice <= rice:
            db.eat.append(eat)
            chicken_debt, id_chicken, total_eat_chicken = algorithm_of_chicken(db)
            rice_debt, id_rice, total_eat_rice = algorithm_of_rice(db)
            debt_printer(db, chicken_debt, id_chicken, True)
            debt_printer(db, rice_debt, id_rice, False)
            eaten_chicken_printer(db, id_chicken, total_eat_chicken)
            eaten_rice_printer(db, id_rice, total_eat_rice)
            write_database(db)
        else:
            raise HTTPException(
                status_code=400, detail="There is not enough chicken or rice"
            )
    except HTTPException as e:
        raise e
    return eat


@app.post("/buy/")
async def create_buy(buy: Buy) -> Buy:
    db = read_database()
    if not db:
        db = Database(buy=[], eat=[], debt=[])
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    history = user_buy_history(buy.username, db.buy)
    if history == []:
        _ago = None
    else:
        _ago = round(
            (
                datetime.utcnow()
                - datetime.strptime(str(history[-1].date), date_format)
            ).total_seconds()
            / 3600
        )
    try:
        if _ago is None or _ago >= 3:
            db.buy.append(buy)
            write_database(db)
        else:
            raise HTTPException(
                status_code=400, detail="you already shopped in 3 hours"
            )
    except Exception:
        raise

    return buy


@app.post("/pay/")
async def pay_Api(debt_payment: Debt) -> Debt:
    db = read_database()
    if not db:
        db = Database(buy=[], eat=[], debt=[])
    if debt_payment.payment_method is "try":
        write_database(
            pay_off(db, debt_payment.creditor, debt_payment.buyer, debt_payment.amount)
        )
    if debt_payment is "usd":
        new_amount = exchange_api(debt_payment.amount, "USD", "TRY")
        write_database(
            pay_off(db, debt_payment.creditor, debt_payment.buyer, new_amount)
        )

    return debt_payment


@app.get("/user_eat_history/")
async def users_eat_api():
    db = read_database()
    if not db:
        db = Database(buy=[], eat=[], debt=[])
        return "There is no data"
    # eat_ago = (datetime.utcnow() - db.eat[-1].date).total_seconds()/3600
    # if eat_ago > 0 and eat_ago < 1:
    #     return f"{db.eat[-1].total_chicken} gr chicken and {db.eat[-1].total_rice} gr rice {int((datetime.utcnow() - db.eat[-1].date).total_seconds()/60)} minute ago by {db.eat[-1].username}"
    # else:
    #     return f"{db.eat[-1].total_chicken} gr chicken  and {db.eat[-1].total_rice} gr rice {round(eat_ago)} hour ago by {db.eat[-1].username} "
    return db.eat[-1]


@app.get("/users_buy_history/")
async def user_buy_api(username: str, password: str):
    history = user_buy_history(
        User(username=username, password=password), db.buy
    )  # type:ignore
    # if history == []:
    #     _ago = None
    # else:
    #     _ago = (datetime.utcnow() - history[-1].date).total_seconds()/3600

    # if _ago != None and _ago > 0.0 and _ago < 1.0:

    #     return f"your last purchase {history[-1].buy_chicken} gr  chicken {int((datetime.utcnow() - history[-1].date).total_seconds()/60)} minutes ago"

    # if _ago != None and _ago > 1.0:

    #     return f"your last purchas {history[-1].buy_chicken} gr  chicken {round(_ago)} hour ago"

    # if _ago == None:

    return "you have not made a recent purchase"


@app.post("/debt/")
async def user_debt(user: User) -> t.List["Debt"]:
    db = read_database()
    if not db:
        db = Database(buy=[], eat=[], debt=[])
        return db.debt
    sum_debts_dict = sum_debts(db)
    debt_buyer_list:t.List[str] = []
    debt_creditor_list:t.List[str] = []
    debt_amount_list:
    debt_usd_debt_list = []
    debt: t.List["Debt"] = []
    for key, value in sum_debts_dict.items():
        if f"-{user}" in str(key):
            debt_buyer_list.append(str(key).split("-")[0])
            debt_creditor_list.append(user.username)
            debt_amount_list.append(float(value))
            debt_usd_debt_list.append(float(exchange_api(value, "TRY", "USD")))
    for key in debt_buyer_list:
        debt_list = Debt(
            buyer=debt_buyer_list,
            creditor=debt_creditor_list,
            amount=debt_amount_list,
            usd_amount=debt_usd_debt_list,
            date=datetime.utcnow(),
        )
    debt_list = Debt(
        buyer=debt_buyer_list,
        creditor=debt_creditor_list,
        amount=debt_amount_list,
        usd_amount=debt_usd_debt_list,
        date=datetime.utcnow(),
    )
    debt.append(debt_list)
    return debt


# @app.delete("/delete_eat/")
# async def delete_eat():
#     del db.eat[-1]
#     write_database(db)
#     return  db.eat
