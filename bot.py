import telebot
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv
from flask import Flask, request,jsonify

def get_stat():
    d = {}
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT candidat FROM users1")
    c = cursor.fetchall()
    c = [int(i[0]) for i in c if i[0] != None]
    for i in c:
        cursor.execute("SELECT name FROM candidats1 WHERE id = ?",(i,))
        name = cursor.fetchall()[0][0]
        if name in d:
            d[name] += 1
        else:
            d[name] = 1
    return d

def gen_markup(i):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM candidats1")
    a = cursor.fetchall()
    markup.add(telebot.types.InlineKeyboardButton("Голосовать", callback_data = str(a[i][0])))
    return markup

bot = telebot.TeleBot("480467230:AAEJ3pDSZ2mwHxbAeFoEW5uAo8BXHvKPp8I")
server = Flask(__name__)
"""
cursor.execute('''CREATE TABLE candidats2
             (name, bio, photo, count)''')
cursor.execute('''CREATE TABLE users2
             (name,id,class)''')
conn.commit()
"""
z = ["7-ИКТ","7-ХБ","7-М","7-Ф","8-ХБ","8-М","8-Ф","9-ХБ","9-М","9-Ф","10-ИКТ","10-ХБ","10-Ф","10-М","11-ХБ","11-Ф","11-М"]
classes = {}
for i in z:
    classes[i] = 0

def formating_candidats(name,bio,url):
    symb = f"<a href='{url}'>&#8203;</a>"
    text = f'{symb}<b>{name}</b>\n{bio}'
    return text

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.from_user.id
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT candidat FROM users1 WHERE id = ?", (chat_id,))
    voted = cursor.fetchall()
    if voted[0][0] == None:
        cursor.execute("UPDATE users1 set candidat = ? WHERE id = ?",(call.data,chat_id))
        conn.commit()
        bot.answer_callback_query(call.id, "Вы успешно проголосовали!")
    else:
        bot.answer_callback_query(call.id, "Нельзя голосовать повторно!")
    conn.close()
@bot.message_handler(commands = ["start"])
def hello(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT registered FROM users1 WHERE id = ?",(message.chat.id,))
    status_new_user = cursor.fetchall()
    but1 = telebot.types.KeyboardButton(text="Регистрация")
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    keyboard.add(but1)
    keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    but2 = telebot.types.KeyboardButton(text="Список кандидатов")
    keyboard1.add(but2)
    try:
        cursor.execute("insert into users1 values (?,?,?,?,?)", (None, message.chat.id, None, None,0))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    try:
        if status_new_user[0][0] == 0:
            bot.send_message(message.chat.id, """Привет, в Ришельевском лицее проходят выборы президента лицея!\nРегестрируйся и голосуй за понравившегося кандидата!""", reply_markup = keyboard)
        else:
            bot.send_message(message.chat.id,
                         """Привет, в Ришельевском лицее проходят выборы президента лицея!\nРегестрируйся и голосуй за понравившегося кандидата!\nВы уже зарегестрированны.""",reply_markup = keyboard1)
    except:
        bot.send_message(message.chat.id,
                         """Привет, в Ришельевском лицее проходят выборы президента лицея!\nРегестрируйся и голосуй за понравившегося кандидата!""",
                         reply_markup=keyboard)

    conn.close()

@bot.message_handler(func=lambda m: m.text == "Регистрация")
def registration(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT registered FROM users1 WHERE id = ?", (message.chat.id,))
    status_new_user = cursor.fetchall()
    try:
        if status_new_user[0][0] == 0:
            msg = bot.send_message(message.chat.id,"Просим вас вводить данные корректно, каждый телеграм аккаунт учавствующий в опросе виден администрации.\nВведите ваше имя и фамилию в именительном падеже, без ошибок.", reply_markup=telebot.types.ReplyKeyboardRemove(True))
            conn.close()
            bot.register_next_step_handler(msg, process_name_step)
        else:
            bot.send_message(message.chat.id,"Вы уже зарегестрированны.")
    except:
        msg = bot.send_message(message.chat.id,
                               "Просим вас вводить данные корректно, каждый телеграм аккаунт учавствующий в опросе виден администрации.\nВведите ваше имя и фамилию в именительном падеже, без ошибок.",
                               reply_markup=telebot.types.ReplyKeyboardRemove(True))
        conn.close()
        bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users1 set name = ? WHERE id = ?",(message.text,message.chat.id))
        conn.commit()
    except:
        bot.send_message(message.chat.id,"Перепройдите регестрацию. Для этого заново введите /start")
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for but in z:
        keyboard.add(telebot.types.KeyboardButton(text=but))
    conn.close()
    msg = bot.send_message(message.chat.id, 'Выберите ваш класс',reply_markup = keyboard)
    bot.register_next_step_handler(msg, process_class_step)

def process_class_step(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton(text="Список кандидатов"))
    cursor.execute("SELECT class FROM users1 WHERE class = ?",(message.text,))
    a = cursor.fetchall()
    if message.text in z:
        try:
            if len(a) <= 28:
                cursor.execute("UPDATE users1 set class = ? WHERE id = ?",(message.text,message.chat.id))
                cursor.execute("UPDATE users1 set registered = 1 WHERE id = ?", (message.chat.id,))
                conn.commit()
                bot.send_message(message.chat.id,"Регистрация успешно завершена.",reply_markup = keyboard)
            else:
                bot.send_message(message.chat.id,"Места в вашем классе кончились, обратитесь к администрации лицея.",reply_markup = telebot.types.ReplyKeyboardRemove(True))

        except:
            cursor.execute("UPDATE users1 set class = ? WHERE id = ?", (message.text, message.chat.id))
            cursor.execute("UPDATE users1 set registered = 1 WHERE id = ?", (message.chat.id,))
            conn.commit()
            bot.send_message(message.chat.id, "Регистрация успешно завершена.", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Перепройдите регестрацию. Для этого заново введите /start")

    conn.close()

@bot.message_handler(func=lambda m: m.text == "Список кандидатов")
def show(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    cursor.execute("SELECT candidat FROM users1 WHERE id = ?", (message.chat.id,))
    voted = cursor.fetchall()
    cursor.execute("SELECT registered FROM users1 WHERE id=?",(message.chat.id,))
    if voted[0][0] == None:
        try:
            stat = cursor.fetchall()[0][0]
            if stat == 1:
                cursor.execute("SELECT * FROM candidats1")
                cands = cursor.fetchall()
                for cand in cands:
                    bot.send_message(message.chat.id, formating_candidats(cand[0], cand[1], cand[2]), parse_mode="html",
                                    reply_markup=gen_markup(cand[3]))
            else:
                bot.send_message(message.chat.id, "Сначала пройдите регистрацию!")
        except:
            bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позднее.")
        conn.close()

@bot.message_handler(func=lambda m: m.text == "Результаты")
def get_stats(message):
    d = get_stat()
    data_names = d.keys()
    data_values = d.values()
    dpi = 80
    fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))
    mpl.rcParams.update({'font.size': 9})
    plt.title('Голоса кандидатов.(%)')
    xs = range(len(data_names))
    plt.pie(
        data_values, autopct='%.1f', radius=1.1,
        explode=[0.15] + [0 for _ in range(len(data_names) - 1)])
    plt.legend(
        bbox_to_anchor=(-0.40, 0.65, 0.25, 0.25),
        loc='lower left', labels=data_names)
    fig.savefig('pie.png')
    s = ""
    for i in d.keys():
        s+=i+": "+str(d[i])+"\n"
    bot.send_message(message.chat.id,s)
    bot.send_photo(message.chat.id,open("pie.png","rb"))

@bot.message_handler(func=lambda m: m.text == "+5")
def plus(message):
    conn = sqlite3.connect("rl.db")
    cursor = conn.cursor()
    for i in range(5):
        cursor.execute("insert into users1 values (?,?,?,?,?)", (None, message.chat.id, None, 0, 0))
    conn.commit()

@server.route('/', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://rllic.herokuapp.com/')
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))