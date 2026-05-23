import time
import os
import random
import json
from dotenv import load_dotenv

load_dotenv()

def clear():
    if os.name == 'nt':
        os.system('cls')

# ANSI Color Codes for beautiful terminal visuals
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
LIGHT_BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
RED = "\033[91m"
GOLD = "\033[38;5;214m"

# Global data management
user_data = {}
current_user = None
current_inv = []  
current_secrets = {}  
current_money = 0  
current_charms = {} 

# CHANGED: Now utilizing a proper .json extension for universal compatibility
SAVE_FILE = "progress_data.json"

def log_inventory():
    save_progress()

def save_progress():
    """Saves progress into a clean, human-readable, beautifully indented JSON structure."""
    payload = {"users": user_data}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        # indent=4 makes the raw .json file incredibly organized and readable if opened manually
        json.dump(payload, f, indent=4, ensure_ascii=False)

def load_progress():
    """Loads the database. Also features automated migration protocols for old legacy files."""
    global user_data
    
    # Backward compatibility: If the old .txt log file exists, migrate its contents to the new JSON file automatically
    LEGACY_FILE = "inventory_log.txt"
    if os.path.exists(LEGACY_FILE) and not os.path.exists(SAVE_FILE):
        try:
            with open(LEGACY_FILE, "r", encoding="utf-8") as f:
                legacy_payload = json.load(f)
            user_data = legacy_payload.get("users", {})
            save_progress() # Write to new organized file format
            os.remove(LEGACY_FILE) # Remove old clutter file
            print(f"{GREEN}[SYSTEM] Successfully migrated legacy data format into '{SAVE_FILE}'!{RESET}")
        except Exception:
            pass

    if not os.path.exists(SAVE_FILE):
        return
        
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict) and "users" in payload:
            user_data = payload["users"]
        else:
            inv = payload.get("inventory", [])
            secrets_dict = payload.get("secrets", {})
            user_data = {"default": {"inventory": inv, "secrets": secrets_dict, "money": 200, "charms": {}}}
        
        # Keep everything normalized and properly schema-mapped inside memory arrays
        for u, data in user_data.items():
            if "money" not in data: data["money"] = 200
            if "charms" not in data: data["charms"] = {}
            if "inventory" not in data: data["inventory"] = []
            if "secrets" not in data: data["secrets"] = {}
            if "last_daily" not in data: data["last_daily"] = 0
    except Exception:
        print(f"{RED}Warning: failed to load progress data database. Initializing clean environment...{RESET}")

def show_inv():
    print(f"\n{BOLD}=== {CYAN}YOUR INVENTORY{RESET}{BOLD} ==={RESET}")
    if not current_inv:
        print(f"{GRAY}You have not opened any cases yet.{RESET}")
    else:
        counts = {}
        for item in current_inv:
            counts[item] = counts.get(item, 0) + 1
        for item, qty in counts.items():
            color = CYAN if "Netherite" in item else (PURPLE if "Epic" in item else (GOLD if "Developer" in item else RESET))
            if qty > 1:
                print(f"- {color}{item}{RESET} {GREEN}(x{qty}){RESET}")
            else:
                print(f"- {color}{item}{RESET}")

def show_money():
    print(f"You currently have: {YELLOW}{current_money}{RESET} coins.")

Case1 = ["Hat", "Chestplate", "Gloves", "Pants", "Boots"]
Case2 = ["Sword", "Shield", "Bow", "Axe", "Spear"]
Case3 = ["Potion of Healing", "Potion of Strength", "Potion of Speed", "Potion of Invisibility", "Potion of Fire Resistance"]
Case4 = ["Netherite Ingot", "Diamond", "Emerald", "Gold Ingot", "Iron Ingot"]
RareCase = [
    "--+--=Netherite Hat=--+--", 
    "--+--=Netherite Chestplate=--+--", 
    "--+--=Netherite Gloves=--+--", 
    "--+--=Netherite Pants=--+--", 
    "--+--=Netherite Boots=--+--", 
    "--+--=Netherite Sword=--+--", 
    "--+--=Netherite Shield=--+--", 
    "--+--=Netherite Bow=--+--", 
    "--+--=Netherite Axe=--+--", 
    "--+--=Netherite Spear=--+--" 
]
RareWeights = [10, 10, 10, 10, 10, 5, 5, 20, 2, 0.01]
RARE_DROP_CHANCE = 0.1  

EpicCase = [
    "--+--=?!@#--Epic Hat--?!@#=--+--", 
    "--+--=?!@#--Epic Chestplate--?!@#=--+--", 
    "--+--=?!@#--Epic Gloves--?!@#=--+--", 
    "--+--=?!@#--Epic Pants--?!@#=--+--", 
    "--+--=?!@#--Epic Boots--?!@#=--+--", 
    "--+--=?!@#--Epic Sword--?!@#=--+--", 
    "--+--=?!@#--Epic Shield--?!@#=--+--", 
    "--+--=?!@#--Epic Bow--?!@#=--+--", 
    "--+--=?!@#--Epic Axe--?!@#=--+--", 
    "--+--=?!@#--Epic Spear--?!@#=--+--" 
]
EpicWeights = [0.01, 0.01, 0.01, 0.01, 0.01, 0.001, 0.01, 0.01, 0.0001, 0.00001]
EPIC_DROP_CHANCE = 0.01  

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

secrets = [
    "Basic Runes", "Advanced Rune", "Legendary Rune", 
    "Mythic Rune", "Eternal Rune", "Ancient Rune", 
    "Divine Rune", "Cursed Rune", "Hacker Rune"
]
rune_weights = [650, 450, 50, 5, 1, 0.5, 0.1, 0.001, 0.000001]

SHOP_ITEMS = {
    "1": {"name": "Common Case Key", "cost": 30, "type": "case_key"},
    "2": {"name": "Rare Case Key", "cost": 150, "type": "case_key"},
    "3": {"name": "Epic Case Key", "cost": 1000, "type": "case_key"},
    "4": {"name": "Lucky Clover Charm (+5% Magic Luck)", "cost": 500, "type": "charm", "stat": "lucky_clover"},
    "5": {"name": "Golden Dice Charm (+15% Epic Luck)", "cost": 2500, "type": "charm", "stat": "golden_dice"}
}

def get_item_price(item):
    if item in Case1: return 50
    if item in Case2: return 40
    if item in Case3: return 20
    if item in Case4: return 30
    if item in RareCase:
        if "Netherite" in item: return 500
        return 200
    if item in EpicCase: return 50000
    if item in devCase: return 10000
    return 10

def get_secret_price(secret):
    prices = {
        "Basic Runes": 10, "Advanced Rune": 50, "Legendary Rune": 200,
        "Mythic Rune": 500, "Eternal Rune": 1000, "Ancient Rune": 2000,
        "Divine Rune": 5000, "Cursed Rune": 10000, "Hacker Rune": 100000,
    }
    return prices.get(secret, 25)

def sell_item():
    global current_money
    if not current_inv:
        print(f"{RED}You have nothing to sell.{RESET}")
        return
    print("\nWhich item would you like to sell?")
    show_inv()
    choice = input("Enter the exact name of the item: ").strip()
    if choice in current_inv:
        price = get_item_price(choice)
        current_inv.remove(choice)
        current_money += price
        user_data[current_user]["money"] = current_money
        save_progress()
        print(f"{GREEN}Sold {choice} for {price} coins. New balance: {current_money} coins.{RESET}")
    else:
        print(f"{RED}Item not found in your inventory.{RESET}")

def sell_all_items():
    global current_money
    if not current_inv:
        print(f"{RED}Your inventory is already empty!{RESET}")
        return
    confirm = input(f"{YELLOW}Are you absolutely sure you want to sell ALL items? (yes/no): {RESET}").strip().lower()
    if confirm == "yes":
        total_gain = 0
        for item in list(current_inv):
            total_gain += get_item_price(item)
            current_inv.remove(item)
        current_money += total_gain
        user_data[current_user]["money"] = current_money
        save_progress()
        print(f"{GREEN}Success! Sold everything for {total_gain} coins. Balance: {current_money}{RESET}")

def sell_secret():
    global current_money
    if not current_secrets:
        print(f"{RED}You have no secrets to sell.{RESET}")
        return
    print("\nWhich secret would you like to sell?")
    for rune, qty in current_secrets.items():
        print(f"- {PURPLE}{rune}{RESET} (x{qty})")
    choice = input("Enter the exact name of the secret: ").strip()
    if choice in current_secrets and current_secrets[choice] > 0:
        price = get_secret_price(choice)
        current_secrets[choice] -= 1
        if current_secrets[choice] == 0:
            del current_secrets[choice]
        current_money += price
        user_data[current_user]["money"] = current_money
        save_progress()
        print(f"{GREEN}Sold {choice} for {price} coins. New balance: {current_money} coins.{RESET}")
    else:
        print(f"{RED}Secret not found or you have none of that type.{RESET}")

def roll_animation(case_tier):
    print(f"{BOLD}{LIGHT_BLUE}[UNBOXING {case_tier}]{RESET} Spinning slots ", end="", flush=True)
    for _ in range(4):
        time.sleep(0.25)
        print("■ ", end="", flush=True)
    print("\n")

def open_random_case(silent=False):
    rare_mod = 0.05 if "lucky_clover" in current_charms else 0.0
    epic_mod = 0.02 if "golden_dice" in current_charms else 0.0

    epic_roll = EPIC_DROP_CHANCE + epic_mod
    rare_roll = RARE_DROP_CHANCE + rare_mod

    roll = random.random()
    if roll < epic_roll:
        if not silent: roll_animation("EPIC CASE")
        item = random.choices(EpicCase, weights=EpicWeights, k=1)[0]
        print(f"{PURPLE}✨ LEGENDARY! You pulled from the EPIC Case and received: {item}! ✨{RESET}")
    elif roll < (epic_roll + rare_roll):
        if not silent: roll_animation("RARE CASE")
        item = random.choices(RareCase, weights=RareWeights, k=1)[0]
        print(f"{CYAN}💎 Lucky you! You pulled from the Rare Case and received: {item}! 💎{RESET}")
    else:
        if not silent: roll_animation("STANDARD CASE")
        case_number = random.randint(1, 4)
        if case_number == 1:
            item = random.choice(Case1)
            if not silent: print(f"You opened Armor Case and received: {item}!")
        elif case_number == 2:
            item = random.choice(Case2)
            if not silent: print(f"You opened Weapon Case and received: {item}!")
        elif case_number == 3:
            item = random.choice(Case3)
            if not silent: print(f"You opened Potion Case and received: {item}!")
        else:
            item = random.choice(Case4)
            if not silent: print(f"You opened Ores Case and received: {item}!")
            
    current_inv.append(item)
    unlocked = random.choices(secrets, weights=rune_weights, k=1)[0]
    count = current_secrets.get(unlocked, 0) + 1
    current_secrets[unlocked] = count
    save_progress()
    if not silent:
        if count > 1:
            print(f"You also unlocked a rune: {YELLOW}{unlocked}{RESET}! (x{count})")
        else:
            print(f"You also unlocked a rune: {YELLOW}{unlocked}{RESET}!")

def set_user(username):
    global current_user, current_inv, current_secrets, current_money, current_charms
    current_user = username
    if username not in user_data:
        # Initializing structured data sets
        user_data[username] = {
            "money": 200, 
            "last_daily": 0,
            "charms": {}, 
            "inventory": [], 
            "secrets": {}
        }
        
    current_inv = user_data[username]["inventory"]
    current_secrets = user_data[username]["secrets"]
    current_money = user_data[username]["money"]
    current_charms = user_data[username]["charms"]

def select_user():
    name = input("Enter your username: ").strip()
    while not name:
        print(f"{RED}Username cannot be empty.{RESET}")
        name = input("Enter your username: ").strip()
    set_user(name)
    print(f"\n{GREEN}Welcome back, {name}! Let the RNG be with you.{RESET}")
    show_money()

def open_shop():
    global current_money
    while True:
        clear()
        print(f"\n{BOLD}{GOLD}======== 🏪 THE RNG GOLD MINE SHOP 🏪 ========{RESET}")
        print(f"Your Wallet: {YELLOW}{current_money}{RESET} Coins\n")
        for key, item in SHOP_ITEMS.items():
            print(f"[{key}] {item['name']} - Price: {YELLOW}{item['cost']}{RESET} Coins")
        print("[B] Go Back to Main Base Menu\n")
        
        choice = input("Select an item to purchase: ").strip().lower()
        if choice == 'b':
            break
        elif choice in SHOP_ITEMS:
            selected = SHOP_ITEMS[choice]
            if current_money >= selected['cost']:
                current_money -= selected['cost']
                user_data[current_user]["money"] = current_money
                
                if selected['type'] == 'charm':
                    current_charms[selected['stat']] = True
                    user_data[current_user]["charms"] = current_charms
                    print(f"\n{GREEN}⚡ Permanently activated {selected['name']}!{RESET}")
                else:
                    print(f"\n{GREEN}Bought {selected['name']}! Opening your paid item slot now...{RESET}")
                    open_random_case(silent=False)
                save_progress()
                input("\nPress Enter to continue...")
            else:
                print(f"{RED}Insufficient coins! Go flip some rolls.{RESET}")
                time.sleep(1.5)
        else:
            print(f"{RED}Invalid Choice.{RESET}")
            time.sleep(1)

def show_leaderboard():
    print(f"\n{BOLD}{GOLD}🏆 GLOBAL SERVER LEADERBOARDS 🏆{RESET}")
    if not user_data:
        print("No players logged yet.")
        return
    sorted_users = sorted(user_data.items(), key=lambda x: x[1].get("money", 0), reverse=True)
    for idx, (user, data) in enumerate(sorted_users[:5], 1):
        print(f"Rank #{idx}: {BOLD}{user}{RESET} - {YELLOW}{data.get('money', 0)}{RESET} Coins")

def play_coin_flip():
    global current_money
    print(f"\n{BOLD}{YELLOW}🎲 COIN FLIP GAMBLE MODE 🎲{RESET}")
    try:
        bet = int(input(f"Enter amount to bet (You have {current_money}): "))
        if bet <= 0 or bet > current_money:
            print(f"{RED}Invalid bet constraint.{RESET}")
            return
    except ValueError:
        print(f"{RED}Please enter numbers only.{RESET}")
        return

    side = input("Pick Sides! (H for Heads / T for Tails): ").strip().upper()
    if side not in ['H', 'T']:
        print(f"{RED}Invalid selection.{RESET}")
        return

    print("Flipping coin...")
    time.sleep(1)
    outcome = random.choice(['H', 'T'])
    side_str = "Heads" if outcome == 'H' else "Tails"
    
    if side == outcome:
        current_money += bet
        print(f"{GREEN}🎉 You Won! The coin landed on {side_str}! Earned +{bet} coins.{RESET}")
    else:
        current_money -= bet
        print(f"{RED}💥 Oof! The coin landed on {side_str}. You lost -{bet} coins.{RESET}")
        
    user_data[current_user]["money"] = current_money
    save_progress()

def claim_daily():
    global current_money
    now = time.time()
    last_claimed = user_data[current_user].get("last_daily", 0)
    
    if now - last_claimed >= 86400:
        reward = random.randint(150, 400)
        current_money += reward
        user_data[current_user]["money"] = current_money
        user_data[current_user]["last_daily"] = now
        save_progress()
        print(f"{GREEN}🎁 Daily reward claimed! You scooped up {YELLOW}{reward}{RESET} coins!{RESET}")
    else:
        remaining = int(86400 - (now - last_claimed))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        print(f"{RED}Cooldown Active! Come back in {hours}h {minutes}m to claim again.{RESET}")

def trash_item():
    if not current_inv:
        print(f"{RED}Your inventory is completely clean.{RESET}")
        return
    print("\n--- TRASH RECYCLING DESTRUCT ---")
    show_inv()
    target = input("Enter exact name of item to delete forever: ").strip()
    if target in current_inv:
        current_inv.remove(target)
        save_progress()
        print(f"{RED}Discarded {target} successfully.{RESET}")
    else:
        print(f"{RED}Could not find item target.{RESET}")

def gift_item():
    if not current_inv:
        print(f"{RED}Nothing to gift!{RESET}")
        return
    target_player = input("Enter target username to transfer item to: ").strip()
    if target_player not in user_data:
        print(f"{RED}Player database record not found under that name.{RESET}")
        return
    if target_player == current_user:
        print(f"{RED}You can't trade with yourself!{RESET}")
        return
        
    print("\nSelect item to gift:")
    show_inv()
    item_choice = input("Enter exact item name: ").strip()
    if item_choice in current_inv:
        current_inv.remove(item_choice)
        user_data[target_player]["inventory"].append(item_choice)
        save_progress()
        print(f"{GREEN}Successfully gifted 🎁 {item_choice} to user: {target_player}!{RESET}")
    else:
        print(f"{RED}Item matching choice not found inside inventory system.{RESET}")

# Initialize load metrics
load_progress()
select_user()

while True:
    print(f"""
{BOLD}{CYAN}============= 🎲 MAIN RNG SYSTEM ENGINE ============= {RESET}
 {BOLD}Active Player:{RESET} {GREEN}{current_user}{RESET}    |  {BOLD}Coins Balance:{RESET} {YELLOW}{current_money}{RESET}

 [1]   Roll Case Slot      [8]   Open Storage Folder Location
 [afk] Auto-Roll Simulation  [shop] Browse Coin Merchant Store
 [2]   Save Progress & Exit  [top]  Global Balance Rankings
 [3]   Look At Items Inv    [flip] Double or Nothing Coin Gamble
 [4]   Look At Runes Log    [daily] Claim Free 24h Coin Drop
 [5]   Sell Item Unit       [trash] Wipe Item From Inventory
 [6]   Sell Rune Unit       [gift] Send Item To Another User Profile
 [7]   Query Balance Coins  [sellall] Instant Cash Cleanout Inventory
 ---------------------------------------------------
 {GRAY}(Type 'dev' to activate administrator dashboard context overrides){RESET}
    """)
    
    action = input("Execute action command string: ").strip().lower()

    if action == "1":
        open_random_case()
    elif action == "afk":
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
                    verify = input("Type 'y' if you are sure you want no delay: ").strip().lower()
                    if verify != 'y': delay = 0.5
            except ValueError:
                delay = 0.5
            print(f"\nRolling {count} cases silently to prevent buffer overloads...")
            for i in range(count):
                open_random_case(silent=True)
                if delay > 0: time.sleep(delay)
            print(f"{GREEN}AFK rolling complete. Progress written securely.{RESET}")
    elif action == "2":
        save_progress()
        print("Goodbye!")
        input("Press Enter to exit...")
        break
    elif action == "3":
        show_inv()
    elif action == "4":
        print(f"\n{BOLD}Secrets found:{RESET}")
        if not current_secrets:
            print("- <none>")
        else:
            for rune, qty in current_secrets.items():
                print(f"- {PURPLE}{rune}{RESET} (x{qty})" if qty > 1 else f"- {PURPLE}{rune}{RESET}")
    elif action == "5":
        sell_item()
    elif action == "6":
        sell_secret()
    elif action == "7":
        show_money()
    elif action == "8":
        folder = os.path.abspath(os.path.dirname(SAVE_FILE) or ".")
        try:
            os.startfile(folder)
            print(f"Opened folder: {folder}")
        except Exception as e:
            print(f"Unable to open folder automatically: {e}")
    elif action == "shop":
        open_shop()
    elif action == "top":
        show_leaderboard()
    elif action == "flip":
        play_coin_flip()
    elif action == "daily":
        claim_daily()
    elif action == "trash":
        trash_item()
    elif action == "gift":
        gift_item()
    elif action == "sellall":
        sell_all_items()
    elif action == "dev":
        developer_password = os.getenv("DEV_PASS")
        pwd = input("Enter developer password: ")
        if pwd != developer_password:
            print("Incorrect password. Developer mode denied.")
        else:
            print("Developer mode: Activated!")
            actiondev = input("Enter developer action (1:add item, 2:remove item, 3:show inventory, 4:dev case, 5:add secret, 6:modify money, 7:epic case): ")
            if actiondev == "1":
                new_item = input("Enter the name of the item to add: ")
                current_inv.append(new_item)
                log_inventory()
                print(f"Added {new_item} to inventory.")
            elif actiondev == "2":
                item_to_remove = input("Enter the name of the item to remove: ")
                if item_to_remove in current_inv:
                    current_inv.remove(item_to_remove)
                    log_inventory()
                    print(f"Removed {item_to_remove} from inventory.")
            elif actiondev == "5":
                secret = input("Enter the name of the secret rune to add: ")
                current_secrets[secret] = current_secrets.get(secret, 0) + 1
                save_progress()
            elif actiondev == "6":
                try:
                    amt = int(input("Enter amount to set money to: "))
                except ValueError:
                    pass
                else:
                    current_money = amt
                    user_data[current_user]["money"] = current_money
                    save_progress()
    else:
        print(f"{RED}Invalid input command choice, please check menu layouts and try again.{RESET}")

    input(f"\n{GRAY}Press Enter to return to system deck...{RESET}")
    clear()