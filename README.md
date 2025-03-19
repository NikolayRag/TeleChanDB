# TeleChanDB
### General data base and transport over TG channel

---

## **1. Idea**


### **Product Description**

**TeleChanDB** is a lightweight, decentralized database system that leverages the power of Telegram channels and bots by storing entire data, tags, and schema in one dedicated Telegram channel.  

The channel-DB is accessed by a Telegram Bot acting as an admin, with implicit TG bots limitations.  
As **TeleChanDB** is not polling bot, it can be used as multiple clients in concurence.

Due to the nature of TG and TG Bots **TeleChanDB** is focused on personal or small groups use with high accessability and data reliability at first place.

Create, Read, Update, and Delete (CRUD) operations are available for low-level access to the DB.  


### **Chat DB Structure**
The whole DB is a collection of: **Records**, **Tags** and **Schema**, which are stored within ordinary Channel messages.  

- **Record**  
Data itself is an ascii-encoded message, which is labeled by named **Tags** with optional value each.

- **Tag**  
An entity and a corresponding message that maintains mapping of named value to referenced **Records** messages by their channel Id's.

- **Schema**  
A list of **Tags** with corresponding messages Id's.  
**Schema** message should always exist, and blank one is created at channel init.

- **DB Entry**  
Chat Description field as a fixed entry point that holds **Schema** message Id.

### TGDB entities format

```
- DB Entry (Channel Description)
  > "SchemaMsgId": <SchemaMsgId>

- Schema Message
  > "Type": "Schema",
  > "Tags": {"<Tag>": <TagMsgId>, ..}

- Tag Message
  > "Type": "Tag",
  > "Tag": "<Tag>",
  > "Records": {[None|<value>]:[<RecordMsgId>, ..], ..}

- Record Message
  > "Type": "Record",
  > "Tags": {"<Tag>":[None|<value>], ..},
  > "Data": <Data>
```


## **Legal Notes**

TG itself and TG bots are not intended to be general database for automated use,
 but **TeleChanDB** acts nothing but acceptable way and stores data as readable messages, so it's user responsibility to apply **TeleChanDB** in reasonable way.
 