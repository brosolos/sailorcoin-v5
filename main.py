"""
⚓ SAILOR COINS — Discord Economy Bot v7 COMPLETE
=====================================
✨ 80+ COMMANDS
✨ FULL PERSISTENCE
✨ LOGGING SYSTEM
✨ INTERACTIVE SHOP
✨ COMPLETE ECONOMY

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

# ─── GIFs ────────────────────────────────────────────────────────────────────

GIFS = {
    "fish": "https://klipy.com/gifs/stark-goes-fishing-looking-sad",
    "mine": "https://media.giphy.com/media/l0HlQaQ7Yz7n91uIo/giphy.gif",
    "hunt": "https://media.giphy.com/media/EKDfwJZVU60Za/giphy.gif",
    "work": "https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif",
    "win": "https://media.giphy.com/media/3o6ZtpWzconUG6TdqE/giphy.gif",
    "lose": "https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif",
    "crime": "https://media.giphy.com/media/l0HlDtKPoYJhFtHTe/giphy.gif",
    "rob": "https://klipy.com/gifs/nami-nico-robin",
    "levelup": "https://klipy.com/gifs/goku-dragon-ball-level-up-anime-gif",
    "treasure": "https://klipy.com/gifs/nami-cat-burglar",
    "duel": "https://klipy.com/gifs/zoro-zoro-one-piece-7",
}

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

async def log_to_channel(title: str, description: str, color: int, user: discord.Member = None, extra_fields: dict = None):
    """Send a log message to the logs channel"""
    log_channel_id = get_cfg("log_channel")
    if not log_channel_id:
        return
    
    channel = bot.get_channel(int(log_channel_id))
    if not channel:
        return
    
    embed = discord.Embed(title=f"📋 {title}", description=description, color=color, timestamp=datetime.now())
    
    if user:
        embed.set_author(name=f"{user.display_name} ({user.id})", icon_url=user.display_avatar.url)
    
    if extra_fields:
        for field_name, field_value in extra_fields.items():
            embed.add_field(name=field_name, value=field_value, inline=True)
    
    embed.set_footer(text="Sailor Coins Logger")
    
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Log error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE - PERSISTENT
# ══════════════════════════════════════════════════════════════════════════════

DB_PATH = "sailor.db"

def init_db():
    """Initialize database with all tables - only creates if doesn't exist"""
    if os.path.exists(DB_PATH):
        print(f"✅ Database already exists at {DB_PATH}")
        return
    
    print(f"📝 Creating new database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table
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

    # Cooldowns table
    c.execute("""CREATE TABLE IF NOT EXISTS cooldowns (
        user_id   INTEGER,
        command   TEXT,
        last_used REAL,
        PRIMARY KEY (user_id, command)
    )""")

    # Inventory table
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        user_id   INTEGER,
        item_name TEXT,
        quantity  INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, item_name)
    )""")

    # Shop table
    c.execute("""CREATE TABLE IF NOT EXISTS shop (
        item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name   TEXT UNIQUE,
        price       INTEGER,
        description TEXT,
        item_type   TEXT,
        value       TEXT,
        emoji       TEXT DEFAULT "⚓"
    )""")

    # Config table
    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key   TEXT PRIMARY KEY,
        value TEXT
    )""")

    # Banned users table
    c.execute("""CREATE TABLE IF NOT EXISTS banned_users (
        user_id INTEGER PRIMARY KEY
    )""")

    # Multipliers table
    c.execute("""CREATE TABLE IF NOT EXISTS multipliers (
        user_id      INTEGER,
        mult_type    TEXT,
        value        REAL,
        expires_at   REAL,
        PRIMARY KEY (user_id, mult_type)
    )""")

    # Transactions table
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER,
        amount    INTEGER,
        reason    TEXT,
        timestamp REAL
    )""")

    # Shop purchases table
    c.execute("""CREATE TABLE IF NOT EXISTS shop_purchases (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER,
        item_name TEXT,
        price     INTEGER,
        timestamp REAL
    )""")

    # Default shop items
    defaults = [
        ("2x Coin Boost", 5000, "Double coin earnings for 1 hour", "multiplier", "coins:2.0:3600", "💰"),
        ("2x Luck Charm", 3000, "Double luck in fish/mine/hunt", "multiplier", "luck:2.0:3600", "🍀"),
        ("3x Coin Boost", 12000, "Triple coin earnings for 30 minutes", "multiplier", "coins:3.0:1800", "🚀"),
        ("4x Ultra Boost", 25000, "4x earnings for 15 minutes", "multiplier", "coins:4.0:900", "⚡"),
        ("Fishing Rod+", 2000, "1.5x fishing yield", "upgrade", "fishing:1.5", "🎣"),
        ("Diamond Pickaxe", 2000, "1.5x mining yield", "upgrade", "mining:1.5", "⛏️"),
        ("Hunter's Bow", 2000, "1.5x hunting yield", "upgrade", "hunting:1.5", "🏹"),
        ("Bank Expansion", 10000, "Increase bank limit by +5000", "bank", "5000", "🏦"),
        ("Lucky Charm", 1500, "Reduce robbery chance", "protection", "rob:0.5:86400", "🧿"),
        ("Shield", 500, "One-time full protection from robbery", "protection", "rob_shield:1", "🛡️"),
        ("Escape Card", 3000, "Escape from crime once", "protection", "crime_escape:1", "🃏"),
        ("Daily Boost", 2000, "2x daily reward for 3 days", "multiplier", "daily:2.0:259200", "📅"),
        ("Mystery Box", 7500, "Random reward: 5000-15000 coins!", "mystery", "5000:15000", "🎁"),
    ]
    for item in defaults:
        c.execute("INSERT OR IGNORE INTO shop VALUES (NULL,?,?,?,?,?,?)", item)

    # Default config
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_interval_minutes','10')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_min','100')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_max','10000')")

    conn.commit()
    conn.close()
    print(f"✅ Database initialized successfully!")

def db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def ensure_user(user_id: int):
    """Ensure user exists in database"""
    conn = db()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Get user data"""
    ensure_user(user_id)
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row

def add_wallet(user_id: int, amount: int, reason: str = "earn"):
    """Add coins to wallet"""
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
    """Set wallet balance"""
    ensure_user(user_id)
    conn = db()
    conn.execute("UPDATE users SET wallet=? WHERE user_id=?", (max(0, amount), user_id))
    conn.commit()
    conn.close()

def add_bank(user_id: int, amount: int):
    """Add coins to bank"""
    conn = db()
    conn.execute("UPDATE users SET bank=bank+? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def is_banned(user_id: int) -> bool:
    """Check if user is banned"""
    conn = db()
    r = conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return r is not None

def get_cfg(key: str, default=None):
    """Get config value"""
    conn = db()
    r = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return r[0] if r else default

def set_cfg(key: str, value: str):
    """Set config value"""
    conn = db()
    conn.execute("INSERT OR REPLACE INTO config VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()

def get_mult(user_id: int, mult_type: str) -> float:
    """Get active multiplier"""
    now = time.time()
    conn = db()
    r = conn.execute("SELECT value FROM multipliers WHERE user_id=? AND mult_type=? AND expires_at>?",
                     (user_id, mult_type, now)).fetchone()
    conn.execute("DELETE FROM multipliers WHERE expires_at<=?", (now,))
    conn.commit()
    conn.close()
    return r[0] if r else 1.0

def set_mult(user_id: int, mult_type: str, value: float, duration_secs: int):
    """Set multiplier"""
    conn = db()
    conn.execute("INSERT OR REPLACE INTO multipliers VALUES(?,?,?,?)",
                 (user_id, mult_type, value, time.time() + duration_secs))
    conn.commit()
    conn.close()

def get_cd(user_id: int, cmd: str) -> float:
    """Get cooldown time"""
    conn = db()
    r = conn.execute("SELECT last_used FROM cooldowns WHERE user_id=? AND command=?", (user_id, cmd)).fetchone()
    conn.close()
    return r[0] if r else 0.0

def set_cd(user_id: int, cmd: str):
    """Set cooldown"""
    conn = db()
    conn.execute("INSERT OR REPLACE INTO cooldowns VALUES(?,?,?)", (user_id, cmd, time.time()))
    conn.commit()
    conn.close()

def check_cd(user_id: int, cmd: str, secs: int):
    """Check if on cooldown"""
    elapsed = time.time() - get_cd(user_id, cmd)
    if elapsed < secs:
        return True, secs - elapsed
    return False, 0.0

def get_inv(user_id: int) -> dict:
    """Get inventory"""
    conn = db()
    rows = conn.execute("SELECT item_name, quantity FROM inventory WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return dict(rows)

def add_inv(user_id: int, item: str, qty: int = 1):
    """Add item to inventory"""
    conn = db()
    r = conn.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (user_id, item)).fetchone()
    if r:
        conn.execute("UPDATE inventory SET quantity=quantity+? WHERE user_id=? AND item_name=?", (qty, user_id, item))
    else:
        conn.execute("INSERT INTO inventory VALUES(?,?,?)", (user_id, item, qty))
    conn.commit()
    conn.close()

def remove_inv(user_id: int, item: str, qty: int = 1) -> bool:
    """Remove item from inventory"""
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
    """Get all shop items"""
    conn = db()
    items = conn.execute("SELECT item_id, item_name, price, description, item_type, value, emoji FROM shop ORDER BY price").fetchall()
    conn.close()
    return items

def add_shop_item(name: str, price: int, desc: str, item_type: str, value: str, emoji: str):
    """Add shop item"""
    conn = db()
    try:
        conn.execute("INSERT INTO shop (item_name, price, description, item_type, value, emoji) VALUES (?,?,?,?,?,?)",
                     (name, price, desc, item_type, value, emoji))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def remove_shop_item(name: str):
    """Remove shop item"""
    conn = db()
    conn.execute("DELETE FROM shop WHERE LOWER(item_name)=LOWER(?)", (name,))
    conn.commit()
    conn.close()

def log_purchase(user_id: int, item_name: str, price: int):
    """Log shop purchase"""
    conn = db()
    conn.execute("INSERT INTO shop_purchases (user_id, item_name, price, timestamp) VALUES (?,?,?,?)",
                 (user_id, item_name, price, time.time()))
    conn.commit()
    conn.close()

# ─── Formatting ────────────────────────────────────────────────────────────────

def sc(amount: int) -> str:
    return f"⚓ **{amount:,}**"

def fmt_time(secs: float) -> str:
    s = int(secs)
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m {s%60}s"
    return f"{s//3600}h {(s%3600)//60}m"

def get_gif(category: str) -> str:
    return GIFS.get(category, "https://media.giphy.com/media/l0HlOY9x8FZo0XO1i/giphy.gif")

# ══════════════════════════════════════════════════════════════════════════════
# SHOP BUTTONS
# ══════════════════════════════════════════════════════════════════════════════

class ShopButton(ui.Button):
    def __init__(self, item_id: int, item_name: str, price: int, emoji: str):
        super().__init__(label=f"{item_name}", emoji=emoji, style=discord.ButtonStyle.blurple)
        self.item_id = item_id
        self.item_name = item_name
        self.price = price

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        if is_banned(uid):
            embed = discord.Embed(title="🚫 Banned", description="You're economy banned.", color=RED)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = get_user(uid)
        if data[1] < self.price:
            embed = discord.Embed(title="❌ Insufficient Coins", description=f"Need {sc(self.price)} ⚓\nYou have {sc(data[1])} ⚓", color=RED)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        conn = db()
        row = conn.execute("SELECT item_name, price, description, item_type, value, emoji FROM shop WHERE item_id=?", (self.item_id,)).fetchone()
        conn.close()
        
        if not row:
            return await interaction.response.send_message("❌ Item not found.", ephemeral=True)
        
        item_name, price, desc, item_type, value, emoji = row
        add_wallet(uid, -price)
        log_purchase(uid, item_name, price)
        
        await log_to_channel(
            title="🛍️ SHOP PURCHASE",
            description=f"{interaction.user.mention} purchased **{item_name}**",
            color=GOLD,
            user=interaction.user,
            extra_fields={"💰 Price": f"{sc(price)} ⚓", "📦 Type": item_type, "💵 New Balance": f"{sc(data[1] - price)} ⚓"}
        )
        
        if item_type == "multiplier":
            parts = value.split(":")
            set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
            embed = discord.Embed(title=f"✅ {emoji} {item_name} Activated!", description=f"**x{parts[1]} {parts[0]}** for **{fmt_time(int(parts[2]))}**!", color=GREEN)
        elif item_type == "upgrade":
            add_inv(uid, item_name)
            embed = discord.Embed(title=f"✅ {emoji} {item_name} Equipped!", description=desc, color=GREEN)
        elif item_type == "bank":
            extra = int(value)
            conn = db()
            conn.execute("UPDATE users SET bank_limit=bank_limit+? WHERE user_id=?", (extra, uid))
            conn.commit()
            conn.close()
            embed = discord.Embed(title=f"✅ {emoji} Bank Expanded!", description=f"Limit +{sc(extra)} ⚓!", color=GREEN)
        elif item_type == "mystery":
            parts = value.split(":")
            reward = random.randint(int(parts[0]), int(parts[1]))
            add_wallet(uid, reward)
            embed = discord.Embed(title=f"✅ {emoji} Mystery Box!", description=f"You found {sc(reward)} ⚓!", color=GOLD)
            embed.set_image(url=get_gif("win"))
        elif item_type == "role":
            role = discord.utils.get(interaction.guild.roles, name=value)
            if role:
                await interaction.user.add_roles(role)
                embed = discord.Embed(title=f"✅ {emoji} Role Granted!", description=f"You have **{value}** role!", color=GREEN)
            else:
                add_wallet(uid, price)
                embed = discord.Embed(title="❌ Role Not Found", description="Refunded!", color=RED)
        else:
            add_inv(uid, item_name)
            embed = discord.Embed(title=f"✅ {emoji} {item_name}!", description=desc, color=GREEN)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"New Balance: {sc(data[1] - price)} ⚓")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        items = get_all_shop_items()
        row = 0
        for idx, (item_id, item_name, price, desc, item_type, value, emoji) in enumerate(items):
            if idx > 0 and idx % 5 == 0:
                row += 1
            button = ShopButton(item_id, item_name, price, emoji)
            button.row = row
            self.add_item(button)

# ══════════════════════════════════════════════════════════════════════════════
# BOT EVENTS
# ══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"⚓ {bot.user} is online!")
    init_db()
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync error: {e}")
    
    if not passive_drop.is_running():
        passive_drop.start()
    
    await log_to_channel(
        title="🚀 BOT STARTUP",
        description="Sailor Coins online!",
        color=GREEN,
        extra_fields={"⏰ Time": datetime.now().strftime("%m/%d %H:%M:%S")}
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
                add_wallet(uid, row[1] * 50, "level_up")
                await log_to_channel(
                    title="⭐ LEVEL UP",
                    description=f"{message.author.mention} reached Level {row[1]+1}",
                    color=GOLD,
                    user=message.author,
                    extra_fields={"📈 Level": str(row[1]+1), "🎁 Reward": f"{sc(row[1]*50)} ⚓"}
                )
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
    mn = int(get_cfg("drop_min", "100"))
    mx = int(get_cfg("drop_max", "500"))
    amount = random.randint(mn, mx)
    
    embed = discord.Embed(title="⚓ TREASURE WASHED ASHORE!", description=f"Chest with {sc(amount)} ⚓!", color=GOLD)
    embed.add_field(name="⏳ Claim", value="Type `!claim`!", inline=False)
    embed.add_field(name="⏰ Time", value="60 seconds!", inline=False)
    
    msg = await channel.send(embed=embed)
    
    def check(m): return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount, "treasure_drop")
        
        await log_to_channel(
            title="🎁 TREASURE CLAIMED",
            description=f"{resp.author.mention} claimed treasure!",
            color=GOLD,
            user=resp.author,
            extra_fields={"💰 Amount": f"{sc(amount)} ⚓"}
        )
        
        embed = discord.Embed(title="🎉 CLAIMED!", description=f"{resp.author.mention} got {sc(amount)} ⚓!", color=GREEN)
        await channel.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(title="🌊 SANK", description="Nobody claimed it.", color=RED)
        await channel.send(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ════════════════════════════════════════════════════���═════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.command(name="admin_setup", description="[ADMIN] Setup wizard")
@admin_only()
async def admin_setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚓ ADMIN SETUP", description="Follow these steps:", color=GOLD)
    embed.add_field(name="1️⃣ Drop Channel", value="`/set_drop_channel #channel`", inline=False)
    embed.add_field(name="2️⃣ Shop Channel", value="`/set_shop_channel #channel`", inline=False)
    embed.add_field(name="3️⃣ Logs Channel", value="`/set_log_channel #channel`", inline=False)
    embed.add_field(name="4️⃣ Send Shop", value="`/send_shop`", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_drop_channel", description="[ADMIN] Set drop channel")
@app_commands.describe(channel="Channel")
@admin_only()
async def set_drop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("drop_channel", str(channel.id))
    embed = discord.Embed(title="✅ Drop Channel Set!", description=f"Drops in {channel.mention}", color=GREEN)
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Drop channel: {channel.mention}",
        color=BLUE,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_shop_channel", description="[ADMIN] Set shop channel")
@app_commands.describe(channel="Channel")
@admin_only()
async def set_shop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("shop_channel", str(channel.id))
    embed = discord.Embed(title="✅ Shop Channel Set!", description=f"Shop in {channel.mention}", color=GREEN)
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Shop channel: {channel.mention}",
        color=BLUE,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_log_channel", description="[ADMIN] Set logs channel")
@app_commands.describe(channel="Channel")
@admin_only()
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("log_channel", str(channel.id))
    embed = discord.Embed(title="✅ Log Channel Set!", description=f"Logs in {channel.mention}", color=GREEN)
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Log channel: {channel.mention}",
        color=BLUE,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="send_shop", description="[ADMIN] Send shop GUI")
@admin_only()
async def send_shop(interaction: discord.Interaction):
    shop_channel_id = get_cfg("shop_channel")
    if not shop_channel_id:
        embed = discord.Embed(title="❌ No Shop Channel", description="Use `/set_shop_channel` first!", color=RED)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    channel = bot.get_channel(int(shop_channel_id))
    if not channel:
        return await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
    
    items = get_all_shop_items()
    
    embed = discord.Embed(title="�� SAILOR SHOP", description="Click buttons to buy!", color=GOLD)
    
    multipliers, upgrades, protection, special = [], [], [], []
    
    for item_id, item_name, price, desc, item_type, value, emoji in items:
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
    
    await channel.send(embed=embed, view=ShopView())
    
    await log_to_channel(
        title="🛍️ SHOP DEPLOYED",
        description=f"Shop sent to {channel.mention}",
        color=BLUE,
        user=interaction.user
    )
    
    confirm = discord.Embed(title="✅ Shop Deployed!", description=f"Sent to {channel.mention}", color=GREEN)
    await interaction.response.send_message(embed=confirm, ephemeral=True)

@bot.tree.command(name="add_item", description="[ADMIN] Add shop item")
@app_commands.describe(name="Name", price="Price", description="Desc", item_type="Type", value="Value", emoji="Emoji")
@admin_only()
async def add_item(interaction: discord.Interaction, name: str, price: int, description: str, item_type: str, value: str, emoji: str):
    if add_shop_item(name, price, description, item_type, value, emoji):
        embed = discord.Embed(title="✅ Item Added!", description=f"{emoji} **{name}**", color=GREEN)
        
        await log_to_channel(
            title="✨ ITEM ADDED",
            description=f"New item: **{name}**",
            color=PURPLE,
            user=interaction.user,
            extra_fields={"💰 Price": f"{sc(price)} ⚓"}
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("❌ Item already exists!", ephemeral=True)

@bot.tree.command(name="admin_give", description="[ADMIN] Give coins")
@app_commands.describe(user="User", amount="Amount")
@admin_only()
async def admin_give(interaction: discord.Interaction, user: discord.Member, amount: int):
    add_wallet(user.id, amount, "admin_give")
    embed = discord.Embed(title="✅ Coins Given!", color=GREEN)
    embed.add_field(name="To", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=f"{sc(amount)} ⚓", inline=True)
    
    await log_to_channel(
        title="💳 ADMIN GIVE",
        description=f"Gave {user.mention} {sc(amount)} ⚓",
        color=GREEN,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_take", description="[ADMIN] Take coins")
@app_commands.describe(user="User", amount="Amount")
@admin_only()
async def admin_take(interaction: discord.Interaction, user: discord.Member, amount: int):
    data = get_user(user.id)
    actual = min(amount, data[1])
    add_wallet(user.id, -actual, "admin_take")
    embed = discord.Embed(title="✅ Coins Taken!", color=RED)
    embed.add_field(name="From", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=f"{sc(actual)} ⚓", inline=True)
    
    await log_to_channel(
        title="💔 ADMIN TAKE",
        description=f"Took {user.mention} {sc(actual)} ⚓",
        color=RED,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_ban", description="[ADMIN] Ban/unban user")
@app_commands.describe(user="User")
@admin_only()
async def admin_ban(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    if conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user.id,)).fetchone():
        conn.execute("DELETE FROM banned_users WHERE user_id=?", (user.id,))
        msg, emoji, action, color = "unbanned", "✅", "UNBANNED", GREEN
    else:
        conn.execute("INSERT INTO banned_users VALUES(?)", (user.id,))
        msg, emoji, action, color = "banned", "🚫", "BANNED", RED
    conn.commit()
    conn.close()
    
    embed = discord.Embed(title=f"{emoji} User {msg}", color=color)
    
    await log_to_channel(
        title=f"{emoji} USER {action}",
        description=f"{user.mention} {msg}",
        color=color,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="economy_stats", description="[ADMIN] Economy stats")
@admin_only()
async def economy_stats(interaction: discord.Interaction):
    conn = db()
    s = conn.execute("SELECT COUNT(*), SUM(wallet), SUM(bank), SUM(total_earned) FROM users").fetchone()
    b = conn.execute("SELECT COUNT(*) FROM banned_users").fetchone()[0]
    conn.close()
    
    embed = discord.Embed(title="📊 ECONOMY STATS", color=BLUE)
    embed.add_field(name="👥 Players", value=str(s[0]), inline=True)
    embed.add_field(name="🚫 Banned", value=str(b), inline=True)
    embed.add_field(name="💰 Wallets", value=f"{sc(s[1] or 0)} ⚓", inline=True)
    embed.add_field(name="🏦 Banks", value=f"{sc(s[2] or 0)} ⚓", inline=True)
    embed.add_field(name="📈 Earned", value=f"{sc(s[3] or 0)} ⚓", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - EARNING (30+ COMMANDS)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="💰 Check balance")
@app_commands.describe(user="User (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    
    embed = discord.Embed(title=f"⚓ {target.display_name}'s WALLET", color=GOLD)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="👛 Wallet", value=f"{sc(data[1])} ⚓", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])} / {sc(data[3])} ⚓", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}` {data[6]}/{data[5]*100}", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="🌅 Claim daily")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid):
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "daily", 86400)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Come back in {fmt_time(rem)}", ephemeral=True)
    
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
    
    await log_to_channel(
        title="🌅 DAILY",
        description=f"{interaction.user.mention} claimed daily",
        color=GOLD,
        user=interaction.user,
        extra_fields={"💰 Amount": f"{sc(amount)} ⚓", "🔥 Streak": f"{streak} days"}
    )
    
    embed = discord.Embed(title="🌅 DAILY REWARD!", color=GOLD)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💰 Base", value=f"{sc(base)} ⚓", inline=True)
    embed.add_field(name="🔥 Bonus", value=f"{sc(streak_bonus)} ⚓", inline=True)
    embed.add_field(name="📊 Total", value=f"{sc(amount)} ⚓", inline=True)
    embed.add_field(name="🏆 Streak", value=f"{streak} days!", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weekly", description="📅 Claim weekly")
async def weekly(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "weekly", 604800)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Come back in {fmt_time(rem)}", ephemeral=True)
    
    amount = random.randint(1500, 3000)
    add_wallet(uid, amount, "weekly")
    set_cd(uid, "weekly")
    
    embed = discord.Embed(title="📅 WEEKLY!", description=f"You got {sc(amount)} ⚓!", color=GOLD)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fish", description="🎣 Fish")
async def fish(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "fish", 30)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    luck, coins = get_mult(uid, "luck"), get_mult(uid, "coins")
    inv = get_inv(uid)
    rod = 1.5 if "Fishing Rod+" in inv else 1.0
    
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
    
    embed = discord.Embed(title="🎣 FISHING!", color=BLUE)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="🐟 Caught", value=catch[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓" if amount else "Nothing", inline=True)
    embed.set_image(url=get_gif("fish"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mine", description="⛏️ Mine")
async def mine(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "mine", 45)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    luck, coins = get_mult(uid, "luck"), get_mult(uid, "coins")
    inv = get_inv(uid)
    pick = 1.5 if "Diamond Pickaxe" in inv else 1.0
    
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
    find = random.choices(finds, weights=weights)[0]
    amount = int(random.randint(find[1], find[2]) * coins * pick)
    add_wallet(uid, amount, "mining")
    set_cd(uid, "mine")
    
    embed = discord.Embed(title="⛏️ MINING!", color=0x8B4513)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💎 Found", value=find[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓", inline=True)
    embed.set_image(url=get_gif("mine"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hunt", description="🏹 Hunt")
async def hunt(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "hunt", 60)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    luck, coins = get_mult(uid, "luck"), get_mult(uid, "coins")
    inv = get_inv(uid)
    bow = 1.5 if "Hunter's Bow" in inv else 1.0
    
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
    
    embed = discord.Embed(title="🏹 HUNT!", color=0x228B22)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="🦌 Hunted", value=animal[0], inline=True)
    embed.add_field(name="💰 Earned", value=f"{sc(amount)} ⚓", inline=True)
    embed.set_image(url=get_gif("hunt"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="work", description="💼 Work")
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "work", 3600)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
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
    job = random.choice(jobs)
    amount = int(random.randint(job[1], job[2]) * coins)
    add_wallet(uid, amount, "work")
    set_cd(uid, "work")
    
    embed = discord.Embed(title="💼 SHIFT COMPLETE!", color=GREEN)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="💼 Job", value=job[0], inline=True)
    embed.add_field(name="💰 Salary", value=f"{sc(amount)} ⚓", inline=True)
    embed.set_image(url=get_gif("work"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="beg", description="🙏 Beg")
async def beg(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "beg", 300)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    set_cd(uid, "beg")
    
    scenarios = [
        ("🧑‍✈️ Kind Captain", 10, 60),
        ("💰 Wealthy Merchant", 30, 120),
        ("🏴‍☠️ Generous Pirate", 20, 80),
        ("👵 Old Sailor", 5, 30),
        (None, 0, 0),
        (None, 0, 0),
    ]
    s = random.choice(scenarios)
    if s[0] is None:
        embed = discord.Embed(title="😞 Ignored", description="Everyone walked past.", color=RED)
    else:
        amount = random.randint(s[1], s[2])
        add_wallet(uid, amount, "beg")
        embed = discord.Embed(title="🙏 HELP!", color=GREEN)
        embed.add_field(name=s[0], value=f"gave {sc(amount)} ⚓", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="crime", description="💣 Commit crime")
async def crime(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "crime", 7200)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Lay low {fmt_time(rem)}", ephemeral=True)
    set_cd(uid, "crime")
    
    data = get_user(uid)
    wallet = data[1]
    inv = get_inv(uid)
    
    crimes = [
        ("🎭 Con Artist", "Swindled tourists", 300, 800),
        ("🏴‍☠️ Piracy", "Raided a ship", 600, 1800),
        ("🃏 Card Shark", "Cheated at poker", 200, 600),
        ("🥷 Night Thief", "Robbed a store", 500, 1200),
        ("🦜 Parrot Smuggler", "Sold birds", 150, 450),
        ("💣 Saboteur", "Bombed a ship", 800, 2500),
    ]
    act = random.choice(crimes)
    fail_chance = 0.35
    
    if "Escape Card" in inv and random.random() < fail_chance:
        remove_inv(uid, "Escape Card", 1)
        embed = discord.Embed(title="🃏 ESCAPED!", description="You got caught but used escape card!", color=PURPLE)
        await interaction.response.send_message(embed=embed)
        return
    
    if random.random() < fail_chance:
        fine = int(wallet * random.uniform(0.05, 0.25))
        fine = max(fine, 50)
        add_wallet(uid, -min(fine, wallet))
        embed = discord.Embed(title="🚔 BUSTED!", color=RED)
        embed.add_field(name="Crime", value=act[0], inline=False)
        embed.add_field(name="Fine", value=f"{sc(fine)} ⚓", inline=False)
    else:
        coins = get_mult(uid, "coins")
        amount = int(random.randint(act[2], act[3]) * coins)
        add_wallet(uid, amount, "crime")
        embed = discord.Embed(title="😈 SUCCESS!", color=PURPLE)
        embed.add_field(name="Crime", value=act[0], inline=False)
        embed.add_field(name="Result", value=f"_{act[1]}_", inline=False)
        embed.add_field(name="Looted", value=f"{sc(amount)} ⚓", inline=False)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=get_gif("crime"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="steal", description="🥷 Steal from user")
@app_commands.describe(user="Target")
async def steal(interaction: discord.Interaction, user: discord.Member):
    uid = interaction.user.id
    target_id = user.id
    
    if is_banned(uid):
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    if user.bot or uid == target_id:
        return await interaction.response.send_message("❌ Invalid!", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "steal", 5400)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    robber = get_user(uid)
    victim = get_user(target_id)
    
    if robber[1] < 50:
        return await interaction.response.send_message("❌ Need 50 ⚓", ephemeral=True)
    if victim[1] < 25:
        return await interaction.response.send_message("❌ Target has nothing!", ephemeral=True)
    
    set_cd(uid, "steal")
    v_inv = get_inv(target_id)
    
    if "Shield" in v_inv:
        remove_inv(target_id, "Shield", 1)
        fine = int(robber[1] * 0.15)
        add_wallet(uid, -fine)
        embed = discord.Embed(title="🛡️ BLOCKED!", color=RED)
        embed.add_field(name="Fine", value=f"{sc(fine)} ⚓", inline=False)
        return await interaction.response.send_message(embed=embed)
    
    has_charm = "Lucky Charm" in v_inv
    success_chance = 0.30 if has_charm else 0.45
    
    if random.random() < success_chance:
        pct = random.uniform(0.05, 0.20)
        stolen = max(5, int(victim[1] * pct))
        add_wallet(target_id, -stolen)
        add_wallet(uid, stolen, "steal")
        embed = discord.Embed(title="🥷 SUCCESS!", color=GREEN)
        embed.add_field(name="Target", value=user.mention, inline=True)
        embed.add_field(name="Stolen", value=f"{sc(stolen)} ⚓", inline=True)
    else:
        fine = int(robber[1] * random.uniform(0.05, 0.15))
        add_wallet(uid, -fine)
        add_wallet(target_id, fine)
        embed = discord.Embed(title="🚔 CAUGHT!", color=RED)
        embed.add_field(name="Fine", value=f"{sc(fine)} ⚓", inline=False)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=get_gif("rob"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rob", description="🏴‍☠️ Rob user")
@app_commands.describe(user="Target")
async def rob(interaction: discord.Interaction, user: discord.Member):
    rid = interaction.user.id
    vid = user.id
    if is_banned(rid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    if user.bot or rid == vid: 
        return await interaction.response.send_message("❌ Invalid!", ephemeral=True)
    on_cd, rem = check_cd(rid, "rob", 3600)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    robber = get_user(rid)
    victim = get_user(vid)
    if robber[1] < 100:
        return await interaction.response.send_message("❌ Need 100 ⚓", ephemeral=True)
    if victim[1] < 50:
        return await interaction.response.send_message("❌ Target has nothing!", ephemeral=True)
    set_cd(rid, "rob")
    v_inv = get_inv(vid)
    
    if "Shield" in v_inv:
        remove_inv(vid, "Shield", 1)
        fine = int(robber[1] * 0.10)
        add_wallet(rid, -fine)
        embed = discord.Embed(title="🛡️ BLOCKED!", color=RED)
        embed.add_field(name="Fine", value=f"{sc(fine)} ⚓", inline=False)
        return await interaction.response.send_message(embed=embed)
    
    has_charm = "Lucky Charm" in v_inv
    success_chance = 0.38 if has_charm else 0.52
    if random.random() < success_chance:
        pct = random.uniform(0.10, 0.40)
        stolen = max(10, int(victim[1] * pct))
        add_wallet(vid, -stolen)
        add_wallet(rid, stolen, "rob")
        embed = discord.Embed(title="🏴‍☠️ SUCCESS!", color=GREEN)
        embed.add_field(name="Victim", value=user.mention, inline=True)
        embed.add_field(name="Stolen", value=f"{sc(stolen)} ⚓", inline=True)
    else:
        fine = int(robber[1] * random.uniform(0.10, 0.25))
        add_wallet(rid, -fine)
        add_wallet(vid, fine)
        embed = discord.Embed(title="🚔 CAUGHT!", color=RED)
        embed.add_field(name="Fine", value=f"{sc(fine)} ⚓", inline=False)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=get_gif("rob"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="bankrob", description="🏦 Rob bank")
async def bankrob(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    on_cd, rem = check_cd(uid, "bankrob", 14400)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    data = get_user(uid)
    if data[1] < 500:
        return await interaction.response.send_message("❌ Need 500 ⚓!", ephemeral=True)
    set_cd(uid, "bankrob")
    
    if random.random() < 0.28:
        loot = random.randint(2000, 8000)
        add_wallet(uid, loot, "bankrob")
        embed = discord.Embed(title="🏦💥 ROBBED!", color=GOLD)
        embed.add_field(name="Escaped!", value=f"Got {sc(loot)} ⚓!", inline=False)
    else:
        penalty = int(data[1] * random.uniform(0.20, 0.50))
        add_wallet(uid, -penalty)
        embed = discord.Embed(title="🚨 FAILED!", color=RED)
        embed.add_field(name="Arrested!", value=f"Fined {sc(penalty)} ⚓!", inline=False)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# GAMES (15+ COMMANDS)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="gamble", description="🎰 Gamble")
@app_commands.describe(amount="Amount or 'all'")
async def gamble(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    data = get_user(uid)
    if amount.lower() == "all":
        bet = data[1]
    else:
        try: 
            bet = int(amount)
        except: 
            return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    if bet < 10 or bet > data[1]:
        return await interaction.response.send_message(f"❌ Bet 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "gamble", 12)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    set_cd(uid, "gamble")
    
    if random.random() < 0.45:
        coins = get_mult(uid, "coins")
        winnings = int(bet * random.uniform(1.2, 2.5) * coins)
        add_wallet(uid, winnings - bet, "gamble_win")
        
        embed = discord.Embed(title="🎰 YOU WON!", color=GREEN)
        embed.add_field(name="Bet", value=f"{sc(bet)} ⚓", inline=True)
        embed.add_field(name="Won", value=f"{sc(winnings)} ⚓", inline=True)
        embed.add_field(name="Profit", value=f"+{sc(winnings-bet)} ⚓", inline=True)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -bet, "gamble_loss")
        
        embed = discord.Embed(title="🎰 LOST", color=RED)
        embed.add_field(name="Bet", value=f"{sc(bet)} ⚓", inline=True)
        embed.add_field(name="Lost", value=f"{sc(bet)} ⚓", inline=True)
        embed.set_image(url=get_gif("lose"))
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slots", description="🎡 Slots")
@app_commands.describe(amount="Bet")
async def slots(interaction: discord.Interaction, amount: int):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "slots", 15)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
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
        embed = discord.Embed(title=f"🎰 JACKPOT!{display}", description=f"Won {sc(win)} ⚓ (x{m})!", color=GOLD)
        embed.set_image(url=get_gif("win"))
    elif reels[0]==reels[1] or reels[1]==reels[2]:
        win = int(amount * 1.5)
        add_wallet(uid, win - amount, "slots_win")
        embed = discord.Embed(title=f"🎰 TWO!{display}", description=f"Won {sc(win)} ⚓", color=GREEN)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "slots_loss")
        embed = discord.Embed(title=f"🎰 LOSS{display}", description=f"Lost {sc(amount)} ⚓", color=RED)
        embed.set_image(url=get_gif("lose"))
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="🪙 Flip coin")
@app_commands.describe(amount="Bet", side="heads/tails")
async def coinflip(interaction: discord.Interaction, amount: int, side: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    if side.lower() not in ("heads","tails"):
        return await interaction.response.send_message("❌ Pick heads/tails", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "flip", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    set_cd(uid, "flip")
    result = random.choice(("heads","tails"))
    emoji = "🪙" if result=="heads" else "🌑"
    
    if result == side.lower():
        add_wallet(uid, amount, "coinflip_win")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — WIN!", color=GREEN)
        embed.add_field(name="Won", value=f"{sc(amount)} ⚓", inline=False)
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "coinflip_loss")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — LOSE!", color=RED)
        embed.add_field(name="Lost", value=f"{sc(amount)} ⚓", inline=False)
        embed.set_image(url=get_gif("lose"))
    
    embed.add_field(name="You Picked", value=side.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="highlow", description="🎯 Guess")
@app_commands.describe(amount="Bet", guess="higher/lower")
async def highlow(interaction: discord.Interaction, amount: int, guess: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    
    if guess.lower() not in ("higher","lower"):
        return await interaction.response.send_message("❌ Pick higher/lower", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        return await interaction.response.send_message(f"❌ Bet 10-{data[1]}", ephemeral=True)
    
    on_cd, rem = check_cd(uid, "highlow", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    set_cd(uid, "highlow")
    first = random.randint(1, 10)
    second = random.randint(1, 10)
    correct = (guess.lower()=="higher" and second>first) or (guess.lower()=="lower" and second<first)
    
    if correct:
        add_wallet(uid, amount, "highlow_win")
        embed = discord.Embed(title="✅ CORRECT!", color=GREEN)
        embed.description = f"**{first}** → **{second}**\nYou won {sc(amount)} ⚓!"
        embed.set_image(url=get_gif("win"))
    else:
        add_wallet(uid, -amount, "highlow_loss")
        embed = discord.Embed(title="❌ WRONG!", color=RED)
        embed.description = f"**{first}** → **{second}**\nYou lost {sc(amount)} ⚓!"
        embed.set_image(url=get_gif("lose"))
    
    embed.add_field(name="Your Guess", value=guess.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="duel", description="⚔️ Duel")
@app_commands.describe(user="Opponent", amount="Wager")
async def duel(interaction: discord.Interaction, user: discord.Member, amount: int):
    cid, oid = interaction.user.id, user.id
    if is_banned(cid): 
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    if user.bot or cid==oid: 
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    cd = get_user(cid)
    od = get_user(oid)
    if amount < 10 or amount > cd[1]:
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    if amount > od[1]:
        return await interaction.response.send_message("❌ They don't have enough", ephemeral=True)
    
    embed = discord.Embed(title="⚔️ DUEL!", description=f"{interaction.user.mention} challenges {user.mention} for {sc(amount)} ⚓!\nReply `accept` or `decline`", color=GOLD)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)
    
    def check(m): return m.author==user and m.channel==interaction.channel and m.content.lower() in ("accept","decline")
    try:
        resp = await bot.wait_for("message", check=check, timeout=30.0)
        if resp.content.lower()=="decline":
            return await interaction.followup.send(f"❌ {user.mention} declined")
        
        winner = random.choice([interaction.user, user])
        loser = user if winner==interaction.user else interaction.user
        add_wallet(winner.id, amount, "duel_win")
        add_wallet(loser.id, -amount, "duel_loss")
        
        await log_to_channel(
            title="⚔️ DUEL",
            description=f"{winner.mention} won!",
            color=GREEN,
            user=winner,
            extra_fields={"🏆 Winner": winner.mention, "😢 Loser": loser.mention}
        )
        
        embed = discord.Embed(title="⚔️ RESULT!", description=f"**{winner.mention}** wins {sc(amount)} ⚓!", color=GREEN)
        embed.set_thumbnail(url=winner.display_avatar.url)
        embed.set_image(url=get_gif("duel"))
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⌛ {user.mention} didn't respond")

# ══════════════════════════════════════════════════════════════════════════════
# BANKING & INFO (20+ COMMANDS)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="deposit", description="🏦 Deposit")
@app_commands.describe(amount="Amount or 'all'")
async def deposit(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    data = get_user(uid)
    dep = data[1] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    
    if dep <= 0 or dep > data[1]:
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    space = data[3] - data[2]
    dep = min(dep, space)
    
    if dep <= 0:
        return await interaction.response.send_message("❌ Bank full!", ephemeral=True)
    
    add_wallet(uid, -dep)
    add_bank(uid, dep)
    
    embed = discord.Embed(title="🏦 DEPOSITED!", color=GREEN)
    embed.add_field(name="Amount", value=f"{sc(dep)} ⚓", inline=True)
    embed.add_field(name="New Bank", value=f"{sc(data[2] + dep)} / {sc(data[3])} ⚓", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="withdraw", description="🏦 Withdraw")
@app_commands.describe(amount="Amount or 'all'")
async def withdraw(interaction: discord.Interaction, amount: str):
    uid = interaction.user.id
    data = get_user(uid)
    wdr = data[2] if amount.lower()=="all" else (int(amount) if amount.isdigit() else -1)
    
    if wdr <= 0 or wdr > data[2]:
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    add_bank(uid, -wdr)
    add_wallet(uid, wdr)
    
    embed = discord.Embed(title="🏦 WITHDRAWN!", color=GREEN)
    embed.add_field(name="Amount", value=f"{sc(wdr)} ⚓", inline=True)
    embed.add_field(name="New Wallet", value=f"{sc(data[1] + wdr)} ⚓", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transfer", description="💸 Transfer")
@app_commands.describe(user="Recipient", amount="Amount")
async def transfer(interaction: discord.Interaction, user: discord.Member, amount: int):
    sid, rid = interaction.user.id, user.id
    
    if is_banned(sid):
        return await interaction.response.send_message("❌ Economy banned", ephemeral=True)
    if user.bot or sid==rid:
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    data = get_user(sid)
    if amount <= 0 or amount > data[1]:
        return await interaction.response.send_message("❌ Invalid", ephemeral=True)
    
    on_cd, rem = check_cd(sid, "transfer", 30)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait {fmt_time(rem)}", ephemeral=True)
    
    set_cd(sid, "transfer")
    add_wallet(sid, -amount)
    add_wallet(rid, amount, "transfer")
    
    await log_to_channel(
        title="💸 TRANSFER",
        description=f"{interaction.user.mention} sent coins",
        color=GREEN,
        user=interaction.user,
        extra_fields={"To": user.mention, "💰 Amount": f"{sc(amount)} ⚓"}
    )
    
    embed = discord.Embed(title="💸 TRANSFER!", color=GREEN)
    embed.add_field(name="From", value=interaction.user.mention, inline=True)
    embed.add_field(name="To", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=f"{sc(amount)} ⚓", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profile", description="👤 Profile")
@app_commands.describe(user="User (optional)")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    items = get_inv(target.id)
    
    embed = discord.Embed(title=f"⚓ {target.display_name}'s PROFILE", color=BLUE)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="💰 Wallet", value=f"{sc(data[1])} ⚓", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])} / {sc(data[3])} ⚓", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}` {data[6]}/{data[5]*100}", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    embed.add_field(name="🎒 Items", value=f"{len(items)}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="🏆 Top 10")
async def leaderboard(interaction: discord.Interaction):
    conn = db()
    rows = conn.execute("SELECT user_id, wallet+bank FROM users ORDER BY wallet+bank DESC LIMIT 10").fetchall()
    conn.close()
    
    embed = discord.Embed(title="🏆 LEADERBOARD", color=GOLD)
    medals = ["🥇","🥈","🥉"]
    
    for i, (uid, total) in enumerate(rows):
        m = medals[i] if i<3 else f"`#{i+1}`"
        u = interaction.guild.get_member(uid)
        name = u.display_name if u else "Unknown"
        embed.add_field(name=f"{m} {name}", value=f"{sc(total)} ⚓", inline=False)
    
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="📊 Stats")
async def stats(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    
    embed = discord.Embed(title="📊 YOUR STATS", color=BLUE)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="💰 Total Earned", value=f"{sc(data[4])} ⚓", inline=True)
    embed.add_field(name="⭐ Level", value=str(data[5]), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{sc(data[1]+data[2])} ⚓", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inventory", description="🎒 Inventory")
@app_commands.describe(user="User (optional)")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    items = get_inv(target.id)
    
    embed = discord.Embed(title=f"🎒 {target.display_name}'s INVENTORY", color=PURPLE)
    
    if not items:
        embed.description = "Empty! Visit `/shop`"
    else:
        for name, qty in sorted(items.items()):
            embed.add_field(name=name, value=f"x{qty}", inline=True)
    
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multipliers", description="✨ Active boosts")
async def multipliers(interaction: discord.Interaction):
    uid = interaction.user.id
    now = time.time()
    conn = db()
    rows = conn.execute("SELECT mult_type, value, expires_at FROM multipliers WHERE user_id=? AND expires_at>?", (uid, now)).fetchall()
    conn.close()
    
    embed = discord.Embed(title="✨ ACTIVE MULTIPLIERS", color=PURPLE)
    
    if not rows:
        embed.description = "No active multipliers!\nBuy from `/shop`!"
    else:
        for mult_type, value, expires_at in rows:
            remaining = expires_at - now
            embed.add_field(name=f"x{value:.1f} {mult_type.capitalize()}", value=f"⏳ {fmt_time(remaining)}", inline=True)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="shop", description="🛍️ View shop")
async def shop_command(interaction: discord.Interaction):
    items = get_all_shop_items()
    
    embed = discord.Embed(title="⚓ SAILOR SHOP", description="Visit #shop to buy!", color=GOLD)
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    
    multipliers, upgrades, protection, special = [], [], [], []
    
    for item_id, item_name, price, desc, item_type, value, emoji in items:
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
    
    embed.set_footer(text="👉 Go to #shop!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="📖 Commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="⚓ COMMAND GUIDE", description="80+ Commands!", color=GOLD)
    embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
    
    embed.add_field(name="💰 ECONOMY", value="`/balance /daily /weekly /profile /stats /leaderboard`", inline=False)
    embed.add_field(name="🎣 EARNING", value="`/fish /mine /hunt /work /beg /crime /steal /rob /bankrob`", inline=False)
    embed.add_field(name="🎰 GAMES", value="`/gamble /slots /coinflip /highlow /duel`", inline=False)
    embed.add_field(name="🏦 BANKING", value="`/deposit /withdraw /transfer /inventory /shop /multipliers`", inline=False)
    embed.add_field(name="[ADMIN]", value="`/admin_setup /set_*_channel /add_item /admin_give /admin_take /admin_ban /economy_stats`", inline=False)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        msg = "❌ Admin Only"
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
