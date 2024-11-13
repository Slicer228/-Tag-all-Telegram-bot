import sqlite3, json, datetime
conn = sqlite3.connect("DATABASE.db")
cur = conn.cursor()

def get_chat_url(chat_id: str) -> str:
	return f"https://t.me/ALL_BOT_2_0_bot?start={chat_id}"

def del_chat(chat_id: str) -> None:
	try:
		cur.execute(f"DELETE FROM chats WHERE chatid = '{chat_id}'")
		conn.commit()
	except Exception as e:
		pass

def add_error(chat_id: str,error: str) -> None:
	date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	cur.execute(f"INSERT INTO Errors(error, chatid, time) VALUES('{error}', '{chat_id}', '{date}')")
	conn.commit()

def check_state(chat_id: str) -> bool:
	try:
		if cur.execute(f"SELECT state FROM chats WHERE chatid = '{chat_id}'").fetchone()[0] == 1:
			return True
		else:
			return False
	except Exception as e:
		add_error(chat_id,e)
		return False

def set_state(chat_id) -> bool:
	try:
		cur.execute(f"UPDATE chats SET state = True WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def unset_state(chat_id) -> bool:
	try:
		cur.execute(f"UPDATE chats SET state = False WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def add_chat(chat_id: str,chat_name: str) -> bool:
	try:
		t = [0]
		cur.execute(f"INSERT INTO chats(chatid, chatname, state, userlist, lmesg) VALUES('{chat_id}', '{chat_name}', False, '{json.dumps(t)}', '{json.dumps(t)}')")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def update_chat_id(chat_id: str) -> bool:
	try:
		cur.execute(f"UPDATE chats SET chatid = '{chat_id}' WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id, e)
		return False

def update_chat_name(chat_id: str, chat_name: str) -> bool:
	try:
		cur.execute(f"UPDATE chats SET chatname = '{chat_name}' WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def add_user(chat_id: str, userid: str) -> bool:
	try:
		userlist = cur.execute(f"SELECT userlist FROM chats WHERE chatid = '{chat_id}'").fetchone()[0]
		userlist = json.loads(userlist)
		if userid in userlist:
			return False
		userlist.append(userid)
		userlist = json.dumps(userlist)
		cur.execute(f"UPDATE chats SET userlist = '{userlist}' WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def del_user(chat_id: str, userid: str) -> bool:
	try:
		userlist = cur.execute(f"SELECT userlist FROM chats WHERE chatid = '{chat_id}'").fetchone()[0]
		userlist = json.loads(userlist)
		userlist.remove(userid)
		userlist = json.dumps(userlist)
		cur.execute(f"UPDATE chats SET userlist = '{userlist}' WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		add_error(chat_id,e)
		return False

def get_userlist(chat_id: str) -> list:
	try:
		userlist = cur.execute(f"SELECT userlist FROM chats WHERE chatid = '{chat_id}'").fetchone()[0]
		userlist = json.loads(userlist)
		return userlist
	except Exception as e:
		add_error(chat_id,e)
		return []

def add_last_msgs(chat_id: str,msg_ids: list) -> bool:
	try:
		msgs = json.dumps(msg_ids)
		cur.execute(f"UPDATE chats SET lmesg = '{msgs}' WHERE chatid = '{chat_id}'")
		conn.commit()
		return True
	except Exception as e:
		print(e)
		add_error(chat_id,e)
		return False

def get_last_msgs(chat_id: str) -> list:
	try:
		data = cur.execute(f"SELECT lmesg FROM chats WHERE chatid = '{chat_id}'").fetchone()[0]
		return json.loads(data)
	except Exception as e:
		add_error(chat_id,e)
		return []
