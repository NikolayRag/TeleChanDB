!review, init 1: +0 "" Ki 25/03/17 01:41:54
	redundant

 general, initial 2: +2 "TeleChanDB\TeleChanDB.py" Ki 25/02/04 21:33:45
	make basic Init/Create/Read/Update/Delete/List routines

 general, memo 3: +0 "TeleChanDB\TeleChanDB.py" Ki 25/02/04 21:05:31
	Implement locking mechanisms or use versioning to manage concurrent access and ensure data consistency.

 general, memo 4: +0 "TeleChanDB\TeleChanDB.py" Ki 25/01/19 14:16:27
	Incorporate robust error handling, retry logic, and logging to manage exceptions and maintain system stability.

!general, memo 5: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/11 02:03:16
	Optimize message handling, consider sharding the index if it becomes too large, and monitor performance to make necessary adjustments.

!general, memo 6: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/11 02:02:56
	Implement authentication and authorization mechanisms within the bot to control access to CRUD operations.

!general, memo 7: +0 "" Ki 25/03/11 02:02:45
	Ensure atomic updates to both the data records and the index message, possibly using transactional approaches or confirming successful edits before finalizing operations.

+review, init 8: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/15 00:33:25
	create Schema for no-data

+checkpoint 11: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/15 02:58:34
	Handle Bot error due to wrong ID or right or whatever

+refactor 12: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/18 03:17:47
	Move to TCSchema or something

=general 13: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/15 03:16:34
	Dump Tags

+general, schema 14: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/17 10:35:21
	Parse Schema

=general, schema 15: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/17 10:37:21
	Parse Tags

 general, memo 16: +2 "TeleChanDB\TeleChanDB.py" Ki 25/03/18 03:06:45
	Handle TG limits!

-optimize, tglimits 17: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/19 14:05:55
	Allow batch read

 optimize, tglimits, try 18: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/19 14:06:35
	Clean temporary messages at end mb

=check 19: +0 "TeleChanDB\TeleChanDB.py" Ki 25/03/19 17:17:36
	Load tags list

