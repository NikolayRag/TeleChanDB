# =todo 2 (general, initial) +2: make basic Init/Create/Read/Update/Delete/List routines
# =todo 16 (checkpoint, memo) +2: Handle TG limits!
# -todo 24 (checkpoint, tglimits, bot) +3: Make commit function and flow, as TG limits modification


## **Concurrency Management**
### Multiple clients may perform operations simultaneously, leading to potential race conditions.
#  todo 3 (feature, memo) +0: Implement locking mechanisms or use versioning to manage concurrent access and ensure data consistency.

### **Error Handling**
### Network issues, API rate limits, or unexpected bot behavior can cause failures.
#  todo 4 (feature, memo) +0: Incorporate robust error handling, retry logic, and logging to manage exceptions and maintain system stability.


from .TGIO import *
import json
import time

import logging as log


# -todo 28 (tgio, limits) +0: implement lazy load and commit
'''
Schema contains reference list of all used Tags messages.
'''
class TCSchema:
	def __init__(self):
		self.schemaMessageId = None
		self.isSaved = True

		self.tagList = {} # {"<Tag>":TCTag, ..}



	'''
	Update Tag-to-Record mapping.
	Create Tag if none yet.
	'''
	def tag(self, tagN, id=0, born=True):
		if not tagN in self.tagList:
			if not born:
				return

			cTag = TCTag(tagN, id, isSaved=False)
			self.tagList[tagN] = cTag

			if not id: # loaded are saved obviously
				log.info(f"New Tag <{tagN}>")
				self.isSaved = False


		return self.tagList[tagN]



	def collectSchema(self):
		outT = {}
		for tagN, tagV in self.tagList.items():
			outT[tagN] = tagV.getMId()

		
		return {"Type":"Schema", "Tags": outT}



	def collectTags(self):
		return [t for n,t in self.tagList.items()]



'''
TCTag is a list of appliance to Records.
'''
class TCTag:
	def __init__(self, name, tagMsgId, isSaved):
		self.name = name
		self.tagMsgId = tagMsgId
		self.recordsMap = {} #{None|<value>:[<RecordMsgId>, ..], ..}

		self.isSaved = isSaved



	def getMId(self):
		return self.tagMsgId



	def getMap(self):
		return self.recordsMap



	'''
	Load entire Tag with mapping
	'''
	# -todo 21 (schema) +0: Load Tag Mapping
	def set(self, _id=0):
		if _id:
			self.tagMsgId = _id
		self.isSaved = True



	def map(self, _value, _recId, _remove=False):
		_value = str(_value) if _value!=None else ''

		## init empty list for value
		if _value not in self.recordsMap:
			self.recordsMap[_value] = []
		cMapList = self.recordsMap[_value]


		if _remove:
			if _recId in cMapList:
				cMapList.remove(_recId)

				self.isSaved = False

		else:
			if _recId not in cMapList:
				cMapList += [_recId]
				
				self.isSaved = False





class TeleChanDB:

	
	##
	## SERVICE FNs
	##



	'''
	JSON to/from tg messages
	'''
	def __jsonToTG(self, _str, indent=None):
		return json.dumps(_str, indent=indent)



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
	  > "SchemaId": <SchemaMsgId>
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



	'''
	Return Tags dict from Schema message
	'''
	def __validateSchemaMsg(self, _jsSchema):
		if not _jsSchema:
			return
		if _jsSchema.get('Type') != 'Schema':
			return
		
		tagsList = _jsSchema.get('Tags')
		if type(tagsList) != dict:
			return


		return tagsList



	'''
	Load Schema and Tags Messages
	'''
	def _loadSchema(self):
		schemaMsg = self.bot.read(self.channelId, self.theSchema.schemaMessageId)
		if not schemaMsg:
			log.error("Schema load error")
			return

		cSchema = self.__jsonFromTG(schemaMsg)
		cTags = self.__validateSchemaMsg(cSchema)
		if not cTags:
			log.error("Schema format error")
			return


		for cTagN, cTagId in cTags.items():
			tagMsg = self.bot.read(self.channelId, cTagId)
			tagData = self.__jsonFromTG(tagMsg)

			cTag = self.theSchema.tag(cTagN, id=cTagId)
			for tagV, tagMap in tagData['Records'].items():
				log.debug(f"Tag '{cTagN}' bound: {tagV} to {tagMap}")
				for recId in tagMap:
					cTag.map(tagV, recId)

			cTag.set()


		log.info(f"Schema loaded from msgId {self.theSchema.schemaMessageId} with {len(self.theSchema.tagList)} Tags")
		return True



	'''
	Save Tags and Schema
	'''
	def _saveSchema(self, init=False):

		for cTag in self.theSchema.collectTags():
			if cTag.isSaved:
				continue


			outTag = {
				"Type": "Tag",
				"Tag": cTag.name,
				"Records": cTag.getMap()
			}
			outTag = self.__jsonToTG(outTag)

			if not cTag.getMId(): ## create tag message
				tagId = self.bot.send(self.channelId, outTag)
				if not tagId:
					log.error(f"Tag not created")
					return

				cTag.set(tagId)

			else: ## update existing
				if not self.bot.update(self.channelId, cTag.getMId(), outTag):
					log.error(f"Tag {cTag.getMId()} '{cTag.name}' not updated for {cTag.getMId()} id")
					return

			cTag.isSaved = True

			log.info(f"Tag '{cTag.name}' stored with len {len(cTag.getMap())}")



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

		self.theSchema.schemaMessageId = self._loadEntry()

		if self.theSchema.schemaMessageId and self._loadSchema():
			return True


		if not self._saveSchema(init=True):
			return

		if not self._saveEntry(self.theSchema.schemaMessageId):
			return


		log.info(f"Channel was inited, Schema created at {self.theSchema.schemaMessageId}")
		return True



	'''
	List values for specified /tags/
	If no /tags/ specified, list all tags and they values.

	If /ids/ set, list dicts of {/value/:[id,..],..}
	'''
	def list(self, tags=False, ids=False):
		if not self.channelId:
			log.error(f"Channel is not inited")
			return

		tagsA = self.theSchema.collectTags()

		if tags == False:
			tags = [t.name for t in tagsA]


		if ids:
			tList = {t.name:{vK:vV for vK,vV in t.getMap().items()} for t in tagsA}
		else:
			tList = {t.name:[v for v in t.getMap().keys()] for t in tagsA}

		return {tN:tV for tN,tV in tList.items() if tN in tags}



	def write(self, content, tags={}):
		if not self.channelId:
			log.error(f"Channel is not inited")
			return


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


		tags[''] = 'id' # Non-orphan tag

		for tagN, tagV in tags.items():
			self.theSchema.tag(tagN).map(tagV, recordId)

		if not self._saveSchema():
			log.error(f"Schema update error for record {recordId}")
			return

		return recordId
		


