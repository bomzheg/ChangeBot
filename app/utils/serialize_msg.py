def get_text(message):
    return message.text or message.caption or "нетекстовое сообщение"


def serialize_message(message):
    rez = f"message ID {message.message_id}. "
    if message.chat.type == "channel":
        rez += f"В канале(!), с ID {message.chat.id}, названием {message.chat.title}, "
        rez += f"юзернеймом @{str(message.chat.username)} было отправлено сообщение {get_text(message.text)}"
        return rez

    if message.chat.type == "private":
        rez += "В личке с ботом, "
    elif message.chat.type == "group":
        rez += f"В группе с ID {message.chat.id}, "
    elif message.chat.type == "supergroup":
        rez += f"В супергруппе с ID {message.chat.id}, "

    rez += f"пользователь с "
    if message.from_user.username:
        rez += f"юзернеймом @{message.from_user.username}"
    else:
        rez += f"ID {message.from_user.id}"

    rez += f" написал: {get_text(message)}"
    return rez
