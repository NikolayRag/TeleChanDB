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

