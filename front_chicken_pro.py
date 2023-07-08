from data__mine import *
import math
import requests
FILENMAE = "chicken.json"


any_user = input("Your username:\n")
any_password = input("\nEnter your password\n")
user = User(username=any_user, password=any_password)
Methods = {
    1: "eat",
    2: "buy",
    3: "see purchase history",
    4: "see eat history",
    5: "payy of bitch",
    6: "exit"
}
Users = {
    1: "user1",
    2: "user2",
    3: "user3",
    4: "user4",
    5: "user5",
    6: "exit"

}

db = read_database()
if not db:
    db = Database(buy=[], eat=[], debt=[])
history = user_buy_history(user, db.buy)
if history:
    _ago = None
else:
    _ago = round((datetime.utcnow() - history[-1].date).total_seconds()/3600)

chicken, rice = total(db)
print(f"hello , we have {chicken} gr chicken and {rice} gr rice")
for method in Methods:
    print(f"{method} - {Methods[method]}")
any_choose = input("Waiting for your input:...\n")
any_username = []
eating_rice = []
eating_chicken = []
username = ""
user_number = 0
if any_choose == "1":
    while username != Users[6]:
        if user_number != 0:
            del Users[user_number]
        for user in Users:
            print(f"{user} - {Users[user]}")
        user_number = int(input("Who is eating?:...\n"))
        username = Users[user_number]

        if username != Users[6]:

            any_username.append(username)

            chicken_amount = float(
                input("How much chicken do you want to eat?:\n"))
            rice_amount = float(input("How much rice do you want to eat?:\n"))
            eating_rice.append(rice_amount)
            eating_chicken.append(chicken_amount)

    sum_rice = sum(eating_rice)
    sum_chicken = sum(eating_chicken)
    eat = Eat(


        username=any_username,
        eat_chicken=eating_chicken,
        eat_rice=eating_rice,
        total_chicken=sum_chicken,
        total_rice=sum_rice

    )

    try:
        if chicken >= sum_chicken and rice >= sum_rice:
            db.eat.append(eat)
            chicken_debt, id_chicken, total_eat_chicken = algorithm_of_chicken(
                db)
            rice_debt, id_rice, total_eat_rice = algorithm_of_rice(db)

            db = debt_printer(db, chicken_debt, id_chicken, True)
            db = debt_printer(db, rice_debt, id_rice, False)
            db = eaten_chicken_printer(db, id_chicken, total_eat_chicken)
            db = eaten_rice_printer(db, id_rice, total_eat_rice)
            write_database(db)
            print("\nEnjoy your meal\n")

        else:
            raise Exception("Not enough chickens or rice")
    except Exception as e:
        raise


if any_choose == "2":

    try:
        if _ago is None or _ago >= 3:
            buying_rice = float(input("How much rice do you want to buy?:\n"))
            if buying_rice != 0.0:
                price_rice = float(input("how much did you get the rice\n"))
            else:
                price_rice = 0
                buying_rice = 1
            buying_chicken = float(
                input("How much chicken do you want to buy?:\n"))
            if buying_chicken != 0.0:
                price_chicken = float(
                    input("how much did you get the chicken\n"))
            else:
                price_chicken = 0
                buying_chicken = 1
            buy = Buy(
                username=any_user,
                buy_rice=(0 if buying_rice == 1 else buying_rice),
                buy_chicken=(0 if buying_chicken == 1 else buying_chicken),
                eaten_chicken=0.0,
                eaten_rice=0.0,
                per_chicken=price_chicken / buying_chicken,
                per_rice=price_rice / buying_rice,
            )

            db.buy.append(buy)
            write_database(db)
        else:
            raise Exception("you already shopped in 3 hours")
    except Exception as e:
        print("Error:", str(e))

if any_choose == "3":

    if _ago == 0:
        print((datetime.utcnow() - history[-1].date).total_seconds()/60)
        print(
            f"your last purchase {history[-1].buy_chicken} gr  chicken {int((datetime.utcnow() - history[-1].date).total_seconds()/60)} minutes ago")
    if _ago != None and _ago != 0:

        print(
            f"your last purchas {history[-1].buy_chicken} gr  chicken {_ago} hour ago")
    if _ago == None:
        print("you have not made a recent purchase\n")

if any_choose == "4":

    eat_ago = round(
        (datetime.utcnow() - db.eat[-1].date).total_seconds()/3600)
    if eat_ago == 0:
        print(f"{db.eat[-1].total_chicken} gr chicken and {db.eat[-1].total_rice} gr rice {int((datetime.utcnow() - db.eat[-1].date).total_seconds()/60)} minute ago by {db.eat[-1].username} ")
    else:
        print(
            f"{db.eat[-1].total_chicken} gr chicken  and {db.eat[-1].total_rice} gr rice {eat_ago} hour ago by {db.eat[-1].username} ")

    contunie = input("would you like to see the details\n"
                     "1 - Yes\n"
                     "2 - NO\n")
    if contunie == "1":
        print("\nchicken quantities : \n")
        for item in range(len(db.eat[-1].username)):
            print(
                f"{db.eat[-1].username[item] } -> {db.eat[-1].eat_chicken[item]} gr chicken ")
        print("\nrice quantities : \n")
        for item in range(len(db.eat[-1].username)):
            print(
                f"{db.eat[-1].username[item] } -> {db.eat[-1].eat_rice[item]} gr rice")
if any_choose == "5":
    sum_debts_dict = sum_debts(db)
    buyer_list = []
    are_you_sure = ""
    for user in Users:
        key = f"{Users[user]}-{any_user}"
        if key in sum_debts_dict and sum_debts_dict[key] != 0:

            from_currency = "TRY"

            to_currency = "USD"

            amount = sum_debts_dict[key]

            response = requests.get(
                f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

            print(
                f"buyer -> {Users[user]}- creditor ->{any_user} = {sum_debts_dict[key]} {from_currency} -> {response.json()['rates'][to_currency]} {to_currency} ")

            buyer_list.append(Users[user])
    contunie = input("would you like to pay\n"
                     "1 - Yes with TRY\n"
                     "2 - Yes with USD\n"
                     "3 - NO\n")
    if contunie == "1" or contunie == "2":
        i = 0
        for buyer in buyer_list:
            print(f"{i}-{buyer}")
            i += 1

    if contunie == "3":
        print("are you a pool 🤨🤨🤨")
        exit(0)
    buyer_choose = input("Who do you want to repay your debt to?\n")
    key_buyer = f"{buyer_list[int(buyer_choose)]}-{any_user}"
    if contunie == "1":
        are_you_sure = input(f"Your debt is {sum_debts_dict[key_buyer] } TRY\n"

                             "1 - Pay all\n"
                             "2 - pay as you want\n"
                             "3 - Cancel\n")
    if contunie == "2":
        from_currency = "TRY"

        to_currency = "USD"

        amount = sum_debts_dict[key_buyer]

        response = requests.get(
            f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

        are_you_sure = input(f"Your debt is {response.json()['rates'][to_currency]} USD \n"

                             "1 - Pay all\n"
                             "2 - pay as you want\n"
                             "3 - Cancel\n")

    if are_you_sure == "1":
        write_database(pay_off(db, any_user, buyer_list[int(
            buyer_choose)], sum_debts_dict[key_buyer]))
        print("🫴🫴🫴🫴")

    if are_you_sure == "2" and contunie == "2":
        from_currency = "USD"

        to_currency = "TRY"

        amount = input("how much do you want to pay?\n")

        response = requests.get(
            f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

        write_database(pay_off(db, any_user, buyer_list[int(
            buyer_choose)], float(response.json()['rates'][to_currency])))
        print("🫴🫴🫴🫴")
    if are_you_sure == "2" and contunie == "1":
        per_debt = input("how much do you want to pay?\n")
        write_database(pay_off(db, any_user, buyer_list[int(
            buyer_choose)], float(per_debt)))
        print("🫴🫴🫴🫴")
    if are_you_sure == "3":
        print("ne dedi ne dedi ✋✋✋")
