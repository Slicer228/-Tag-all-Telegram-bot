import time

from aiogram import types, Bot, Dispatcher, F
from aiogram.filters.command import Command
from aiogram.methods.get_chat import GetChat
from aiogram import filters
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import KICKED, LEFT, RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR
from cfg import bottoken, admin
from func import *
import asyncio, logging
from aiogram.types import FSInputFile
from time import sleep
import base64
import re,os
logging.basicConfig(level=logging.INFO)
bot = Bot(bottoken)
dp = Dispatcher()

async def send_to_all_text1(chat_id: int,text):
	for user in get_userlist(chat_id):
		try:
			await bot.send_message(chat_id=user, text=text,disable_web_page_preview=True)
		except Exception as e:
			pass

async def send_to_all_document1(chat_id: int,document):
	for user in get_userlist(chat_id):
		try:
			await bot.send_document(chat_id=user, document=document)
		except Exception as e:
			pass

async def del_files(files: list) -> None:
	for i in files:
		try:
			os.remove(i)
		except:
			pass

async def check_timer(state: FSMContext,username: str,chat_id: int,timer: int,user_id: int,text: str,chat_title: str):
	timer1 = timer
	if timer <= 0:
		try:
			data = await state.get_data()
			await send_to_all_media_group(chat_id,data['media'].build())
		except Exception as e:
			pass
		if text == '/all':
			count = await send_to_all_text(chat_id=chat_id,text=f'<i>Вас тегнул(а) <a href = "https://t.me/{username}">{username}</a> из чата </i><b>{chat_title}</b>')
			if count == 0:
				await bot.send_message(chat_id=chat_id, text=f'Сообщение никому не отправлено')
			elif count == 1:
				await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено одному человеку')
			else:
				if count % 10 == 1:
					await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено {count} человеку')
				else:
					await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено {count} людям')
		else:
			count = await send_to_all_text(chat_id=chat_id,text=f'<i>Сообщение от <a href = "https://t.me/{username}">{username}</a> из чата </i><b>{chat_title}:</b>\n\n' + text.replace('/all',''))
			if count == 0:
				await bot.send_message(chat_id=chat_id, text=f'Сообщение никому не отправлено')
			elif count == 1:
				await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено одному человеку')
			else:
				if count % 10 == 1:
					await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено {count} человеку')
				else:
					await bot.send_message(chat_id=chat_id, text=f'Сообщение отправлено {count} людям')
		await state.clear()
	else:
		timer1 = timer1 - 1
		await asyncio.sleep(1)
		await check_timer(state,username,chat_id,timer1,user_id,text,chat_title)

async def send_to_all_text(chat_id: int,text):
	last = []
	count = 0
	for user in get_userlist(chat_id):
		try:
			m = await bot.send_message(chat_id=user, text=text,disable_web_page_preview=True)
			last.append(m.message_id)
			count += 1
		except Exception as e:
			last.append(0)
			pass
	if ('Вас тегнул' in text) and ('из чата' in text):
		pass
	else:
		add_last_msgs(chat_id, last)
	return count

async def send_to_all_media_group(chat_id: int,media):
	try:
		с = 0
		last = []
		for user in get_userlist(chat_id):
			try:
				m = await bot.send_media_group(chat_id=user,media=media)
				last.append(m.message_id)
				с += 1
			except Exception as e:
				last.append(0)
				pass
		if с == 0:
			pass
		else:
			add_last_msgs(chat_id, last)
	except Exception as e:
		return False

async def send_to_all_animation(chat_id: int,animation):
	last = []
	for user in get_userlist(chat_id):
		try:
			m = await bot.send_animation(chat_id=user,animation=animation)
			last.append(m.message_id)
		except Exception as e:
			last.append(0)
			pass
	add_last_msgs(chat_id, last)

async def send_to_all_document(chat_id: int,document):
	last = []
	for user in get_userlist(chat_id):
		try:
			m = await bot.send_document(chat_id=user, document=document)
			last.append(m.message_id)
		except Exception as e:
			last.append(0)
			pass
	add_last_msgs(chat_id, last)

async def send_to_all_audio(chat_id,audio):
	last = []
	for user in get_userlist(chat_id):
		try:
			m = await bot.send_audio(chat_id=user, audio=audio)
			last.append(m.message_id)
		except Exception as e:
			last.append(0)
			pass
	add_last_msgs(chat_id, last)

async def send_to_all_voice(chat_id: int,msg_id):
	last = []
	for user in get_userlist(chat_id):
		try:
			m = await bot.copy_message(from_chat_id=chat_id, message_id=msg_id,chat_id=user)
			last.append(m.message_id)
		except Exception as e:
			last.append(0)
			pass
	add_last_msgs(chat_id, last)

class sec(StatesGroup):
	sd = State()

@dp.message(Command('version'))
async def epta(msg: types.Message):
	if msg.chat.type == 'private' and msg.from_user.id == admin[0]:
		await msg.answer("2.0")

@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT)>>(MEMBER | ADMINISTRATOR | CREATOR)))
async def added_to_group(event: ChatMemberUpdated):
	if event.chat.type == 'private':
		pass
	else:
		if add_chat(event.chat.id, event.chat.title):
			await bot.send_message(text=f'Группа успешно авторизована!\nЧтобы бот работал корректно, надо сделать его администратором\nСсылка на подключение к рассылке из группы: {get_chat_url(event.chat.id)} (нужно перейти и нажать старт)\n/help - для получения списка доступных команд',chat_id=event.chat.id)
		else:
			await bot.send_message(text='Произошла ошибка при авторизации группы!',chat_id=event.chat.id)

@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=(MEMBER | ADMINISTRATOR | CREATOR) >> (KICKED | LEFT)))
async def added_to_group(event: ChatMemberUpdated):
		if event.chat.type == 'private':
			pass
		else:
			del_chat(event.chat.id)

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=(MEMBER | ADMINISTRATOR | CREATOR) >> (KICKED | LEFT)))
async def added_to_group(event: ChatMemberUpdated):
		if event.chat.type == 'private':
			pass
		else:
			del_user(event.chat.id,event.old_chat_member.user.id)

@dp.message(Command('start'))
async def start(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			if msg.text == '/start':
				pass
			else:
				if add_user(msg.text.split(' ')[1],msg.chat.id):
					await msg.answer(f"Вы успешно подключились к группе!")
				else:
					await msg.answer("Вы уже подключены к этой группе!\nЛибо произошла ошибка.")


@dp.message(Command('connect'),F.text)
async def connect(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			await msg.answer(f"Ссылка на подключение к рассылке из группы: {get_chat_url(msg.chat.id)} (нужно перейти и нажать старт)")

@dp.message(Command('set_for_all'),F.text)
async def set_for_all(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			adm = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if str(adm.status) == 'ChatMemberStatus.CREATOR' or str(adm.status) == 'ChatMemberStatus.ADMINISTRATOR':
				set_state(msg.chat.id)
				await msg.reply("Теперь все пользователи могут рассылать сообщения!")

@dp.message(Command('connmail'),F.text)
async def connmail(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat or msg.chat.type == 'private':
		pass
	else:
		adm = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
		if str(adm.status) == 'ChatMemberStatus.CREATOR' or str(adm.status) == 'ChatMemberStatus.ADMINISTRATOR':
			if add_lp_mail(msg.chat.id,msg.text):
				await msg.reply("Почта добавлена!")
			else:
				await msg.reply("Что-то пошло не так")

@dp.message(Command('unset_for_all'),F.text)
async def set_for_all(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			adm = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if str(adm.status) == 'ChatMemberStatus.CREATOR' or str(adm.status) == 'ChatMemberStatus.ADMINISTRATOR':
				unset_state(msg.chat.id)
				await msg.reply("Теперь только некоторые люди могут рассылать сообщения!")

@dp.message(Command('help'),F.text)
async def help(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			await msg.answer("Доступные команды:\n/all - этой командой могут пользоваться создатель и администраторы чата. После команды напишите текст, который хотите разослать, либо прикрепите фото или видео, либо перешлите нужное сообщение после команды если не отправилось все что нужно(ВАЖНО ПРИ ПЕРЕСЫЛКЕ ПРИПИСЫВАТЬ КОМАНДУ А НЕ ПОСЛЕ ПЕРЕСЫЛКИ)\n/stop - для прекращения рассылки сообщений конкретно юзеру, который ввел команду\n/set_for_all - ставит разрешение всем рассылать сообщения(доступно только создателю чата и администраторам)\n/unset_for_all - убирает разрешение всем рассылать сообщения(доступно только создателю чата и администраторам)\n/dellast - удалить последнее разосланное сообщение\n/connmail логин пароль доступна администраторам и владельцу, пишите соотвественно логин почты и пароль для внешних приложений, будет вам рассылка")

@dp.message(Command('stop'),F.text)
async def stop(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			if del_user(msg.chat.id,msg.from_user.id):
				await msg.reply("Вы успешно отказались от рассылки!")
			else:
				await msg.reply("Что то пошло не так, возможно, вы уже отказались от рассылки")

@dp.message(Command('dellast'),F.text)
async def del_last_mesg(msg: types.Message):
	if msg.forward_from or msg.forward_from_chat:
		pass
	else:
		if msg.chat.type == 'private':
			pass
		else:
			adm = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if str(adm.status) == 'ChatMemberStatus.CREATOR' or str(adm.status) == 'ChatMemberStatus.ADMINISTRATOR' or check_state(msg.chat.id):
				userlist = get_userlist(msg.chat.id)
				lastmsgs = get_last_msgs(msg.chat.id)
				schet = 0
				for i in range(1,len(userlist)):
					try:
						await bot.delete_message(chat_id=userlist[i],message_id=lastmsgs[i])
						schet += 1
					except Exception as e:
						pass
				if schet == 0:
					await msg.reply(f"Сообщение ни у кого не удалены")
				elif schet == 1:
					await msg.reply(f"Сообщение удалено только у одного человека")
				else:
					if schet % 10 == 1:
						await msg.reply(f"Сообщение удалено у {schet} человека")
					else:
						await msg.reply(f"Сообщение удалено у {schet} людей")

@dp.message(Command('all'))
async def all(msg: types.Message,state: FSMContext):
	if msg.forward_from or msg.forward_from_chat:
		if msg.chat.type != 'private':
			try:
				await asyncio.sleep(0.5)
				data1 = await state.get_data()
				if data1['val']:
					data = await state.get_data()
					medias = data['media']
					if (msg.photo and msg.from_user.id == data['adminid']) or (msg.photo and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						try:
							if data['val']:
								medias.add_photo(media=msg.photo[0].file_id)
							await state.update_data(media=medias)
						except Exception as e:
							med = MediaGroupBuilder()
							await state.update_data(media=med, adminid=msg.from_user.id)
							if data['val']:
								await send_to_all_media_group(chat_id=msg.chat.id, media=medias.build())
							data = await state.get_data()
							medias = data['media']
							medias.add_photo(media=msg.photo[0].file_id)
							await state.update_data(media=medias)
					elif (msg.video and msg.from_user.id == data['adminid']) or (msg.video and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						try:
							if data['val']:
								medias.add_video(media=msg.video.file_id)
							await state.update_data(media=medias)
						except Exception as e:
							med = MediaGroupBuilder()
							await state.update_data(media=med, adminid=msg.from_user.id)
							if data['val']:
								await send_to_all_media_group(chat_id=msg.chat.id, media=data['media'].build())
							data = await state.get_data()
							medias = data['media']
							medias.add_video(media=msg.video.file_id)
							await state.update_data(media=data['media'])
							await state.set_state(sec.sd)
					elif (msg.animation and msg.from_user.id == data['adminid']) or (msg.animation and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						if data['val']:
							await send_to_all_animation(msg.chat.id, msg.animation.file_id)
					elif (msg.voice and msg.from_user.id == data['adminid']) or (msg.voice and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						if data['val']:
							await send_to_all_voice(msg.chat.id, msg.message_id)
					elif (msg.document and msg.from_user.id == data['adminid']) or (msg.document and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						if data['val']:
							await send_to_all_document(msg.chat.id, msg.document.file_id)
					elif (msg.audio and msg.from_user.id == data['adminid']) or (msg.audio and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						if data['val']:
							await send_to_all_audio(msg.chat.id, msg.audio.id)
					elif (msg.video_note and msg.from_user.id == data['adminid']) or (msg.voice and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
						if data['val']:
							await send_to_all_voice(msg.chat.id, msg.message_id)
					elif msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat):
						if data['val']:
							await send_to_all_text(msg.chat.id, msg.text)
			except Exception as e:
				pass
	else:
		await state.set_state(sec.sd)
		await state.update_data(val=False, media=MediaGroupBuilder(),adminid = msg.from_user.id)
		if msg.chat.type == 'private':
			pass
		else:
			adm = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if str(adm.status) == 'ChatMemberStatus.CREATOR' or str(adm.status) == 'ChatMemberStatus.ADMINISTRATOR' or check_state(msg.chat.id):
				if msg.photo:
					await state.update_data(val = True,media = MediaGroupBuilder(),adminid = msg.from_user.id,text = msg.caption.replace('/all',f'Сообщение от {msg.from_user.username}\n'))
					data = await state.get_data()
					media = data['media']
					media.add_photo(media=msg.photo[0].file_id)
					await state.update_data(media = media)
					await check_timer(state=state,username=msg.from_user.username,user_id=msg.from_user.id,timer=7,text=msg.caption,chat_title=msg.chat.title,chat_id=msg.chat.id)
				elif msg.video:
					await state.update_data(val = True,media=MediaGroupBuilder(),adminid = msg.from_user.id,text = msg.caption.replace('/all',f'Сообщение от {msg.from_user.username}\n'))
					data = await state.get_data()
					media = data['media']
					media.add_video(media=msg.video.file_id)
					await state.update_data(media=media)
					await check_timer(state=state,username=msg.from_user.username,user_id=msg.from_user.id,timer=7,text=msg.caption,chat_title=msg.chat.title,chat_id=msg.chat.id)
				elif msg.animation:
					await state.update_data(val = True,media=MediaGroupBuilder(), adminid=msg.from_user.id,text=msg.caption.replace('/all', f'Сообщение от {msg.from_user.username}\n'))
					await send_to_all_animation(chat_id=msg.chat.id,animation=msg.animation.file_id)
					await check_timer(state=state, username=msg.from_user.username, user_id=msg.from_user.id, timer=7,text=msg.caption, chat_title=msg.chat.title, chat_id=msg.chat.id)
				elif msg.audio:
					await state.update_data(val = True,media=MediaGroupBuilder(), adminid=msg.from_user.id,text=msg.caption.replace('/all', f'Сообщение от {msg.from_user.username}\n'))
					await send_to_all_audio(chat_id=msg.chat.id, audio=msg.audio.file_id)
					await check_timer(state=state, username=msg.from_user.username, user_id=msg.from_user.id, timer=7,text=msg.caption, chat_title=msg.chat.title, chat_id=msg.chat.id)
				elif msg.document:
					await state.update_data(val = True,media=MediaGroupBuilder(), adminid=msg.from_user.id,text=msg.caption.replace('/all', f'Сообщение от {msg.from_user.username}\n'))
					await send_to_all_document(chat_id=msg.chat.id, document=msg.document.file_id)
					await check_timer(state=state, username=msg.from_user.username, user_id=msg.from_user.id, timer=7,text=msg.caption, chat_title=msg.chat.title, chat_id=msg.chat.id)
				else:
					await state.update_data(val = True,media=MediaGroupBuilder(), adminid=msg.from_user.id,text=msg.text.replace('/all', f'Сообщение от {msg.from_user.username}\n'))
					await check_timer(state=state, username=msg.from_user.username, user_id=msg.from_user.id, timer=7,text=msg.text, chat_title=msg.chat.title, chat_id=msg.chat.id)

@dp.message(sec.sd)
async def secs(msg: types.Message,state: FSMContext):
	if msg.chat.type == 'private':
		pass
	else:
		await asyncio.sleep(0.5)
		data = await state.get_data()
		medias = data['media']
		if (msg.photo and msg.from_user.id == data['adminid']) or (msg.photo and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			try:
				if data['val']:
					medias.add_photo(media=msg.photo[0].file_id)
				await state.update_data(media = medias)
			except Exception as e:
				med = MediaGroupBuilder()
				await state.update_data(media=med, adminid=msg.from_user.id)
				if data['val']:
					await send_to_all_media_group(chat_id=msg.chat.id,media=medias.build())
				data = await state.get_data()
				medias = data['media']
				medias.add_photo(media=msg.photo[0].file_id)
				await state.update_data(media=medias)
		elif (msg.video and msg.from_user.id == data['adminid']) or (msg.video and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			try:
				if data['val']:
					medias.add_video(media=msg.video.file_id)
				await state.update_data(media=medias)
			except Exception as e:
				med = MediaGroupBuilder()
				await state.update_data(media=med, adminid=msg.from_user.id)
				if data['val']:
					await send_to_all_media_group(chat_id=msg.chat.id, media=data['media'].build())
				data = await state.get_data()
				medias = data['media']
				medias.add_video(media=msg.video.file_id)
				await state.update_data(media=data['media'])
				await state.set_state(sec.sd)
		elif (msg.animation and msg.from_user.id == data['adminid']) or (msg.animation and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			if data['val']:
				await send_to_all_animation(msg.chat.id,msg.animation.file_id)
		elif (msg.voice and msg.from_user.id == data['adminid']) or (msg.voice and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			if data['val']:
				await send_to_all_voice(msg.chat.id,msg.message_id)
		elif (msg.document and msg.from_user.id == data['adminid']) or (msg.document and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			if data['val']:
				await send_to_all_document(msg.chat.id,msg.document.file_id)
		elif (msg.audio and msg.from_user.id == data['adminid']) or (msg.audio and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			if data['val']:
				await send_to_all_audio(msg.chat.id,msg.audio.id)
		elif (msg.video_note and msg.from_user.id == data['adminid']) or (msg.voice and msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat)):
			if data['val']:
				await send_to_all_voice(msg.chat.id, msg.message_id)
		elif msg.from_user.id == data['adminid'] and (msg.forward_from or msg.forward_from_chat):
			if data['val']:
				await send_to_all_text(msg.chat.id,msg.text)


async def main():
	try:
		await dp.start_polling(bot,skip_updates=True)
	finally:
		await bot.session.close()
if __name__ == '__main__':
	asyncio.run(main())