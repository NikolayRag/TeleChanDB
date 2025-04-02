import telebot

import logging as log


'''
General TG messages read-write interface.

TGIO is TG Bot capable of creating, reading, modifying and deleting specified messages.
It should have rights assigned elsewhere to deal with messages, i.e. be an admin.

In addition channel description can be read and written.
'''
class TGIO:
	def __init__(self, botToken):
		self.bot = telebot.TeleBot(botToken)



	def send(self, _chanId, _content):
		try:
			msgOut = self.bot.send_message(_chanId, _content)
			return msgOut

		except Exception as e:
			log.debug(f"Bot error at Message create,\n {e}<\n")



	def update(self, _chanId, _msgId, _newContent):
		try:
			self.bot.edit_message_text(chat_id=_chanId, message_id=_msgId, text=_newContent)
			return True

		except Exception as e:
			log.debug(f"Bot error at Message Update,\n {e}<\n")



#  todo 25 (optimize, tglimits) +2: Make commit logic
#  todo 18 (optimize, tglimits) +0: Clean temporary messages at end mb
#  todo 17 (optimize, tglimits) +0: Allow batch read
	def read(self, _chanId, _msgId):
		try:
			cMsg = self.bot.forward_message(
				chat_id=_chanId,
				from_chat_id=_chanId,
				message_id=_msgId
			)
			self.bot.delete_message(chat_id=_chanId, message_id=cMsg.message_id)

			return cMsg

		except Exception as e:
			log.debug(f"Bot error at Message Read,\n {e}<\n")




	'''
	Get Schema message id from the Channel Description

	Expected description format:
	  > "SchemaMsgId": <SchemaMsgId>
	'''
	def loadDscr(self, _chanId):
		try:
			tgChat = self.bot.get_chat(_chanId)
			return tgChat.description

		except Exception as e:
			log.debug(f"Bot error at Description Read,\n {e}<\n")



	'''
	Update channel description to store Schema message ID
	'''
	def saveDscr(self, _chanId, _newDscr):
		try:
			self.bot.set_chat_description(_chanId, _newDscr)
			return True

		except Exception as e:
			log.debug(f"Bot error at Description Write,\n {e}<\n")
