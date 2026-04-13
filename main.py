"""
⚓ SAILOR COINS — Discord Economy Bot
=====================================
Required env vars:
  DISCORD_TOKEN  — your bot token
  GUILD_ID       — your server ID (for faster slash command sync)

Install deps:
  pip install -r requirements.txt
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import random
import asyncio
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN    = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))

# ─── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Colors ───────────────────────────────────────────────────────────────────

GOLD   = 0xFFD700
RED    = 0xFF4444
GREEN  = 0x44FF88
BLUE   = 0x4488FF
PURPLE = 0xAA44FF

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect("sailor.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id      INTEGER PRIMARY KEY,
        wallet       INTEGER DEFAULT 0,
        bank         INTEGER DEFAULT 0,
        bank_limit   INTEGER DEFAULT 5000,
        total_earned INTEGER DEFAULT 0,
        level        INTEGER DEFAULT 1,
        xp           INTEGER DEFAULT 0,
        streak       INTEGER DEFAULT 0,
        last_daily   REAL    DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cooldowns (
        user_id   INTEGER,
        command   TEXT,
        last_used REAL,
        PRIMARY KEY (user_id, command)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        user_id   INTEGER,
        item_name TEXT,
        quantity  INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, item_name)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS shop (
        item_name   TEXT PRIMARY KEY,
        price       INTEGER,
        description TEXT,
        item_type   TEXT,
        value       TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key   TEXT PRIMARY KEY,
        value TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS banned_users (
        user_id INTEGER PRIMARY KEY
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS multipliers (
        user_id      INTEGER,
        mult_type    TEXT,
        value        REAL,
        expires_at   REAL,
        PRIMARY KEY (user_id, mult_type)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER,
        amount    INTEGER,
        reason    TEXT,
        timestamp REAL
    )""")

    # Default shop items
    defaults = [
        ("2x Coin Boost",       5000,  "Double coin earnings for 1 hour",              "multiplier", "coins:2.0:3600"),
        ("2x Luck Charm",       3000,  "Double luck in fish/mine/hunt for 1 hour",      "multiplier", "luck:2.0:3600"),
        ("3x Coin Boost",       12000, "Triple coin earnings for 30 minutes",           "multiplier", "coins:3.0:1800"),
        ("Fishing Rod+",        2000,  "Catch bigger fish — 1.5x fishing yield",        "upgrade",    "fishing:1.5"),
        ("Diamond Pickaxe",     2000,  "Mine richer veins — 1.5x mining yield",         "upgrade",    "mining:1.5"),
        ("Hunter's Bow",        2000,  "Hunt bigger prey — 1.5x hunting yield",         "upgrade",    "hunting:1.5"),
        ("Bank Expansion",      10000, "Increase bank limit by +5000",                  "bank",       "5000"),
        ("VIP Role",            25000, "Receive the VIP role in the server",            "role",       "VIP"),
        ("Lucky Charm",         1500,  "Reduces your robbery chance for 24 hours",      "protection", "rob:0.5:86400"),
        ("Shield",              500,   "One-time full protection from robbery",         "protection", "rob_shield:1"),
        ("Escape Card",         3000,  "Escape from being caught during a crime once",  "protection", "crime_escape:1"),
        ("Daily Boost",         2000,  "2x daily reward for the next 3 days",           "multiplier", "daily:2.0:259200"),
    ]
    for item in defaults:
        c.execute("INSERT OR IGNORE INTO shop VALUES (?,?,?,?,?)", item)

    # Default config
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_interval_minutes','30')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_min','100')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_max','500')")

    conn.commit()
    conn.close()

# ─── DB helpers ───────────────────────────────────────────────────────────────

def db():
    return sqlite3.connect("sailor.db")

def ensure_user(user_id: int):
    conn = db()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    ensure_user(user_id)
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row

def add_wallet(user_id: int, amount: int):
    ensure_user(user_id)
    conn = db()
    conn.execute("UPDATE users SET wallet=wallet+? WHERE user_id=?", (amount, user_id))
    if amount > 0:
        conn.execute("UPDATE users SET total_earned=total_earned+? WHERE user_id=?", (amount, user_id))
        conn.execute("INSERT INTO transactions(user_id,amount,reason,timestamp) VALUES(?,?,?,?)",
                     (user_id, amount, "earn", time.time()))
    conn.commit()
    conn.close()

def set_wallet(user_id: int, amount: int):
    ensure_user(user_id)
    conn = db()
    conn.execute("UPDATE users SET wallet=? WHERE user_id=?", (max(0, amount), user_id))
    conn.commit()
    conn.close()

def add_bank(user_id: int, amount: int):
    conn = db()
    conn.execute("UPDATE users SET bank=bank+? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def is_banned(user_id: int) -> bool:
    conn = db()
    r = conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return r is not None

def get_cfg(key: str, default=None):
    conn = db()
    r = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return r[0] if r else default

def set_cfg(key: str, value: str):
    conn = db()
    conn.execute("INSERT OR REPLACE INTO config VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()

def get_mult(user_id: int, mult_type: str) -> float:
    now = time.time()
    conn = db()
    r = conn.execute(
        "SELECT value FROM multipliers WHERE user_id=? AND mult_type=? AND expires_at>?",
        (user_id, mult_type, now)
    ).fetchone()
    conn.execute("DELETE FROM multipliers WHERE expires_at<=?", (now,))
    conn.commit()
    conn.close()
    return r[0] if r else 1.0

def set_mult(user_id: int, mult_type: str, value: float, duration_secs: int):
    conn = db()
    conn.execute(
        "INSERT OR REPLACE INTO multipliers VALUES(?,?,?,?)",
        (user_id, mult_type, value, time.time() + duration_secs)
    )
    conn.commit()
    conn.close()

def get_cd(user_id: int, cmd: str) -> float:
    conn = db()
    r = conn.execute("SELECT last_used FROM cooldowns WHERE user_id=? AND command=?", (user_id, cmd)).fetchone()
    conn.close()
    return r[0] if r else 0.0

def set_cd(user_id: int, cmd: str):
    conn = db()
    conn.execute("INSERT OR REPLACE INTO cooldowns VALUES(?,?,?)", (user_id, cmd, time.time()))
    conn.commit()
    conn.close()

def reset_all_cd(user_id: int):
    conn = db()
    conn.execute("DELETE FROM cooldowns WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def check_cd(user_id: int, cmd: str, secs: int):
    """Returns (on_cooldown: bool, remaining: float)"""
    elapsed = time.time() - get_cd(user_id, cmd)
    if elapsed < secs:
        return True, secs - elapsed
    return False, 0.0

def get_inv(user_id: int) -> dict:
    conn = db()
    rows = conn.execute("SELECT item_name, quantity FROM inventory WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return dict(rows)

def add_inv(user_id: int, item: str, qty: int = 1):
    conn = db()
    r = conn.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (user_id, item)).fetchone()
    if r:
        conn.execute("UPDATE inventory SET quantity=quantity+? WHERE user_id=? AND item_name=?", (qty, user_id, item))
    else:
        conn.execute("INSERT INTO inventory VALUES(?,?,?)", (user_id, item, qty))
    conn.commit()
    conn.close()

def remove_inv(user_id: int, item: str, qty: int = 1) -> bool:
    conn = db()
    r = conn.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (user_id, item)).fetchone()
    if not r:
        conn.close()
        return False
    if r[0] <= qty:
        conn.execute("DELETE FROM inventory WHERE user_id=? AND item_name=?", (user_id, item))
    else:
        conn.execute("UPDATE inventory SET quantity=quantity-? WHERE user_id=? AND item_name=?", (qty, user_id, item))
    conn.commit()
    conn.close()
    return True

# ─── Formatting helpers ───────────────────────────────────────────────────────

def sc(amount: int) -> str:
    return f"⚓ **{amount:,}** Sailor Coins"

def fmt_time(secs: float) -> str:
    s = int(secs)
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m {s%60}s"
    return f"{s//3600}h {(s%3600)//60}m"

# ══════════════════════════════════════════════════════════════════════════════
# BOT EVENTS
# ══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"⚓ {bot.user} is online!")
    init_db()
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")
    
    if not passive_drop.is_running():
        passive_drop.start()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or is_banned(message.author.id):
        return
    uid = message.author.id
    on_cd, _ = check_cd(uid, "chat_reward", 60)
    if not on_cd:
        mult = get_mult(uid, "coins")
        reward = int(random.randint(2, 8) * mult)
        add_wallet(uid, reward)
        set_cd(uid, "chat_reward")
        # XP + level-up
        conn = db()
        ensure_user(uid)
        conn.execute("UPDATE users SET xp=xp+? WHERE user_id=?", (random.randint(1, 3), uid))
        row = conn.execute("SELECT xp, level FROM users WHERE user_id=?", (uid,)).fetchone()
        if row and row[0] >= row[1] * 100:
            conn.execute("UPDATE users SET level=level+1, xp=0 WHERE user_id=?", (uid,))
            conn.commit()
            conn.close()
            try:
                lvl_embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"{message.author.mention} reached **Level {row[1]+1}**! Here's {sc(row[1]*50)} as a reward!",
                    color=GOLD
                )
                add_wallet(uid, row[1] * 50)
                await message.channel.send(embed=lvl_embed, delete_after=10)
            except Exception:
                pass
        else:
            conn.commit()
            conn.close()
    await bot.process_commands(message)

# ══════════════════════════════════════════════════════════════════════════════
# PASSIVE DROP TASK
# ══════════════════════════════════════════════════════════════════════════════

@tasks.loop(minutes=30)
async def passive_drop():
    drop_channel_id = get_cfg("drop_channel")
    if not drop_channel_id:
        return
    channel = bot.get_channel(int(drop_channel_id))
    if not channel:
        return
    mn  = int(get_cfg("drop_min", "100"))
    mx  = int(get_cfg("drop_max", "500"))
    amount = random.randint(mn, mx)
    embed = discord.Embed(
        title="⚓ Treasure Washed Ashore!",
        description=f"A chest containing **{sc(amount)}** has appeared!\nType `!claim` to grab it — first come, first served!",
        color=GOLD
    )
    embed.set_footer(text="You have 60 seconds!")
    await channel.send(embed=embed)
    def check(m): return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount)
        await channel.send(embed=discord.Embed(
            title="🎉 Chest Claimed!",
            description=f"{resp.author.mention} snatched {sc(amount)}!",
            color=GREEN
        ))
    except asyncio.TimeoutError:
        await channel.send(embed=discord.Embed(
            title="🌊 Chest Sank",
            description="Nobody claimed the chest in time... it sank.",
            color=RED
        ))

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PERMISSION CHECK
# ══════════════════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - ECONOMY
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="Check your Sailor Coins balance")
@app_commands.describe(user="Check another user's balance (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    embed = discord.Embed(title=f"⚓ {target.display_name}'s Wallet", color=GOLD)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="👛 Wallet",      value=sc(data[1]), inline=True)
    embed.add_field(name="🏦 Bank",        value=f"{sc(data[2])} / {sc(data[3])}", inline=True)
    embed.add_field(name="💰 Net Worth",   value=sc(data[1]+data[2]), inline=True)
    embed.add_field(name="⭐ Level",       value=f"Lvl {data[5]}  |  {data[6]} XP", inline=True)
    embed.add_field(name="📈 Total Earned",value=sc(data[4]), inline=True)
    embed.add_field(name="🔥 Daily Streak",value=f"{data[7]} days", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Claim your daily Sailor Coins reward")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid):
        return await interaction.response.send_message("❌ You're economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "daily", 86400)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="⏳ Already claimed!", description=f"Come back in **{fmt_time(rem)}**", color=RED)
        )
    data = get_user(uid)
    streak = data[7] + 1
    daily_mult = get_mult(uid, "daily")
    base = random.randint(200, 500)
    streak_bonus = min(streak * 10, 300)
    amount = int((base + streak_bonus) * daily_mult)
    add_wallet(uid, amount)
    set_cd(uid, "daily")
    conn = db()
    conn.execute("UPDATE users SET streak=?, last_daily=? WHERE user_id=?", (streak, time.time(), uid))
    conn.commit()
    conn.close()
    embed = discord.Embed(title="🌅 Daily Reward!", color=GOLD)
    embed.add_field(name="Earned",        value=sc(amount), inline=True)
    embed.add_field(name="🔥 Streak",     value=f"{streak} days", inline=True)
    embed.add_field(name="Streak Bonus",  value=sc(streak_bonus), inline=True)
    embed.set_footer(text="Come back tomorrow to keep your streak!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weekly", description="Claim your weekly bonus")
async def weekly(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "weekly", 604800)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="⏳ Weekly Claimed", description=f"Come back in **{fmt_time(rem)}**", color=RED)
        )
    amount = random.randint(1500, 3000)
    add_wallet(uid, amount)
    set_cd(uid, "weekly")
    embed = discord.Embed(title="📅 Weekly Reward!", description=f"You claimed {sc(amount)}!", color=GOLD)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - EARNING
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="fish", description="Cast your line and fish for Sailor Coins")
async def fish(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "fish", 30)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="🎣 Still Fishing", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    rod   = 1.5 if "Fishing Rod+" in inv else 1.0
    catches = [
        ("🥾 Old Boot",       0,    5,    6,  False),
        ("🐟 Small Fish",     10,   50,   38, True),
        ("🐠 Tropical Fish",  30,   80,   25, True),
        ("🐡 Pufferfish",     50,   120,  15, True),
        ("🦑 Giant Squid",    80,   200,  8,  True),
        ("🦈 Shark",          150,  350,  5,  True),
        ("🐳 Blue Whale",     350,  700,  2,  True),
        ("💎 Treasure Chest", 600,  1400, 1,  True),
    ]
    weights = [c[3] * (luck if c[4] else max(1, 1/luck)) for c in catches]
    catch = random.choices(catches, weights=weights)[0]
    amount = int(random.randint(catch[1], catch[2]) * coins * rod) if catch[2] > 0 else 0
    if amount > 0:
        add_wallet(uid, amount)
    set_cd(uid, "fish")
    embed = discord.Embed(title="🎣 Fishing Results!", color=BLUE)
    embed.add_field(name="You caught", value=catch[0], inline=True)
    embed.add_field(name="Earned",     value=sc(amount) if amount else "Nothing 😢", inline=True)
    if luck > 1: 
        embed.set_footer(text=f"🍀 Luck x{luck:.1f} active!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mine", description="Descend into the mines for Sailor Coins")
async def mine(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "mine", 45)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="⛏️ Still Mining", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    pick  = 1.5 if "Diamond Pickaxe" in inv else 1.0
    finds = [
        ("🪨 Stone",           5,   20,   38),
        ("🔩 Iron Ore",        20,  60,   28),
        ("🥇 Gold Nugget",     60,  150,  16),
        ("💎 Diamond",         150, 400,  9),
        ("🔮 Mystic Crystal",  300, 700,  6),
        ("⚓ Sailor's Gem",     600, 1200, 2),
        ("🌟 Ancient Artifact",900, 2500, 1),
    ]
    weights = [f[3] * luck for f in finds]
    find   = random.choices(finds, weights=weights)[0]
    amount = int(random.randint(find[1], find[2]) * coins * pick)
    add_wallet(uid, amount)
    set_cd(uid, "mine")
    embed = discord.Embed(title="⛏️ Mining Results!", color=0x8B4513)
    embed.add_field(name="You found", value=find[0], inline=True)
    embed.add_field(name="Earned",    value=sc(amount), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hunt", description="Hunt wild creatures for Sailor Coins")
async def hunt(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "hunt", 60)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="🏹 Still Hunting", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    bow   = 1.5 if "Hunter's Bow" in inv else 1.0
    animals = [
        ("🐰 Rabbit",       15,  40,  35),
        ("🦊 Fox",          40,  100, 25),
        ("🦌 Deer",         80,  200, 20),
        ("🐗 Wild Boar",    150, 350, 12),
        ("🐻 Bear",         300, 700, 5),
        ("🐉 Sea Dragon",   700, 1800, 2),
        ("🦄 Mythic Beast", 1500,3000, 1),
    ]
    weights = [a[3] * luck for a in animals]
    animal = random.choices(animals, weights=weights)[0]
    amount = int(random.randint(animal[1], animal[2]) * coins * bow)
    add_wallet(uid, amount)
    set_cd(uid, "hunt")
    embed = discord.Embed(title="🏹 Hunt Results!", color=0x228B22)
    embed.add_field(name="You hunted", value=animal[0], inline=True)
    embed.add_field(name="Earned",     value=sc(amount), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="work", description="Work a shift and earn honest Sailor Coins")
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "work", 3600)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="💼 Still on Shift", description=f"Clock back in after **{fmt_time(rem)}**", color=RED)
        )
    coins = get_mult(uid, "coins")
    jobs = [
        ("🧑‍✈️ Ship Captain",       220, 450),
        ("🧑‍🍳 Ship Cook",           100, 260),
        ("🧑‍🔧 Engineer",            150, 360),
        ("🧑‍💻 Navigator",           180, 400),
        ("🏴‍☠️ Pirate Lookout",      130, 320),
        ("🎣 Pro Fisherman",         90,  230),
        ("⚓ Dock Worker",            80,  210),
        ("🗺️ Cartographer",         160, 380),
        ("🦜 Parrot Trainer",       70,  180),
        ("💣 Cannon Operator",      200, 420),
    ]
    job    = random.choice(jobs)
    amount = int(random.randint(job[1], job[2]) * coins)
    add_wallet(uid, amount)
    set_cd(uid, "work")
    embed = discord.Embed(title="💼 Shift Complete!", color=GREEN)
    embed.add_field(name="Job",    value=job[0],    inline=True)
    embed.add_field(name="Salary", value=sc(amount), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="crime", description="Commit a crime — high risk, high reward")
async def crime(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "crime", 7200)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="🕵️ Laying Low", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    set_cd(uid, "crime")
    data   = get_user(uid)
    wallet = data[1]
    inv    = get_inv(uid)
    crimes = [
        ("🎭 Con Artist",    "Swindled tourists",      300,  800),
        ("🏴‍☠️ Piracy",       "Raided a cargo ship",    600,  1800),
        ("🃏 Card Shark",    "Cheated at poker",        200,  600),
        ("🥷 Night Thief",   "Robbed a jewelry store",  500,  1200),
        ("🦜 Parrot Smuggler","Sold exotic birds",       150,  450),
        ("💣 Saboteur",      "Bombed a rival's ship",   800,  2500),
    ]
    act = random.choice(crimes)
    fail_chance = 0.35
    if "Escape Card" in inv and random.random() < fail_chance:
        remove_inv(uid, "Escape Card", 1)
        embed = discord.Embed(title="🃏 Escape Card Used!", description="You got caught but used your Escape Card!", color=PURPLE)
        await interaction.response.send_message(embed=embed)
        return
    if random.random() < fail_chance:
        fine = int(wallet * random.uniform(0.05, 0.25))
        fine = max(fine, 50)
        add_wallet(uid, -min(fine, wallet))
        embed = discord.Embed(title="🚔 Busted!", color=RED)
        embed.add_field(name="Crime Attempted", value=act[0],    inline=False)
        embed.add_field(name="Fine Paid",        value=sc(fine), inline=False)
    else:
        coins  = get_mult(uid, "coins")
        amount = int(random.randint(act[2], act[3]) * coins)
        add_wallet(uid, amount)
        embed = discord.Embed(title="😈 Crime Successful!", color=PURPLE)
        embed.add_field(name="Crime",   value=act[0],                 inline=False)
        embed.add_field(name="Result",  value=f"_{act[1]}_",          inline=False)
        embed.add_field(name="Looted",  value=sc(amount),             inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="beg", description="Beg passers-by for Sailor Coins")
async def beg(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "beg", 300)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="😑 People are tired of you", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    set_cd(uid, "beg")
    scenarios = [
        ("🧑‍✈️ A kind captain", 10, 60),
        ("💰 A wealthy merchant", 30, 120),
        ("🏴‍☠️ A generous pirate", 20, 80),
        ("👵 An old sailor", 5, 30),
        (None, 0, 0),
        (None, 0, 0),
    ]
    s = random.choice(scenarios)
    if s[0] is None:
        embed = discord.Embed(title="😞 Ignored", description="Everyone walked right past you.", color=RED)
    else:
        amount = random.randint(s[1], s[2])
        add_wallet(uid, amount)
        embed = discord.Embed(title="🙏 Someone Helped!", color=GREEN)
        embed.add_field(name=s[0], value=f"gave you {sc(amount)}", inline=False)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - PVP
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="rob", description="Attempt to rob another user's wallet")
@app_commands.describe(user="The user you want to rob")
async def rob(interaction: discord.Interaction, user: discord.Member):
    rid = interaction.user.id
    vid = user.id
    if is_banned(rid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    if user.bot or rid == vid: 
        return await interaction.response.send_message("❌ Invalid target!", ephemeral=True)
    on_cd, rem = check_cd(rid, "rob", 3600)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="⏳ Hiding", description=f"Wait **{fmt_time(rem)}**", color=RED)
        )
    robber = get_user(rid)
    victim = get_user(vid)
    if robber[1] < 100:
        return await interaction.response.send_message("❌ You need at least ⚓ 100 to rob someone.", ephemeral=True)
    if victim[1] < 50:
        return await interaction.response.send_message("❌ That person has nothing to steal!", ephemeral=True)
    set_cd(rid, "rob")
    v_inv = get_inv(vid)
    if "Shield" in v_inv:
        remove_inv(vid, "Shield", 1)
        fine = int(robber[1] * 0.10)
        add_wallet(rid, -fine)
        embed = discord.Embed(title="🛡️ Shield Blocked You!", color=RED)
        embed.add_field(name="Fine Paid", value=sc(fine), inline=False)
        return await interaction.response.send_message(embed=embed)
    has_charm = "Lucky Charm" in v_inv
    success_chance = 0.38 if has_charm else 0.52
    if random.random() < success_chance:
        pct    = random.uniform(0.10, 0.40)
        stolen = max(10, int(victim[1] * pct))
        add_wallet(vid, -stolen)
        add_wallet(rid, stolen)
        embed = discord.Embed(title="🥷 Robbery Successful!", color=GREEN)
        embed.add_field(name="Victim",  value=user.mention,  inline=True)
        embed.add_field(name="Stolen",  value=sc(stolen),    inline=True)
        embed.set_footer(text=f"Swiped {pct:.0%} of their wallet")
    else:
        fine = int(robber[1] * random.uniform(0.10, 0.25))
        add_wallet(rid, -fine)
        add_wallet(vid, fine)
        embed = discord.Embed(title="🚔 Caught!", color=RED)
        embed.add_field(name="Fine Paid to Victim", value=sc(fine), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="bankrob", description="Rob the bank — massive reward, massive risk")
async def bankrob(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "bankrob", 14400)
    if on_cd:
        return await interaction.response.send_message(
            embed=discord.Embed(title="🚔 Heat is Too Hot", description=f"Lay low for **{fmt_time(rem)}**", color=RED)
        )
    data = get_user(uid)
    if data[1] < 500:
        return await interaction.response.send_message("❌ You need ⚓ 500+ in your wallet to attempt this!", ephemeral=True)
    set_cd(uid, "bankrob")
    if random.random() < 0.28:
        loot = random.randint(2000, 8000)
        add_wallet(uid, loot)
        embed = discord.Embed(title="🏦💥 BANK ROBBED!", color=GOLD)
        embed.add_field(name="🎉 Heist Successful!", value=f"You escaped with {sc(loot)}!", inline=False)
        embed.set_footer(text="You're a living legend...")
    else:
        penalty = int(data[1] * random.uniform(0.20, 0.50))
        add_wallet(uid, -penalty)
        embed = discord.Embed(title="🚨 HEIST FAILED!", color=RED)
        embed.add_field(name="Arrested!", value=f"Fined {sc(penalty)}!", inline=False)
    await interaction.response.send_message(embed=embed)

# ═════════════════════════════���════════════════════════════════════════════════
# MEMBER COMMANDS - GAMES
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="gamble", description="Gamble your Sailor Coins")
@app_commands.describe(amount="Amount to gamble, or 'all'")
async def gamble(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    data = get_user(uid)
    if amount.lower() == "all":
        bet = data[1]
    else:
        try: 
            bet = int(amount)
        except: 
            return await interaction.response.send_message("❌ Invalid amount.", ephemeral=True)
    if bet < 10 or bet > data[1]:
        return await interaction.response.send_message("❌ Invalid bet (min ⚓ 10).", ephemeral=True)
    on_cd, rem = check_cd(uid, "gamble", 12)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    set_cd(uid, "gamble")
    if random.random() < 0.45:
        coins     = get_mult(uid, "coins")
        winnings  = int(bet * random.uniform(1.2, 2.5) * coins)
        add_wallet(uid, winnings - bet)
        embed = discord.Embed(title="🎰 You Won!", color=GREEN)
        embed.add_field(name="Bet",    value=sc(bet),          inline=True)
        embed.add_field(name="Won",    value=sc(winnings),     inline=True)
        embed.add_field(name="Profit", value=sc(winnings-bet), inline=True)
    else:
        add_wallet(uid, -bet)
        embed = discord.Embed(title="🎰 House Wins", color=RED)
        embed.add_field(name="Lost", value=sc(bet), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slots", description="Spin the slot machine")
@app_commands.describe(amount="Amount to bet (min 10)")
async def slots(interaction: discord.Interaction, amount: int):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid bet.", ephemeral=True)
    on_cd, rem = check_cd(uid, "slots", 15)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    set_cd(uid, "slots")
    syms    = ["⚓","🌊","🐠","💎","🌟","🏴‍☠️","🦈"]
    weights = [30,   25,  20,  10,   7,    5,   3]
    reels   = random.choices(syms, weights=weights, k=3)
    display = " | ".join(reels)
    if reels[0] == reels[1] == reels[2]:
        mults = {"⚓":5,"🌊":4,"🐠":3,"💎":8,"🌟":12,"🏴‍☠️":18,"🦈":15}
        m     = mults.get(reels[0], 3)
        win   = amount * m
        add_wallet(uid, win - amount)
        embed = discord.Embed(title=f"🎰 JACKPOT! {display}", description=f"Won {sc(win)} (x{m})", color=GOLD)
    elif reels[0]==reels[1] or reels[1]==reels[2]:
        win = int(amount * 1.5)
        add_wallet(uid, win - amount)
        embed = discord.Embed(title=f"🎰 Two of a Kind! {display}", description=f"Won {sc(win)}", color=GREEN)
    else:
        add_wallet(uid, -amount)
        embed = discord.Embed(title=f"🎰 No Match  {display}", description=f"Lost {sc(amount)}", color=RED)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="Flip a coin — double or nothing!")
@app_commands.describe(amount="Bet amount", side="heads or tails")
async def coinflip(interaction: discord.Interaction, amount: int, side: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    if side.lower() not in ("heads","tails"):
        return await interaction.response.send_message("❌ Pick 'heads' or 'tails'.", ephemeral=True)
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid bet.", ephemeral=True)
    on_cd, rem = check_cd(uid, "flip", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    set_cd(uid, "flip")
    result = random.choice(("heads","tails"))
    emoji  = "🪙" if result=="heads" else "🌑"
    if result == side.lower():
        add_wallet(uid, amount)
        embed = discord.Embed(title=f"{emoji} {result.upper()} — You Win!", color=GREEN)
        embed.add_field(name="Won", value=sc(amount), inline=False)
    else:
        add_wallet(uid, -amount)
        embed = discord.Embed(title=f"{emoji} {result.upper()} — You Lose!", color=RED)
        embed.add_field(name="Lost", value=sc(amount), inline=False)
    embed.set_footer(text=f"You picked {side} | Result: {result}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="highlow", description="Guess if the next number is higher or lower")
@app_commands.describe(amount="Bet amount", guess="higher or lower")
async def highlow(interaction: discord.Interaction, amount: int, guess: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    if guess.lower() not in ("higher","lower"):
        return await interaction.response.send_message("❌ Guess 'higher' or 'lower'.", ephemeral=True)
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid bet.", ephemeral=True)
    on_cd, rem = check_cd(uid, "highlow", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    set_cd(uid, "highlow")
    first  = random.randint(1, 10)
    second = random.randint(1, 10)
    correct = (guess.lower()=="higher" and second>first) or (guess.lower()=="lower" and second<first)
    if correct:
        add_wallet(uid, amount)
        embed = discord.Embed(title="✅ Correct!", color=GREEN)
        embed.description = f"**{first}** → **{second}** | You guessed **{guess}** and won {sc(amount)}!"
    else:
        add_wallet(uid, -amount)
        embed = discord.Embed(title="❌ Wrong!", color=RED)
        embed.description = f"**{first}** → **{second}** | You guessed **{guess}** and lost {sc(amount)}."
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="duel", description="Challenge another user to a coin duel")
@app_commands.describe(user="Opponent", amount="Wager amount")
async def duel(interaction: discord.Interaction, user: discord.Member, amount: int):
    cid, oid = interaction.user.id, user.id
    if is_banned(cid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    if user.bot or cid==oid: 
        return await interaction.response.send_message("❌ Invalid opponent.", ephemeral=True)
    cd = get_user(cid)
    od = get_user(oid)
    if amount < 10 or amount > cd[1]:
        return await interaction.response.send_message("❌ Invalid wager.", ephemeral=True)
    if amount > od[1]:
        return await interaction.response.send_message("❌ Opponent doesn't have enough coins.", ephemeral=True)
    embed = discord.Embed(title="⚔️ Duel Challenge!",
                          description=f"{interaction.user.mention} challenges {user.mention} to a duel for {sc(amount)}!\n{user.mention}, reply with `accept` or `decline`.",
                          color=GOLD)
    await interaction.response.send_message(embed=embed)
    def check(m): return m.author==user and m.channel==interaction.channel and m.content.lower() in ("accept","decline")
    try:
        resp = await bot.wait_for("message", check=check, timeout=30.0)
        if resp.content.lower()=="decline":
            return await interaction.followup.send(f"❌ {user.mention} declined the duel.")
        winner = random.choice([interaction.user, user])
        loser  = user if winner==interaction.user else interaction.user
        add_wallet(winner.id, amount)
        add_wallet(loser.id, -amount)
        await interaction.followup.send(embed=discord.Embed(
            title="⚔️ Duel Result!",
            description=f"**{winner.mention}** wins {sc(amount)}! Better luck next time, {loser.mention}!",
            color=GREEN
        ))
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⌛ {user.mention} didn't respond. Duel cancelled.")

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - BANK & TRANSFER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="deposit", description="Deposit Sailor Coins into your bank")
@app_commands.describe(amount="Amount to deposit, or 'all'")
async def deposit(interaction: discord.Interaction, amount: str):
    uid  = interaction.user.id
    data = get_user(uid)
    dep  = data[1] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    if dep <= 0 or dep > data[1]:
        return await interaction.response.send_message("❌ Invalid amount.", ephemeral=True)
    space = data[3] - data[2]
    dep = min(dep, space)
    if dep <= 0:
        return await interaction.response.send_message("❌ Bank full! Buy a Bank Expansion in `/shop`.", ephemeral=True)
    add_wallet(uid, -dep)
    add_bank(uid, dep)
    embed = discord.Embed(title="🏦 Deposited!", color=GREEN)
    embed.add_field(name="Amount", value=sc(dep), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="withdraw", description="Withdraw Sailor Coins from your bank")
@app_commands.describe(amount="Amount to withdraw, or 'all'")
async def withdraw(interaction: discord.Interaction, amount: str):
    uid  = interaction.user.id
    data = get_user(uid)
    wdr  = data[2] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    if wdr <= 0 or wdr > data[2]:
        return await interaction.response.send_message("❌ Invalid amount.", ephemeral=True)
    add_bank(uid, -wdr)
    add_wallet(uid, wdr)
    embed = discord.Embed(title="🏦 Withdrawn!", color=GREEN)
    embed.add_field(name="Amount", value=sc(wdr), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transfer", description="Send Sailor Coins to another user")
@app_commands.describe(user="Recipient", amount="Amount to send")
async def transfer(interaction: discord.Interaction, user: discord.Member, amount: int):
    sid, rid = interaction.user.id, user.id
    if is_banned(sid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    if user.bot or sid==rid: 
        return await interaction.response.send_message("❌ Invalid recipient.", ephemeral=True)
    data = get_user(sid)
    if amount <= 0 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid amount.", ephemeral=True)
    on_cd, rem = check_cd(sid, "transfer", 30)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    set_cd(sid, "transfer")
    add_wallet(sid, -amount)
    add_wallet(rid, amount)
    embed = discord.Embed(title="💸 Transfer Complete!", color=GREEN)
    embed.add_field(name="To",     value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(amount),   inline=True)
    await interaction.response.send_message(embed=embed)

# ═════════════════════════════════════════════════════��════════════════════════
# MEMBER COMMANDS - SHOP & INVENTORY
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="shop", description="Browse the Sailor Coins shop")
async def shop(interaction: discord.Interaction):
    conn = db()
    items = conn.execute("SELECT item_name, price, description FROM shop ORDER BY price").fetchall()
    conn.close()
    embed = discord.Embed(title="⚓ Sailor Shop", description="Use `/buy <item>` to purchase!", color=GOLD)
    for item in items:
        embed.add_field(name=f"{item[0]}  —  {sc(item[1])}", value=item[2], inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(item="Item name (from /shop)")
async def buy(interaction: discord.Interaction, item: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    conn = db()
    row  = conn.execute("SELECT * FROM shop WHERE LOWER(item_name)=LOWER(?)", (item,)).fetchone()
    conn.close()
    if not row:
        return await interaction.response.send_message("❌ Item not found. Check `/shop`.", ephemeral=True)
    item_name, price, desc, item_type, value = row
    data = get_user(uid)
    if data[1] < price:
        return await interaction.response.send_message(f"❌ Need {sc(price)}, you have {sc(data[1])}.", ephemeral=True)
    add_wallet(uid, -price)
    if item_type == "multiplier":
        parts = value.split(":")
        set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
        embed = discord.Embed(title=f"✅ {item_name} Activated!", description=f"**x{parts[1]} {parts[0]}** for **{fmt_time(int(parts[2]))}**!", color=GREEN)
    elif item_type == "upgrade":
        add_inv(uid, item_name)
        embed = discord.Embed(title=f"✅ {item_name} Equipped!", description=desc, color=GREEN)
    elif item_type == "bank":
        extra = int(value)
        conn = db()
        conn.execute("UPDATE users SET bank_limit=bank_limit+? WHERE user_id=?", (extra, uid))
        conn.commit()
        conn.close()
        embed = discord.Embed(title="🏦 Bank Expanded!", description=f"Limit increased by {sc(extra)}!", color=GREEN)
    elif item_type == "role":
        role = discord.utils.get(interaction.guild.roles, name=value)
        if role:
            await interaction.user.add_roles(role)
            embed = discord.Embed(title="🎖️ Role Granted!", description=f"You now have the **{value}** role!", color=GREEN)
        else:
            add_wallet(uid, price)
            embed = discord.Embed(title="❌ Role Not Found", description="Refunded!", color=RED)
    elif item_type == "protection":
        add_inv(uid, item_name)
        embed = discord.Embed(title=f"🛡️ {item_name} Added!", description=desc, color=GREEN)
    else:
        add_inv(uid, item_name)
        embed = discord.Embed(title=f"✅ {item_name} Purchased!", description=desc, color=GREEN)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inventory", description="View your inventory")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    items  = get_inv(target.id)
    embed  = discord.Embed(title=f"🎒 {target.display_name}'s Inventory", color=PURPLE)
    if not items:
        embed.description = "Empty! Check out `/shop` to buy items."
    else:
        for name, qty in items.items():
            embed.add_field(name=name, value=f"x{qty}", inline=True)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - INFO
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="leaderboard", description="Top 10 richest sailors")
async def leaderboard(interaction: discord.Interaction):
    conn = db()
    rows = conn.execute("SELECT user_id, wallet+bank FROM users ORDER BY wallet+bank DESC LIMIT 10").fetchall()
    conn.close()
    embed  = discord.Embed(title="⚓ Sailor Coins Leaderboard", color=GOLD)
    medals = ["🥇","🥈","🥉"]
    for i, (uid, total) in enumerate(rows):
        m    = medals[i] if i<3 else f"`#{i+1}`"
        u    = interaction.guild.get_member(uid)
        name = u.display_name if u else "Unknown"
        embed.add_field(name=f"{m}  {name}", value=sc(total), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profile", description="View your sailor economy profile")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data   = get_user(target.id)
    items  = get_inv(target.id)
    embed  = discord.Embed(title=f"⚓ {target.display_name}'s Profile", color=BLUE)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="👛 Wallet",       value=sc(data[1]),        inline=True)
    embed.add_field(name="🏦 Bank",         value=sc(data[2]),        inline=True)
    embed.add_field(name="💰 Net Worth",    value=sc(data[1]+data[2]),inline=True)
    embed.add_field(name="⭐ Level",        value=str(data[5]),       inline=True)
    embed.add_field(name="✨ XP",           value=f"{data[6]} / {data[5]*100}", inline=True)
    embed.add_field(name="🔥 Streak",       value=f"{data[7]} days",  inline=True)
    embed.add_field(name="🏆 Total Earned", value=sc(data[4]),        inline=True)
    embed.add_field(name="🎒 Items Held",   value=str(len(items)),    inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multipliers", description="View your active multipliers")
async def multipliers(interaction: discord.Interaction):
    uid = interaction.user.id
    now = time.time()
    conn = db()
    rows = conn.execute(
        "SELECT mult_type, value, expires_at FROM multipliers WHERE user_id=? AND expires_at>?",
        (uid, now)
    ).fetchall()
    conn.close()
    embed = discord.Embed(title="✨ Active Multipliers", color=PURPLE)
    if not rows:
        embed.description = "No active multipliers. Buy some from `/shop`!"
    else:
        for mult_type, value, expires_at in rows:
            remaining = expires_at - now
            embed.add_field(name=f"x{value:.1f} {mult_type.capitalize()}", value=f"Expires in {fmt_time(remaining)}", inline=True)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ════════════════════��═════════════════════════════════════════════════════════

@bot.tree.command(name="give", description="[ADMIN] Give Sailor Coins to a user")
@app_commands.describe(user="Target user", amount="Amount to give")
@admin_only()
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    add_wallet(user.id, amount)
    embed = discord.Embed(title="✅ Coins Given", color=GREEN)
    embed.add_field(name="To",     value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(amount),   inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="take", description="[ADMIN] Take Sailor Coins from a user")
@app_commands.describe(user="Target user", amount="Amount to remove")
@admin_only()
async def take(interaction: discord.Interaction, user: discord.Member, amount: int):
    data   = get_user(user.id)
    actual = min(amount, data[1])
    add_wallet(user.id, -actual)
    embed = discord.Embed(title="✅ Coins Taken", color=RED)
    embed.add_field(name="From",   value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(actual),   inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setbalance", description="[ADMIN] Set a user's wallet balance")
@app_commands.describe(user="Target user", amount="New balance")
@admin_only()
async def setbalance(interaction: discord.Interaction, user: discord.Member, amount: int):
    set_wallet(user.id, max(0, amount))
    await interaction.response.send_message(f"✅ Set {user.mention}'s wallet to {sc(amount)}.", ephemeral=True)

@bot.tree.command(name="resetuser", description="[ADMIN] Fully reset a user's economy data")
@app_commands.describe(user="User to reset")
@admin_only()
async def resetuser(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    for t in ("users","inventory","cooldowns","multipliers"):
        conn.execute(f"DELETE FROM {t} WHERE user_id=?", (user.id,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ {user.mention}'s economy data wiped.", ephemeral=True)

@bot.tree.command(name="setdropchannel", description="[ADMIN] Set the channel for passive coin drops")
@app_commands.describe(channel="Drop channel")
@admin_only()
async def setdropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("drop_channel", str(channel.id))
    await interaction.response.send_message(f"✅ Drops will appear in {channel.mention}!", ephemeral=True)

@bot.tree.command(name="dropconfig", description="[ADMIN] Configure drop amount and interval")
@app_commands.describe(min_amount="Min drop", max_amount="Max drop", interval_minutes="Minutes between drops")
@admin_only()
async def dropconfig(interaction: discord.Interaction, min_amount: int = None, max_amount: int = None, interval_minutes: int = None):
    if min_amount:    set_cfg("drop_min", str(min_amount))
    if max_amount:    set_cfg("drop_max", str(max_amount))
    if interval_minutes and interval_minutes >= 5:
        set_cfg("drop_interval_minutes", str(interval_minutes))
        passive_drop.change_interval(minutes=interval_minutes)
    mn = get_cfg("drop_min","100")
    mx = get_cfg("drop_max","500")
    iv = get_cfg("drop_interval_minutes","30")
    await interaction.response.send_message(
        f"✅ Drop config: min=**{mn}** max=**{mx}** every=**{iv} min**", ephemeral=True
    )

@bot.tree.command(name="manualdrop", description="[ADMIN] Trigger a coin drop manually")
@app_commands.describe(amount="Amount to drop")
@admin_only()
async def manualdrop(interaction: discord.Interaction, amount: int):
    cid = get_cfg("drop_channel")
    if not cid:
        return await interaction.response.send_message("❌ No drop channel set.", ephemeral=True)
    channel = bot.get_channel(int(cid))
    await interaction.response.send_message(f"✅ Dropping {sc(amount)} in {channel.mention}!", ephemeral=True)
    embed = discord.Embed(title="⚓ Admin Drop!", description=f"**{sc(amount)}** just dropped!\nType `!claim` to grab it!", color=GOLD)
    await channel.send(embed=embed)
    def check(m): return m.channel==channel and not m.author.bot and m.content.lower()=="!claim"
    try:
        r = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(r.author.id, amount)
        await channel.send(embed=discord.Embed(title="🎉 Claimed!", description=f"{r.author.mention} got {sc(amount)}!", color=GREEN))
    except asyncio.TimeoutError:
        await channel.send(embed=discord.Embed(title="⌛ Expired", description="Nobody claimed it.", color=RED))

@bot.tree.command(name="addshopitem", description="[ADMIN] Add an item to the shop")
@app_commands.describe(name="Item name", price="Price", description="Description", item_type="multiplier/upgrade/role/bank/protection", value="Item value string")
@admin_only()
async def addshopitem(interaction: discord.Interaction, name: str, price: int, description: str, item_type: str, value: str):
    conn = db()
    conn.execute("INSERT OR REPLACE INTO shop VALUES(?,?,?,?,?)", (name, price, description, item_type, value))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ **{name}** added to shop for {sc(price)}.", ephemeral=True)

@bot.tree.command(name="removeshopitem", description="[ADMIN] Remove an item from the shop")
@app_commands.describe(name="Item name")
@admin_only()
async def removeshopitem(interaction: discord.Interaction, name: str):
    conn = db()
    conn.execute("DELETE FROM shop WHERE LOWER(item_name)=LOWER(?)", (name,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ **{name}** removed from shop.", ephemeral=True)

@bot.tree.command(name="economyban", description="[ADMIN] Ban/unban a user from the economy")
@app_commands.describe(user="Target user")
@admin_only()
async def economyban(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    if conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user.id,)).fetchone():
        conn.execute("DELETE FROM banned_users WHERE user_id=?", (user.id,))
        msg, color = f"✅ {user.mention} **unbanned** from economy.", GREEN
    else:
        conn.execute("INSERT INTO banned_users VALUES(?)", (user.id,))
        msg, color = f"🚫 {user.mention} **banned** from economy.", RED
    conn.commit()
    conn.close()
    await interaction.response.send_message(embed=discord.Embed(description=msg, color=color))

@bot.tree.command(name="resetcooldowns", description="[ADMIN] Reset all cooldowns for a user")
@app_commands.describe(user="Target user")
@admin_only()
async def resetcooldowns(interaction: discord.Interaction, user: discord.Member):
    reset_all_cd(user.id)
    await interaction.response.send_message(f"✅ All cooldowns reset for {user.mention}.", ephemeral=True)

@bot.tree.command(name="setmultiplier", description="[ADMIN] Give a multiplier to a user")
@app_commands.describe(user="Target user", mult_type="coins or luck", value="Multiplier value (e.g. 2.0)", hours="Duration in hours")
@admin_only()
async def setmultiplier(interaction: discord.Interaction, user: discord.Member, mult_type: str, value: float, hours: float):
    set_mult(user.id, mult_type, value, int(hours * 3600))
    await interaction.response.send_message(
        f"✅ Set **x{value} {mult_type}** for {user.mention} for **{hours} hours**.", ephemeral=True
    )

@bot.tree.command(name="giveitem", description="[ADMIN] Give an item directly to a user's inventory")
@app_commands.describe(user="Target user", item="Item name", quantity="Quantity")
@admin_only()
async def giveitem(interaction: discord.Interaction, user: discord.Member, item: str, quantity: int = 1):
    add_inv(user.id, item, quantity)
    await interaction.response.send_message(f"✅ Gave **{quantity}x {item}** to {user.mention}.", ephemeral=True)

@bot.tree.command(name="economystats", description="[ADMIN] View global economy statistics")
@admin_only()
async def economystats(interaction: discord.Interaction):
    conn = db()
    s = conn.execute("SELECT COUNT(*), SUM(wallet), SUM(bank), SUM(total_earned) FROM users").fetchone()
    b = conn.execute("SELECT COUNT(*) FROM banned_users").fetchone()[0]
    r = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    conn.close()
    embed = discord.Embed(title="📊 Economy Statistics", color=BLUE)
    embed.add_field(name="👥 Players",         value=str(s[0]),           inline=True)
    embed.add_field(name="🚫 Banned",          value=str(b),              inline=True)
    embed.add_field(name="💰 In Wallets",      value=sc(s[1] or 0),      inline=True)
    embed.add_field(name="🏦 In Banks",        value=sc(s[2] or 0),      inline=True)
    embed.add_field(name="📈 Ever Earned",     value=sc(s[3] or 0),      inline=True)
    embed.add_field(name="🛍️ Total Items Held",value=str(r),              inline=True)
    embed.add_field(name="🏧 In Circulation",  value=sc((s[1] or 0)+(s[2] or 0)), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="broadcast", description="[ADMIN] Send an announcement to the drop channel")
@app_commands.describe(message="Your announcement text")
@admin_only()
async def broadcast(interaction: discord.Interaction, message: str):
    cid = get_cfg("drop_channel")
    if not cid:
        return await interaction.response.send_message("❌ No drop channel set.", ephemeral=True)
    channel = bot.get_channel(int(cid))
    embed = discord.Embed(title="📢 Announcement", description=message, color=GOLD)
    embed.set_footer(text=f"From {interaction.user.display_name}")
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Broadcast sent!", ephemeral=True)

@bot.tree.command(name="wipeeconomy", description="[ADMIN] ⚠️ Permanently wipe ALL economy data")
@admin_only()
async def wipeeconomy(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚠️ DANGER ZONE",
        description="This deletes **ALL** economy data permanently.\nType `CONFIRM WIPE` in chat within 30s to proceed.",
        color=RED
    )
    await interaction.response.send_message(embed=embed)
    def check(m): return m.author==interaction.user and m.channel==interaction.channel and m.content=="CONFIRM WIPE"
    try:
        await bot.wait_for("message", check=check, timeout=30.0)
        conn = db()
        for t in ("users","inventory","cooldowns","multipliers","transactions"):
            conn.execute(f"DELETE FROM {t}")
        conn.commit()
        conn.close()
        await interaction.followup.send(embed=discord.Embed(title="💀 Economy Wiped", description="All data deleted.", color=RED))
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Wipe cancelled.", ephemeral=True)

@bot.tree.command(name="addxp", description="[ADMIN] Add XP to a user")
@app_commands.describe(user="Target user", amount="XP to add")
@admin_only()
async def addxp(interaction: discord.Interaction, user: discord.Member, amount: int):
    ensure_user(user.id)
    conn = db()
    conn.execute("UPDATE users SET xp=xp+? WHERE user_id=?", (amount, user.id))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Added **{amount} XP** to {user.mention}.", ephemeral=True)

@bot.tree.command(name="setlevel", description="[ADMIN] Set a user's level")
@app_commands.describe(user="Target user", level="New level")
@admin_only()
async def setlevel(interaction: discord.Interaction, user: discord.Member, level: int):
    ensure_user(user.id)
    conn = db()
    conn.execute("UPDATE users SET level=?, xp=0 WHERE user_id=?", (max(1, level), user.id))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Set {user.mention} to **Level {level}**.", ephemeral=True)

@bot.tree.command(name="synccommands", description="[ADMIN] Force sync slash commands")
@admin_only()
async def synccommands(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    synced = await bot.tree.sync()
    await interaction.followup.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)

# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        msg = "❌ You need **Administrator** permission to use that command."
    else:
        msg = f"❌ Error: `{error}`"
        print(f"[ERROR] {error}")
    try:
        await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        await interaction.followup.send(msg, ephemeral=True)

# ══════════════════════════════════════════════════════════════════��═══════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set!")
    init_db()
    bot.run(TOKEN)
