### **Concurrency Management**
### Multiple clients may perform operations simultaneously, leading to potential race conditions.
#  todo 3 (general, memo) +0: Implement locking mechanisms or use versioning to manage concurrent access and ensure data consistency.

### **Error Handling**
### Network issues, API rate limits, or unexpected bot behavior can cause failures.
#  todo 4 (general, memo) +0: Incorporate robust error handling, retry logic, and logging to manage exceptions and maintain system stability.

#  todo 16 (general, memo) +2: Handle TG limits!


#  todo 2 (general, initial) +2: make basic Init/Create/Read/Update/Delete/List routines
import telebot

from .TGIO import *
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
		self.isSaved = True

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

			self.isSaved = False


		cTag = self.tagList[tagN]
		cTag.setMap(tagV, recId, remove)


	def collectSchema(self):
		outT = {}
		for tagN, tagV in self.tagList.items():
			outT[tagN] = tagV.getTagMsgId()
		
		return {"Type":"Schema", "Tags": outT}



	def collectTags(self):
		return [t for n,t in self.tagList.items()]



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

				self.isSaved = False

		else:
			if _recId not in cMapValue:
				cMapValue += [_recId]
				
				self.isSaved = False





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




	##
	## PRIVATE FNs
	##



	'''
	Get Schema message id from the Channel Description

	Expected description format:
	  > "SchemaMsgId": <SchemaMsgId>
	'''
	def _loadEntry(self, _fieldName="SchemaID"):
		tgChat = self.bot.loadDscr(self.channelId)
		if tgChat==None:
			return

		descriptJson = self.__jsonFromTG(tgChat)
		if descriptJson and (_fieldName in descriptJson):
			try:
				return int(descriptJson[_fieldName])
			except:
				log.debug(f"Bot error with Description format: {descriptJson[_fieldName]}")
				return



	'''
	Update channel description to store Schema message ID
	'''
	def _saveEntry(self, _newId, _fieldName="SchemaID"):
		dscrNew = self.__jsonToTG(
			{_fieldName: _newId}
		)

		return self.bot.saveDscr(self.channelId, dscrNew)



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
		schema_msg = self.bot.read(self.channelId, self.theSchema.schemaMessageId)
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

		for cTag in self.theSchema.collectTags():
			if cTag.isSaved:
				continue


			outTag = {
				"Type": "Tag",
				"Tag": cTag.name,
				"Records": cTag.recordsMap
			}
			outTag = self.__jsonToTG(outTag)

			if not cTag.tagMsgId: ## create tag message
				tagId = self.bot.send(self.channelId, outTag)
				if not tagId:
					log.error(f"Tag not created")
					return

				cTag.tagMsgId = tagId

			else: ## update existing
				if not self.bot.update(self.channelId, cTag.tagMsgId, outTag):
					log.error(f"Tag not updated for {cTag.tagMsgId} id")
					return

			cTag.isSaved = True

			log.info(f"Tag '{cTag.name}' stored")



		schemaStr = self.theSchema.collectSchema()
		schemaStr = self.__jsonToTG(schemaStr)

		if not init:
			if not self.theSchema.isSaved:
				if not self.bot.update(self.channelId, self.theSchema.schemaMessageId, schemaStr):
					log.error(f"Schema message not saved")
					return

				self.theSchema.isSaved = True

			else:
				log.info(f"No Schema changes")

			return True


		msgId = self.bot.send(self.channelId, schemaStr)
		if msgId:
			self.theSchema.schemaMessageId = msgId

			return True




	##
	## PUBLIC
	##



	def __init__(self, botToken, channelId):
		self.bot = TGIO(botToken)
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



		if self.theSchema.schemaMessageId and self._loadSchema(): #Ok
			# =todo 15 (general, schema) +0: Parse Tags
#			for cTag in self.theSchema.tagList:
#				clclc
		self.theSchema.schemaMessageId = self._loadEntry()

			return True


		if not self._saveSchema(init=True):
			return

		if not self._saveEntry(self.theSchema.schemaMessageId):
			return


		log.info(f"Channel was inited, Schema created at {self.theSchema.schemaMessageId}")
		return True



	'''
	Write new Record
	'''
	def write(self, content, tags={}):
		if not self.channelId:
			log.error(f"Channel is not inited")
			return


		tags[''] = None # Non-orphan tag

		cRecord = self.__jsonToTG({
			'Type': 'Record',
			'Tags': tags,
			'Data': content
		})

		recordId = self.bot.send(self.channelId, cRecord)
		if not recordId:
			log.error(f"Message write error: <{content[:25]}...>")
			return
		else:
			log.info(f"Record saved for {recordId} id: : <{content[:15]}..>")


		for tagN, tagV in tags.items():
			self.theSchema.tagMaintain(tagN, tagV, recordId)

		if not self._saveSchema():
			log.error(f"Schema update error for record {recordId}")
			return

		return True
		


