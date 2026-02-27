import time
import os
import random

def clear():
    if os.name == 'nt':
        os.system('cls')

import json

# mapping of username to their saved data (inventory, secrets and money)
user_data = {}
current_user = None
current_inv = []  # will reference user_data[current_user]["inventory"]
current_secrets = {}  # will reference user_data[current_user]["secrets"]
current_money = 0  # will reference user_data[current_user]["money"]

# persistent storage helpers
SAVE_FILE = "inventory_log.txt"

# compatibility wrapper for existing calls
# original version wrote a plain text file; we now simply persist JSON

def log_inventory():
    """Legacy name retained for backward compatibility.
    It simply saves the complete progress to disk.
    """
    save_progress()

def save_progress():
    """Persist the entire user_data mapping to disk.

    The file format is now {
        "users": { username: {"inventory": [...], "secrets": {...}}, ... }
    }

    Backwards compatibility is handled during load; old files will be
    converted to a single "default" user.
    """
    payload = {"users": user_data}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def load_progress():
    """Load the saved data from disk into user_data.

    If the file contains the old single-inventory format, convert it to a
    "default" user so existing progress is not lost.
    """
    global user_data
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict) and "users" in payload:
            user_data = payload["users"]
        else:
            # backward compatibility: convert old format to new structure
            inv = payload.get("inventory", [])
            secrets = payload.get("secrets", {})
            # old saves never had money, give default starter amount
            user_data = {"default": {"inventory": inv, "secrets": secrets, "money": 200}}
        # ensure every user entry has a money field
        for u, data in user_data.items():
            if "money" not in data:
                data["money"] = 200
    except Exception:
        print("Warning: failed to load progress, starting fresh.")


def show_inv():
    print("Your inventory contains:")
    if not current_inv:
        print("You have not opened any cases yet.")
    else:
        # count duplicates so we can display quantities
        counts = {}
        for item in current_inv:
            counts[item] = counts.get(item, 0) + 1
        for item, qty in counts.items():
            if qty > 1:
                print(f"- {item}(x{qty})")
            else:
                print(f"- {item}")

def show_money():
    """Display the current money balance."""
    print(f"You currently have: {current_money} coins.")


def get_item_price(item):
    """Return the sale price for an item based on its type/rarity."""
    # basic pricing rules; can be tuned later
    if item in Case1:
        return 50
    if item in Case2:
        return 40
    if item in Case3:
        return 20
    if item in Case4:
        return 30
    if item in RareCase:
        # rare case items are more valuable; if they contain Netherite treat higher
        if "Netherite" in item:
            return 500
        return 200
    if item in EpicCase:
        # epic case items are extremely valuable
        return 50000
    if item in devCase:
        return 10000
    # fallback for unknown items
    return 10


def get_secret_price(secret):
    """Return sale price for a secret rune based on its name."""
    prices = {
        "Basic Runes": 10,
        "Advanced Rune": 50,
        "Legendary Rune": 200,
        "Mythic Rune": 500,
        "Eternal Rune": 1000,
        "Ancient Rune": 2000,
        "Divine Rune": 5000,
        "Cursed Rune": 10000,
        "Hacker Rune": 100000,
    }
    return prices.get(secret, 25)


def sell_item():
    """Prompt the user to sell an item from inventory."""
    global current_money
    if not current_inv:
        print("You have nothing to sell.")
        return
    print("Which item would you like to sell?")
    show_inv()
    choice = input("Enter the exact name of the item: ").strip()
    if choice in current_inv:
        price = get_item_price(choice)
        current_inv.remove(choice)
        current_money += price
        user_data[current_user]["money"] = current_money
        save_progress()
        print(f"Sold {choice} for {price} coins. New balance: {current_money} coins.")
    else:
        print("Item not found in your inventory.")


def sell_secret():
    """Prompt the user to sell one unit of a secret rune."""
    global current_money
    if not current_secrets:
        print("You have no secrets to sell.")
        return
    print("Which secret would you like to sell?")
    for rune, qty in current_secrets.items():
        print(f"- {rune} (x{qty})")
    choice = input("Enter the exact name of the secret: ").strip()
    if choice in current_secrets and current_secrets[choice] > 0:
        price = get_secret_price(choice)
        current_secrets[choice] -= 1
        if current_secrets[choice] == 0:
            del current_secrets[choice]
        current_money += price
        user_data[current_user]["money"] = current_money
        save_progress()
        print(f"Sold {choice} for {price} coins. New balance: {current_money} coins.")
    else:
        print("Secret not found or you have none of that type.")

Case1 = ["Hat", "Chestplate", "Gloves", "Pants", "Boots"]
Case2 = ["Sword", "Shield", "Bow", "Axe", "Spear"]
Case3 = ["Potion of Healing", "Potion of Strength", "Potion of Speed", "Potion of Invisibility", "Potion of Fire Resistance"]
Case4 = ["Netherite Ingot", "Diamond", "Emerald", "Gold Ingot", "Iron Ingot"]
RareCase = [
    "--+--=Netherite Hat=--+--", # 10% relative weight
    "--+--=Netherite Chestplate=--+--", # 10% relative weight
    "--+--=Netherite Gloves=--+--", # 10% relative weight
    "--+--=Netherite Pants=--+--", # 10% relative weight
    "--+--=Netherite Boots=--+--", # 10% relative weight
    "--+--=Netherite Sword=--+--", # 5% relative weight
    "--+--=Netherite Shield=--+--", # 5% relative weight
    "--+--=Netherite Bow=--+--", # 20% relative weight
    "--+--=Netherite Axe=--+--", # 2% relative weight
    "--+--=Netherite Spear=--+--" # 0.01% relative weight
]
RareWeights = [10, 10, 10, 10, 10, 5, 5, 20, 2, 0.01]
RARE_DROP_CHANCE = 0.1  # 10% by default

EpicCase = [
    "--+--=?!@#--Epic Hat--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Chestplate--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Gloves--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Pants--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Boots--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Sword--?!@#=--+--", # 0.001%
    "--+--=?!@#--Epic Shield--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Bow--?!@#=--+--", # 0.01%
    "--+--=?!@#--Epic Axe--?!@#=--+--", # 0.0001%
    "--+--=?!@#--Epic Spear--?!@#=--+--" # 0.00001%
]
EpicWeights = [0.01, 0.01, 0.01, 0.01, 0.01, 0.001, 0.01, 0.01, 0.0001, 0.00001]
EPIC_DROP_CHANCE = 0.01  # 1% by default

devCase = [
    "--+--=?!@#--Developer Hat--?!@#=--+--",
    "--+--=?!@#--Developer Chestplate--?!@#=--+--",
    "--+--=?!@#--Developer Gloves--?!@#=--+--",
    "--+--=?!@#--Developer Pants--?!@#=--+--",
    "--+--=?!@#--Developer Boots--?!@#=--+--",
    "--+--=?!@#--Developer Sword--?!@#=--+--",
    "--+--=?!@#--Developer Shield--?!@#=--+--",
    "--+--=?!@#--Developer Bow--?!@#=--+--",
    "--+--=?!@#--Developer Axe--?!@#=--+--",
    "--+--=?!@#--Developer Spear--?!@#=--+--"
]

# list of possible secrets (runes)
secrets = [
    "Basic Runes", # 65% chance to get
    "Advanced Rune", # 45% chance to get
    "Legendary Rune",  # 5% chance to get
    "Mythic Rune", # 0.5% chance to get
    "Eternal Rune", # 0.1% chance to get
    "Ancient Rune", # 0.05% chance to get
    "Divine Rune", # 0.01% chance to get
    "Cursed Rune", # 0.0001% chance to get
    "Hacker Rune" # 0.0000001% chance to get
    ]

# load previous progress, if any
load_progress()

# ask who is playing so we keep inventories separate

def set_user(username):
    """Switch to (or create) the named user.

    After calling this the globals `current_inv` and `current_secrets` will
    refer to that user's data structures so the rest of the code can remain
    mostly unchanged.
    """
    global current_user, current_inv, current_secrets
    current_user = username
    if username not in user_data:
        # initialize new account with starter money
        user_data[username] = {"inventory": [], "secrets": {}, "money": 200}
    # ensure older profiles have a money field
    if "money" not in user_data[username]:
        user_data[username]["money"] = 200
    current_inv = user_data[username]["inventory"]
    current_secrets = user_data[username]["secrets"]
    global current_money
    current_money = user_data[username]["money"]

def select_user():
    name = input("Enter your username: ").strip()
    while not name:
        print("Username cannot be empty.")
        name = input("Enter your username: ").strip()
    set_user(name)
    print(f"Welcome, {name}!")
    show_money()

select_user()

# helper to open a single random case and handle inventory/secrets

def open_random_case():
    # choose epic, rare, or common
    if random.random() < EPIC_DROP_CHANCE:
        item = random.choices(EpicCase, weights=EpicWeights, k=1)[0]
        print(f"LEGENDARY! You pulled from the EPIC Case and received: {item}!")
    elif random.random() < RARE_DROP_CHANCE:
        item = random.choices(RareCase, weights=RareWeights, k=1)[0]
        print(f"Lucky you! You pulled from the Rare Case and received: {item}!")
    else:
        case_number = random.randint(1, 4)
        if case_number == 1:
            item = random.choice(Case1)
            print(f"You opened Armor Case and received: {item}!")
        elif case_number == 2:
            item = random.choice(Case2)
            print(f"You opened Weapon Case and received: {item}!")
        elif case_number == 3:
            item = random.choice(Case3)
            print(f"You opened Potion Case and received: {item}!")
        else:
            item = random.choice(Case4)
            print(f"You opened Ores Case and received: {item}!")
    current_inv.append(item)
    # unlock rune
    weights = [65, 45, 5, 0.5, 0.1, 0.05, 0.01, 0.0001, 0.0000001]
    unlocked = random.choices(secrets, weights=weights, k=1)[0]
    count = current_secrets.get(unlocked, 0) + 1
    current_secrets[unlocked] = count
    save_progress()
    if count > 1:
        print(f"You also unlocked a rune: {unlocked}! (x{count})")
    else:
        print(f"You also unlocked a rune: {unlocked}!")

while True:
    action = input(
        "Please enter an action (type '1' to open a case, 'afk' to auto-roll, '2' to quit, '3' to view your inventory, "
        "'4' to see all secrets you have unlocked, '5' to sell an item, '6' to sell a secret, '7' to view your money, or 'dev' for developer mode): "
    )

    # handle each valid command explicitly and loop back automatically
    if action == "1":
        open_random_case()

    elif action == "afk":
        # automated rolling for a number of cases with optional delay
        try:
            count = int(input("How many cases should I open while you're AFK? "))
            if count <= 0:
                print("Please enter a positive number of cases.")
                continue
        except ValueError:
            print("That wasn't a valid number.")
            continue
        else:
            try:
                delay = float(input("Delay between each roll in seconds (e.g. 0.5): "))
                if delay == 0:
                    verify = input(
                        "Type 'y' if you are sure you want no delay between rolls "
                        "(this may cause issues on slower machines) and 'n' to cancel: "
                    ).strip().lower()
                    if verify == 'n':
                        print("Exiting AFK mode.")
                        continue
                    elif verify != 'y':
                        # anything else is unexpected – fall back to safe default
                        print("Unrecognized response; using default delay of 0.5s.")
                        delay = 0.5
            except ValueError:
                delay = 0.5
            print(f"Rolling {count} cases automatically...")
            for i in range(count):
                open_random_case()
                time.sleep(delay)
            print("AFK rolling complete.")

    elif action == "2":
        # make sure we write the latest state before quitting
        save_progress()
        print("Goodbye!")
        input("Press Enter to exit...")
        break

    elif action == "3":
        show_inv()

    elif action == "4":
        print("Secrets found:")
        if not current_secrets:
            print("- <none>")
        else:
            for rune, qty in current_secrets.items():
                if qty > 1:
                    print(f"- {rune} (x{qty})")
                else:
                    print(f"- {rune}")

    elif action == "5":
        sell_item()

    elif action == "6":
        sell_secret()

    elif action == "7":
        show_money()

    elif action == "8":
        # open the directory containing the save file so user can inspect it
        folder = os.path.abspath(os.path.dirname(SAVE_FILE) or ".")
        try:
            # 'os.startfile' works on Windows to open in explorer
            os.startfile(folder)
            print(f"Opened folder: {folder}")
        except Exception as e:
            print(f"Unable to open folder automatically: {e}")
        

    elif action == "dev":
        developer_password = "Kane_rock17yt"
        pwd = input("Enter developer password: ")
        if pwd != developer_password:
            print("Incorrect password. Developer mode denied.")
        else:
            print("Developer mode: Activated!")
            actiondev = input(
                "Enter developer action (1:add item, 2:remove item, 3:show inventory, 4:dev case, 5:add secret, 6:modify money, 7:epic case): "
            )
            if actiondev == "1":
                new_item = input("Enter the name of the item to add: ")
                if new_item not in Case1 + Case2 + Case3 + Case4 + RareCase + EpicCase + devCase:
                    print("Item not found!")
                else:
                    current_inv.append(new_item)
                    log_inventory()
                    print(f"Added {new_item} to inventory.")
            elif actiondev == "2":
                item_to_remove = input("Enter the name of the item to remove: ")
                if item_to_remove in current_inv:
                    current_inv.remove(item_to_remove)
                    log_inventory()
                    print(f"Removed {item_to_remove} from inventory.")
                else:
                    print(f"{item_to_remove} not found in inventory.")
            elif actiondev == "3":
                show_inv()
            elif actiondev == "4":
                print("Developer Case contains:")
                for item in devCase:
                    print(f"- {item}")
                if input("Add any to inventory? (yes/no): ").strip().lower() == "yes":
                    choice = input("Enter the exact item string to add (copy from above): ").strip()
                    if choice in devCase:
                        current_inv.append(choice)
                        log_inventory()
                        print(f"Added {choice} to inventory.")
                    else:
                        print("Item not found in Developer Case.")
            elif actiondev == "5":
                secret = input("Enter the name of the secret rune to add: ")
                current_secrets[secret] = current_secrets.get(secret, 0) + 1
                save_progress()
                print(f"Added secret rune: {secret}!")
            elif actiondev == "6":
                try:
                    amt = int(input("Enter amount to set money to: "))
                except ValueError:
                    print("Invalid number.")
                else:
                    current_money = amt
                    user_data[current_user]["money"] = current_money
                    save_progress()
                    print(f"Money balance set to {current_money} coins.")
            elif actiondev == "7":
                print("Epic Case contains:")
                for item in EpicCase:
                    print(f"- {item}")
                if input("Add any to inventory? (yes/no): ").strip().lower() == "yes":
                    choice = input("Enter the exact item string to add (copy from above): ").strip()
                    if choice in EpicCase:
                        current_inv.append(choice)
                        log_inventory()
                        print(f"Added {choice} to inventory.")
                    else:
                        print("Item not found in Epic Case.")

    else:
        print("Invalid input, please try again.")

    # pause before next iteration
    input("Press Enter to continue...")
    clear()
