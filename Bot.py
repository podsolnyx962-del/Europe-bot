import telebot
from telebot import types

# Твой токен уже встроен сюда
TOKEN = '8574301915:AAHse7pg-tP2U9nX5IDWJio03e7QN0PaI8g'
bot = telebot.TeleBot(TOKEN)

# База данных игроков в памяти
players = {}

class Country:
    def __init__(self, name, money, army, factories, stability):
        self.name = name
        self.money = money
        self.army = army
        self.factories = factories
        self.stability = stability
        self.year = 2014
        self.turn = 1

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇦 Украина", callback_data="select_ukraine"),
        types.InlineKeyboardButton("🇷🇺 Россия", callback_data="select_russia"),
        types.InlineKeyboardButton("🇩🇪 Германия", callback_data="select_germany"),
        types.InlineKeyboardButton("🇫🇷 Франция", callback_data="select_france"),
        types.InlineKeyboardButton("🇵🇱 Польша", callback_data="select_poland"),
        types.InlineKeyboardButton("🇬🇧 Великобритания", callback_data="select_uk")
    )
    bot.send_message(
        message.chat.id, 
        "🇪🇺 **Стратегия: Европа 2014**\n\nДобро пожаловать, господин президент! Выберите государство для управления:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def country_selected(call):
    country_key = call.data.split('_')[1]
    
    data = {
        'ukraine': Country("Украина", 600, 8, 10, 70),
        'russia': Country("Россия", 2000, 25, 35, 80),
        'germany': Country("Германия", 3500, 15, 50, 95),
        'france': Country("Франция", 3000, 14, 40, 90),
        'poland': Country("Польша", 1200, 10, 18, 85),
        'uk': Country("Великобритания", 3200, 12, 42, 90)
    }
    
    players[call.message.chat.id] = data[country_key]
    
    bot.answer_callback_query(call.id, f"Вы выбрали: {data[country_key].name}!")
    show_game_menu(call.message.chat.id)

def show_game_menu(chat_id):
    p = players[chat_id]
    
    text = (
        f"🏛 **Страна:** {p.name}\n"
        f"📅 **Год:** {p.year} (Ход: {p.turn})\n\n"
        f"💰 **Бюджет:** {p.money} млн $\n"
        f"⚔️ **Армия:** {p.army} див.\n"
        f"🏭 **Заводы:** {p.factories} шт.\n"
        f"⚖️ **Стабильность:** {p.stability}%\n"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🏭 Строить завод (-500 млн)", callback_data="action_factory"),
        types.InlineKeyboardButton("⚔️ Нанять армию (-200 млн)", callback_data="action_army"),
        types.InlineKeyboardButton("📈 Собрать налоги (+300 млн)", callback_data="action_taxes"),
        types.InlineKeyboardButton("⏩ Следующий ход", callback_data="action_next_turn")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('action_'))
def handle_action(call):
    chat_id = call.message.chat.id
    if chat_id not in players:
        bot.answer_callback_query(call.id, "Игра не начата. Введите /start")
        return
        
    p = players[chat_id]
    action = call.data.split('_')[1]
    
    if action == "factory":
        if p.money >= 500:
            p.money -= 500
            p.factories += 2
            bot.answer_callback_query(call.id, "Заводы построены!")
        else:
            bot.answer_callback_query(call.id, "Недостаточно средств!")
            
    elif action == "army":
        if p.money >= 200:
            p.money -= 200
            p.army += 2
            bot.answer_callback_query(call.id, "Армия пополнена!")
        else:
            bot.answer_callback_query(call.id, "Недостаточно средств!")
            
    elif action == "taxes":
        p.money += 300
        p.stability = max(0, p.stability - 10)
        bot.answer_callback_query(call.id, "Налоги собраны, стабильность упала.")
        
    elif action == "next_turn":
        p.turn += 1
        p.year = 2014 + (p.turn // 4)
        income = (p.factories * 30) - (p.army * 10)
        p.money += income
        bot.answer_callback_query(call.id, f"Ход завершен. Доход: {income} млн $")

    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
        
    show_game_menu(chat_id)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
  
