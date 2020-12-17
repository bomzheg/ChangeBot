import json
from app.config import LISTEN_PORT, LISTEN_IP
from app.misc import dp


@dp.message_handler(commands=["status"], is_superuser=True)
async def get_html(message):
    url = f'http://{LISTEN_IP}:{LISTEN_PORT}/healthcheck'
    session = dp.bot.session
    async with session.get(url) as r:
        if not r.status == 200:
            return await message.reply(
                f"Ответ от {url}:\n{r.status}"
            )
        x = await r.json()
        return await message.reply(json.dumps(x, indent=4))
