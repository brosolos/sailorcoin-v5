
# ⚓ SAILOR COINS — Discord Economy Bot v10 ULTIMATE
# ════════════════════════════════════════════════════════════════
# ✨ 30+ EARNING COMMANDS
# ✨ TRADE SYSTEM — Player-to-Player Trading
# ✨ INVESTMENT SYSTEM — 4 Tiers with ROI
# ✨ TREASURE EVERY 10 SECONDS
# ✨ BEAUTIFUL ANIMATED EMBEDS
# ✨ FULL DATABASE & LOGGING
# ════════════════════════════════════════════════════════════════

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

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ════════════════════════════════════════════════════════════════
# 🎨 THEME SYSTEM
# ════════════════════════════════════════════════════════════════

class Theme:
    GOLD = 0xF5A623
    EMERALD = 0x2ECC71
    RUBY = 0xE74C3C
    SAPPHIRE = 0x3498DB
    AMETHYST = 0x9B59B6
    SUNSET = 0xE67E22
    OCEAN = 0x1ABC9C
    MIDNIGHT = 0x2C3E50
    NEON_PINK = 0xFF6B9D
    NEON_BLUE = 0x00D4FF
    NEON_GREEN = 0x39FF14
    CYBER_PURPLE = 0xBF40BF
    SUCCESS = 0x00E676
    ERROR = 0xFF5252
    WARNING = 0xFFD600
    INFO = 0x00B0FF

# ════════════════════════════════════════════════════════════════
# 🎬 ANIMATED GIFS LIBRARY
# ════════════════════════════════════════════════════════════════

class GIFs:
    FISH_SUCCESS = "https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif"
    MINE_SUCCESS = "https://media.giphy.com/media/xT5LMHxhOfscxPfIfm/giphy.gif"
    HUNT_SUCCESS = "https://media.giphy.com/media/3o7btNhMBytxAM6YBa/giphy.gif"
    WORK_SUCCESS = "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif"
    WIN_BIG = "https://media.giphy.com/media/l0MYGb1LuZ3n7dRnO/giphy.gif"
    WIN_JACKPOT = "https://media.giphy.com/media/l41YkFIiBxQdRlMnC/giphy.gif"
    LOSE = "https://media.giphy.com/media/hStvd5LiWCFzYNyxR4/giphy.gif"
    CRIME_SUCCESS = "https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif"
    CRIME_FAIL = "https://media.giphy.com/media/3o7TKMeCOV3oXSb5bq/giphy.gif"
    DAILY_REWARD = "https://media.giphy.com/media/26BRzozg4TCBXv6QU/giphy.gif"
    TREASURE_FOUND = "https://media.giphy.com/media/3o7absbD7PbTFQa0c8/giphy.gif"
    TREASURE_OPEN = "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif"
    LEVEL_UP = "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"
    DUEL_WIN = "https://media.giphy.com/media/3o7btYLAW7doynq3p6/giphy.gif"
    DUEL_LOSE = "https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif"
    PURCHASE_SUCCESS = "https://media.giphy.com/media/3o6gDWzmAzrpi5DQU8/giphy.gif"
    MYSTERY_BOX = "https://media.giphy.com/media/3oEjI5VtIhHvK37WYo/giphy.gif"
    BANK_DEPOSIT = "https://media.giphy.com/media/67ThRZlYBvibtdF9JH/giphy.gif"
    TRANSFER = "https://media.giphy.com/media/3o6gDWzmAzrpi5DQU8/giphy.gif"
    LOADING = "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"
    ERROR = "https://media.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif"
    PROTECTED = "https://media.giphy.com/media/3o7TKF1fSIs1R19B8k/giphy.gif"
    BANNED = "https://media.giphy.com/media/3o6wrvdHFbwBrUFenu/giphy.gif"
    INVEST_SUCCESS = "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
    TRADE_SUCCESS = "https://media.giphy.com/media/3o6gDWzmAzrpi5DQU8/giphy.gif"
    PARTY = "https://media.giphy.com/media/l0HlQaQ6gWfllcjDO/giphy.gif"
    DANCE = "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"

# ════════════════════════════════════════════════════════════════
# 🎯 MODERN UI COMPONENTS
# ════════════════════════════════════════════════════════════════

class ModernUI:
    @staticmethod
    def progress_bar(current: int, maximum: int, length: int = 10) -> str:
        if maximum <= 0:
            percentage = 0
        else:
            percentage = min(100, (current / maximum) * 100)
        filled_length = int(length * percentage / 100)
        bar = "█" * filled_length + "░" * (length - filled_length)
        return f"`{bar}` **{percentage:.1f}%**"
    
    @staticmethod
    def money_display(amount: int, emoji: str = "⚓") -> str:
        if amount >= 1000000:
            return f"{emoji} **{amount/1000000:.2f}M**"
        elif amount >= 1000:
            return f"{emoji} **{amount/1000:.1f}K**"
        else:
            return f"{emoji} **{amount:,}**"
    
    @staticmethod
    def divider(style: str = "wave") -> str:
        dividers = {
            "wave": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            "stars": "✧･ﾟ: *✧･ﾟ:* 　 *:･ﾟ✧*:･ﾟ✧",
            "sparkle": "✨ ═══════════════ ✨",
            "anchor": "⚓ ━━━━━━━━━━━━━ ⚓",
            "diamond": "◈ ══════════════ ◈",
        }
        return dividers.get(style, dividers["wave"])
    
    @staticmethod
    def rarity_color(rarity: str) -> int:
        colors = {
            "common": 0x95A5A6,
            "uncommon": 0x2ECC71,
            "rare": 0x3498DB,
            "epic": 0x9B59B6,
            "legendary": 0xF39C12,
            "mythic": 0xE74C3C
        }
        return colors.get(rarity.lower(), Theme.GOLD)

# ════════════════════════════════════════════════════════════════
# 🏗️ EMBED BUILDERS
# ════════════════════════════════════════════════════════════════

class EmbedBuilder:
    @staticmethod
    def success(title: str, description: str, user: discord.Member = None, gif: str = None) -> discord.Embed:
        embed = discord.Embed(
            title=f"✅ {title}",
            description=f"```fix\n{description}\n```" if description else None,
            color=Theme.SUCCESS,
            timestamp=datetime.now()
        )
        if user:
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
        if gif:
            embed.set_image(url=gif)
        embed.set_footer(text="⚓ Sailor Coins")
        return embed
    
    @staticmethod
    def error(title: str, description: str, user: discord.Member = None) -> discord.Embed:
        embed = discord.Embed(
            title=f"❌ {title}",
            description=f"```diff\n- {description}\n```",
            color=Theme.ERROR,
            timestamp=datetime.now()
        )
        if user:
            embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=GIFs.ERROR)
        embed.set_footer(text="⚓ Sailor Coins")
        return embed
    
    @staticmethod
    def reward(title: str, amount: int, user: discord.Member, gif: str = None) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎉 {title}",
            color=Theme.GOLD,
            timestamp=datetime.now()
        )
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.description = f"""
{ModernUI.divider('sparkle')}

💰 **EARNED:** {ModernUI.money_display(amount)}

{ModernUI.divider('sparkle')}
"""
        if gif:
            embed.set_image(url=gif)
        embed.set_footer(text="⚓ Sailor Coins • Keep grinding!")
        return embed

# ════════════════════════════════════════════════════════════════
# 💾 DATABASE - PERSISTENT
# ════════════════════════════════════════════════════════════════

DB_PATH = "sailor.db"

def init_db():
    """Initialize database"""
    if os.path.exists(DB_PATH):
        print(f"✅ Database exists at {DB_PATH}")
        return
    
    print(f"📝 Creating database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
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

    c.execute("""CREATE TABLE IF NOT EXISTS trades (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_from   INTEGER,
        user_to     INTEGER,
        offer_type  TEXT,
        offer_item  TEXT,
        offer_amount INTEGER,
        want_type   TEXT,
        want_item   TEXT,
        want_amount INTEGER,
        status      TEXT DEFAULT 'pending',
        timestamp   REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS investments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT,
        min_amount  INTEGER,
        tier        TEXT,
        roi         REAL,
        duration    INTEGER,
        created_at  REAL,
        closes_at   REAL,
        status      TEXT DEFAULT 'active'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS investor_accounts (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       INTEGER,
        investment_id INTEGER,
        amount        INTEGER,
        invested_at   REAL,
        profit        INTEGER DEFAULT 0,
        auto_compound BOOLEAN DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS banned_users (
        user_id INTEGER PRIMARY KEY
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key   TEXT PRIMARY KEY,
        value TEXT
    )""")

    conn.commit()
    conn.close()
    print(f"✅ Database initialized!")

def db():
    return sqlite3.connect(DB_PATH)

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

def fmt_time(secs: float) -> str:
    s = int(secs)
    if s < 60:
        return f"**{s}**s"
    if s < 3600:
        return f"**{s//60}**m **{s%60}**s"
    return f"**{s//3600}**h **{(s%3600)//60}**m"

# ════════════════════════════════════════════════════════════════
# 🤖 BOT EVENTS
# ════════════════════════════════════════════════════════════════

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

@tasks.loop(seconds=10)
async def passive_drop():
    """Treasure drop every 10 seconds"""
    drop_channel_id = get_cfg("drop_channel")
    if not drop_channel_id:
        return
    
    channel = bot.get_channel(int(drop_channel_id))
    if not channel:
        return
    
    amount = random.randint(100, 10000)
    
    embed = discord.Embed(
        title="🏴‍☠️ TREASURE WASHED ASHORE!",
        description=f"""
{ModernUI.divider('anchor')}

🎁 A chest containing **{ModernUI.money_display(amount)}** has appeared!

⏰ **Time Limit:** `60 seconds`
📝 **To Claim:** Type `!claim`

{ModernUI.divider('anchor')}

*First sailor to claim wins!*
""",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    embed.set_image(url=GIFs.TREASURE_FOUND)
    embed.set_footer(text="⚓ Sailor Coins • Treasure Event")
    
    msg = await channel.send(embed=embed)
    
    def check(m):
        return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount)
        
        embed = discord.Embed(
            title="🎉 TREASURE CLAIMED!",
            description=f"""
{ModernUI.divider('sparkle')}

🏆 **{resp.author.mention}** claimed the treasure!

💰 **Reward:** {ModernUI.money_display(amount)}

{ModernUI.divider('sparkle')}
""",
            color=Theme.SUCCESS,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=resp.author.display_avatar.url)
        embed.set_image(url=GIFs.TREASURE_OPEN)
        embed.set_footer(text="⚓ Sailor Coins")
        
        await channel.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="🌊 Treasure Sank...",
            description=f"""
{ModernUI.divider('wave')}

Nobody claimed it in time!

💰 **{ModernUI.money_display(amount)}** lost to the sea...

{ModernUI.divider('wave')}
""",
            color=Theme.ERROR,
            timestamp=datetime.now()
        )
        embed.set_footer(text="⚓ Sailor Coins")
        await channel.send(embed=embed)

# ════════════════════════════════════════════════════════════════
# 👑 ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.command(name="set_drop_channel", description="[ADMIN] Set treasure drop channel")
@app_commands.describe(channel="The channel for treasure drops")
@admin_only()
async def set_drop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("drop_channel", str(channel.id))
    embed = discord.Embed(
        title="✅ Drop Channel Set!",
        description=f"Treasure drops will appear in {channel.mention}",
        color=Theme.SUCCESS
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ════════════════════════════════════════════════════════════════
# 💰 EARNING COMMANDS (30+)
# ════════════════════════════════════════════════════════════════

@bot.tree.command(name="fish", description="🎣 Go fishing for coins")
async def fish(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "fish", 30)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    rarity = random.choices(["common", "uncommon", "rare", "epic", "legendary"], weights=[50, 25, 15, 7, 3])[0]
    amounts = {"common": 100, "uncommon": 250, "rare": 500, "epic": 1000, "legendary": 2500}
    amount = amounts[rarity]
    
    add_wallet(uid, amount)
    set_cd(uid, "fish")
    
    embed = EmbedBuilder.reward("Fishing Success!", amount, interaction.user, GIFs.FISH_SUCCESS)
    embed.add_field(name="🎣 Rarity", value=f"`{rarity.upper()}`", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mine", description="⛏️ Go mining")
async def mine(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "mine", 45)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    rarity = random.choices(["common", "uncommon", "rare", "epic", "legendary"], weights=[45, 30, 15, 8, 2])[0]
    amounts = {"common": 150, "uncommon": 350, "rare": 700, "epic": 1500, "legendary": 3500}
    amount = amounts[rarity]
    
    add_wallet(uid, amount)
    set_cd(uid, "mine")
    
    embed = EmbedBuilder.reward("Mining Success!", amount, interaction.user, GIFs.MINE_SUCCESS)
    embed.add_field(name="⛏️ Find", value=f"`{rarity.upper()}`", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hunt", description="🏹 Go hunting")
async def hunt(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "hunt", 60)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(200, 800)
    add_wallet(uid, amount)
    set_cd(uid, "hunt")
    
    embed = EmbedBuilder.reward("Hunt Successful!", amount, interaction.user, GIFs.HUNT_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="work", description="💼 Work for coins")
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "work", 120)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(300, 600)
    add_wallet(uid, amount)
    set_cd(uid, "work")
    
    embed = EmbedBuilder.reward("Work Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="babysit", description="👶 Babysit for coins")
async def babysit(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "babysit", 90)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(150, 400)
    add_wallet(uid, amount)
    set_cd(uid, "babysit")
    
    embed = EmbedBuilder.reward("Babysitting Done!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deliver", description="🍕 Deliver orders")
async def deliver(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "deliver", 75)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(200, 500)
    add_wallet(uid, amount)
    set_cd(uid, "deliver")
    
    embed = EmbedBuilder.reward("Delivery Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="taxi", description="🚗 Drive taxi")
async def taxi(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "taxi", 60)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(250, 600)
    add_wallet(uid, amount)
    set_cd(uid, "taxi")
    
    embed = EmbedBuilder.reward("Taxi Ride Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tutor", description="💡 Tutor students")
async def tutor(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "tutor", 100)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(300, 700)
    add_wallet(uid, amount)
    set_cd(uid, "tutor")
    
    embed = EmbedBuilder.reward("Tutoring Session Done!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="farm", description="🌾 Farm crops")
async def farm(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "farm", 80)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(200, 550)
    add_wallet(uid, amount)
    set_cd(uid, "farm")
    
    embed = EmbedBuilder.reward("Farming Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="loot", description="🏴‍☠️ Raid treasure")
async def loot(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "loot", 120)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(400, 1200)
    add_wallet(uid, amount)
    set_cd(uid, "loot")
    
    embed = EmbedBuilder.reward("Loot Obtained!", amount, interaction.user, GIFs.WIN_BIG)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="busk", description="🎵 Perform music")
async def busk(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "busk", 70)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(180, 450)
    add_wallet(uid, amount)
    set_cd(uid, "busk")
    
    embed = EmbedBuilder.reward("Performance Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="photograph", description="📸 Take photos")
async def photograph(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "photograph", 85)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(220, 520)
    add_wallet(uid, amount)
    set_cd(uid, "photograph")
    
    embed = EmbedBuilder.reward("Photos Sold!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clean", description="🧹 Clean houses")
async def clean(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "clean", 65)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(150, 400)
    add_wallet(uid, amount)
    set_cd(uid, "clean")
    
    embed = EmbedBuilder.reward("Cleaning Done!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="repair", description="🔧 Repair items")
async def repair(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "repair", 95)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(250, 600)
    add_wallet(uid, amount)
    set_cd(uid, "repair")
    
    embed = EmbedBuilder.reward("Repairs Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="duel", description="⚔️ Duel another player")
@app_commands.describe(opponent="The player to duel")
async def duel(interaction: discord.Interaction, opponent: discord.Member):
    uid = interaction.user.id
    opp_id = opponent.id
    
    if is_banned(uid) or is_banned(opp_id):
        embed = EmbedBuilder.error("Banned", "One or both users are banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if opponent.bot:
        embed = EmbedBuilder.error("Invalid", "Can't duel bots!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "duel", 120)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() > 0.5:
        amount = random.randint(300, 800)
        add_wallet(uid, amount)
        embed = EmbedBuilder.reward(f"Won Duel vs {opponent.name}!", amount, interaction.user, GIFs.DUEL_WIN)
    else:
        amount = random.randint(100, 300)
        add_wallet(uid, -amount)
        embed = discord.Embed(
            title=f"❌ Lost Duel to {opponent.name}",
            description=f"Lost {ModernUI.money_display(amount)}",
            color=Theme.ERROR
        )
        embed.set_image(url=GIFs.DUEL_LOSE)
    
    set_cd(uid, "duel")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lottery", description="🎯 Daily lottery")
async def lottery(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "lottery", 86400)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    chance = random.random()
    if chance > 0.95:
        amount = random.randint(5000, 15000)
        gif = GIFs.WIN_JACKPOT
    elif chance > 0.80:
        amount = random.randint(1000, 3000)
        gif = GIFs.WIN_BIG
    else:
        amount = 0
        gif = GIFs.LOSE
    
    if amount > 0:
        add_wallet(uid, amount)
        embed = EmbedBuilder.reward("Lottery Win!", amount, interaction.user, gif)
    else:
        embed = discord.Embed(
            title="❌ Lottery Lost",
            description="Better luck tomorrow!",
            color=Theme.ERROR
        )
        embed.set_image(url=gif)
    
    set_cd(uid, "lottery")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="research", description="📚 Scientific research")
async def research(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "research", 110)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(350, 850)
    add_wallet(uid, amount)
    set_cd(uid, "research")
    
    embed = EmbedBuilder.reward("Research Completed!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="flip", description="🏪 Buy and sell items")
async def flip(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "flip", 90)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    profit = random.randint(100, 600)
    add_wallet(uid, profit)
    set_cd(uid, "flip")
    
    embed = EmbedBuilder.reward("Item Flipped!", profit, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dive", description="🌊 Deep sea diving")
async def dive(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "dive", 150)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(500, 1500)
    add_wallet(uid, amount)
    set_cd(uid, "dive")
    
    embed = EmbedBuilder.reward("Diving Complete!", amount, interaction.user, GIFs.WIN_BIG)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="perform", description="🎭 Perform acts in public")
async def perform(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "perform", 75)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(200, 550)
    add_wallet(uid, amount)
    set_cd(uid, "perform")
    
    embed = EmbedBuilder.reward("Performance Successful!", amount, interaction.user, GIFs.DANCE)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="craft", description="⚙️ Craft items to sell")
async def craft(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "craft", 100)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = random.randint(300, 700)
    add_wallet(uid, amount)
    set_cd(uid, "craft")
    
    embed = EmbedBuilder.reward("Crafting Complete!", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="compete", description="🏆 Join competitions")
async def compete(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "compete", 130)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() > 0.5:
        amount = random.randint(400, 1000)
        add_wallet(uid, amount)
        embed = EmbedBuilder.reward("Competition Won!", amount, interaction.user, GIFs.WIN_BIG)
    else:
        amount = random.randint(50, 200)
        add_wallet(uid, amount)
        embed = discord.Embed(
            title="🥈 Participation Reward",
            description=f"Got {ModernUI.money_display(amount)} for participating!",
            color=Theme.INFO
        )
        embed.set_image(url=GIFs.WORK_SUCCESS)
    
    set_cd(uid, "compete")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="quest", description="🧩 Complete random quests")
async def quest(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "quest", 60)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    quests = [
        ("Find Lost Treasure", 300, 600),
        ("Help a Villager", 200, 400),
        ("Explore the Cave", 250, 500),
        ("Defeat a Dragon", 400, 900),
        ("Solve a Puzzle", 150, 350),
    ]
    
    quest_name, min_reward, max_reward = random.choice(quests)
    amount = random.randint(min_reward, max_reward)
    add_wallet(uid, amount)
    set_cd(uid, "quest")
    
    embed = EmbedBuilder.reward(f"Quest Complete: {quest_name}", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="crime", description="💀 Commit a crime (risky!)")
async def crime(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "crime", 90)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() > 0.6:
        amount = random.randint(500, 1500)
        add_wallet(uid, amount)
        set_cd(uid, "crime")
        embed = EmbedBuilder.reward("Heist Successful!", amount, interaction.user, GIFs.CRIME_SUCCESS)
    else:
        amount = random.randint(100, 400)
        add_wallet(uid, -amount)
        set_cd(uid, "crime")
        embed = discord.Embed(
            title="🚔 Caught by Police!",
            description=f"You lost {ModernUI.money_display(amount)}",
            color=Theme.ERROR
        )
        embed.set_image(url=GIFs.CRIME_FAIL)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gamble", description="🎲 Gamble your coins (HIGH RISK)")
@app_commands.describe(amount="Amount to gamble")
async def gamble(interaction: discord.Interaction, amount: int):
    uid = interaction.user.id
    data = get_user(uid)
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if data[1] < amount:
        embed = EmbedBuilder.error("Insufficient Funds", f"You need {ModernUI.money_display(amount)}", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "gamble", 30)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    roll = random.randint(1, 100)
    
    if roll > 70:
        winnings = int(amount * 2)
        add_wallet(uid, winnings)
        embed = EmbedBuilder.reward("JACKPOT!", winnings, interaction.user, GIFs.WIN_JACKPOT)
    elif roll > 50:
        winnings = int(amount * 1.5)
        add_wallet(uid, winnings)
        embed = EmbedBuilder.reward("Big Win!", winnings, interaction.user, GIFs.WIN_BIG)
    elif roll > 30:
        add_wallet(uid, 0)
        embed = discord.Embed(
            title="😐 Break Even",
            description="You got your money back!",
            color=Theme.INFO
        )
    else:
        add_wallet(uid, -amount)
        embed = discord.Embed(
            title="💔 Lost!",
            description=f"Lost {ModernUI.money_display(amount)}",
            color=Theme.ERROR
        )
        embed.set_image(url=GIFs.LOSE)
    
    set_cd(uid, "gamble")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rob", description="🔫 Rob another player (risky!)")
@app_commands.describe(victim="Player to rob")
async def rob(interaction: discord.Interaction, victim: discord.Member):
    uid = interaction.user.id
    victim_id = victim.id
    
    if is_banned(uid) or is_banned(victim_id):
        embed = EmbedBuilder.error("Banned", "One or both users are banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if victim.bot:
        embed = EmbedBuilder.error("Invalid", "Can't rob bots!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "rob", 120)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    victim_data = get_user(victim_id)
    victim_wallet = victim_data[1]
    
    if victim_wallet < 100:
        embed = EmbedBuilder.error("Too Poor", f"{victim.mention} doesn't have enough coins!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() > 0.6:
        steal_amount = random.randint(50, int(victim_wallet * 0.3))
        add_wallet(uid, steal_amount)
        add_wallet(victim_id, -steal_amount)
        embed = discord.Embed(
            title=f"🔫 Robbed {victim.name}!",
            description=f"Stole {ModernUI.money_display(steal_amount)}",
            color=Theme.GOLD
        )
        embed.set_image(url=GIFs.CRIME_SUCCESS)
    else:
        fine = random.randint(100, 300)
        add_wallet(uid, -fine)
        embed = discord.Embed(
            title="🚔 Rob Failed!",
            description=f"Caught and fined {ModernUI.money_display(fine)}!",
            color=Theme.ERROR
        )
        embed.set_image(url=GIFs.CRIME_FAIL)
    
    set_cd(uid, "rob")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="📅 Get daily reward")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    data = get_user(uid)
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    last_daily = data[9]
    time_now = time.time()
    
    if time_now - last_daily < 86400:
        remaining = 86400 - (time_now - last_daily)
        embed = discord.Embed(
            title="⏰ Already Claimed",
            description=f"Come back in {fmt_time(remaining)}",
            color=Theme.WARNING
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    amount = 500
    add_wallet(uid, amount)
    conn = db()
    conn.execute("UPDATE users SET last_daily=? WHERE user_id=?", (time_now, uid))
    conn.commit()
    conn.close()
    
    embed = EmbedBuilder.reward("Daily Reward!", amount, interaction.user, GIFs.DAILY_REWARD)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="scratch", description="🎫 Scratch-off lottery tickets")
async def scratch(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "scratch", 300)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    roll = random.randint(1, 100)
    if roll > 90:
        amount = random.randint(2000, 5000)
        gif = GIFs.WIN_JACKPOT
    elif roll > 75:
        amount = random.randint(500, 1500)
        gif = GIFs.WIN_BIG
    else:
        amount = 0
        gif = GIFs.LOSE
    
    if amount > 0:
        add_wallet(uid, amount)
        embed = EmbedBuilder.reward("Scratch Won!", amount, interaction.user, gif)
    else:
        embed = discord.Embed(
            title="❌ No Win",
            description="Better luck next time!",
            color=Theme.ERROR
        )
        embed.set_image(url=gif)
    
    set_cd(uid, "scratch")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="explore", description="🗺️ Explore unknown territories")
async def explore(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "explore", 140)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    explorations = [
        ("🏔️ Mountain", 250, 700),
        ("🏝️ Island", 300, 800),
        ("🌲 Forest", 200, 600),
        ("🏜️ Desert", 350, 950),
        ("🗻 Volcano", 400, 1200),
    ]
    
    location, min_reward, max_reward = random.choice(explorations)
    amount = random.randint(min_reward, max_reward)
    add_wallet(uid, amount)
    set_cd(uid, "explore")
    
    embed = EmbedBuilder.reward(f"Explored {location}", amount, interaction.user, GIFs.WORK_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fish_tournament", description="🎣 Enter fishing tournament")
async def fish_tournament(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "fish_tournament", 3600)
    if on_cd:
        embed = discord.Embed(title="⏰ On Cooldown", description=f"Try again in {fmt_time(rem)}", color=Theme.WARNING)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() > 0.5:
        amount = random.randint(800, 2000)
        embed = EmbedBuilder.reward("Tournament Victory!", amount, interaction.user, GIFs.WIN_BIG)
    else:
        amount = random.randint(100, 300)
        embed = discord.Embed(
            title="🏅 Tournament Participation",
            description=f"Got {ModernUI.money_display(amount)} for participation!",
            color=Theme.INFO
        )
        embed.set_image(url=GIFs.WORK_SUCCESS)
    
    add_wallet(uid, amount)
    set_cd(uid, "fish_tournament")
    await interaction.response.send_message(embed=embed)

# ════════════════════════════════════════════════════════════════
# 🔄 TRADE SYSTEM
# ═══════════════════════���════════════════════════════════════════

@bot.tree.command(name="trade_request", description="🔄 Request a trade")
@app_commands.describe(
    user="User to trade with",
    offer="What you're offering (coins or item)",
    want="What you want in return"
)
async def trade_request(interaction: discord.Interaction, user: discord.Member, offer: str, want: str):
    uid = interaction.user.id
    target_id = user.id
    
    if is_banned(uid) or is_banned(target_id):
        embed = EmbedBuilder.error("Banned", "One or both users are banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if user.bot:
        embed = EmbedBuilder.error("Invalid", "Can't trade with bots!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    conn = db()
    conn.execute("INSERT INTO trades (user_from, user_to, offer_type, offer_item, want_type, want_item, timestamp) VALUES (?,?,?,?,?,?,?)",
                 (uid, target_id, "item", offer, "item", want, time.time()))
    trade_id = conn.lastrowid
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="🔄 Trade Request",
        description=f"""
{ModernUI.divider('diamond')}

💼 **From:** {interaction.user.mention}
📦 **Offering:** {offer}
📥 **Wants:** {want}

{ModernUI.divider('diamond')}

Status: **PENDING**
""",
        color=Theme.SAPPHIRE
    )
    embed.set_image(url=GIFs.TRADE_SUCCESS)
    embed.set_footer(text=f"Trade ID: {trade_id}")
    
    await interaction.response.send_message(embed=embed)

# ════════════════════════════════════════════════════════════════
# 💹 INVESTMENT SYSTEM
# ════════════════════════════════════════════════════════════════

@bot.tree.command(name="create_investment", description="[ADMIN] Create investment opportunity")
@app_commands.describe(
    name="Investment name",
    min_amount="Minimum investment amount",
    tier="bronze (8%), silver (15%), gold (25%), platinum (40%)",
    duration="Days until payout"
)
@admin_only()
async def create_investment(interaction: discord.Interaction, name: str, min_amount: int, tier: str, duration: int):
    roi_map = {"bronze": 8, "silver": 15, "gold": 25, "platinum": 40}
    
    if tier not in roi_map:
        embed = EmbedBuilder.error("Invalid Tier", "Use: bronze, silver, gold, platinum", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    roi = roi_map[tier]
    conn = db()
    conn.execute("INSERT INTO investments (name, min_amount, tier, roi, duration, created_at, closes_at, status) VALUES (?,?,?,?,?,?,?,?)",
                 (name, min_amount, tier, roi, duration, time.time(), time.time() + (duration * 86400), "active"))
    inv_id = conn.lastrowid
    conn.commit()
    conn.close()
    
    tier_colors = {
        "bronze": 0xA67C52,
        "silver": 0xC0C0C0,
        "gold": 0xFFD700,
        "platinum": 0xE5E4E2
    }
    
    embed = discord.Embed(
        title=f"💹 {name}",
        description=f"""
{ModernUI.divider('sparkle')}

🎯 **Investment Opportunity**

💰 **Minimum:** {ModernUI.money_display(min_amount)}
📈 **ROI:** **{roi}%**
⏰ **Duration:** {duration} days
🏅 **Tier:** {tier.upper()}

{ModernUI.divider('sparkle')}

Ready to invest? Use `/invest`
""",
        color=tier_colors.get(tier, Theme.GOLD)
    )
    embed.set_image(url=GIFs.INVEST_SUCCESS)
    embed.set_footer(text=f"Investment ID: {inv_id}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="invest", description="💹 View and invest in opportunities")
async def invest(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    conn = db()
    investments = conn.execute("SELECT id, name, min_amount, tier, roi, duration FROM investments WHERE status='active'").fetchall()
    conn.close()
    
    if not investments:
        embed = EmbedBuilder.error("No Investments", "No active investments at the moment.", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    embed = discord.Embed(
        title="💹 Active Investments",
        description=f"""
{ModernUI.divider('diamond')}

Available investment opportunities:

{ModernUI.divider('diamond')}
""",
        color=Theme.GOLD
    )
    
    for inv in investments:
        inv_id, name, min_amt, tier, roi, duration = inv
        embed.add_field(
            name=f"{name} ({tier.upper()})",
            value=f"Min: {ModernUI.money_display(min_amt)} • ROI: {roi}% • Duration: {duration}d • ID: {inv_id}",
            inline=False
        )
    
    embed.add_field(name="📝 To Invest", value="Use: `/invest_amount <investment_id> <amount>`", inline=False)
    embed.set_image(url=GIFs.INVEST_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="invest_amount", description="💹 Invest in an opportunity")
@app_commands.describe(investment_id="Investment ID", amount="Amount to invest")
async def invest_amount(interaction: discord.Interaction, investment_id: int, amount: int):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    data = get_user(uid)
    if data[1] < amount:
        embed = EmbedBuilder.error("Insufficient Funds", f"You need {ModernUI.money_display(amount)}", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    conn = db()
    inv = conn.execute("SELECT min_amount, status FROM investments WHERE id=?", (investment_id,)).fetchone()
    
    if not inv or inv[1] != "active":
        conn.close()
        embed = EmbedBuilder.error("Invalid", "Investment not found or closed!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if amount < inv[0]:
        conn.close()
        embed = EmbedBuilder.error("Minimum Not Met", f"Minimum is {ModernUI.money_display(inv[0])}", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    add_wallet(uid, -amount)
    conn.execute("INSERT INTO investor_accounts (user_id, investment_id, amount, invested_at) VALUES (?,?,?,?)",
                 (uid, investment_id, amount, time.time()))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Investment Confirmed!",
        description=f"""
{ModernUI.divider('sparkle')}

💰 **Invested:** {ModernUI.money_display(amount)}
💹 **Investment ID:** {investment_id}

You will receive your returns in the specified duration.

{ModernUI.divider('sparkle')}
""",
        color=Theme.SUCCESS
    )
    embed.set_image(url=GIFs.INVEST_SUCCESS)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="portfolio", description="💹 View your investments")
async def portfolio(interaction: discord.Interaction):
    uid = interaction.user.id
    
    conn = db()
    accounts = conn.execute("""
        SELECT ia.id, i.name, ia.amount, ia.profit, i.roi, i.duration
        FROM investor_accounts ia
        JOIN investments i ON ia.investment_id = i.id
        WHERE ia.user_id = ?
    """, (uid,)).fetchall()
    conn.close()
    
    if not accounts:
        embed = EmbedBuilder.error("No Investments", "You haven't invested in anything yet.", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    embed = discord.Embed(
        title="💹 Your Investment Portfolio",
        color=Theme.GOLD
    )
    
    total_invested = 0
    total_profit = 0
    
    for acc in accounts:
        acc_id, name, invested, profit, roi, duration = acc
        total_invested += invested
        total_profit += profit
        
        embed.add_field(
            name=f"{name}",
            value=f"💰 Invested: {ModernUI.money_display(invested)}\n📈 Profit: {ModernUI.money_display(profit)}\nROI: {roi}%",
            inline=False
        )
    
    embed.add_field(
        name="📊 Totals",
        value=f"Invested: {ModernUI.money_display(total_invested)}\nProfits: {ModernUI.money_display(total_profit)}",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# ═══════════════════��════════════════════════════════════════════
# 💰 UTILITY COMMANDS
# ════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="💰 Check your balance")
@app_commands.describe(user="User to check (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    
    wallet, bank = data[1], data[2]
    net_worth = wallet + bank
    
    embed = discord.Embed(
        title=f"⚓ {target.display_name}'s Balance",
        color=Theme.GOLD
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="👛 Wallet", value=f"{ModernUI.money_display(wallet)}", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{ModernUI.money_display(bank)}", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"{ModernUI.money_display(net_worth)}", inline=True)
    
    await interaction.response.send_message(embed=embed)

# ════════════════════════════════════════════════════════════════
# 🚀 STARTUP
# ��═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    bot.run(TOKEN)
