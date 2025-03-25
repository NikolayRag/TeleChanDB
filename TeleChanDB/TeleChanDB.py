### **Concurrency Management**
### Multiple clients may perform operations simultaneously, leading to potential race conditions.
#  todo 3 (general, memo) +0: Implement locking mechanisms or use versioning to manage concurrent access and ensure data consistency.

### **Error Handling**
### Network issues, API rate limits, or unexpected bot behavior can cause failures.
#  todo 4 (general, memo) +0: Incorporate robust error handling, retry logic, and logging to manage exceptions and maintain system stability.

#  todo 16 (general, memo) +2: Handle TG limits!


#  todo 2 (general, initial) +2: make basic Init/Create/Read/Update/Delete/List routines
import telebot
import json
import time

import logging as log


'''
Schema contains reference list of all used Tags.
Each Tag refers to it's own list of appliance.
'''
class TCSchema:
	def __init__(self):
		self.schemaMessageId = None

		self.tagList = {} # {"<Tag>":TCTag, ..}



	def tagLoad(self, tagN, tagMsgId):
		cTag = TCTag(tagN, tagMsgId, isSaved=True)
		self.tagList[tagN] = cTag
	


	'''
	Specify Tag to Record mapping.
	Create Tag if none yet.
	'''
	def tagMaintain(self, tagN, tagV, recId, remove=False):
		if not tagN in self.tagList:
			cTag = TCTag(tagN, 0, isSaved=False)
			self.tagList[tagN] = cTag

		cTag = self.tagList[tagN]
		cTag.setMap(tagV, recId, remove)


	def collectTags(self):
		outT = {}
		for tagN, tagV in self.tagList.items():
			outT[tagN] = tagV.getTagMsgId()
		
		return {"Type":"Schema", "Tags": outT}




class TCTag:
	def __init__(self, name, tagMsgId, isSaved):
		self.name = name
		self.tagMsgId = tagMsgId
		self.recordsMap = {} #{None|<value>:[<RecordMsgId>, ..], ..}

		self.isSaved = isSaved



	def getTagMsgId(self):
		return self.tagMsgId



	def setMap(self, _value, _recId, _remove):
		if _value not in self.recordsMap:
			self.recordsMap[_value] = []
		cMapValue = self.recordsMap[_value]


		if _remove:
			if _recId in cMapValue:
				cMapValue.remove(_recId)

		else:
			if _recId not in cMapValue:
				cMapValue += [_recId]





class TeleChanDB:

	
	##
	## SERVICE FNs
	##



	'''
	JSON to/from tg messages
	'''
	def __jsonToTG(self, _str):
		return json.dumps(_str)


	def __jsonFromTG(self, _str):
		try:
			return json.loads(_str)
		except:
			None



	def __botSend(self, _content):
		try:
			msgOut = self.bot.send_message(self.channelId, _content)
			return msgOut

		except Exception as e:
			log.info(f"Bot error at Message create,\n {e}\n")



	def __botUpdate(self, _msgId, _content):
		try:
			self.bot.edit_message_text(chat_id=self.channelId, message_id=_msgId, text=_content)
			return True

		except Exception as e:
			log.info(f"Bot error at Message Update,\n {e}\n")



#  todo 18 (optimize, tglimits, try) +0: Clean temporary messages at end mb
	def __botRead(self, _chanId, _msgId):
# -todo 17 (optimize, tglimits) +0: Allow batch read
		try:
			cMsg = self.bot.forward_message(
				chat_id=_chanId,
				from_chat_id=_chanId,
				message_id=_msgId
			)
			self.bot.delete_message(chat_id=_chanId, message_id=cMsg.message_id)

			return cMsg

		except Exception as e:
			log.info(f"Bot error at Message Read,\n {e}\n")



	##
	## PRIVATE FNs
	##



	'''
	Get Schema message id from the Channel Description

	Expected description format:
	  > "SchemaMsgId": <SchemaMsgId>
	'''
	def _loadDscr(self, _fieldName="SchemaID"):
		try:
			tgChat = self.bot.get_chat(self.channelId)
		except Exception as e:
			log.info(f"Bot error at Description Read,\n {e}\n")
			return

		descriptJson = self.__jsonFromTG(tgChat.description)
		if descriptJson and (_fieldName in descriptJson):
			try:
				return int(descriptJson[_fieldName])
			except:
				log.info(f"Bot error with Description format: {descriptJson[_fieldName]}")
				return



	'''
	Update channel description to store Schema message ID
	'''
	def _saveDscr(self, _newId, _fieldName="SchemaID"):
		dscrNew = self.__jsonToTG(
			{_fieldName: _newId}
		)

		try:
			self.bot.set_chat_description(self.channelId, dscrNew)
			return True

		except Exception as e:
			log.info(f"Bot error at Description Write,\n {e}\n")



	def __parseSchemaMsg(self, _jsSchema):
		if not _jsSchema:
			return
		if _jsSchema.get('Type') != 'Schema':
			return
		
		tagsList = _jsSchema.get('Tags')
		if type(tagsList) != dict:
			return


		# =todo 19 (check) +0: Load tags list
		for cTagN, cTagMsgId in tagsList.items():
			self.theSchema.tagLoad(cTagN, cTagMsgId)


		return True



	'''
	Load Schema and Tags Messages
	'''
	def _loadSchema(self):
		schema_msg = self.__botRead(self.channelId, self.theSchema.schemaMessageId)
		if not schema_msg:
			log.error("Schema load error")
			return



		cSchema = self.__jsonFromTG(schema_msg.text)
		if not self.__parseSchemaMsg(cSchema):
			log.error("Schema format error")
			return

		log.info(f"Schema loaded from msgId {self.theSchema.schemaMessageId} with {len(self.theSchema.tagList)} Tags")
		return True



	'''
	Save Schema message
	'''
	def _saveSchema(self, init=False):
		schemaStr = self.theSchema.collectTags()
		schemaStr = self.__jsonToTG(schemaStr)


		if not init:
			# =todo 13 (general) +0: Dump Tags
			updOk = self.__botUpdate(self.theSchema.schemaMessageId, schemaStr)
			return updOk


		msg = self.__botSend(schemaStr)
		if msg:
			self.theSchema.schemaMessageId = msg.message_id

			return True




	##
	## PUBLIC
	##



	def __init__(self, botToken, channelId):
		self.bot = telebot.TeleBot(botToken)
		self.channelId = channelId

		self.theSchema = TCSchema()

		self.records = {}


		if not self._initChannel():
			self.channelId = None

			log.error(f"Channel error")


	'''
	Check if TG Channel is DataBase by reading it Description and Schema message.
	
	Create blank Schema and fix Description if needed.
	'''
	def _initChannel(self):

		self.theSchema.schemaMessageId  = self._loadDscr()


		if self.theSchema.schemaMessageId and self._loadSchema(): #Ok
			# =todo 15 (general, schema) +0: Parse Tags
#			for cTag in self.theSchema.tagList:
#				clclc

			return True


		if not self._saveSchema(init=True):
			return

		if not self._saveDscr(self.theSchema.schemaMessageId):
			return


		log.info(f"Channel was inited, Schema created at {self.theSchema.schemaMessageId}")
		return True
