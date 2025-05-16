import logging
logging.basicConfig(level=logging.INFO)



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

print(f"Test Init")
tcdb = TeleChanDB(bot_token, channel_id)


print(f"Test List")
tags = tcdb.list()
print(f"Tag list: {tags}")


print(f"Test Create")
tcdb.write('The first test record.', tags={'test':None, 'someTag':1})
tcdb.write('Second record.', tags={'test':None, 'someTag':2})
tcdb.write('One more record.', tags={'someTag':3, 'otherTag':None})
testId = tcdb.write('By id.', tags={'someTag':2})
tagsV = tcdb.list(['someTag', ''], ids=True)
print(f"Tags listed: {tagsV}")

readData = tcdb.read(tags={'someTag':1}, ids=testId)
for cId,cRecord in readData.items():
	print(f"{cId}: {json.dumps(cRecord, indent=4)}")
