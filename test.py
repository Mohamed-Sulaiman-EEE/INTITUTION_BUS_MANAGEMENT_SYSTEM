'''
import telegram
#token that can be generated talking with @BotFather on telegram
my_token = '5917226874:AAHQXNbwuBqirLFJutBRxekZU8O2KgtEomM'

def send(msg, chat_id, token=my_token):
	"""
	Send a mensage to a telegram user specified on chatId
	chat_id must be a number!
	"""
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=chat_id, text=msg)


id = -1001657216845
msg="test"
send(msg=msg, chat_id=id , token=my_token)
print("Done")

'''
import requests

def send_to_telegram(message):
    chatID = -1001657216845
    apiToken = '5917226874:AAHQXNbwuBqirLFJutBRxekZU8O2KgtEomM'
    chatID = '515382482'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")

