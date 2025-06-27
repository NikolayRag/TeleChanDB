import logging
logging.basicConfig(level=logging.INFO)

import json, random


from TeleChanDB import TeleChanDB

'''
Initialize with your bot token and channel ID.

Your bot should be a channel admin with full rights.
'''

bot_token = ''
channel_id = ''

from test_keys import *

'''
Test cases for init:
- No connection
- Wrong channel id
- Not admin
- No description
- Corrupted description
- No Schema message
- Corrupted Schema message
- (repairable) Missing Tags messages
- (repairable) Corrupted Tags messages
- (TG limits) Many Tags messages
'''

print(f"\n----\nTest Init")
tcdb = TeleChanDB(bot_token, channel_id)
if not tcdb.isInited():
	exit()


print(f"\n----\nTest Create")


tcdb.write('The first test record.', tags={'test':None, 'someTag':1})
tcdb.write('Second record.', tags={'test':None, 'someTag':2})
tcdb.write('One more record.', tags={'someTag':3, 'otherTag':None})
testId = tcdb.write('By id.', tags={'someTag':2})
print(f"\n----\nTest List")
tagsV = tcdb.list(['someTag', ''], ids=True)
if tagsV==None:
	exit()

print(f"Tags listed: {tagsV}")


print(f"\n----\nTest Read by Tags and Id")
readData = tcdb.read(tags={'someTag':1}, ids=[testId])
if not readData:
	exit()

for cId,cRecord in readData.items():
	print(f"{cId}: {json.dumps(cRecord, indent=4)}")


tagVal = int(random.random()*100)
print(f"\n----\nTest Change for {tagVal}")
changeOk = tcdb.change(testId, f"Changed to {tagVal}", tags={'someTag':tagVal, 'id':1})
if not changeOk:
	exit()


input("Press Enter to finalize test...")


print(f"\n----\nTest Delete by Tags")
delData = tcdb.delete(tags={'':''})
print(f"Deleted {delData}")


changedData = tcdb.read(ids=[testId])
print(f"\nRecord {testId} changed:\n{changedData[testId]}")

