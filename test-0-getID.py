print('''
  To get channel Id make this bot admin of channel
  and forward any message from that channel to bot itself.
''')

import telebot

# Replace with your bot's token
TOKEN = ""
bot = telebot.TeleBot(TOKEN)

# This function will be triggered when the bot receives a message in the channel
@bot.message_handler(func=lambda m: True)
def get_channel_id(message):

    if message.forward_from_chat:
        bot.send_message(message.chat.id, message.forward_from_chat.id)
        
        print(f"From: {message.forward_from_chat.id}")


bot.polling()
