"""
⚓ SAILOR COINS — Discord Economy Bot v5
=====================================
PREMIUM FEATURES:
  - Animated GIFs for all commands
  - Beautiful professional embeds
  - Custom role shop items
  - Advanced economy system
  - COMPREHENSIVE LOGGING SYSTEM ⭐
  - Admin dashboard
  - Interactive shop GUI
  - 60+ commands
  - Full economy tracking

Required env vars:
  DISCORD_TOKEN  — your bot token
  GUILD_ID       — your server ID
"""

import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import sqlite3
import random
import asyncio
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()

TOKEN    = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))

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
ORANGE = 0xFF8C00
DARK_BLUE = 0x1f1f2e
AQUA = 0x00D4FF

# ─── GIF URLs ────────��───────────────────────────────────────────────────────

GIFS = {
    "fish": [
        "https://media.giphy.com/media/13d2jHlSlxklVe/giphy.gif",
        "https://media.giphy.com/media/l0HlR4Z0wJP0TqCW4/giphy.gif",
        "https://media.giphy.com/media/dTJd5ygpxJ0N2/giphy.gif",
    ],
    "mine": [
        "https://media.giphy.com/media/l0HlQaQ7Yz7n91uIo/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    ],
    "hunt": [
        "https://media.giphy.com/media/EKDfwJZVU60Za/giphy.gif",
        "https://media.giphy.com/media/l0HlDtKPoYJhFtHTe/giphy.gif",
    ],
    "work": [
        "https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    ],
    "gamble": [
        "https://media.giphy.com/media/EKDfwJZVU60Za/giphy.gif",
        "https://media.giphy.com/media/l0HlNaQ7d1v0FKy0M/giphy.gif",
    ],
    "win": [
        "https://media.giphy.com/media/l0HlQaQ7Yz7n91uIo/giphy.gif",
        "https://media.giphy.com/media/3o6ZtpWzconUG6TdqE/giphy.gif",
    ],
    "lose": [
        "https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    ],
    "crime": [
        "https://media.giphy.com/media/l0HlDtKPoYJhFtHTe/giphy.gif",
        "https://media.giphy.com/media/l3q2K6HIiNbOAmqXK/giphy.gif",
    ],
    "rob": [
        "https://media.giphy.com/media/26uf0EUf6YXklWwgE/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    ],
    "levelup": [
        "https://media.giphy.com/media/3o6ZtpWzconUG6TdqE/giphy.gif",
        "https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif",
    ],
    "treasure": [
        "https://media.giphy.com/media/Nyx6NFlAhJx8Y/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING SYSTEM
# ═════════════════════════════��════════════════════════════════════════════════

async def log_to_channel(title: str, description: str, color: int, user: discord.Member = None, extra_fields: dict = None):
    """Send a log message to the logs channel"""
    log_channel_id = get_cfg("log_channel")
    if not log_channel_id:
        return
    
    channel = bot.get_channel(int(log_channel_id))
    if not channel:
        return
    
    embed = discord.Embed(
        title=f"📋 {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    
    if user:
        embed.set_author(name=f"{user.display_name} ({user.id})", icon_url=user.display_avatar.url)
    
    if extra_fields:
        for field_name, field_value in extra_fields.items():
            embed.add_field(name=field_name, value=field_value, inline=True)
    
    embed.set_footer(text="Sailor Coins Economy Logger")
    
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to log: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE - ENHANCED WITH ROLES
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
        last_daily   REAL    DEFAULT 0,
        invites      INTEGER DEFAULT 0
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
        item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name   TEXT UNIQUE,
        price       INTEGER,
        description TEXT,
        item_type   TEXT,
        value       TEXT,
        emoji       TEXT DEFAULT "⚓",
        image_url   TEXT DEFAULT ""
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

    c.execute("""CREATE TABLE IF NOT EXISTS invites (
        inviter_id   INTEGER,
        invitee_id   INTEGER,
        invite_date  REAL,
        PRIMARY KEY (inviter_id, invitee_id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS shop_purchases (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER,
        item_name TEXT,
        price     INTEGER,
        timestamp REAL
    )""")

    # Default shop items with images
    defaults = [
        ("2x Coin Boost",       5000,  "Double coin earnings for 1 hour",              "multiplier", "coins:2.0:3600", "💰", ""),
        ("2x Luck Charm",       3000,  "Double luck in fish/mine/hunt",                "multiplier", "luck:2.0:3600", "🍀", ""),
        ("3x Coin Boost",       12000, "Triple coin earnings for 30 minutes",          "multiplier", "coins:3.0:1800", "🚀", ""),
        ("4x Ultra Boost",      25000, "4x earnings for 15 minutes",                   "multiplier", "coins:4.0:900", "⚡", ""),
        ("Fishing Rod+",        2000,  "1.5x fishing yield",                           "upgrade",    "fishing:1.5", "🎣", ""),
        ("Diamond Pickaxe",     2000,  "1.5x mining yield",                            "upgrade",    "mining:1.5", "⛏️", ""),
        ("Hunter's Bow",        2000,  "1.5x hunting yield",                           "upgrade",    "hunting:1.5", "🏹", ""),
        ("Bank Expansion",      10000, "Increase bank limit by +5000",                 "bank",       "5000", "🏦", ""),
        ("Lucky Charm",         1500,  "Reduce robbery chance for 24 hours",           "protection", "rob:0.5:86400", "🧿", ""),
        ("Shield",              500,   "One-time full protection from robbery",        "protection", "rob_shield:1", "🛡️", ""),
        ("Escape Card",         3000,  "Escape from crime once",                       "protection", "crime_escape:1", "🃏", ""),
        ("Daily Boost",         2000,  "2x daily reward for 3 days",                   "multiplier", "daily:2.0:259200", "📅", ""),
        ("Mystery Box",         7500,  "Random reward: 5000-15000 coins!",             "mystery",    "5000:15000", "🎁", ""),
    ]
    for item in defaults:
        c.execute("INSERT OR IGNORE INTO shop VALUES (NULL,?,?,?,?,?,?,?)", item)

    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_interval_minutes','30')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_min','100')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_max','500')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('invite_reward','500')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('shop_channel','')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('log_channel','')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_channel','')")

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

def add_wallet(user_id: int, amount: int, reason: str = "earn"):
    ensure_user(user_id)
    conn = db()
    conn.execute("UPDATE users SET wallet=wallet+? WHERE user_id=?", (amount, user_id))
    if amount > 0:
        conn.execute("UPDATE users SET total_earned=total_earned+? WHERE user_id=?", (amount, user_id))
        conn.execute("INSERT INTO transactions(user_id,amount,reason,timestamp) VALUES(?,?,?,?)",
                     (user_id, amount, reason, time.time()))
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

def check_cd(user_id: int, cmd: str, secs: int):
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

def get_all_shop_items():
    conn = db()
    items = conn.execute("SELECT item_id, item_name, price, description, item_type, value, emoji, image_url FROM shop ORDER BY price").fetchall()
    conn.close()
    return items

def add_shop_item(name: str, price: int, desc: str, item_type: str, value: str, emoji: str, image: str = ""):
    conn = db()
    try:
        conn.execute("INSERT INTO shop (item_name, price, description, item_type, value, emoji, image_url) VALUES (?,?,?,?,?,?,?)",
                     (name, price, desc, item_type, value, emoji, image))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def remove_shop_item(name: str):
    conn = db()
    conn.execute("DELETE FROM shop WHERE LOWER(item_name)=LOWER(?)", (name,))
    conn.commit()
    conn.close()

def log_purchase(user_id: int, item_name: str, price: int):
    """Log a shop purchase"""
    conn = db()
    conn.execute("INSERT INTO shop_purchases (user_id, item_name, price, timestamp) VALUES (?,?,?,?)",
                 (user_id, item_name, price, time.time()))
    conn.commit()
    conn.close()

# ─── Formatting helpers ───────────────────────────────────────────────────────

def sc(amount: int) -> str:
    return f"⚓ **{amount:,}**"

def fmt_time(secs: float) -> str:
    s = int(secs)
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m {s%60}s"
    return f"{s//3600}h {(s%3600)//60}m"

def get_gif(category: str) -> str:
    return random.choice(GIFS.get(category, ["https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif"]))

# ══════════════════════════════════════════════════════════════════════════════
# SHOP BUTTONS - BEAUTIFUL DESIGN
# ══════════════════════════════════════════════════════════════════════════════

class ShopButton(ui.Button):
    def __init__(self, item_id: int, item_name: str, price: int, emoji: str):
        super().__init__(label=f"{item_name}", emoji=emoji, style=discord.ButtonStyle.blurple, row=0)
        self.item_id = item_id
        self.item_name = item_name
        self.price = price

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        if is_banned(uid):
            embed = discord.Embed(
                title="🚫 Banned",
                description="You're economy banned from this bot.",
                color=RED
            )
            embed.set_footer(text="Appeal with admins")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = get_user(uid)
        if data[1] < self.price:
            embed = discord.Embed(
                title="❌ Insufficient Coins",
                description=f"**Need:** {sc(self.price)} ⚓\n**You have:** {sc(data[1])} ⚓",
                color=RED
            )
            embed.set_thumbnail(url="https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif")
            embed.set_footer(text="Earn more by using /fish, /mine, /work!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        conn = db()
        row = conn.execute("SELECT item_name, price, description, item_type, value, emoji, image_url FROM shop WHERE item_id=?", (self.item_id,)).fetchone()
        conn.close()
        
        if not row:
            return await interaction.response.send_message("❌ Item not found.", ephemeral=True)
        
        item_name, price, desc, item_type, value, emoji, image_url = row
        add_wallet(uid, -price)
        log_purchase(uid, item_name, price)
        
        # Log to channel
        await log_to_channel(
            title="🛍️ SHOP PURCHASE",
            description=f"{interaction.user.mention} purchased **{item_name}**",
            color=GOLD,
            user=interaction.user,
            extra_fields={
                "💰 Price": f"{sc(price)} ⚓",
                "📦 Type": item_type,
                "💵 New Balance": f"{sc(data[1] - price)} ⚓"
            }
        )
        
        if item_type == "multiplier":
            parts = value.split(":")
            set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
            embed = discord.Embed(
                title=f"✅ {emoji} {item_name} Activated!",
                description=f"**x{parts[1]} {parts[0]}** boost active for **{fmt_time(int(parts[2]))}**!\n\n🔥 Your earnings are now multiplied!",
                color=GREEN
            )
        elif item_type == "upgrade":
            add_inv(uid, item_name)
            embed = discord.Embed(
                title=f"✅ {emoji} {item_name} Equipped!",
                description=desc,
                color=GREEN
            )
        elif item_type == "bank":
            extra = int(value)
            conn = db()
            conn.execute("UPDATE users SET bank_limit=bank_limit+? WHERE user_id=?", (extra, uid))
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title=f"✅ {emoji} Bank Expanded!",
                description=f"Bank limit increased by {sc(extra)} ⚓!",
                color=GREEN
            )
        elif item_type == "mystery":
            parts = value.split(":")
            reward = random.randint(int(parts[0]), int(parts[1]))
            add_wallet(uid, reward)
            embed = discord.Embed(
                title=f"✅ {emoji} Mystery Box Opened!",
                description=f"🎉 **You found {sc(reward)} ⚓!** 🎉",
                color=GOLD
            )
            embed.set_image(url=get_gif("win"))
        elif item_type == "role":
            role = discord.utils.get(interaction.guild.roles, name=value)
            if role:
                await interaction.user.add_roles(role)
                embed = discord.Embed(
                    title=f"✅ {emoji} Role Granted!",
                    description=f"🎖️ You now have the **{value}** role!",
                    color=GREEN
                )
                # Log role purchase
                await log_to_channel(
                    title="🎖️ ROLE PURCHASE",
                    description=f"{interaction.user.mention} purchased and received role **{value}**",
                    color=PURPLE,
                    user=interaction.user,
                    extra_fields={
                        "💰 Price": f"{sc(price)} ⚓",
                        "🎖️ Role": value
                    }
                )
            else:
                add_wallet(uid, price)
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description="The role doesn't exist. Refunded!",
                    color=RED
                )
        else:
            add_inv(uid, item_name)
            embed = discord.Embed(
                title=f"✅ {emoji} {item_name} Purchased!",
                description=desc,
                color=GREEN
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"New Balance: {sc(data[1] - price)} ⚓")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        items = get_all_shop_items()
        
        row = 0
        for idx, (item_id, item_name, price, desc, item_type, value, emoji, image) in enumerate(items):
            if idx > 0 and idx % 5 == 0:
                row += 1
            button = ShopButton(item_id, item_name, price, emoji)
            button.row = row
            self.add_item(button)

# ══════════════════════════════════════════════════════════════════════════════
# BOT EVENTS & TASKS
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
    
    # Log bot startup
    await log_to_channel(
        title="🚀 BOT STARTUP",
        description=f"Sailor Coins bot is now online!",
        color=GREEN,
        extra_fields={
            "⏰ Time": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "✅ Status": "Online"
        }
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or is_banned(message.author.id):
        return
    uid = message.author.id
    on_cd, _ = check_cd(uid, "chat_reward", 60)
    if not on_cd:
        mult = get_mult(uid, "coins")
        reward = int(random.randint(2, 8) * mult)
        add_wallet(uid, reward, "chat")
        set_cd(uid, "chat_reward")
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
                    title="🎉 LEVEL UP!",
                    description=f"{message.author.mention} reached **Level {row[1]+1}**!",
                    color=GOLD
                )
                lvl_embed.add_field(name="🎁 Level Reward", value=f"{sc(row[1]*50)} ⚓", inline=False)
                lvl_embed.set_thumbnail(url=message.author.display_avatar.url)
                lvl_embed.set_image(url=get_gif("levelup"))
                add_wallet(uid, row[1] * 50, "level_up")
                
                # Log level up
                await log_to_channel(
                    title="⭐ LEVEL UP",
                    description=f"{message.author.mention} reached Level {row[1]+1}",
                    color=GOLD,
                    user=message.author,
                    extra_fields={
                        "📈 New Level": str(row[1]+1),
                        "🎁 Reward": f"{sc(row[1]*50)} ⚓"
                    }
                )
                
                await message.channel.send(embed=lvl_embed, delete_after=15)
            except:
                pass
        else:
            conn.commit()
            conn.close()
    await bot.process_commands(message)

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
        title="⚓ TREASURE WASHED ASHORE!",
        description=f"A mysterious chest appeared containing **{sc(amount)} ⚓**!",
        color=GOLD
    )
    embed.add_field(name="⏳ How to Claim", value="Type `!claim` to grab it — first come, first served!", inline=False)
    embed.add_field(name="⏰ Time Limit", value="You have 60 seconds!", inline=False)
    embed.set_image(url=get_gif("treasure"))
    embed.set_footer(text="Be fast!")
    
    msg = await channel.send(embed=embed)
    
    def check(m): return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount, "treasure_drop")
        
        # Log treasure drop
        await log_to_channel(
            title="🎁 TREASURE CLAIMED",
            description=f"{resp.author.mention} claimed a treasure drop!",
            color=GOLD,
            user=resp.author,
            extra_fields={
                "💰 Amount": f"{sc(amount)} ⚓",
                "⏱️ Time": f"{datetime.now().strftime('%H:%M:%S')}"
            }
        )
        
        embed = discord.Embed(
            title="🎉 CHEST CLAIMED!",
            description=f"{resp.author.mention} snatched {sc(amount)} ⚓!",
            color=GREEN
        )
        embed.set_thumbnail(url=resp.author.display_avatar.url)
        embed.set_image(url=get_gif("win"))
        await channel.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="🌊 CHEST SANK",
            description="Nobody claimed the chest in time... it sank into the ocean.",
            color=RED
        )
        embed.set_image(url="https://media.giphy.com/media/l0HlYy9x8F5n7SK5i/giphy.gif")
        await channel.send(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS - SETUP & MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.command(name="admin_setup", description="[ADMIN] Complete setup wizard")
@admin_only()
async def admin_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚓ SAILOR COINS - ADMIN SETUP",
        description="Follow these steps to set up your economy bot:",
        color=GOLD
    )
    embed.add_field(
        name="Step 1️⃣ - Drop Channel",
        value="`/set_drop_channel #channel`\n(Where treasure chests appear)",
        inline=False
    )
    embed.add_field(
        name="Step 2️⃣ - Shop Channel",
        value="`/set_shop_channel #channel`\n(Where shop GUI appears)",
        inline=False
    )
    embed.add_field(
        name="Step 3️⃣ - Logs Channel",
        value="`/set_log_channel #channel`\n(Where all activity is logged)",
        inline=False
    )
    embed.add_field(
        name="Step 4️⃣ - Send Shop",
        value="`/send_shop`\n(Deploy the interactive shop)",
        inline=False
    )
    embed.add_field(
        name="Step 5️⃣ - Configure",
        value="`/set_invite_reward 500`\n(Set coins per invite)",
        inline=False
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    embed.set_footer(text="Complete all steps for full functionality!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_drop_channel", description="[ADMIN] Set treasure drop channel")
@app_commands.describe(channel="Channel for drops")
@admin_only()
async def set_drop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("drop_channel", str(channel.id))
    embed = discord.Embed(
        title="✅ Drop Channel Set!",
        description=f"Treasure drops will appear in {channel.mention}",
        color=GREEN
    )
    embed.add_field(name="Frequency", value="Every 30 minutes", inline=True)
    embed.add_field(name="Amount", value="100-500 ⚓", inline=True)
    
    # Log setup
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Drop channel set to {channel.mention}",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "📝 Setting": "drop_channel",
            "✅ Status": "Updated"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_shop_channel", description="[ADMIN] Set shop GUI channel")
@app_commands.describe(channel="Channel for shop")
@admin_only()
async def set_shop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("shop_channel", str(channel.id))
    embed = discord.Embed(
        title="✅ Shop Channel Set!",
        description=f"Shop GUI will be sent to {channel.mention}",
        color=GREEN
    )
    embed.set_footer(text="Use /send_shop to deploy")
    
    # Log setup
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Shop channel set to {channel.mention}",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "📝 Setting": "shop_channel",
            "✅ Status": "Updated"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_log_channel", description="[ADMIN] Set logs channel")
@app_commands.describe(channel="Channel for logs")
@admin_only()
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("log_channel", str(channel.id))
    embed = discord.Embed(
        title="✅ Log Channel Set!",
        description=f"All activity will be logged to {channel.mention}",
        color=GREEN
    )
    embed.add_field(name="📋 Logged Events", value="Shop purchases, level-ups, bans, transfers, and more", inline=False)
    embed.set_footer(text="Logs are now active!")
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Log channel set to {channel.mention}",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "📝 Setting": "log_channel",
            "✅ Status": "Updated"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="send_shop", description="[ADMIN] Send interactive shop")
@admin_only()
async def send_shop(interaction: discord.Interaction):
    shop_channel_id = get_cfg("shop_channel")
    if not shop_channel_id:
        embed = discord.Embed(
            title="❌ No Shop Channel",
            description="Use `/set_shop_channel` first!",
            color=RED
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    channel = bot.get_channel(int(shop_channel_id))
    if not channel:
        return await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
    
    items = get_all_shop_items()
    
    embed = discord.Embed(
        title="⚓ SAILOR SHOP",
        description="**Click buttons below to purchase items!**\n\n💡 *Tip: Use multipliers to boost your earnings*",
        color=DARK_BLUE
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    
    # Group items
    multipliers = []
    upgrades = []
    protection = []
    special = []
    
    for item_id, item_name, price, desc, item_type, value, emoji, image in items:
        display = f"{emoji} **{item_name}** - {sc(price)} ⚓"
        if item_type == "multiplier":
            multipliers.append(display)
        elif item_type == "upgrade":
            upgrades.append(display)
        elif item_type == "protection":
            protection.append(display)
        else:
            special.append(display)
    
    if multipliers:
        embed.add_field(name="🚀 BOOSTERS", value="\n".join(multipliers), inline=False)
    if upgrades:
        embed.add_field(name="⚙️ UPGRADES", value="\n".join(upgrades), inline=False)
    if protection:
        embed.add_field(name="🛡️ PROTECTION", value="\n".join(protection), inline=False)
    if special:
        embed.add_field(name="🎁 SPECIAL", value="\n".join(special), inline=False)
    
    embed.set_footer(text="✨ Instant delivery to inventory • Ephemeral confirmation")
    
    await channel.send(embed=embed, view=ShopView())
    
    # Log shop deployment
    await log_to_channel(
        title="🛍️ SHOP DEPLOYED",
        description=f"Interactive shop sent to {channel.mention}",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "📦 Items": str(len(items)),
            "📍 Channel": channel.mention
        }
    )
    
    confirm_embed = discord.Embed(
        title="✅ Shop Deployed!",
        description=f"Interactive shop sent to {channel.mention}",
        color=GREEN
    )
    await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

@bot.tree.command(name="add_item", description="[ADMIN] Add item to shop")
@app_commands.describe(
    name="Item name",
    price="Price in ⚓",
    description="Description",
    item_type="multiplier/upgrade/bank/role/protection/mystery",
    value="Item value",
    emoji="Button emoji"
)
@admin_only()
async def add_item(interaction: discord.Interaction, name: str, price: int, description: str, item_type: str, value: str, emoji: str):
    if add_shop_item(name, price, description, item_type, value, emoji):
        embed = discord.Embed(
            title="✅ Item Added!",
            description=f"{emoji} **{name}** added to shop",
            color=GREEN
        )
        embed.add_field(name="💰 Price", value=f"{sc(price)} ⚓", inline=True)
        embed.add_field(name="📝 Type", value=item_type, inline=True)
        embed.add_field(name="📄 Description", value=description, inline=False)
        
        # Log item addition
        await log_to_channel(
            title="✨ SHOP ITEM ADDED",
            description=f"New item **{name}** added to shop",
            color=PURPLE,
            user=interaction.user,
            extra_fields={
                "💰 Price": f"{sc(price)} ⚓",
                "📝 Type": item_type,
                "📦 Emoji": emoji
            }
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="❌ Item Already Exists",
            description=f"**{name}** is already in the shop",
            color=RED
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="remove_item", description="[ADMIN] Remove item from shop")
@app_commands.describe(name="Item name")
@admin_only()
async def remove_item(interaction: discord.Interaction, name: str):
    remove_shop_item(name)
    embed = discord.Embed(
        title="✅ Item Removed!",
        description=f"**{name}** removed from shop",
        color=GREEN
    )
    
    # Log item removal
    await log_to_channel(
        title="🗑️ SHOP ITEM REMOVED",
        description=f"Item **{name}** removed from shop",
        color=RED,
        user=interaction.user,
        extra_fields={
            "📝 Item": name,
            "⏰ Time": datetime.now().strftime("%H:%M:%S")
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="add_role_item", description="[ADMIN] Add custom role to shop")
@app_commands.describe(
    name="Item name",
    price="Price in ⚓",
    description="Description",
    role="Discord role to give",
    emoji="Emoji"
)
@admin_only()
async def add_role_item(interaction: discord.Interaction, name: str, price: int, description: str, role: discord.Role, emoji: str):
    if add_shop_item(name, price, description, "role", role.name, emoji):
        embed = discord.Embed(
            title="✅ Role Item Added!",
            description=f"{emoji} **{name}** added to shop",
            color=GREEN
        )
        embed.add_field(name="💰 Price", value=f"{sc(price)} ⚓", inline=True)
        embed.add_field(name="🎖️ Role", value=role.mention, inline=True)
        embed.add_field(name="📄 Description", value=description, inline=False)
        
        # Log role item addition
        await log_to_channel(
            title="🎖️ ROLE ITEM ADDED",
            description=f"New role item **{name}** added to shop",
            color=PURPLE,
            user=interaction.user,
            extra_fields={
                "💰 Price": f"{sc(price)} ⚓",
                "🎖️ Role": role.name,
                "📦 Emoji": emoji
            }
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="❌ Item Already Exists", color=RED)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_invite_reward", description="[ADMIN] Set invite reward")
@app_commands.describe(amount="Coins per invite")
@admin_only()
async def set_invite_reward(interaction: discord.Interaction, amount: int):
    set_cfg("invite_reward", str(amount))
    embed = discord.Embed(
        title="✅ Invite Reward Updated!",
        description=f"Users now earn {sc(amount)} ⚓ per invite",
        color=GREEN
    )
    embed.set_footer(text="Updated for all future invites")
    
    # Log configuration change
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Invite reward updated to {sc(amount)} ⚓",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "📝 Setting": "invite_reward",
            "💰 New Value": f"{sc(amount)} ⚓"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_give", description="[ADMIN] Give coins to user")
@app_commands.describe(user="Target user", amount="Amount")
@admin_only()
async def admin_give(interaction: discord.Interaction, user: discord.Member, amount: int):
    add_wallet(user.id, amount, "admin_give")
    embed = discord.Embed(title="✅ Coins Given", color=GREEN)
    embed.add_field(name="👤 To", value=user.mention, inline=True)
    embed.add_field(name="💰 Amount", value=f"{sc(amount)} ⚓", inline=True)
    embed.add_field(name="📊 New Balance", value=f"{sc(get_user(user.id)[1])} ⚓", inline=True)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Log admin give
    await log_to_channel(
        title="💳 ADMIN GIVE",
        description=f"Admin {interaction.user.mention} gave coins to {user.mention}",
        color=GREEN,
        user=interaction.user,
        extra_fields={
            "👤 Recipient": user.mention,
            "💰 Amount": f"{sc(amount)} ⚓"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_take", description="[ADMIN] Take coins from user")
@app_commands.describe(user="Target user", amount="Amount")
@admin_only()
async def admin_take(interaction: discord.Interaction, user: discord.Member, amount: int):
    data = get_user(user.id)
    actual = min(amount, data[1])
    add_wallet(user.id, -actual, "admin_take")
    embed = discord.Embed(title="✅ Coins Taken", color=RED)
    embed.add_field(name="👤 From", value=user.mention, inline=True)
    embed.add_field(name="💰 Amount", value=f"{sc(actual)} ⚓", inline=True)
    embed.add_field(name="📊 New Balance", value=f"{sc(data[1] - actual)} ⚓", inline=True)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Log admin take
    await log_to_channel(
        title="💔 ADMIN TAKE",
        description=f"Admin {interaction.user.mention} took coins from {user.mention}",
        color=RED,
        user=interaction.user,
        extra_fields={
            "👤 Target": user.mention,
            "💰 Amount": f"{sc(actual)} ⚓"
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_ban", description="[ADMIN] Ban/unban user")
@app_commands.describe(user="User to ban/unban")
@admin_only()
async def admin_ban(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    if conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user.id,)).fetchone():
        conn.execute("DELETE FROM banned_users WHERE user_id=?", (user.id,))
        msg, emoji = "unbanned", "✅"
        color = GREEN
        action = "UNBANNED"
    else:
        conn.execute("INSERT INTO banned_users VALUES(?)", (user.id,))
        msg, emoji = "banned", "🚫"
        color = RED
        action = "BANNED"
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title=f"{emoji} User {msg.capitalize()}",
        description=f"{user.mention} has been {msg} from the economy",
        color=color
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Log ban
    await log_to_channel(
        title=f"{emoji} USER {action}",
        description=f"{user.mention} has been {msg}",
        color=color,
        user=interaction.user,
        extra_fields={
            "👤 Target": user.mention,
            "📝 Action": action,
            "⏰ Time": datetime.now().strftime("%H:%M:%S")
        }
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="economy_stats", description="[ADMIN] Economy statistics")
@admin_only()
async def economy_stats(interaction: discord.Interaction):
    conn = db()
    s = conn.execute("SELECT COUNT(*), SUM(wallet), SUM(bank), SUM(total_earned) FROM users").fetchone()
    b = conn.execute("SELECT COUNT(*) FROM banned_users").fetchone()[0]
    r = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    p = conn.execute("SELECT COUNT(*) FROM shop_purchases").fetchone()[0]
    conn.close()
    
    embed = discord.Embed(title="📊 ECONOMY STATISTICS", color=BLUE)
    embed.add_field(name="👥 Total Players", value=str(s[0]), inline=True)
    embed.add_field(name="🚫 Banned Users", value=str(b), inline=True)
    embed.add_field(name="💰 In Wallets", value=f"{sc(s[1] or 0)} ⚓", inline=True)
    embed.add_field(name="🏦 In Banks", value=f"{sc(s[2] or 0)} ⚓", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{sc(s[3] or 0)} ⚓", inline=True)
    embed.add_field(name="🛍️ Items Circulating", value=str(r), inline=True)
    embed.add_field(name="🛒 Total Purchases", value=str(p), inline=True)
    embed.add_field(name="🏧 Total Circulation", value=f"{sc((s[1] or 0)+(s[2] or 0))} ⚓", inline=False)
    embed.set_footer(text="Real-time data")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="view_logs", description="[ADMIN] View recent activity logs")
@admin_only()
async def view_logs(interaction: discord.Interaction):
    conn = db()
    purchases = conn.execute("SELECT user_id, item_name, price, timestamp FROM shop_purchases ORDER BY timestamp DESC LIMIT 10").fetchall()
    conn.close()
    
    embed = discord.Embed(title="📋 RECENT SHOP PURCHASES", color=BLUE)
    
    if not purchases:
        embed.description = "No purchases yet"
    else:
        for user_id, item_name, price, timestamp in purchases:
            time_str = datetime.fromtimestamp(timestamp).strftime("%m/%d %H:%M")
            embed.add_field(
                name=f"👤 User {user_id}",
                value=f"**{item_name}** - {sc(price)} ⚓\n*{time_str}*",
                inline=False
            )
    
    embed.set_footer(text="Last 10 purchases")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELP COMMAND
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="help", description="📖 View all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚓ SAILOR COINS - COMMAND GUIDE",
        description="**Complete list of all available commands**",
        color=GOLD
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    
    embed.add_field(
        name="💰 ECONOMY",
        value="`/balance` - Check wallet & bank\n`/daily` - Daily reward (24h)\n`/weekly` - Weekly bonus (7d)\n`/profile` - View profile\n`/stats` - View stats",
        inline=False
    )
    
    embed.add_field(
        name="🎣 EARNING",
        value="`/fish` - Fish (30s)\n`/mine` - Mine (45s)\n`/hunt` - Hunt (60s)\n`/work` - Work (1h)",
        inline=False
    )
    
    embed.add_field(
        name="🎰 GAMES",
        value="`/gamble` - Gamble coins\n`/slots` - Slot machine\n`/coinflip` - Coin flip\n`/highlow` - Guess higher/lower",
        inline=False
    )
    
    embed.add_field(
        name="🏦 BANKING",
        value="`/deposit` - Deposit coins\n`/withdraw` - Withdraw coins\n`/transfer` - Send to user\n`/inventory` - View items\n`/shop` - View shop",
        inline=False
    )
    
    embed.add_field(
        name="📊 INFO",
        value="`/leaderboard` - Top 10\n`/multipliers` - Active boosts",
        inline=False
    )
    
    embed.set_footer(text="Use /shop to buy boosters and upgrades!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="shop", description="🛍️ View shop preview")
async def shop_command(interaction: discord.Interaction):
    items = get_all_shop_items()
    
    embed = discord.Embed(
        title="⚓ SAILOR SHOP",
        description="**Visit the #shop channel for interactive shopping!**\n\n*Click buttons to buy instantly*",
        color=GOLD
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    
    multipliers = []
    upgrades = []
    protection = []
    special = []
    
    for item_id, item_name, price, desc, item_type, value, emoji, image in items:
        display = f"{emoji} **{item_name}** - {sc(price)} ⚓"
        if item_type == "multiplier":
            multipliers.append(display)
        elif item_type == "upgrade":
            upgrades.append(display)
        elif item_type == "protection":
            protection.append(display)
        else:
            special.append(display)
    
    if multipliers:
        embed.add_field(name="🚀 BOOSTERS", value="\n".join(multipliers), inline=False)
    if upgrades:
        embed.add_field(name="⚙️ UPGRADES", value="\n".join(upgrades), inline=False)
    if protection:
        embed.add_field(name="🛡️ PROTECTION", value="\n".join(protection), inline=False)
    if special:
        embed.add_field(name="🎁 SPECIAL", value="\n".join(special), inline=False)
    
    embed.set_footer(text="👉 Go to #shop and click buttons to purchase!")
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - ECONOMY
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="💰 Check your balance")
@app_commands.describe(user="Check another user (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    
    embed = discord.Embed(
        title=f"⚓ {target.display_name}'s WALLET",
        color=GOLD
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="👛 Wallet", value=f"{sc(data[1])} ⚓", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])} ⚓ / {sc(data[3])} ⚓", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}`\n{data[6]}/{data[5]*100} XP", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days 🏆", inline=True)
    
    embed.set_footer(text=f"Last checked: {datetime.now().strftime('%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="🌅 Claim daily reward")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid):
        embed = discord.Embed(title="🚫 Banned", description="You're economy banned.", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "daily", 86400)
    if on_cd:
        embed = discord.Embed(
            title="⏳ Already Claimed!",
            description=f"Come back in **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    data = get_user(uid)
    streak = data[7] + 1
    daily_mult = get_mult(uid, "daily")
    base = random.randint(200, 500)
    streak_bonus = min(streak * 10, 300)
    amount = int((base + streak_bonus) * daily_mult)
    add_wallet(uid, amount, "daily")
    set_cd(uid, "daily")
    conn = db()
    conn.execute("UPDATE users SET streak=?, last_daily=? WHERE user_id=?", (streak, time.time(), uid))
    conn.commit()
    conn.close()
    
    # Log daily reward
    await log_to_channel(
        title="🌅 DAILY REWARD",
        description=f"{interaction.user.mention} claimed their daily reward",
        color=GOLD,
        user=interaction.user,
        extra_fields={
            "💰 Amount": f"{sc(amount)} ⚓",
            "🔥 Streak": f"{streak} days",
            "📊 Base": f"{sc(base)} ⚓"
        }
    )
    
    embed = discord.Embed(
        title="🌅 DAILY REWARD CLAIMED!",
        color=GOLD
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💰 Base Reward", value=f"{sc(base)} ⚓", inline=True)
    embed.add_field(name="🔥 Streak Bonus", value=f"{sc(streak_bonus)} ⚓", inline=True)
    embed.add_field(name="📊 Total", value=f"{sc(amount)} ⚓", inline=True)
    embed.add_field(name="🏆 Streak", value=f"{streak} days in a row!", inline=False)
    embed.set_image(url=get_gif("win"))
    embed.set_footer(text="Come back tomorrow to keep your streak!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weekly", description="📅 Claim weekly bonus")
async def weekly(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "weekly", 604800)
    if on_cd:
        embed = discord.Embed(title="⏳ Already Claimed", description=f"Come back in **{fmt_time(rem)}**", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(1500, 3000)
    add_wallet(uid, amount, "weekly")
    set_cd(uid, "weekly")
    
    # Log weekly reward
    await log_to_channel(
        title="📅 WEEKLY REWARD",
        description=f"{interaction.user.mention} claimed their weekly reward",
        color=GOLD,
        user=interaction.user,
        extra_fields={
            "💰 Amount": f"{sc(amount)} ⚓"
        }
    )
    
    embed = discord.Embed(
        title="📅 WEEKLY BONUS!",
        description=f"You claimed {sc(amount)} ⚓!",
        color=GOLD
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=get_gif("win"))
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - EARNING (Fish/Mine/Hunt/Work)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="fish", description="🎣 Cast your line and fish")
async def fish(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "fish", 30)
    if on_cd:
        embed = discord.Embed(title="🎣 Still Fishing", description=f"Wait **{fmt_time(rem)}**", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    rod   = 1.5 if "Fishing Rod+" in inv else 1.0
    
    catches = [
        ("🥾 Old Boot", 0, 5, 6, False),
        ("🐟 Small Fish", 10, 50, 38, True),
        ("🐠 Tropical Fish", 30, 80, 25, True),
        ("🐡 Pufferfish", 50, 120, 15, True),
        ("🦑 Giant Squid", 80, 200, 8, True),
        ("🦈 Shark", 150, 350, 5, True),
        ("🐳 Blue Whale", 350, 700, 2, True),
        ("💎 Treasure Chest", 600, 1400, 1, True),
    ]
    weights = [c[3] * (luck if c[4] else max(1, 1/luck)) for c in catches]
    catch = random.choices(catches, weights=weights)[0]
    amount = int(random.randint(catch[1], catch[2]) * coins * rod) if catch[2] > 0 else 0
    if amount > 0:
        add_wallet(uid, amount, "fishing")
    set_cd(uid, "fish")
    
    # Log fishing
    if amount > 0:
        await log_to_channel(
            title="🎣 FISHING",
            description=f"{interaction.user.mention} caught {catch[0]}",
            color=BLUE,
            user=interaction.user,
            extra_fields={
                "💰 Earned": f"{sc(amount)} ⚓",
                "🐟 Catch": catch[0]
            }
        )
    
    embed = discord.Embed(title="🎣 FISHING RESULTS!", color=BLUE)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="🐟 Caught", value=catch[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓" if amount else "Nothing 😢", inline=True)
    if rod > 1:
        embed.add_field(name="⚙️ Rod Bonus", value=f"+{int((rod-1)*100)}%", inline=True)
    embed.set_image(url=get_gif("fish"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mine", description="⛏️ Descend into the mines")
async def mine(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "mine", 45)
    if on_cd:
        embed = discord.Embed(title="⛏️ Still Mining", description=f"Wait **{fmt_time(rem)}**", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    pick  = 1.5 if "Diamond Pickaxe" in inv else 1.0
    
    finds = [
        ("🪨 Stone", 5, 20, 38),
        ("🔩 Iron Ore", 20, 60, 28),
        ("🥇 Gold Nugget", 60, 150, 16),
        ("💎 Diamond", 150, 400, 9),
        ("🔮 Mystic Crystal", 300, 700, 6),
        ("⚓ Sailor's Gem", 600, 1200, 2),
        ("🌟 Ancient Artifact", 900, 2500, 1),
    ]
    weights = [f[3] * luck for f in finds]
    find   = random.choices(finds, weights=weights)[0]
    amount = int(random.randint(find[1], find[2]) * coins * pick)
    add_wallet(uid, amount, "mining")
    set_cd(uid, "mine")
    
    # Log mining
    await log_to_channel(
        title="⛏️ MINING",
        description=f"{interaction.user.mention} found {find[0]}",
        color=0x8B4513,
        user=interaction.user,
        extra_fields={
            "💰 Earned": f"{sc(amount)} ⚓",
            "💎 Find": find[0]
        }
    )
    
    embed = discord.Embed(title="⛏️ MINING RESULTS!", color=0x8B4513)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💎 Found", value=find[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓", inline=True)
    if pick > 1:
        embed.add_field(name="⚙️ Pickaxe Bonus", value=f"+{int((pick-1)*100)}%", inline=True)
    embed.set_image(url=get_gif("mine"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hunt", description="🏹 Hunt wild creatures")
async def hunt(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "hunt", 60)
    if on_cd:
        embed = discord.Embed(title="🏹 Still Hunting", description=f"Wait **{fmt_time(rem)}**", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    luck  = get_mult(uid, "luck")
    coins = get_mult(uid, "coins")
    inv   = get_inv(uid)
    bow   = 1.5 if "Hunter's Bow" in inv else 1.0
    
    animals = [
        ("🐰 Rabbit", 15, 40, 35),
        ("🦊 Fox", 40, 100, 25),
        ("🦌 Deer", 80, 200, 20),
        ("🐗 Wild Boar", 150, 350, 12),
        ("🐻 Bear", 300, 700, 5),
        ("🐉 Sea Dragon", 700, 1800, 2),
        ("🦄 Mythic Beast", 1500, 3000, 1),
    ]
    weights = [a[3] * luck for a in animals]
    animal = random.choices(animals, weights=weights)[0]
    amount = int(random.randint(animal[1], animal[2]) * coins * bow)
    add_wallet(uid, amount, "hunting")
    set_cd(uid, "hunt")
    
    # Log hunting
    await log_to_channel(
        title="🏹 HUNTING",
        description=f"{interaction.user.mention} hunted {animal[0]}",
        color=0x228B22,
        user=interaction.user,
        extra_fields={
            "💰 Earned": f"{sc(amount)} ⚓",
            "🦌 Animal": animal[0]
        }
    )
    
    embed = discord.Embed(title="🏹 HUNT RESULTS!", color=0x228B22)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="🦌 Hunted", value=animal[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓", inline=True)
    if bow > 1:
        embed.add_field(name="⚙️ Bow Bonus", value=f"+{int((bow-1)*100)}%", inline=True)
    embed.set_image(url=get_gif("hunt"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="work", description="💼 Work a shift")
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "work", 3600)
    if on_cd:
        embed = discord.Embed(title="💼 Still on Shift", description=f"Clock back in after **{fmt_time(rem)}**", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    coins = get_mult(uid, "coins")
    jobs = [
        ("🧑‍✈️ Ship Captain", 220, 450),
        ("🧑‍🍳 Ship Cook", 100, 260),
        ("🧑‍🔧 Engineer", 150, 360),
        ("🧑‍💻 Navigator", 180, 400),
        ("🏴‍☠️ Pirate Lookout", 130, 320),
        ("🎣 Pro Fisherman", 90, 230),
        ("⚓ Dock Worker", 80, 210),
        ("🗺️ Cartographer", 160, 380),
        ("🦜 Parrot Trainer", 70, 180),
        ("💣 Cannon Operator", 200, 420),
    ]
    job    = random.choice(jobs)
    amount = int(random.randint(job[1], job[2]) * coins)
    add_wallet(uid, amount, "work")
    set_cd(uid, "work")
    
    # Log work
    await log_to_channel(
        title="💼 WORK",
        description=f"{interaction.user.mention} worked as {job[0].split()[0:2]}",
        color=GREEN,
        user=interaction.user,
        extra_fields={
            "💼 Job": job[0],
            "💰 Salary": f"{sc(amount)} ⚓"
        }
    )
    
    embed = discord.Embed(title="💼 SHIFT COMPLETE!", color=GREEN)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💼 Position", value=job[0], inline=True)
    embed.add_field(name="💰 Salary", value=f"{sc(amount)} ⚓", inline=True)
    if coins > 1:
        embed.add_field(name="🚀 Multiplier", value=f"x{coins:.1f}", inline=True)
    embed.set_image(url=get_gif("work"))
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - GAMES
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="gamble", description="🎰 Gamble your coins")
@app_commands.describe(amount="Amount, or 'all'")
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
        return await interaction.response.send_message(f"❌ Bet must be 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "gamble", 12)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "gamble")
    
    if random.random() < 0.45:
        coins = get_mult(uid, "coins")
        winnings = int(bet * random.uniform(1.2, 2.5) * coins)
        add_wallet(uid, winnings - bet, "gamble_win")
        
        # Log gamble win
        await log_to_channel(
            title="🎰 GAMBLE WIN",
            description=f"{interaction.user.mention} won at gambling!",
            color=GREEN,
            user=interaction.user,
            extra_fields={
                "💵 Bet": f"{sc(bet)} ⚓",
                "🎉 Won": f"{sc(winnings)} ⚓",
                "💲 Profit": f"+{sc(winnings-bet)} ⚓"
            }
        )
        
        embed = discord.Embed(title="🎰 YOU WON!", color=GREEN)
        embed.add_field(name="💵 Bet", value=f"{sc(bet)} ⚓", inline=True)
        embed.add_field(name="🎉 Won", value=f"{sc(winnings)} ⚓", inline=True)
        embed.add_field(name="💲 Profit", value=f"+{sc(winnings-bet)} ⚓", inline=True)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -bet, "gamble_loss")
        
        # Log gamble loss
        await log_to_channel(
            title="🎰 GAMBLE LOSS",
            description=f"{interaction.user.mention} lost at gambling",
            color=RED,
            user=interaction.user,
            extra_fields={
                "💵 Bet": f"{sc(bet)} ⚓",
                "😢 Lost": f"{sc(bet)} ⚓"
            }
        )
        
        embed = discord.Embed(title="🎰 HOUSE WINS", color=RED)
        embed.add_field(name="💵 Bet", value=f"{sc(bet)} ⚓", inline=True)
        embed.add_field(name="😢 Lost", value=f"{sc(bet)} ⚓", inline=True)
        embed.set_image(url=get_gif("lose"))
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slots", description="🎡 Spin the slot machine")
@app_commands.describe(amount="Bet amount")
async def slots(interaction: discord.Interaction, amount: int):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet must be 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "slots", 15)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "slots")
    
    syms = ["⚓","🌊","🐠","💎","🌟","🏴‍☠️","🦈"]
    weights = [30, 25, 20, 10, 7, 5, 3]
    reels = random.choices(syms, weights=weights, k=3)
    display = f" {reels[0]} | {reels[1]} | {reels[2]} "
    
    if reels[0] == reels[1] == reels[2]:
        mults = {"⚓":5,"🌊":4,"🐠":3,"💎":8,"🌟":12,"🏴‍☠️":18,"🦈":15}
        m = mults.get(reels[0], 3)
        win = amount * m
        add_wallet(uid, win - amount, "slots_jackpot")
        
        # Log jackpot
        await log_to_channel(
            title="🎡 SLOTS JACKPOT!",
            description=f"{interaction.user.mention} hit the jackpot!",
            color=GOLD,
            user=interaction.user,
            extra_fields={
                "🎰 Reels": display.strip(),
                "🎉 Won": f"{sc(win)} ⚓",
                "📊 Multiplier": f"x{m}"
            }
        )
        
        embed = discord.Embed(title=f"🎰 JACKPOT!{display}", description=f"🎉 Won {sc(win)} ⚓ (x{m})!", color=GOLD)
        embed.set_image(url=get_gif("win"))
    elif reels[0]==reels[1] or reels[1]==reels[2]:
        win = int(amount * 1.5)
        add_wallet(uid, win - amount, "slots_win")
        
        embed = discord.Embed(title=f"🎰 TWO OF A KIND!{display}", description=f"Won {sc(win)} ⚓", color=GREEN)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "slots_loss")
        
        embed = discord.Embed(title=f"🎰 NO MATCH{display}", description=f"Lost {sc(amount)} ⚓", color=RED)
        embed.set_image(url=get_gif("lose"))
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="🪙 Flip a coin")
@app_commands.describe(amount="Bet amount", side="heads or tails")
async def coinflip(interaction: discord.Interaction, amount: int, side: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    if side.lower() not in ("heads","tails"):
        return await interaction.response.send_message("❌ Pick **heads** or **tails**", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet must be 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "flip", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "flip")
    result = random.choice(("heads","tails"))
    emoji = "🪙" if result=="heads" else "🌑"
    
    if result == side.lower():
        add_wallet(uid, amount, "coinflip_win")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — YOU WIN!", color=GREEN)
        embed.add_field(name="💲 Won", value=f"{sc(amount)} ⚓", inline=True)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "coinflip_loss")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — YOU LOSE!", color=RED)
        embed.add_field(name="💲 Lost", value=f"{sc(amount)} ⚓", inline=True)
        embed.set_image(url=get_gif("lose"))
    
    embed.add_field(name="📍 You Picked", value=side.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="highlow", description="🎯 Guess higher or lower")
@app_commands.describe(amount="Bet amount", guess="higher or lower")
async def highlow(interaction: discord.Interaction, amount: int, guess: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    if guess.lower() not in ("higher","lower"):
        return await interaction.response.send_message("❌ Guess **higher** or **lower**", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet must be 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "highlow", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "highlow")
    first  = random.randint(1, 10)
    second = random.randint(1, 10)
    correct = (guess.lower()=="higher" and second>first) or (guess.lower()=="lower" and second<first)
    
    if correct:
        add_wallet(uid, amount, "highlow_win")
        embed = discord.Embed(title="✅ CORRECT!", color=GREEN)
        embed.description = f"**{first}** → **{second}** ✓\n\nYou won {sc(amount)} ⚓!"
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "highlow_loss")
        embed = discord.Embed(title="❌ WRONG!", color=RED)
        embed.description = f"**{first}** → **{second}** ✗\n\nYou lost {sc(amount)} ⚓!"
        embed.set_image(url=get_gif("lose"))
    
    embed.add_field(name="📍 Your Guess", value=guess.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - BANKING & TRANSFER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="deposit", description="🏦 Deposit coins")
@app_commands.describe(amount="Amount, or 'all'")
async def deposit(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    data = get_user(uid)
    dep = data[1] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    
    if dep <= 0 or dep > data[1]:
        return await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
    
    space = data[3] - data[2]
    dep = min(dep, space)
    
    if dep <= 0:
        return await interaction.response.send_message("❌ Bank full! Buy Bank Expansion in shop", ephemeral=True)
    
    add_wallet(uid, -dep)
    add_bank(uid, dep)
    
    # Log deposit
    await log_to_channel(
        title="🏦 DEPOSIT",
        description=f"{interaction.user.mention} deposited coins",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "💰 Amount": f"{sc(dep)} ⚓",
            "🏧 New Bank": f"{sc(data[2] + dep)}/{sc(data[3])} ⚓"
        }
    )
    
    embed = discord.Embed(title="🏦 DEPOSITED!", color=GREEN)
    embed.add_field(name="💰 Amount", value=f"{sc(dep)} ⚓", inline=True)
    embed.add_field(name="🏧 New Balance", value=f"{sc(data[2] + dep)} / {sc(data[3])} ⚓", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="withdraw", description="🏦 Withdraw coins")
@app_commands.describe(amount="Amount, or 'all'")
async def withdraw(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    data = get_user(uid)
    wdr = data[2] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    
    if wdr <= 0 or wdr > data[2]:
        return await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
    
    add_bank(uid, -wdr)
    add_wallet(uid, wdr)
    
    # Log withdrawal
    await log_to_channel(
        title="🏦 WITHDRAWAL",
        description=f"{interaction.user.mention} withdrew coins",
        color=BLUE,
        user=interaction.user,
        extra_fields={
            "💰 Amount": f"{sc(wdr)} ⚓",
            "👛 New Wallet": f"{sc(data[1] + wdr)} ⚓"
        }
    )
    
    embed = discord.Embed(title="🏦 WITHDRAWN!", color=GREEN)
    embed.add_field(name="💰 Amount", value=f"{sc(wdr)} ⚓", inline=True)
    embed.add_field(name="👛 New Wallet", value=f"{sc(data[1] + wdr)} ⚓", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transfer", description="💸 Send coins to user")
@app_commands.describe(user="Recipient", amount="Amount")
async def transfer(interaction: discord.Interaction, user: discord.Member, amount: int):
    sid, rid = interaction.user.id, user.id
    
    if is_banned(sid):
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    if user.bot or sid==rid:
        return await interaction.response.send_message("❌ Invalid recipient", ephemeral=True)
    
    data = get_user(sid)
    if amount <= 0 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
    
    on_cd, rem = check_cd(sid, "transfer", 30)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(sid, "transfer")
    add_wallet(sid, -amount)
    add_wallet(rid, amount, "transfer")
    
    # Log transfer
    await log_to_channel(
        title="💸 TRANSFER",
        description=f"{interaction.user.mention} sent coins to {user.mention}",
        color=GREEN,
        user=interaction.user,
        extra_fields={
            "📥 From": interaction.user.mention,
            "📤 To": user.mention,
            "💰 Amount": f"{sc(amount)} ⚓"
        }
    )
    
    embed = discord.Embed(title="💸 TRANSFER COMPLETE!", color=GREEN)
    embed.add_field(name="📤 From", value=interaction.user.mention, inline=True)
    embed.add_field(name="📥 To", value=user.mention, inline=True)
    embed.add_field(name="💰 Amount", value=f"{sc(amount)} ⚓", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - INFO & STATS
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="profile", description="👤 View your profile")
@app_commands.describe(user="User (optional)")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    items = get_inv(target.id)
    
    embed = discord.Embed(title=f"⚓ {target.display_name.upper()}'S PROFILE", color=BLUE)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="💰 Wallet", value=f"{sc(data[1])} ⚓", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])} / {sc(data[3])} ⚓", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}`\n{data[6]}/{data[5]*100} XP", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days 🏆", inline=True)
    embed.add_field(name="🎒 Items", value=f"{len(items)} unique", inline=True)
    
    embed.set_footer(text=f"Joined: {datetime.now().strftime('%m/%d/%Y')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="🏆 Top 10 richest")
async def leaderboard(interaction: discord.Interaction):
    conn = db()
    rows = conn.execute("SELECT user_id, wallet+bank FROM users ORDER BY wallet+bank DESC LIMIT 10").fetchall()
    conn.close()
    
    embed = discord.Embed(title="🏆 SAILOR COINS LEADERBOARD", color=GOLD)
    medals = ["🥇","🥈","🥉"]
    
    for i, (uid, total) in enumerate(rows):
        m = medals[i] if i<3 else f"`#{i+1}`"
        u = interaction.guild.get_member(uid)
        name = u.display_name if u else "Unknown"
        embed.add_field(name=f"{m} {name}", value=f"{sc(total)} ⚓", inline=False)
    
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="📊 Your statistics")
async def stats(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    
    embed = discord.Embed(title="📊 YOUR STATISTICS", color=BLUE)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="💰 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="⭐ Level", value=str(data[5]), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inventory", description="🎒 View your items")
@app_commands.describe(user="User (optional)")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    items = get_inv(target.id)
    
    embed = discord.Embed(title=f"🎒 {target.display_name}'s INVENTORY", color=PURPLE)
    
    if not items:
        embed.description = "Empty! Visit `/shop` to buy items"
    else:
        for name, qty in sorted(items.items()):
            embed.add_field(name=name, value=f"x{qty}", inline=True)
    
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multipliers", description="✨ View active boosts")
async def multipliers(interaction: discord.Interaction):
    uid = interaction.user.id
    now = time.time()
    conn = db()
    rows = conn.execute(
        "SELECT mult_type, value, expires_at FROM multipliers WHERE user_id=? AND expires_at>?",
        (uid, now)
    ).fetchall()
    conn.close()
    
    embed = discord.Embed(title="✨ ACTIVE MULTIPLIERS", color=PURPLE)
    
    if not rows:
        embed.description = "No active multipliers.\n\nBuy boosts from `/shop`!"
    else:
        for mult_type, value, expires_at in rows:
            remaining = expires_at - now
            embed.add_field(
                name=f"x{value:.1f} {mult_type.capitalize()}",
                value=f"⏳ {fmt_time(remaining)}",
                inline=True
            )
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        msg = "❌ **Admin Only**\n\nYou need Administrator permissions."
    else:
        msg = f"❌ Error: `{error}`"
        print(f"[ERROR] {error}")
    try:
        await interaction.response.send_message(msg, ephemeral=True)
    except:
        await interaction.followup.send(msg, ephemeral=True)

# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set!")
    init_db()
    bot.run(TOKEN)
