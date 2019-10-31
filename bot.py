#!/usr/bin/env python3

import csv
import os
import sys
from datetime import datetime

import requests
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler


def get_btc_price(currency, exchange):
    url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=" + currency + "&e=" + exchange
    response = requests.get(url)
    return response.json()[currency]

def send_price_telegram(currency, exchange, price):
    bot = telegram.Bot(token=os.environ.get('TELEGRAM_BOT_API_KEY'))
    text = text="BTC/" + currency + " from " + exchange + ": " + currency + " " + str(price)
    bot.send_message(chat_id=os.environ.get('TELEGRAM_CHAT_ID'), text=text)

def bot():
    btc_usd_price = get_btc_price('USD', 'Bitfinex')
    btc_krw_price = get_btc_price('KRW', 'Bithumb')

    with open(sys.argv[1], mode='a') as csv_file:
        price_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d-%H:%M")

        price_writer.writerow([date_time, btc_usd_price, btc_krw_price])

    # send_price_telegram('USD', 'Bitfinex', btc_usd_price)
    send_price_telegram('KRW', 'Bithumb', btc_krw_price)

if __name__ == '__main__':
    if not os.environ.get('TELEGRAM_BOT_API_KEY') or not os.environ.get('TELEGRAM_CHAT_ID'):
        exit("Please check that TELEGRAM_BOT_API_KEY and TELEGRAM_CHAT_ID env variables are set")

    if len(sys.argv) ==1 :
        exit("Please specify a CSV output file.")

    if not os.path.exists(sys.argv[1]):
        with open(sys.argv[1], mode='w') as csv_file:
            csv_file.write("Date,Bitfinex-BTC-USD,Bithumb-BTC-KRW\n")

    scheduler = BlockingScheduler()
    scheduler.add_job(bot, 'interval', seconds=60)

    print('Press Ctrl+C to exit')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
