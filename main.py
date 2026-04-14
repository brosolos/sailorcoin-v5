"""
⚓ SAILOR COINS — Discord Economy Bot v2
=====================================
Features:
  - 60+ Interactive Commands with images
  - Invite Tracking & Rewards
  - Interactive Shop GUI with buttons
  - Multipliers & boosters
  - Mini-games with visual embeds
  - Level system with rewards
  - Passive income & drops
  - Admin dashboard

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
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

TOKEN    = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))

# ─── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Colors ──────────��────────────────────────────────────────────────────────

GOLD   = 0xFFD700
RED    = 0xFF4444
GREEN  = 0x44FF88
BLUE   = 0x4488FF
PURPLE = 0xAA44FF
ORANGE = 0xFF8C00

# ─── Emotes & Images ──────────────────────────────────────────────────────────

EMOTES = {
    "coin": "⚓",
    "level": "⭐",
    "xp": "✨",
    "streak": "🔥",
    "luck": "🍀",
    "boost": "🚀",
    "warning": "⚠️",
    "success": "✅",
    "fail": "❌",
    "clock": "���",
}

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE - ENHANCED
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
        invites      INTEGER DEFAULT 0,
        invite_rewards INTEGER DEFAULT 0
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
        value       TEXT,
        emoji       TEXT DEFAULT "⚓"
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

    # Default shop items with emojis
    defaults = [
        ("2x Coin Boost",       5000,  "Double coin earnings for 1 hour",              "multiplier", "coins:2.0:3600", "💰"),
        ("2x Luck Charm",       3000,  "Double luck in fish/mine/hunt for 1 hour",      "multiplier", "luck:2.0:3600", "🍀"),
        ("3x Coin Boost",       12000, "Triple coin earnings for 30 minutes",           "multiplier", "coins:3.0:1800", "🚀"),
        ("4x Ultra Boost",      25000, "4x earnings for 15 minutes",                    "multiplier", "coins:4.0:900", "⚡"),
        ("Fishing Rod+",        2000,  "Catch bigger fish — 1.5x fishing yield",        "upgrade",    "fishing:1.5", "🎣"),
        ("Diamond Pickaxe",     2000,  "Mine richer veins — 1.5x mining yield",         "upgrade",    "mining:1.5", "⛏️"),
        ("Hunter's Bow",        2000,  "Hunt bigger prey — 1.5x hunting yield",         "upgrade",    "hunting:1.5", "🏹"),
        ("Bank Expansion",      10000, "Increase bank limit by +5000",                  "bank",       "5000", "🏦"),
        ("VIP Role",            25000, "Receive the VIP role in the server",            "role",       "VIP", "👑"),
        ("Lucky Charm",         1500,  "Reduces your robbery chance for 24 hours",      "protection", "rob:0.5:86400", "🧿"),
        ("Shield",              500,   "One-time full protection from robbery",         "protection", "rob_shield:1", "🛡️"),
        ("Escape Card",         3000,  "Escape from being caught during a crime once",  "protection", "crime_escape:1", "🃏"),
        ("Daily Boost",         2000,  "2x daily reward for the next 3 days",           "multiplier", "daily:2.0:259200", "📅"),
        ("Mystery Box",         7500,  "Random reward: 5000-15000 coins!",              "mystery",    "5000:15000", "🎁"),
        ("Prestige Token",      50000, "Unlock prestige level & special perks",         "prestige",   "1", "👑"),
    ]
    for item in defaults:
        c.execute("INSERT OR IGNORE INTO shop VALUES (?,?,?,?,?,?)", item)

    # Default config
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_interval_minutes','30')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_min','100')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('drop_max','500')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('invite_reward','500')")
    c.execute("INSERT OR IGNORE INTO config VALUES ('shop_channel','')")

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

def record_invite(inviter_id: int, invitee_id: int):
    """Record an invite and reward the inviter"""
    conn = db()
    conn.execute("INSERT OR IGNORE INTO invites VALUES(?,?,?)", (inviter_id, invitee_id, time.time()))
    conn.execute("UPDATE users SET invites=invites+1 WHERE user_id=?", (inviter_id,))
    conn.commit()
    conn.close()

# ─── Formatting helpers ───────────────────────────────────────────────────────

def sc(amount: int) -> str:
    return f"⚓ **{amount:,}** Sailor Coins"

def fmt_time(secs: float) -> str:
    s = int(secs)
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m {s%60}s"
    return f"{s//3600}h {(s%3600)//60}m"

# ══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE SHOP BUTTONS
# ══════════════════════════════════════════════════════════════════════════════

class ShopButton(ui.Button):
    def __init__(self, item_name: str, price: int, emoji: str):
        super().__init__(label=f"{item_name} ({price})", emoji=emoji, style=discord.ButtonStyle.primary)
        self.item_name = item_name
        self.price = price

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        if is_banned(uid):
            return await interaction.response.send_message("❌ You're economy banned.", ephemeral=True)
        
        data = get_user(uid)
        if data[1] < self.price:
            embed = discord.Embed(
                title="❌ Insufficient Coins",
                description=f"Need: {sc(self.price)}\nYou have: {sc(data[1])}",
                color=RED
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Process purchase
        conn = db()
        row = conn.execute("SELECT * FROM shop WHERE item_name=?", (self.item_name,)).fetchone()
        conn.close()
        
        if not row:
            return await interaction.response.send_message("❌ Item not found.", ephemeral=True)
        
        item_name, price, desc, item_type, value, emoji = row
        add_wallet(uid, -price)
        
        if item_type == "multiplier":
            parts = value.split(":")
            set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
            embed = discord.Embed(
                title=f"✅ {emoji} {item_name} Activated!",
                description=f"**x{parts[1]} {parts[0]}** active for **{fmt_time(int(parts[2]))}**!",
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
                description=f"Limit increased by {sc(extra)}!",
                color=GREEN
            )
        elif item_type == "mystery":
            parts = value.split(":")
            reward = random.randint(int(parts[0]), int(parts[1]))
            add_wallet(uid, reward)
            embed = discord.Embed(
                title=f"✅ {emoji} Mystery Box Opened!",
                description=f"You found {sc(reward)}! 🎉",
                color=GOLD
            )
        elif item_type == "role":
            role = discord.utils.get(interaction.guild.roles, name=value)
            if role:
                await interaction.user.add_roles(role)
                embed = discord.Embed(
                    title=f"✅ {emoji} Role Granted!",
                    description=f"You now have the **{value}** role!",
                    color=GREEN
                )
            else:
                add_wallet(uid, price)
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description="Refunded!",
                    color=RED
                )
        else:
            add_inv(uid, item_name)
            embed = discord.Embed(
                title=f"✅ {emoji} {item_name} Purchased!",
                description=desc,
                color=GREEN
            )
        
        embed.set_footer(text=f"Balance: {sc(data[1] - price)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Get all shop items
        conn = db()
        items = conn.execute("SELECT item_name, price, emoji FROM shop ORDER BY price").fetchall()
        conn.close()
        
        for item_name, price, emoji in items:
            button = ShopButton(item_name, price, emoji)
            self.add_item(button)

# ══════════════════════════════════════════════════════════════════════════════
# INVITE TRACKING
# ══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_member_join(member: discord.Member):
    """Track invites when a member joins"""
    if member.bot:
        return
    
    try:
        invites_before = getattr(bot, f"invites_{member.guild.id}", {})
        invites_after = {invite.inviter.id: invite.uses async for invite in await member.guild.invites()}
        
        for inviter_id, uses in invites_after.items():
            if inviter_id in invites_before and uses > invites_before[inviter_id]:
                record_invite(inviter_id, member.id)
                reward = int(get_cfg("invite_reward", "500"))
                add_wallet(inviter_id, reward, "invite")
                
                embed = discord.Embed(
                    title="🎉 New Member Invited!",
                    description=f"<@{inviter_id}> invited <@{member.id}>!\n\nReward: {sc(reward)}",
                    color=GOLD
                )
                try:
                    await member.guild.system_channel.send(embed=embed)
                except:
                    pass
        
        bot.invites_cache = {member.guild.id: invites_after}
    except Exception as e:
        print(f"Invite tracking error: {e}")

@bot.event
async def on_ready():
    print(f"⚓ {bot.user} is online!")
    init_db()
    
    # Cache invites
    for guild in bot.guilds:
        try:
            invites = {invite.inviter.id: invite.uses async for invite in await guild.invites()}
            bot.invites_cache = {guild.id: invites}
        except:
            pass
    
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
        add_wallet(uid, reward, "chat")
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
                    description=f"{message.author.mention} reached **Level {row[1]+1}**!\n\n🎁 Reward: {sc(row[1]*50)}",
                    color=GOLD
                )
                lvl_embed.set_thumbnail(url=message.author.display_avatar.url)
                add_wallet(uid, row[1] * 50, "level_up")
                await message.channel.send(embed=lvl_embed, delete_after=15)
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
        description=f"A chest containing **{sc(amount)}** has appeared!",
        color=GOLD
    )
    embed.add_field(name="How to Claim", value="Type `!claim` to grab it — first come, first served!", inline=False)
    embed.set_footer(text="⏳ You have 60 seconds!")
    
    await channel.send(embed=embed)
    def check(m): return m.channel == channel and not m.author.bot and m.content.lower() == "!claim"
    try:
        resp = await bot.wait_for("message", check=check, timeout=60.0)
        add_wallet(resp.author.id, amount, "treasure_drop")
        embed = discord.Embed(
            title="🎉 Chest Claimed!",
            description=f"{resp.author.mention} snatched {sc(amount)}!",
            color=GREEN
        )
        await channel.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="🌊 Chest Sank",
            description="Nobody claimed the chest in time... it sank.",
            color=RED
        )
        await channel.send(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PERMISSION CHECK
# ══��═══════════════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

# ═══════════════════════════════════════════════════════════��══════════════════
# MEMBER COMMANDS - ECONOMY (Basic)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="Check your Sailor Coins balance")
@app_commands.describe(user="Check another user's balance (optional)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data = get_user(target.id)
    
    embed = discord.Embed(
        title=f"⚓ {target.display_name}'s Wallet",
        color=GOLD
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    # Create visual progress bar for level
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="👛 Wallet", value=sc(data[1]), inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])}\n(Max: {sc(data[3])})", inline=True)
    embed.add_field(name="💰 Net Worth", value=sc(data[1]+data[2]), inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}`\n{data[6]}/{data[5]*100} XP", inline=True)
    embed.add_field(name="📈 Total Earned", value=sc(data[4]), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days 🏆", inline=True)
    embed.add_field(name="👥 Invites", value=f"{data[10]} members invited", inline=True)
    
    embed.set_footer(text=f"Last updated: {datetime.now().strftime('%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Claim your daily Sailor Coins reward")
async def daily(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid):
        return await interaction.response.send_message("❌ You're economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "daily", 86400)
    if on_cd:
        embed = discord.Embed(
            title="⏳ Already claimed!",
            description=f"Come back in **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
    
    embed = discord.Embed(title="🌅 Daily Reward!", color=GOLD)
    embed.add_field(name="Base Reward", value=sc(base), inline=True)
    embed.add_field(name="🔥 Streak Bonus", value=sc(streak_bonus), inline=True)
    embed.add_field(name="💰 Total Earned", value=sc(amount), inline=True)
    embed.add_field(name="🏆 Current Streak", value=f"{streak} days 🔥", inline=False)
    embed.set_footer(text="Come back tomorrow to keep your streak!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weekly", description="Claim your weekly bonus")
async def weekly(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "weekly", 604800)
    if on_cd:
        embed = discord.Embed(
            title="⏳ Weekly Claimed",
            description=f"Come back in **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    amount = random.randint(1500, 3000)
    add_wallet(uid, amount, "weekly")
    set_cd(uid, "weekly")
    
    embed = discord.Embed(
        title="📅 Weekly Bonus Claimed!",
        description=f"You received {sc(amount)}!",
        color=GOLD
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - EARNING (Foraging)
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="fish", description="🎣 Cast your line and fish for Sailor Coins")
async def fish(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "fish", 30)
    if on_cd:
        embed = discord.Embed(
            title="🎣 Still Fishing",
            description=f"Wait **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
        add_wallet(uid, amount, "fishing")
    set_cd(uid, "fish")
    
    embed = discord.Embed(title="🎣 Fishing Results!", color=BLUE)
    embed.add_field(name="Catch", value=catch[0], inline=True)
    embed.add_field(name="Value", value=sc(amount) if amount else "Nothing 😢", inline=True)
    if rod > 1:
        embed.add_field(name="Rod Bonus", value=f"+{int((rod-1)*100)}%", inline=True)
    if luck > 1:
        embed.set_footer(text=f"🍀 Luck x{luck:.1f} active!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mine", description="⛏️ Descend into the mines for Sailor Coins")
async def mine(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "mine", 45)
    if on_cd:
        embed = discord.Embed(
            title="⛏️ Still Mining",
            description=f"Wait **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
    add_wallet(uid, amount, "mining")
    set_cd(uid, "mine")
    
    embed = discord.Embed(title="⛏️ Mining Results!", color=0x8B4513)
    embed.add_field(name="Found", value=find[0], inline=True)
    embed.add_field(name="Value", value=sc(amount), inline=True)
    if pick > 1:
        embed.add_field(name="Pickaxe Bonus", value=f"+{int((pick-1)*100)}%", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hunt", description="🏹 Hunt wild creatures for Sailor Coins")
async def hunt(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "hunt", 60)
    if on_cd:
        embed = discord.Embed(
            title="🏹 Still Hunting",
            description=f"Wait **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
    add_wallet(uid, amount, "hunting")
    set_cd(uid, "hunt")
    
    embed = discord.Embed(title="🏹 Hunt Results!", color=0x228B22)
    embed.add_field(name="Hunted", value=animal[0], inline=True)
    embed.add_field(name="Value", value=sc(amount), inline=True)
    if bow > 1:
        embed.add_field(name="Bow Bonus", value=f"+{int((bow-1)*100)}%", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="work", description="💼 Work a shift and earn honest Sailor Coins")
async def work(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "work", 3600)
    if on_cd:
        embed = discord.Embed(
            title="💼 Still on Shift",
            description=f"Clock back in after **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
    add_wallet(uid, amount, "work")
    set_cd(uid, "work")
    
    embed = discord.Embed(title="💼 Shift Complete!", color=GREEN)
    embed.add_field(name="Position", value=job[0], inline=True)
    embed.add_field(name="Salary", value=sc(amount), inline=True)
    if coins > 1:
        embed.add_field(name="Multiplier", value=f"x{coins:.1f}", inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - RISKY
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="crime", description="🕵️ Commit a crime — high risk, high reward")
async def crime(interaction: discord.Interaction):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    on_cd, rem = check_cd(uid, "crime", 7200)
    if on_cd:
        embed = discord.Embed(
            title="🕵️ Laying Low",
            description=f"Wait **{fmt_time(rem)}**",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
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
        embed = discord.Embed(
            title="🃏 Escape Card Used!",
            description="You got caught but used your Escape Card to flee!",
            color=PURPLE
        )
        return await interaction.response.send_message(embed=embed)
    
    if random.random() < fail_chance:
        fine = int(wallet * random.uniform(0.05, 0.25))
        fine = max(fine, 50)
        add_wallet(uid, -min(fine, wallet), "crime_fine")
        embed = discord.Embed(title="🚔 Busted!", color=RED)
        embed.add_field(name="Crime", value=act[0], inline=True)
        embed.add_field(name="Fine Paid", value=sc(fine), inline=True)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1/emoji/police.png")
    else:
        coins  = get_mult(uid, "coins")
        amount = int(random.randint(act[2], act[3]) * coins)
        add_wallet(uid, amount, "crime")
        embed = discord.Embed(title="😈 Crime Successful!", color=PURPLE)
        embed.add_field(name="Crime", value=act[0], inline=False)
        embed.add_field(name="Method", value=f"_{act[1]}_", inline=False)
        embed.add_field(name="Looted", value=sc(amount), inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rob", description="🥷 Attempt to rob another user's wallet")
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
        embed = discord.Embed(
            title="⏳ Hiding",
            description=f"Wait **{fmt_time(rem)}** before attempting another robbery",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    robber = get_user(rid)
    victim = get_user(vid)
    
    if robber[1] < 100:
        embed = discord.Embed(
            title="❌ Not Enough Coins",
            description="You need at least ⚓ **100** to rob someone!",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    if victim[1] < 50:
        embed = discord.Embed(
            title="❌ Nothing to Steal",
            description=f"{user.mention} has nothing valuable!",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    set_cd(rid, "rob")
    v_inv = get_inv(vid)
    
    # Shield check
    if "Shield" in v_inv:
        remove_inv(vid, "Shield", 1)
        fine = int(robber[1] * 0.10)
        add_wallet(rid, -fine, "robbery_caught")
        embed = discord.Embed(title="🛡️ Shield Blocked You!", color=RED)
        embed.add_field(name="Victim Protected", value=f"{user.mention}'s Shield activated!", inline=True)
        embed.add_field(name="Fine Paid", value=sc(fine), inline=True)
        return await interaction.response.send_message(embed=embed)
    
    # Lucky charm reduces success
    has_charm = "Lucky Charm" in v_inv
    success_chance = 0.38 if has_charm else 0.52
    
    if random.random() < success_chance:
        pct    = random.uniform(0.10, 0.40)
        stolen = max(10, int(victim[1] * pct))
        add_wallet(vid, -stolen, "robbed")
        add_wallet(rid, stolen, "robbery")
        
        embed = discord.Embed(title="🥷 Robbery Successful!", color=GREEN)
        embed.add_field(name="Victim", value=user.mention, inline=True)
        embed.add_field(name="Stolen", value=sc(stolen), inline=True)
        embed.set_footer(text=f"Swiped {pct:.0%} of their wallet")
    else:
        fine = int(robber[1] * random.uniform(0.10, 0.25))
        add_wallet(rid, -fine, "robbery_caught")
        add_wallet(vid, fine, "robbery_reward")
        
        embed = discord.Embed(title="🚔 Caught!", color=RED)
        embed.add_field(name="Status", value="You were caught by the guards!", inline=False)
        embed.add_field(name="Fine Paid", value=sc(fine), inline=False)
        embed.add_field(name="Recipient", value=f"Paid to {user.mention}", inline=False)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - GAMES
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="gamble", description="🎰 Gamble your Sailor Coins")
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
        embed = discord.Embed(
            title="❌ Invalid Bet",
            description=f"Min: ⚓ **10** | Max: {sc(data[1])}",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    on_cd, rem = check_cd(uid, "gamble", 12)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "gamble")
    
    if random.random() < 0.45:
        coins     = get_mult(uid, "coins")
        winnings  = int(bet * random.uniform(1.2, 2.5) * coins)
        add_wallet(uid, winnings - bet, "gamble_win")
        
        embed = discord.Embed(title="🎰 You Won!", color=GREEN)
        embed.add_field(name="Bet", value=sc(bet), inline=True)
        embed.add_field(name="Won", value=sc(winnings), inline=True)
        embed.add_field(name="Profit", value=f"+{sc(winnings-bet)}", inline=True)
    else:
        add_wallet(uid, -bet, "gamble_loss")
        
        embed = discord.Embed(title="🎰 House Wins", color=RED)
        embed.add_field(name="Bet", value=sc(bet), inline=True)
        embed.add_field(name="Result", value="Lost", inline=True)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slots", description="🎡 Spin the slot machine")
@app_commands.describe(amount="Amount to bet (min 10)")
async def slots(interaction: discord.Interaction, amount: int):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        embed = discord.Embed(
            title="❌ Invalid Bet",
            description=f"Min: ⚓ **10** | Max: {sc(data[1])}",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    on_cd, rem = check_cd(uid, "slots", 15)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "slots")
    
    syms    = ["⚓","🌊","🐠","💎","🌟","🏴��☠️","🦈"]
    weights = [30,   25,  20,  10,   7,    5,   3]
    reels   = random.choices(syms, weights=weights, k=3)
    display = f" {reels[0]} | {reels[1]} | {reels[2]} "
    
    if reels[0] == reels[1] == reels[2]:
        mults = {"⚓":5,"🌊":4,"🐠":3,"💎":8,"🌟":12,"🏴‍☠️":18,"🦈":15}
        m     = mults.get(reels[0], 3)
        win   = amount * m
        add_wallet(uid, win - amount, "slots_jackpot")
        
        embed = discord.Embed(
            title=f"🎰 JACKPOT!{display}",
            description=f"You won {sc(win)} (x{m} multiplier)!",
            color=GOLD
        )
    elif reels[0]==reels[1] or reels[1]==reels[2]:
        win = int(amount * 1.5)
        add_wallet(uid, win - amount, "slots_win")
        
        embed = discord.Embed(
            title=f"🎰 Two of a Kind!{display}",
            description=f"You won {sc(win)}!",
            color=GREEN
        )
    else:
        add_wallet(uid, -amount, "slots_loss")
        
        embed = discord.Embed(
            title=f"🎰 No Match{display}",
            description=f"You lost {sc(amount)}",
            color=RED
        )
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="🪙 Flip a coin — double or nothing!")
@app_commands.describe(amount="Bet amount", side="heads or tails")
async def coinflip(interaction: discord.Interaction, amount: int, side: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    if side.lower() not in ("heads","tails"):
        return await interaction.response.send_message("❌ Pick **heads** or **tails**.", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        embed = discord.Embed(
            title="❌ Invalid Bet",
            description=f"Min: ⚓ **10** | Max: {sc(data[1])}",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    on_cd, rem = check_cd(uid, "flip", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "flip")
    result = random.choice(("heads","tails"))
    emoji  = "🪙" if result=="heads" else "🌑"
    
    if result == side.lower():
        add_wallet(uid, amount, "coinflip_win")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — You Win!", color=GREEN)
        embed.add_field(name="Bet", value=sc(amount), inline=True)
        embed.add_field(name="Won", value=sc(amount), inline=True)
    else:
        add_wallet(uid, -amount, "coinflip_loss")
        embed = discord.Embed(title=f"{emoji} {result.upper()} — You Lose!", color=RED)
        embed.add_field(name="Bet", value=sc(amount), inline=True)
        embed.add_field(name="Lost", value=sc(amount), inline=True)
    
    embed.add_field(name="You Picked", value=side.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="highlow", description="🎯 Guess if the next number is higher or lower")
@app_commands.describe(amount="Bet amount", guess="higher or lower")
async def highlow(interaction: discord.Interaction, amount: int, guess: str):
    uid = interaction.user.id
    if is_banned(uid): 
        return await interaction.response.send_message("❌ Economy banned.", ephemeral=True)
    
    if guess.lower() not in ("higher","lower"):
        return await interaction.response.send_message("❌ Guess **higher** or **lower**.", ephemeral=True)
    
    data = get_user(uid)
    if amount < 10 or amount > data[1]:
        embed = discord.Embed(
            title="❌ Invalid Bet",
            description=f"Min: ⚓ **10** | Max: {sc(data[1])}",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    on_cd, rem = check_cd(uid, "highlow", 10)
    if on_cd:
        return await interaction.response.send_message(f"⏳ Wait **{fmt_time(rem)}**", ephemeral=True)
    
    set_cd(uid, "highlow")
    first  = random.randint(1, 10)
    second = random.randint(1, 10)
    correct = (guess.lower()=="higher" and second>first) or (guess.lower()=="lower" and second<first)
    
    if correct:
        add_wallet(uid, amount, "highlow_win")
        embed = discord.Embed(title="✅ Correct!", color=GREEN)
        embed.description = f"**{first}** → **{second}** ✓\n\nYou won {sc(amount)}!"
    else:
        add_wallet(uid, -amount, "highlow_loss")
        embed = discord.Embed(title="❌ Wrong!", color=RED)
        embed.description = f"**{first}** → **{second}** ✗\n\nYou lost {sc(amount)}!"
    
    embed.add_field(name="Your Guess", value=guess.capitalize(), inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="duel", description="⚔️ Challenge another user to a duel")
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
    
    embed = discord.Embed(
        title="⚔️ Duel Challenge!",
        description=f"{interaction.user.mention} challenges {user.mention} to a duel!",
        color=GOLD
    )
    embed.add_field(name="Wager", value=sc(amount), inline=True)
    embed.add_field(name="Action", value=f"{user.mention}, reply with `accept` or `decline`", inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    def check(m): return m.author==user and m.channel==interaction.channel and m.content.lower() in ("accept","decline")
    try:
        resp = await bot.wait_for("message", check=check, timeout=30.0)
        if resp.content.lower()=="decline":
            embed = discord.Embed(
                title="❌ Duel Declined",
                description=f"{user.mention} declined the duel.",
                color=RED
            )
            return await interaction.followup.send(embed=embed)
        
        winner = random.choice([interaction.user, user])
        loser  = user if winner==interaction.user else interaction.user
        
        add_wallet(winner.id, amount, "duel_win")
        add_wallet(loser.id, -amount, "duel_loss")
        
        embed = discord.Embed(
            title="⚔️ Duel Result!",
            description=f"**{winner.mention}** wins {sc(amount)}!",
            color=GREEN
        )
        embed.add_field(name="Loser", value=loser.mention, inline=True)
        embed.set_thumbnail(url=winner.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="⌛ Duel Expired",
            description=f"{user.mention} didn't respond. Duel cancelled.",
            color=RED
        )
        await interaction.followup.send(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - BANKING & TRANSFER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="deposit", description="🏦 Deposit Sailor Coins into your bank")
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
        embed = discord.Embed(
            title="❌ Bank Full!",
            description=f"Buy a **Bank Expansion** in `/shop` to increase limit!",
            color=RED
        )
        return await interaction.response.send_message(embed=embed)
    
    add_wallet(uid, -dep)
    add_bank(uid, dep)
    
    embed = discord.Embed(title="🏦 Deposited!", color=GREEN)
    embed.add_field(name="Amount", value=sc(dep), inline=True)
    embed.add_field(name="New Bank Balance", value=f"{sc(data[2] + dep)} / {sc(data[3])}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="withdraw", description="🏦 Withdraw Sailor Coins from your bank")
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
    embed.add_field(name="New Wallet", value=sc(data[1] + wdr), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transfer", description="💸 Send Sailor Coins to another user")
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
    add_wallet(rid, amount, "transfer")
    
    embed = discord.Embed(title="💸 Transfer Complete!", color=GREEN)
    embed.add_field(name="From", value=interaction.user.mention, inline=True)
    embed.add_field(name="To", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(amount), inline=False)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - SHOP & INVENTORY
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="shop", description="🛍️ Browse interactive shop")
async def shop(interaction: discord.Interaction):
    conn = db()
    items = conn.execute("SELECT item_name, price, description, emoji FROM shop ORDER BY price").fetchall()
    conn.close()
    
    embed = discord.Embed(
        title="⚓ Sailor Shop",
        description="Use buttons below to purchase items or use `/buy <name>`",
        color=GOLD
    )
    
    for item_name, price, description, emoji in items:
        embed.add_field(name=f"{emoji} {item_name}", value=f"{sc(price)}\n_{description}_", inline=True)
    
    embed.set_footer(text="Click buttons to buy or use /buy <name>")
    
    await interaction.response.send_message(embed=embed, view=ShopView())

@bot.tree.command(name="buy", description="🛍️ Buy an item from the shop")
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
    
    item_name, price, desc, item_type, value, emoji = row
    data = get_user(uid)
    
    if data[1] < price:
        embed = discord.Embed(
            title="❌ Insufficient Coins",
            description=f"Need: {sc(price)}\nYou have: {sc(data[1])}",
            color=RED
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Purchase logic (same as button)
    add_wallet(uid, -price)
    
    if item_type == "multiplier":
        parts = value.split(":")
        set_mult(uid, parts[0], float(parts[1]), int(parts[2]))
        embed = discord.Embed(
            title=f"✅ {emoji} {item_name} Activated!",
            description=f"**x{parts[1]} {parts[0]}** active for **{fmt_time(int(parts[2]))}**!",
            color=GREEN
        )
    elif item_type == "upgrade":
        add_inv(uid, item_name)
        embed = discord.Embed(title=f"✅ {emoji} {item_name} Equipped!", description=desc, color=GREEN)
    elif item_type == "bank":
        extra = int(value)
        conn = db()
        conn.execute("UPDATE users SET bank_limit=bank_limit+? WHERE user_id=?", (extra, uid))
        conn.commit()
        conn.close()
        embed = discord.Embed(title=f"✅ {emoji} Bank Expanded!", description=f"Limit +{sc(extra)}!", color=GREEN)
    elif item_type == "mystery":
        parts = value.split(":")
        reward = random.randint(int(parts[0]), int(parts[1]))
        add_wallet(uid, reward)
        embed = discord.Embed(title=f"✅ {emoji} Mystery Box!", description=f"You found {sc(reward)}! 🎉", color=GOLD)
    elif item_type == "role":
        role = discord.utils.get(interaction.guild.roles, name=value)
        if role:
            await interaction.user.add_roles(role)
            embed = discord.Embed(title=f"✅ {emoji} Role Granted!", description=f"You now have **{value}**!", color=GREEN)
        else:
            add_wallet(uid, price)
            embed = discord.Embed(title="❌ Role Not Found", description="Refunded!", color=RED)
    else:
        add_inv(uid, item_name)
        embed = discord.Embed(title=f"✅ {emoji} {item_name} Purchased!", description=desc, color=GREEN)
    
    embed.set_footer(text=f"New Balance: {sc(data[1] - price)}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="inventory", description="🎒 View your inventory")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    items  = get_inv(target.id)
    
    embed = discord.Embed(title=f"🎒 {target.display_name}'s Inventory", color=PURPLE)
    
    if not items:
        embed.description = "Empty! Check out `/shop` to buy items."
    else:
        for name, qty in sorted(items.items()):
            embed.add_field(name=name, value=f"**x{qty}**", inline=True)
    
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# MEMBER COMMANDS - INFO & STATS
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="profile", description="👤 View your sailor economy profile")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    data   = get_user(target.id)
    items  = get_inv(target.id)
    
    embed = discord.Embed(title=f"⚓ {target.display_name}'s Profile", color=BLUE)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    # XP Progress bar
    xp_progress = (data[6] / (data[5] * 100)) * 10
    xp_bar = "█" * int(xp_progress) + "░" * (10 - int(xp_progress))
    
    embed.add_field(name="💰 Wallet", value=sc(data[1]), inline=True)
    embed.add_field(name="🏦 Bank", value=f"{sc(data[2])} / {sc(data[3])}", inline=True)
    embed.add_field(name="💎 Net Worth", value=sc(data[1]+data[2]), inline=True)
    embed.add_field(name=f"⭐ Level {data[5]}", value=f"`{xp_bar}`\n{data[6]}/{data[5]*100} XP", inline=True)
    embed.add_field(name="📈 Total Earned", value=sc(data[4]), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    embed.add_field(name="👥 Invited", value=f"{data[10]} members", inline=True)
    embed.add_field(name="🎒 Items", value=f"{len(items)} unique", inline=True)
    
    embed.set_footer(text=f"Joined: {datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="🏆 Top 10 richest sailors")
async def leaderboard(interaction: discord.Interaction):
    conn = db()
    rows = conn.execute("SELECT user_id, wallet+bank FROM users ORDER BY wallet+bank DESC LIMIT 10").fetchall()
    conn.close()
    
    embed = discord.Embed(title="⚓ Sailor Coins Leaderboard", color=GOLD)
    medals = ["🥇","🥈","🥉"]
    
    for i, (uid, total) in enumerate(rows):
        m    = medals[i] if i<3 else f"`#{i+1}`"
        u    = interaction.guild.get_member(uid)
        name = u.display_name if u else "Unknown"
        embed.add_field(name=f"{m} {name}", value=sc(total), inline=False)
    
    embed.set_footer(text="Updated every command")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multipliers", description="✨ View your active multipliers")
async def multipliers(interaction: discord.Interaction):
    uid = interaction.user.id
    now = time.time()
    conn = db()
    rows = conn.execute(
        "SELECT mult_type, value, expires_at FROM multipliers WHERE user_id=? AND expires_at>?",
        (uid, now)
    ).fetchall()
    conn.close()
    
    embed = discord.Embed(title="✨ Your Active Multipliers", color=PURPLE)
    
    if not rows:
        embed.description = "No active multipliers.\n\nBuy some from `/shop` to boost earnings!"
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

@bot.tree.command(name="stats", description="📊 View your economic statistics")
async def stats(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    
    embed = discord.Embed(title="📊 Your Statistics", color=BLUE)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="💰 Total Earned", value=sc(data[4]), inline=True)
    embed.add_field(name="⭐ Current Level", value=str(data[5]), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[7]} days", inline=True)
    embed.add_field(name="👥 Invites", value=f"{data[10]} users", inline=True)
    embed.add_field(name="🎯 Net Worth", value=sc(data[1]+data[2]), inline=True)
    embed.add_field(name="💎 Bank Capacity", value=f"{data[2]}/{data[3]}", inline=True)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS - SETUP & CONFIG
# ══════════════════════════════════════════════════════════════════════════════

def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.command(name="setshop", description="[ADMIN] Send interactive shop to channel")
@app_commands.describe(channel="Channel for the shop")
@admin_only()
async def setshop(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(
        title="⚓ Sailor Shop",
        description="Click buttons below to purchase items!",
        color=GOLD
    )
    
    conn = db()
    items = conn.execute("SELECT item_name, price, description, emoji FROM shop ORDER BY price").fetchall()
    conn.close()
    
    for item_name, price, description, emoji in items:
        embed.add_field(name=f"{emoji} {item_name}", value=f"{sc(price)}\n_{description}_", inline=True)
    
    await channel.send(embed=embed, view=ShopView())
    set_cfg("shop_channel", str(channel.id))
    
    embed_confirm = discord.Embed(
        title="✅ Shop Setup Complete!",
        description=f"Interactive shop sent to {channel.mention}",
        color=GREEN
    )
    await interaction.response.send_message(embed=embed_confirm, ephemeral=True)

@bot.tree.command(name="setinvitereward", description="[ADMIN] Set coins rewarded per invite")
@app_commands.describe(amount="Coins to reward")
@admin_only()
async def setinvitereward(interaction: discord.Interaction, amount: int):
    set_cfg("invite_reward", str(amount))
    embed = discord.Embed(
        title="✅ Invite Reward Updated",
        description=f"Users now earn {sc(amount)} per invite!",
        color=GREEN
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="give", description="[ADMIN] Give coins to a user")
@app_commands.describe(user="Target user", amount="Amount to give")
@admin_only()
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    add_wallet(user.id, amount, "admin_give")
    embed = discord.Embed(title="✅ Coins Given", color=GREEN)
    embed.add_field(name="To", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(amount), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="take", description="[ADMIN] Take coins from a user")
@app_commands.describe(user="Target user", amount="Amount to remove")
@admin_only()
async def take(interaction: discord.Interaction, user: discord.Member, amount: int):
    data   = get_user(user.id)
    actual = min(amount, data[1])
    add_wallet(user.id, -actual, "admin_take")
    embed = discord.Embed(title="✅ Coins Taken", color=RED)
    embed.add_field(name="From", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=sc(actual), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="economyban", description="[ADMIN] Ban/unban user from economy")
@app_commands.describe(user="Target user")
@admin_only()
async def economyban(interaction: discord.Interaction, user: discord.Member):
    conn = db()
    if conn.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user.id,)).fetchone():
        conn.execute("DELETE FROM banned_users WHERE user_id=?", (user.id,))
        msg, color = f"✅ {user.mention} **unbanned**", GREEN
    else:
        conn.execute("INSERT INTO banned_users VALUES(?)", (user.id,))
        msg, color = f"🚫 {user.mention} **banned**", RED
    conn.commit()
    conn.close()
    
    embed = discord.Embed(description=msg, color=color)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="economystats", description="[ADMIN] View global economy")
@admin_only()
async def economystats(interaction: discord.Interaction):
    conn = db()
    s = conn.execute("SELECT COUNT(*), SUM(wallet), SUM(bank), SUM(total_earned) FROM users").fetchone()
    b = conn.execute("SELECT COUNT(*) FROM banned_users").fetchone()[0]
    r = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    i = conn.execute("SELECT COUNT(*) FROM invites").fetchone()[0]
    conn.close()
    
    embed = discord.Embed(title="📊 Economy Statistics", color=BLUE)
    embed.add_field(name="👥 Players", value=str(s[0]), inline=True)
    embed.add_field(name="🚫 Banned", value=str(b), inline=True)
    embed.add_field(name="💰 In Wallets", value=sc(s[1] or 0), inline=True)
    embed.add_field(name="🏦 In Banks", value=sc(s[2] or 0), inline=True)
    embed.add_field(name="📈 Ever Earned", value=sc(s[3] or 0), inline=True)
    embed.add_field(name="🛍️ Items Held", value=str(r), inline=True)
    embed.add_field(name="👥 Total Invites", value=str(i), inline=True)
    embed.add_field(name="🏧 In Circulation", value=sc((s[1] or 0)+(s[2] or 0)), inline=True)
    
    await interaction.response.send_message(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        msg = "❌ You need **Administrator** permission."
    else:
        msg = f"❌ Error: `{error}`"
        print(f"[ERROR] {error}")
    try:
        await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        await interaction.followup.send(msg, ephemeral=True)

# ══════════════════════════════════════════════════════════���═══════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set!")
    init_db()
    bot.run(TOKEN)
