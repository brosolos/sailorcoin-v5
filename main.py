"""
⚓ SAILOR COINS — Discord Economy Bot v8 ULTIMATE
=====================================
✨ 80+ COMMANDS
✨ MODERN GUI WITH ANIMATED EMBEDS
✨ BEAUTIFUL THEMES & PROGRESS BARS
✨ STUNNING GIFS FOR EVERY ACTION
✨ FULL PERSISTENCE & LOGGING

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

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 MODERN THEME SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Theme:
    # Primary Colors
    GOLD = 0xF5A623
    EMERALD = 0x2ECC71
    RUBY = 0xE74C3C
    SAPPHIRE = 0x3498DB
    AMETHYST = 0x9B59B6
    SUNSET = 0xE67E22
    OCEAN = 0x1ABC9C
    MIDNIGHT = 0x2C3E50
    
    # Gradient-like accent colors
    NEON_PINK = 0xFF6B9D
    NEON_BLUE = 0x00D4FF
    NEON_GREEN = 0x39FF14
    CYBER_PURPLE = 0xBF40BF
    
    # Status Colors
    SUCCESS = 0x00E676
    ERROR = 0xFF5252
    WARNING = 0xFFD600
    INFO = 0x00B0FF

# ═══════════════════════════════════════════════════════════════════════════════
# 🎬 ANIMATED GIFS LIBRARY
# ═══════════════════════════════════════════════════════════════════════════════

class GIFs:
    # Fishing
    FISH_SUCCESS = "https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif"
    FISH_RARE = "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif"
    FISH_LEGENDARY = "https://media.giphy.com/media/3oEjHYibHwRL7mrNyo/giphy.gif"
    
    # Mining
    MINE_SUCCESS = "https://media.giphy.com/media/xT5LMHxhOfscxPfIfm/giphy.gif"
    MINE_DIAMOND = "https://media.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif"
    MINE_RARE = "https://media.giphy.com/media/l4FGGafcOHmrlQxG0/giphy.gif"
    
    # Hunting
    HUNT_SUCCESS = "https://media.giphy.com/media/3o7btNhMBytxAM6YBa/giphy.gif"
    HUNT_RARE = "https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif"
    HUNT_LEGENDARY = "https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif"
    
    # Work
    WORK_SUCCESS = "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif"
    WORK_BONUS = "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
    
    # Gambling
    WIN_SMALL = "https://media.giphy.com/media/3o6ZtpWvwnhf34Oj0A/giphy.gif"
    WIN_BIG = "https://media.giphy.com/media/l0MYGb1LuZ3n7dRnO/giphy.gif"
    WIN_JACKPOT = "https://media.giphy.com/media/l41YkFIiBxQdRlMnC/giphy.gif"
    LOSE = "https://media.giphy.com/media/hStvd5LiWCFzYNyxR4/giphy.gif"
    SLOTS_SPIN = "https://media.giphy.com/media/26BRBhmnSxHCjUCJO/giphy.gif"
    
    # Crime & Rob
    CRIME_SUCCESS = "https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif"
    CRIME_FAIL = "https://media.giphy.com/media/3o7TKMeCOV3oXSb5bq/giphy.gif"
    ROB_SUCCESS = "https://media.giphy.com/media/3oEdv4hwWTzBhWvaU0/giphy.gif"
    ROB_FAIL = "https://media.giphy.com/media/l2JhtKtDWYNKdRpoA/giphy.gif"
    
    # Rewards & Treasure
    DAILY_REWARD = "https://media.giphy.com/media/26BRzozg4TCBXv6QU/giphy.gif"
    WEEKLY_REWARD = "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
    TREASURE_FOUND = "https://media.giphy.com/media/3o7absbD7PbTFQa0c8/giphy.gif"
    TREASURE_OPEN = "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif"
    
    # Level Up & Achievement
    LEVEL_UP = "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"
    ACHIEVEMENT = "https://media.giphy.com/media/l0MYGb1LuZ3n7dRnO/giphy.gif"
    STREAK = "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif"
    
    # Duel & Battle
    DUEL_START = "https://media.giphy.com/media/l0HlQXlQ3nHyLMvte/giphy.gif"
    DUEL_WIN = "https://media.giphy.com/media/3o7btYLAW7doynq3p6/giphy.gif"
    DUEL_LOSE = "https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif"
    
    # Shop & Purchase
    SHOP_BROWSE = "https://media.giphy.com/media/3o7TKP9ln2Dr6ze6f6/giphy.gif"
    PURCHASE_SUCCESS = "https://media.giphy.com/media/3o6gDWzmAzrpi5DQU8/giphy.gif"
    MYSTERY_BOX = "https://media.giphy.com/media/3oEjI5VtIhHvK37WYo/giphy.gif"
    
    # Bank & Transfer
    BANK_DEPOSIT = "https://media.giphy.com/media/67ThRZlYBvibtdF9JH/giphy.gif"
    BANK_WITHDRAW = "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif"
    TRANSFER = "https://media.giphy.com/media/3o6gDWzmAzrpi5DQU8/giphy.gif"
    
    # Misc
    LOADING = "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"
    ERROR = "https://media.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif"
    PROTECTED = "https://media.giphy.com/media/3o7TKF1fSIs1R19B8k/giphy.gif"
    BANNED = "https://media.giphy.com/media/3o6wrvdHFbwBrUFenu/giphy.gif"

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 MODERN UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

class ModernUI:
    """Modern UI helper class for beautiful embeds"""
    
    @staticmethod
    def progress_bar(current: int, maximum: int, length: int = 10, 
                     filled: str = "█", empty: str = "░", 
                     show_percentage: bool = True) -> str:
        """Create a modern progress bar"""
        if maximum <= 0:
            percentage = 0
        else:
            percentage = min(100, (current / maximum) * 100)
        filled_length = int(length * percentage / 100)
        bar = filled * filled_length + empty * (length - filled_length)
        if show_percentage:
            return f"`{bar}` **{percentage:.1f}%**"
        return f"`{bar}`"
    
    @staticmethod
    def animated_progress(current: int, maximum: int, length: int = 12) -> str:
        """Create an animated-looking progress bar"""
        if maximum <= 0:
            percentage = 0
        else:
            percentage = min(100, (current / maximum) * 100)
        filled_length = int(length * percentage / 100)
        
        # Modern gradient effect
        chars = ["⬛", "🟫", "🟧", "🟨", "🟩", "🟦", "🟪"]
        bar = ""
        for i in range(length):
            if i < filled_length:
                color_index = min(len(chars) - 1, int((i / length) * len(chars)))
                bar += chars[color_index]
            else:
                bar += "⬜"
        return f"{bar} **{percentage:.0f}%**"
    
    @staticmethod
    def xp_bar(current_xp: int, needed_xp: int, level: int) -> str:
        """Create a beautiful XP progress bar"""
        if needed_xp <= 0:
            percentage = 100
        else:
            percentage = min(100, (current_xp / needed_xp) * 100)
        filled = int(12 * percentage / 100)
        bar = "▰" * filled + "▱" * (12 - filled)
        return f"⭐ **Lv.{level}** `{bar}` **{current_xp}/{needed_xp}** XP"
    
    @staticmethod
    def money_display(amount: int, emoji: str = "⚓") -> str:
        """Format money with beautiful display"""
        if amount >= 1000000:
            return f"{emoji} **{amount/1000000:.2f}M**"
        elif amount >= 1000:
            return f"{emoji} **{amount/1000:.1f}K**"
        else:
            return f"{emoji} **{amount:,}**"
    
    @staticmethod
    def stats_box(title: str, value: str, emoji: str = "📊") -> str:
        """Create a stats display box"""
        return f"```\n{emoji} {title}\n╔══════════════╗\n║ {value:^12} ║\n╚══════════════╝\n```"
    
    @staticmethod
    def divider(style: str = "wave") -> str:
        """Create decorative dividers"""
        dividers = {
            "wave": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            "stars": "✧･ﾟ: *✧･ﾟ:* 　 *:･ﾟ✧*:･ﾟ✧",
            "sparkle": "✨ ═══════════════ ✨",
            "anchor": "⚓ ━━━━━━━━━━━━━ ⚓",
            "diamond": "◈ ══════════════ ◈",
            "dots": "• • • • • • • • • • • •",
        }
        return dividers.get(style, dividers["wave"])
    
    @staticmethod
    def rank_emoji(rank: int) -> str:
        """Get rank emoji"""
        rank_emojis = {
            1: "🥇",
            2: "🥈", 
            3: "🥉",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟"
        }
        return rank_emojis.get(rank, f"`#{rank}`")
    
    @staticmethod
    def rarity_color(rarity: str) -> int:
        """Get color based on rarity"""
        colors = {
            "common": 0x95A5A6,
            "uncommon": 0x2ECC71,
            "rare": 0x3498DB,
            "epic": 0x9B59B6,
            "legendary": 0xF39C12,
            "mythic": 0xE74C3C
        }
        return colors.get(rarity.lower(), Theme.GOLD)

# ═══════════════════════════════════════════════════════════════════════════════
# 🏗️ EMBED BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

class EmbedBuilder:
    """Modern embed builder with consistent styling"""
    
    @staticmethod
    def create_base(title: str, description: str = None, color: int = Theme.GOLD) -> discord.Embed:
        """Create a base embed with modern styling"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        return embed
    
    @staticmethod
    def success(title: str, description: str, user: discord.Member = None, 
                gif: str = None, fields: dict = None) -> discord.Embed:
        """Create a success embed"""
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
        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=True)
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed
    
    @staticmethod
    def error(title: str, description: str, user: discord.Member = None) -> discord.Embed:
        """Create an error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=f"```diff\n- {description}\n```",
            color=Theme.ERROR,
            timestamp=datetime.now()
        )
        if user:
            embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=GIFs.ERROR)
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed
    
    @staticmethod
    def warning(title: str, description: str) -> discord.Embed:
        """Create a warning embed"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=f"```yaml\n{description}\n```",
            color=Theme.WARNING,
            timestamp=datetime.now()
        )
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed
    
    @staticmethod
    def info(title: str, description: str, user: discord.Member = None) -> discord.Embed:
        """Create an info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=Theme.INFO,
            timestamp=datetime.now()
        )
        if user:
            embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed
    
    @staticmethod
    def reward(title: str, amount: int, user: discord.Member, 
               gif: str = None, bonus_info: str = None) -> discord.Embed:
        """Create a reward/earning embed"""
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
        if bonus_info:
            embed.add_field(name="🎁 Bonus Info", value=bonus_info, inline=False)
        
        if gif:
            embed.set_image(url=gif)
        embed.set_footer(text="⚓ Sailor Coins • Keep grinding!", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed
    
    @staticmethod
    def gambling(title: str, won: bool, bet: int, result: int, 
                 user: discord.Member, details: str = None) -> discord.Embed:
        """Create a gambling result embed"""
        if won:
            color = Theme.SUCCESS
            profit = result - bet
            result_text = f"+{profit:,}" if profit > 0 else f"{profit:,}"
            gif = GIFs.WIN_BIG if profit > bet else GIFs.WIN_SMALL
            status = "🎊 WINNER!"
        else:
            color = Theme.ERROR
            result_text = f"-{bet:,}"
            gif = GIFs.LOSE
            status = "💔 LOST"
        
        embed = discord.Embed(
            title=f"🎰 {title}",
            color=color,
            timestamp=datetime.now()
        )
        embed.set_author(name=f"{user.display_name} • {status}", icon_url=user.display_avatar.url)
        
        embed.description = f"""
╔══════════════════════════════╗
║  💵 **Bet:** {ModernUI.money_display(bet)}
║  📊 **Result:** `{result_text}` ⚓
║  💰 **Balance Change:** {ModernUI.money_display(abs(result-bet) if won else bet)}
╚══════════════════════════════╝
"""
        if details:
            embed.add_field(name="🎲 Details", value=details, inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=gif)
        embed.set_footer(text="⚓ Sailor Coins • Gamble responsibly!", icon_url="https://i.imgur.com/AfFp7pu.png")
        return embed

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 LOGGING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

async def log_to_channel(title: str, description: str, color: int, 
                         user: discord.Member = None, extra_fields: dict = None):
    """Send a modern log message to the logs channel"""
    log_channel_id = get_cfg("log_channel")
    if not log_channel_id:
        return
    
    channel = bot.get_channel(int(log_channel_id))
    if not channel:
        return
    
    embed = discord.Embed(
        title=f"📋 {title}",
        description=f"```\n{description}\n```",
        color=color,
        timestamp=datetime.now()
    )
    
    if user:
        embed.set_author(name=f"{user.display_name} ({user.id})", icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
    
    if extra_fields:
        for field_name, field_value in extra_fields.items():
            embed.add_field(name=field_name, value=field_value, inline=True)
    
    embed.set_footer(text="⚓ Sailor Coins Logger", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Log error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 💾 DATABASE - PERSISTENT
# ═══════════════════════════════════════════════════════════════════════════════

DB_PATH = "sailor.db"

def init_db():
    """Initialize database with all tables"""
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
        emoji       TEXT DEFAULT "⚓",
        rarity      TEXT DEFAULT "common"
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

    # Default shop items with rarity
    defaults = [
        ("2x Coin Boost", 5000, "Double coin earnings for 1 hour", "multiplier", "coins:2.0:3600", "💰", "rare"),
        ("2x Luck Charm", 3000, "Double luck in fish/mine/hunt", "multiplier", "luck:2.0:3600", "🍀", "rare"),
        ("3x Coin Boost", 12000, "Triple coin earnings for 30 minutes", "multiplier", "coins:3.0:1800", "🚀", "epic"),
        ("4x Ultra Boost", 25000, "4x earnings for 15 minutes", "multiplier", "coins:4.0:900", "⚡", "legendary"),
        ("Fishing Rod+", 2000, "1.5x fishing yield permanently", "upgrade", "fishing:1.5", "🎣", "uncommon"),
        ("Diamond Pickaxe", 2000, "1.5x mining yield permanently", "upgrade", "mining:1.5", "⛏️", "uncommon"),
        ("Hunter's Bow", 2000, "1.5x hunting yield permanently", "upgrade", "hunting:1.5", "🏹", "uncommon"),
        ("Bank Expansion", 10000, "Increase bank limit by +5000", "bank", "5000", "🏦", "rare"),
        ("Lucky Charm", 1500, "Reduce robbery chance by 50%", "protection", "rob:0.5:86400", "🧿", "uncommon"),
        ("Shield", 500, "One-time full protection from robbery", "protection", "rob_shield:1", "🛡️", "common"),
        ("Escape Card", 3000, "Escape from crime once", "protection", "crime_escape:1", "🃏", "rare"),
        ("Daily Boost", 2000, "2x daily reward for 3 days", "multiplier", "daily:2.0:259200", "📅", "rare"),
        ("Mystery Box", 7500, "Random reward: 5000-15000 coins!", "mystery", "5000:15000", "🎁", "epic"),
        ("Golden Anchor", 50000, "Exclusive collector's item", "collectible", "golden_anchor:1", "⚓", "mythic"),
    ]
    for item in defaults:
        c.execute("INSERT OR IGNORE INTO shop VALUES (NULL,?,?,?,?,?,?,?)", item)

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
    items = conn.execute("SELECT item_id, item_name, price, description, item_type, value, emoji, rarity FROM shop ORDER BY price").fetchall()
    conn.close()
    return items

def add_shop_item(name: str, price: int, desc: str, item_type: str, value: str, emoji: str, rarity: str = "common"):
    """Add shop item"""
    conn = db()
    try:
        conn.execute("INSERT INTO shop (item_name, price, description, item_type, value, emoji, rarity) VALUES (?,?,?,?,?,?,?)",
                     (name, price, desc, item_type, value, emoji, rarity))
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
    """Format coins with style"""
    return ModernUI.money_display(amount)

def fmt_time(secs: float) -> str:
    """Format time beautifully"""
    s = int(secs)
    if s < 60:
        return f"**{s}**s"
    if s < 3600:
        return f"**{s//60}**m **{s%60}**s"
    return f"**{s//3600}**h **{(s%3600)//60}**m"

# ═══════════════════════════════════════════════════════════════════════════════
# 🛍️ MODERN SHOP BUTTONS
# ═══════════════════════════════════════════════════════════════════════════════

class ShopButton(ui.Button):
    def __init__(self, item_id: int, item_name: str, price: int, emoji: str, rarity: str):
        # Color based on rarity
        style_map = {
            "common": discord.ButtonStyle.secondary,
            "uncommon": discord.ButtonStyle.success,
            "rare": discord.ButtonStyle.primary,
            "epic": discord.ButtonStyle.primary,
            "legendary": discord.ButtonStyle.danger,
            "mythic": discord.ButtonStyle.danger
        }
        style = style_map.get(rarity, discord.ButtonStyle.secondary)
        
        super().__init__(label=f"{item_name}", emoji=emoji, style=style)
        self.item_id = item_id
        self.item_name = item_name
        self.price = price
        self.rarity = rarity

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        
        if is_banned(uid):
            embed = EmbedBuilder.error("Banned", "You're economy banned!", interaction.user)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = get_user(uid)
        if data[1] < self.price:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"""
{ModernUI.divider('anchor')}

💰 **Required:** {sc(self.price)}
👛 **Your Wallet:** {sc(data[1])}
📉 **Shortage:** {sc(self.price - data[1])}

{ModernUI.divider('anchor')}

*Keep earning to afford this item!*
""",
                color=Theme.ERROR
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_image(url=GIFs.ERROR)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        conn = db()
        row = conn.execute("SELECT item_name, price, description, item_type, value, emoji, rarity FROM shop WHERE item_id=?", (self.item_id,)).fetchone()
        conn.close()
        
        if not row:
            return await interaction.response.send_message("❌ Item not found.", ephemeral=True)
        
        item_name, price, desc, item_type, value, emoji, rarity = row
        add_wallet(uid, -price)
        log_purchase(uid, item_name, price)
        
        await log_to_channel(
            title="🛍️ SHOP PURCHASE",
            description=f"{interaction.user.display_name} purchased {item_name}",
            color=Theme.GOLD,
            user=interaction.user,
            extra_fields={"💰 Price": f"{sc(price)}", "📦 Type": item_type, "💵 New Balance": f"{sc(data[1] - price)}"}
        )
        
        # Create beautiful purchase embed
        embed = discord.Embed(
            title=f"🎉 Purchase Successful!",
            color=ModernUI.rarity_color(rarity),
            timestamp=datetime.now()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        if item_type == "multiplier":
            parts = value.split(":")
            set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
            embed.description = f"""
{ModernUI.divider('sparkle')}

{emoji} **{item_name}** Activated!

⚡ **Boost:** `x{parts[1]}` {parts[0].capitalize()}
⏰ **Duration:** `{fmt_time(int(parts[2]))}`

{ModernUI.divider('sparkle')}
"""
        elif item_type == "upgrade":
            add_inv(uid, item_name)
            embed.description = f"""
{ModernUI.divider('sparkle')}

{emoji} **{item_name}** Equipped!

📝 *{desc}*

{ModernUI.divider('sparkle')}
"""
        elif item_type == "bank":
            extra = int(value)
            conn = db()
            conn.execute("UPDATE users SET bank_limit=bank_limit+? WHERE user_id=?", (extra, uid))
            conn.commit()
            conn.close()
            embed.description = f"""
{ModernUI.divider('sparkle')}

🏦 **Bank Expanded!**

📈 **New Capacity:** +{sc(extra)}

{ModernUI.divider('sparkle')}
"""
        elif item_type == "mystery":
            parts = value.split(":")
            reward = random.randint(int(parts[0]), int(parts[1]))
            add_wallet(uid, reward)
            embed.description = f"""
{ModernUI.divider('sparkle')}

🎁 **Mystery Box Opened!**

💰 **You Found:** {sc(reward)}

{ModernUI.divider('sparkle')}
"""
            embed.set_image(url=GIFs.MYSTERY_BOX)
        elif item_type == "role":
            role = discord.utils.get(interaction.guild.roles, name=value)
            if role:
                await interaction.user.add_roles(role)
                embed.description = f"""
{ModernUI.divider('sparkle')}

👑 **Role Granted!**

🎭 You now have the **{value}** role!

{ModernUI.divider('sparkle')}
"""
            else:
                add_wallet(uid, price)
                embed = EmbedBuilder.error("Role Not Found", "Refunded your purchase!", interaction.user)
        else:
            add_inv(uid, item_name)
            embed.description = f"""
{ModernUI.divider('sparkle')}

{emoji} **{item_name}** Added to Inventory!

📝 *{desc}*

{ModernUI.divider('sparkle')}
"""
        
        embed.add_field(name="💳 Transaction", value=f"Spent: {sc(price)}", inline=True)
        embed.add_field(name="💰 New Balance", value=f"{sc(data[1] - price)}", inline=True)
        embed.add_field(name="⭐ Rarity", value=f"`{rarity.upper()}`", inline=True)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if item_type != "mystery":
            embed.set_image(url=GIFs.PURCHASE_SUCCESS)
        embed.set_footer(text="⚓ Sailor Coins Shop", icon_url="https://i.imgur.com/AfFp7pu.png")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        items = get_all_shop_items()
        row = 0
        for idx, item in enumerate(items):
            item_id, item_name, price, desc, item_type, value, emoji, rarity = item
            if idx > 0 and idx % 5 == 0:
                row += 1
            if row > 4:  # Discord limit
                break
            button = ShopButton(item_id, item_name, price, emoji, rarity)
            button.row = row
            self.add_item(button)

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 BOT EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

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
        description="Sailor Coins is now online!",
        color=Theme.SUCCESS,
        extra_fields={"⏰ Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
        xp_gain = random.randint(1, 3)
        conn.execute("UPDATE users SET xp=xp+? WHERE user_id=?", (xp_gain, uid))
        row = conn.execute("SELECT xp, level FROM users WHERE user_id=?", (uid,)).fetchone()
        
        if row and row[0] >= row[1] * 100:
            new_level = row[1] + 1
            conn.execute("UPDATE users SET level=level+1, xp=0 WHERE user_id=?", (uid,))
            conn.commit()
            conn.close()
            
            try:
                level_reward = row[1] * 50
                add_wallet(uid, level_reward, "level_up")
                
                # Send level up notification
                embed = discord.Embed(
                    title="⭐ LEVEL UP!",
                    description=f"""
{ModernUI.divider('stars')}

🎉 **Congratulations {message.author.mention}!**

📈 You've reached **Level {new_level}**!

💰 **Reward:** {sc(level_reward)}

{ModernUI.divider('stars')}

*Keep chatting and earning!*
""",
                    color=Theme.GOLD,
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                embed.set_image(url=GIFs.LEVEL_UP)
                embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
                
                await message.channel.send(embed=embed)
                
                await log_to_channel(
                    title="⭐ LEVEL UP",
                    description=f"{message.author.display_name} reached Level {new_level}",
                    color=Theme.GOLD,
                    user=message.author,
                    extra_fields={"📈 New Level": str(new_level), "🎁 Reward": f"{sc(level_reward)}"}
                )
            except:
                pass
        else:
            conn.commit()
            conn.close()
    
    await bot.process_commands(message)

@tasks.loop(minutes=30)
async def passive_drop():
    """Treasure drop event"""
    drop_channel_id = get_cfg("drop_channel")
    if not drop_channel_id:
        return
    
    channel = bot.get_channel(int(drop_channel_id))
    if not channel:
        return
    
    mn = int(get_cfg("drop_min", "100"))
    mx = int(get_cfg("drop_max", "500"))
    amount = random.randint(mn, mx)
    
    embed = discord.Embed(
        title="🏴‍☠️ TREASURE WASHED ASHORE!",
        description=f"""
{ModernUI.divider('anchor')}

🎁 A mysterious chest containing **{sc(amount)}** has appeared!

⏰ **Time Limit:** `60 seconds`
📝 **To Claim:** Type `!claim`

{ModernUI.divider('anchor')}

*First sailor to claim wins!*
""",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    embed.set_image(url=GIFs.TREASURE_FOUND)
    embed.set_footer(text="⚓ Sailor Coins • Treasure Event", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    msg = await channel.send(embed=embed)
    
    def check(m):
        return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount, "treasure_drop")
        
        await log_to_channel(
            title="🎁 TREASURE CLAIMED",
            description=f"{resp.author.display_name} claimed the treasure!",
            color=Theme.GOLD,
            user=resp.author,
            extra_fields={"💰 Amount": f"{sc(amount)}"}
        )
        
        embed = discord.Embed(
            title="🎉 TREASURE CLAIMED!",
            description=f"""
{ModernUI.divider('sparkle')}

🏆 **{resp.author.mention}** claimed the treasure!

💰 **Reward:** {sc(amount)}

{ModernUI.divider('sparkle')}
""",
            color=Theme.SUCCESS,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=resp.author.display_avatar.url)
        embed.set_image(url=GIFs.TREASURE_OPEN)
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        
        await channel.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="🌊 Treasure Sank...",
            description=f"""
{ModernUI.divider('wave')}

Nobody claimed the treasure in time!

💰 **{sc(amount)}** lost to the sea...

{ModernUI.divider('wave')}

*Better luck next time, sailors!*
""",
            color=Theme.ERROR,
            timestamp=datetime.now()
        )
        embed.set_footer(text="⚓ Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
        await channel.send(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# 👑 ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.command(name="admin_setup", description="[ADMIN] Setup wizard for the bot")
@admin_only()
async def admin_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚙️ ADMIN SETUP WIZARD",
        description=f"""
{ModernUI.divider('sparkle')}

Welcome to **Sailor Coins** setup! Follow these steps:

{ModernUI.divider('sparkle')}

**Step 1️⃣** — Set Drop Channel
```/set_drop_channel #channel```

**Step 2️⃣** — Set Shop Channel  
```/set_shop_channel #channel```

**Step 3️⃣** — Set Logs Channel
```/set_log_channel #channel```

**Step 4️⃣** — Deploy Interactive Shop
```/send_shop```

{ModernUI.divider('sparkle')}

**Optional Commands:**
• `/add_item` — Add custom shop items
• `/admin_give` — Give coins to users
• `/admin_take` — Remove coins from users
• `/admin_ban` — Ban/unban from economy
• `/economy_stats` — View economy statistics

{ModernUI.divider('sparkle')}
""",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_image(url=GIFs.SHOP_BROWSE)
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_drop_channel", description="[ADMIN] Set the treasure drop channel")
@app_commands.describe(channel="The channel for treasure drops")
@admin_only()
async def set_drop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("drop_channel", str(channel.id))
    
    embed = discord.Embed(
        title="✅ Drop Channel Set!",
        description=f"""
{ModernUI.divider('anchor')}

🎁 Treasure drops will now appear in:
{channel.mention}

{ModernUI.divider('anchor')}
""",
        color=Theme.SUCCESS,
        timestamp=datetime.now()
    )
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Drop channel set to {channel.mention}",
        color=Theme.INFO,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_shop_channel", description="[ADMIN] Set the shop channel")
@app_commands.describe(channel="The channel for the interactive shop")
@admin_only()
async def set_shop_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("shop_channel", str(channel.id))
    
    embed = discord.Embed(
        title="✅ Shop Channel Set!",
        description=f"""
{ModernUI.divider('anchor')}

🛍️ The shop will be displayed in:
{channel.mention}

Use `/send_shop` to deploy the shop!

{ModernUI.divider('anchor')}
""",
        color=Theme.SUCCESS,
        timestamp=datetime.now()
    )
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Shop channel set to {channel.mention}",
        color=Theme.INFO,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="set_log_channel", description="[ADMIN] Set the logs channel")
@app_commands.describe(channel="The channel for bot logs")
@admin_only()
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_cfg("log_channel", str(channel.id))
    
    embed = discord.Embed(
        title="✅ Log Channel Set!",
        description=f"""
{ModernUI.divider('anchor')}

📋 Bot logs will be sent to:
{channel.mention}

{ModernUI.divider('anchor')}
""",
        color=Theme.SUCCESS,
        timestamp=datetime.now()
    )
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title="⚙️ CONFIG CHANGE",
        description=f"Log channel set to {channel.mention}",
        color=Theme.INFO,
        user=interaction.user
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="send_shop", description="[ADMIN] Deploy the interactive shop")
@admin_only()
async def send_shop(interaction: discord.Interaction):
    shop_channel_id = get_cfg("shop_channel")
    if not shop_channel_id:
        embed = EmbedBuilder.error("No Shop Channel", "Use `/set_shop_channel` first!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    channel = bot.get_channel(int(shop_channel_id))
    if not channel:
        return await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
    
    items = get_all_shop_items()
    
    # Create beautiful shop embed
    embed = discord.Embed(
        title="🛍️ SAILOR COINS SHOP",
        description=f"""
{ModernUI.divider('sparkle')}

Welcome to the **Sailor Shop**! 🏪

Click the buttons below to purchase items instantly!
All purchases are deducted from your wallet.

{ModernUI.divider('sparkle')}
""",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    
    # Categorize items
    categories = {
        "🚀 BOOSTERS": [],
        "⚙️ UPGRADES": [],
        "🛡️ PROTECTION": [],
        "🎁 SPECIAL": []
    }
    
    for item in items:
        item_id, item_name, price, desc, item_type, value, emoji, rarity = item
        rarity_badge = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟠",
            "mythic": "🔴"
        }.get(rarity, "⚪")
        
        display = f"{emoji} **{item_name}** {rarity_badge}\n└ {sc(price)} • *{desc[:30]}...*" if len(desc) > 30 else f"{emoji} **{item_name}** {rarity_badge}\n└ {sc(price)} • *{desc}*"
        
        if item_type == "multiplier":
            categories["🚀 BOOSTERS"].append(display)
        elif item_type == "upgrade":
            categories["⚙️ UPGRADES"].append(display)
        elif item_type == "protection":
            categories["🛡️ PROTECTION"].append(display)
        else:
            categories["🎁 SPECIAL"].append(display)
    
    for cat_name, cat_items in categories.items():
        if cat_items:
            embed.add_field(name=cat_name, value="\n".join(cat_items[:5]), inline=False)
    
    embed.add_field(
        name="📊 Rarity Guide",
        value="⚪ Common • 🟢 Uncommon • 🔵 Rare • 🟣 Epic • 🟠 Legendary • 🔴 Mythic",
        inline=False
    )
    
    embed.set_image(url=GIFs.SHOP_BROWSE)
    embed.set_footer(text="⚓ Click buttons to buy! • Sailor Coins", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await channel.send(embed=embed, view=ShopView())
    
    await log_to_channel(
        title="🛍️ SHOP DEPLOYED",
        description=f"Shop sent to {channel.mention}",
        color=Theme.INFO,
        user=interaction.user
    )
    
    confirm = discord.Embed(
        title="✅ Shop Deployed!",
        description=f"The shop has been sent to {channel.mention}",
        color=Theme.SUCCESS
    )
    confirm.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await interaction.response.send_message(embed=confirm, ephemeral=True)

@bot.tree.command(name="add_item", description="[ADMIN] Add a new shop item")
@app_commands.describe(
    name="Item name",
    price="Item price",
    description="Item description",
    item_type="Type: multiplier, upgrade, protection, mystery, collectible",
    value="Value (e.g., coins:2.0:3600 for multipliers)",
    emoji="Item emoji",
    rarity="Rarity: common, uncommon, rare, epic, legendary, mythic"
)
@admin_only()
async def add_item(interaction: discord.Interaction, name: str, price: int, description: str, 
                   item_type: str, value: str, emoji: str, rarity: str = "common"):
    if add_shop_item(name, price, description, item_type, value, emoji, rarity):
        embed = discord.Embed(
            title="✅ Item Added!",
            description=f"""
{ModernUI.divider('sparkle')}

{emoji} **{name}** has been added to the shop!

💰 **Price:** {sc(price)}
📝 **Description:** {description}
📦 **Type:** {item_type}
⭐ **Rarity:** {rarity.upper()}

{ModernUI.divider('sparkle')}

Use `/send_shop` to update the shop display!
""",
            color=Theme.SUCCESS,
            timestamp=datetime.now()
        )
        embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
        
        await log_to_channel(
            title="✨ ITEM ADDED",
            description=f"New shop item: {name}",
            color=Theme.AMETHYST,
            user=interaction.user,
            extra_fields={"💰 Price": f"{sc(price)}", "⭐ Rarity": rarity}
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = EmbedBuilder.error("Item Exists", "An item with this name already exists!", interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_give", description="[ADMIN] Give coins to a user")
@app_commands.describe(user="The user to give coins to", amount="Amount of coins to give")
@admin_only()
async def admin_give(interaction: discord.Interaction, user: discord.Member, amount: int):
    add_wallet(user.id, amount, "admin_give")
    
    embed = discord.Embed(
        title="💰 Coins Given!",
        description=f"""
{ModernUI.divider('sparkle')}

**Admin Action:** Coins Given

👤 **Recipient:** {user.mention}
💰 **Amount:** {sc(amount)}
👑 **By:** {interaction.user.mention}

{ModernUI.divider('sparkle')}
""",
        color=Theme.SUCCESS,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title="💳 ADMIN GIVE",
        description=f"Gave {user.display_name} {sc(amount)}",
        color=Theme.SUCCESS,
        user=interaction.user,
        extra_fields={"👤 Recipient": user.mention, "💰 Amount": f"{sc(amount)}"}
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_take", description="[ADMIN] Take coins from a user")
@app_commands.describe(user="The user to take coins from", amount="Amount of coins to take")
@admin_only()
async def admin_take(interaction: discord.Interaction, user: discord.Member, amount: int):
    data = get_user(user.id)
    actual = min(amount, data[1])
    add_wallet(user.id, -actual, "admin_take")
    
    embed = discord.Embed(
        title="💔 Coins Taken!",
        description=f"""
{ModernUI.divider('sparkle')}

**Admin Action:** Coins Taken

👤 **From:** {user.mention}
💰 **Amount:** {sc(actual)}
👑 **By:** {interaction.user.mention}

{ModernUI.divider('sparkle')}
""",
        color=Theme.ERROR,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title="💔 ADMIN TAKE",
        description=f"Took {sc(actual)} from {user.display_name}",
        color=Theme.ERROR,
        user=interaction.user,
        extra_fields={"👤 From": user.mention, "💰 Amount": f"{sc(actual)}"}
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_ban", description="[ADMIN] Ban/unban user from economy")
@app_commands.describe(user="The user to ban/unban")
@admin_only()
async def admin_ban(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    if conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user.id,)).fetchone():
        conn.execute("DELETE FROM banned_users WHERE user_id=?", (user.id,))
        action = "UNBANNED"
        emoji = "✅"
        color = Theme.SUCCESS
        gif = None
    else:
        conn.execute("INSERT INTO banned_users VALUES(?)", (user.id,))
        action = "BANNED"
        emoji = "🚫"
        color = Theme.ERROR
        gif = GIFs.BANNED
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title=f"{emoji} User {action}!",
        description=f"""
{ModernUI.divider('anchor')}

👤 **User:** {user.mention}
📋 **Status:** {action}
👑 **By:** {interaction.user.mention}

{ModernUI.divider('anchor')}
""",
        color=color,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    if gif:
        embed.set_image(url=gif)
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await log_to_channel(
        title=f"{emoji} USER {action}",
        description=f"{user.display_name} has been {action.lower()}",
        color=color,
        user=interaction.user,
        extra_fields={"👤 User": user.mention, "📋 Action": action}
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="economy_stats", description="[ADMIN] View economy statistics")
@admin_only()
async def economy_stats(interaction: discord.Interaction):
    conn = db()
    stats = conn.execute("""
        SELECT COUNT(*), COALESCE(SUM(wallet), 0), COALESCE(SUM(bank), 0), 
               COALESCE(SUM(total_earned), 0), COALESCE(AVG(level), 1)
        FROM users
    """).fetchone()
    banned_count = conn.execute("SELECT COUNT(*) FROM banned_users").fetchone()[0]
    top_user = conn.execute("""
        SELECT user_id, wallet+bank as total FROM users ORDER BY total DESC LIMIT 1
    """).fetchone()
    recent_transactions = conn.execute("""
        SELECT COUNT(*) FROM transactions WHERE timestamp > ?
    """, (time.time() - 86400,)).fetchone()[0]
    conn.close()
    
    total_users, total_wallets, total_banks, total_earned, avg_level = stats
    total_economy = (total_wallets or 0) + (total_banks or 0)
    
    embed = discord.Embed(
        title="📊 ECONOMY STATISTICS",
        description=f"""
{ModernUI.divider('sparkle')}

**Server Economy Overview**

{ModernUI.divider('sparkle')}
""",
        color=Theme.SAPPHIRE,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Total Users", value=f"```{total_users:,}```", inline=True)
    embed.add_field(name="🚫 Banned Users", value=f"```{banned_count:,}```", inline=True)
    embed.add_field(name="📈 Avg Level", value=f"```{avg_level:.1f}```", inline=True)
    
    embed.add_field(name="💰 Total in Wallets", value=f"```{sc(total_wallets)}```", inline=True)
    embed.add_field(name="🏦 Total in Banks", value=f"```{sc(total_banks)}```", inline=True)
    embed.add_field(name="💎 Total Economy", value=f"```{sc(total_economy)}```", inline=True)
    
    embed.add_field(name="📈 All-Time Earned", value=f"```{sc(total_earned)}```", inline=True)
    embed.add_field(name="📋 24h Transactions", value=f"```{recent_transactions:,}```", inline=True)
    
    if top_user:
        top_member = interaction.guild.get_member(top_user[0])
        top_name = top_member.display_name if top_member else "Unknown"
        embed.add_field(name="👑 Richest User", value=f"```{top_name}\n{sc(top_user[1])}```", inline=True)
    
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else bot.user.display_avatar.url)
    embed.set_footer(text="⚓ Sailor Coins Admin", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 💰 MEMBER COMMANDS - EARNING
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="💰 Check your or another user's balance")
@app_commands.describe(user="User to check (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    
    # Calculate stats
    wallet, bank, bank_limit = data[1], data[2], data[3]
    total_earned, level, xp, streak = data[4], data[5], data[6], data[7]
    net_worth = wallet + bank
    xp_needed = level * 100
    
    embed = discord.Embed(
        title=f"⚓ {target.display_name}'s Wallet",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    embed.description = f"""
{ModernUI.divider('anchor')}

{ModernUI.xp_bar(xp, xp_needed, level)}

{ModernUI.divider('anchor')}

**💵 Financial Overview**
"""
    
    # Financial fields
    embed.add_field(name="👛 Wallet", value=f"```{sc(wallet)}```", inline=True)
    embed.add_field(name="🏦 Bank", value=f"```{sc(bank)} / {sc(bank_limit)}```", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"```{sc(net_worth)}```", inline=True)
    
    # Progress fields
    embed.add_field(name="📈 Total Earned", value=f"```{sc(total_earned)}```", inline=True)
    embed.add_field(name="🔥 Daily Streak", value=f"```{streak} days```", inline=True)
    
    # Bank capacity bar
    bank_percentage = (bank / bank_limit * 100) if bank_limit > 0 else 0
    embed.add_field(
        name="🏦 Bank Capacity",
        value=ModernUI.progress_bar(bank, bank_limit, 12),
        inline=False
    )
    
    embed.set_footer(text="⚓ Sailor Coins • /help for commands", icon_url="https://i.imgur.com/AfFp7pu.png")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="🌅 Claim your daily reward")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    
    if is_banned(uid):
        embed = EmbedBuilder.error("Banned", "You're banned from the economy!", interaction.user)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    on_cd, rem = check_cd(uid, "daily", 86400)
    if on_cd:
        embed = discord.Embed(
            title="⏰ Daily Already Claimed!",
            description=f"""
{ModernUI.divider('wave')}

Come back in **{fmt_time(rem)}**!

{ModernUI.divider('wave')}
""",
            color=Theme.WARNING
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    data = get_user(uid)
    last_daily = data[8]
    
    # Check streak (if claimed within 48 hours, keep streak)
    if time.time() - last_daily < 172800:  # 48 hours
        streak = data[7] + 1
    else:
        streak = 1
    
    daily_mult = get_mult(uid, "daily")
    base = random.randint(200, 500)
    streak_bonus = min(streak * 15, 500)
    amount = int((base + streak_bonus) * daily_mult)
    
    add_wallet(uid, amount, "daily")
    set_cd(uid, "daily")
    
    conn = db()
    conn.execute("UPDATE users SET streak=?, last_daily=? WHERE user_id=?", (streak, time.time(), uid))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="🌅 DAILY REWARD CLAIMED!",
        color=Theme.GOLD,
        timestamp=datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
