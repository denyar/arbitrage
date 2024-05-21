import json
import requests
import pandas as pd
import numpy as np

def load_tokens():
    """Загрузка списка токенов с CoinGecko"""
    response = requests.get('https://api.coingecko.com/api/v3/coins/list')
    tokens = response.json()
    return tokens

def load_config():
    """Загрузка конфигурации из файла"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    cex_exchanges = config.get('cex_exchanges', [])
    dex_exchanges = config.get('dex_exchanges', [])
    return config, cex_exchanges, dex_exchanges

def get_prices_from_cex(cex_exchanges):
    """Получение цен с централизованных бирж"""
    prices = {}
    for exchange in cex_exchanges:
        response = requests.get(f'https://api.{exchange}.com/api/v3/ticker/price')
        data = response.json()
        for item in data:
            symbol = item['symbol']
            price = float(item['price'])
            if symbol not in prices:
                prices[symbol] = {}
            prices[symbol][exchange] = price
    return prices

def get_prices_from_dex(dex_exchanges):
    """Получение цен с децентрализованных бирж"""
    prices = {}
    for exchange in dex_exchanges:
        response = requests.get(f'https://api.thegraph.com/subgraphs/name/{exchange}/prices')
        data = response.json()['data']['tokens']
        for item in data:
            symbol = item['symbol']
            price = float(item['priceUSD'])
            if symbol not in prices:
                prices[symbol] = {}
            prices[symbol][exchange] = price
    return prices

def find_arbitrage_opportunities(prices_cex, prices_dex, min_profit):
    """Поиск арбитражных возможностей"""
    opportunities = []
    for symbol in prices_cex:
        if symbol in prices_dex:
            cex_prices = prices_cex[symbol]
            dex_prices = prices_dex[symbol]
            for cex in cex_prices:
                for dex in dex_prices:
                    price_cex = cex_prices[cex]
                    price_dex = dex_prices[dex]
                    profit = (price_dex - price_cex) / price_cex * 100
                    if profit >= min_profit:
                        opportunities.append({
                            'symbol': symbol,
                            'cex': cex,
                            'dex': dex,
                            'price_cex': price_cex,
                            'price_dex': price_dex,
                            'profit': profit
                        })
    return opportunities
