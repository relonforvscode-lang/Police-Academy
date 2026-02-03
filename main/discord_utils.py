import os
import logging
import requests
from dotenv import load_dotenv

# load .env from project root when present (no secrets committed to repo)
load_dotenv()

logger = logging.getLogger(__name__)

DISCORD_API_BASE = 'https://discord.com/api/v10'
_raw_token = os.getenv('DISCORD_BOT_TOKEN')
# sanitize token: remove any leading 'Bot ' if present and trim
BOT_TOKEN = None
if _raw_token:
    t = _raw_token.strip()
    if t.lower().startswith('bot '):
        t = t.split(' ', 1)[1]
    BOT_TOKEN = t
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
LOG_CHANNEL_ID = os.getenv('DISCORD_LOG_CHANNEL_ID')

HEADERS = {}
if BOT_TOKEN:
    HEADERS = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }


def send_dm(discord_user_id: str, message: str) -> bool:
    """Send a DM to a user ID using the bot. Returns True on success."""
    if not BOT_TOKEN:
        logger.error('send_dm: no BOT_TOKEN configured')
        return False
    try:
        # create DM channel
        # normalize discord_user_id (accept <@123...>, 123..., or numeric string)
        import re
        m = re.findall(r"(\d+)", str(discord_user_id))
        recipient = m[0] if m else str(discord_user_id)
        payload = {'recipient_id': str(recipient)}
        r = requests.post(f'{DISCORD_API_BASE}/users/@me/channels', json=payload, headers=HEADERS, timeout=10)
        if r.status_code not in (200, 201):
            logger.error('send_dm: failed to create DM channel: %s %s', r.status_code, r.text)
            return False
        channel = r.json().get('id')
        if not channel:
            logger.error('send_dm: no channel id in create response: %s', r.text)
            return False
        # send message
        msg_payload = {'content': message}
        r2 = requests.post(f'{DISCORD_API_BASE}/channels/{channel}/messages', json=msg_payload, headers=HEADERS, timeout=10)
        if r2.status_code in (200, 201):
            return True
        logger.error('send_dm: failed to send message: %s %s', r2.status_code, r2.text)
        return False
    except Exception:
        logger.exception('send_dm: exception while sending DM')
        return False


def add_role(discord_user_id: str, role_id: str) -> bool:
    """Add a role to a guild member. Requires the bot to be in the guild and have MANAGE_ROLES."""
    if not BOT_TOKEN or not GUILD_ID:
        logger.error('add_role: missing BOT_TOKEN or GUILD_ID')
        return False
    try:
        # normalize id
        import re
        m = re.findall(r"(\d+)", str(discord_user_id))
        member_id = m[0] if m else str(discord_user_id)
        url = f'{DISCORD_API_BASE}/guilds/{GUILD_ID}/members/{member_id}/roles/{role_id}'
        r = requests.put(url, headers=HEADERS, timeout=10)
        if r.status_code in (204,):
            return True
        logger.error('add_role: unexpected response %s %s', r.status_code, r.text)
        return False
    except Exception:
        logger.exception('add_role: exception while adding role')
        return False


def send_channel_message(channel_id: str, message: str) -> bool:
    """Send a message to a guild channel using the bot. Returns True on success."""
    if not BOT_TOKEN:
        logger.error('send_channel_message: no BOT_TOKEN configured')
        return False
    try:
        payload = {'content': message}
        r = requests.post(f'{DISCORD_API_BASE}/channels/{channel_id}/messages', json=payload, headers=HEADERS, timeout=10)
        if r.status_code in (200, 201):
            return True
        logger.error('send_channel_message: failed to post: %s %s', r.status_code, r.text)
        return False
    except Exception:
        logger.exception('send_channel_message: exception while posting to channel')
        return False


def get_guild_member_username(discord_user_id: str) -> str | None:
    """Return the username of a guild member (if available)."""
    if not BOT_TOKEN or not GUILD_ID:
        logger.debug('get_guild_member_username: missing BOT_TOKEN or GUILD_ID')
        return None
    try:
        import re
        m = re.findall(r"(\d+)", str(discord_user_id))
        member_id = m[0] if m else str(discord_user_id)
        url = f'{DISCORD_API_BASE}/guilds/{GUILD_ID}/members/{member_id}'
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            logger.error('get_guild_member_username: bad response %s %s', r.status_code, r.text)
            return None
        data = r.json()
        # Prefer the account username (username#discriminator) over guild nickname
        user = data.get('user') or {}
        username = user.get('username')
        discriminator = user.get('discriminator')
        if username:
            return f"{username}#{discriminator}" if discriminator else username
        # fallback to guild nickname only if account username is unavailable
        nick = data.get('nick')
        if nick:
            return nick
        return None
    except Exception:
        logger.exception('get_guild_member_username: exception')
        return None
