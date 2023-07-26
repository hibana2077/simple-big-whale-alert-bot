
import asyncio
import argparse
import time
import websocket
import json
import _thread as thread
from page_parse import get_block_txs_info, check_big_whale
from discordwebhook import send_discord_webhook
from pprint import pprint

argparser = argparse.ArgumentParser()
argparser.add_argument('-at', '--alchemytoken', help='Alchemy Token', required=True)
argparser.add_argument('-d', '--discordwebhook', help='Discord Webhook URL', required=False)
argparser.add_argument('-th', '--threshold', help='Threshold', required=False, default=10000)


WS_BASE = 'wss://eth-mainnet.g.alchemy.com/v2/{}'


def on_message(ws, message):
    #load json
    message = json.loads(message)['params']['result']['number'] if 'params' in json.loads(message) else "NO MESSAGE"
    if message != "NO MESSAGE":
        print(f"### New Block ###")
        print(f"### Block Number: {message} (16)###")
        print(f"### Block Number: {int(message,16)} (10)###")
        while True:
            try:
                print("requesting data...")
                data = asyncio.run(get_block_txs_info(int(message,16)))
                print(data)
                break
            except AttributeError:
                print("AttributeError")
                time.sleep(1)
        while True:
            try:
                print("checking big whale...")
                erc20,eth = asyncio.run(check_big_whale(data, int(argparser.parse_args().threshold)))
                break
            except AttributeError:
                print("AttributeError")
                time.sleep(1)
        pprint(f"###\n ERC20:\n {erc20} \n###")
        pprint(f"###\n ETH:\n {eth} \n###")
        print("sending ERC-20 data...")
        if argparser.parse_args().discordwebhook:
            for key in erc20.keys():
                for data in erc20[key]:
                    send_data = {
                        "content" : "",
                        "username" : "Whale Bot",
                        "embeds" : [
                            {
                            "type": "rich",
                            "title": "Big whale alert",
                            "description": "",
                            "color": int("0x00FFFF", 16),
                            "fields": [
                                {
                                "name": "From",
                                "value": f"`{data['from']}`"
                                },
                                {
                                "name": "To",
                                "value": f"`{data['to']}`"
                                },
                                {
                                "name": "For",
                                "value": f"*{data['value']} {data['currency']} ({data['notional']})*"
                                }
                            ],
                            "thumbnail": {
                                "url": "https://d33wubrfki0l68.cloudfront.net/fcd4ecd90386aeb50a235ddc4f0063cfbb8a7b66/4295e/static/bfc04ac72981166c740b189463e1f74c/40129/eth-diamond-black-white.jpg",
                                "height": 0,
                                "width": 0
                            },
                            "footer": {
                                "text": "Power by hibana2077",
                                "icon_url": "https://w7.pngwing.com/pngs/914/758/png-transparent-github-social-media-computer-icons-logo-android-github-logo-computer-wallpaper-banner-thumbnail.png",
                                "proxy_icon_url": "https://github.com/hibana2077"
                            },
                            "url": f"https://etherscan.io/tx/{key}"
                            }
                        ]
                    }
                send_discord_webhook(argparser.parse_args().discordwebhook, send_data)
            print("sending ETH data...")
            for key in eth.keys():
                send_data = {
                        "content" : "",
                        "username" : "Whale Bot",
                        "embeds" : [
                            {
                            "type": "rich",
                            "title": "Big whale alert",
                            "description": "",
                            "color": int("0x00FFFF", 16),
                            "fields": [
                                {
                                "name": "From",
                                "value": f"`{eth[key]['from']}`"
                                },
                                {
                                "name": "To",
                                "value": f"`{eth[key]['to']}`"
                                },
                                {
                                "name": "For",
                                "value": f"*{eth[key]['value']} {eth[key]['currency']} ({eth[key]['notional']})*"
                                }
                            ],
                            "thumbnail": {
                                "url": "https://d33wubrfki0l68.cloudfront.net/fcd4ecd90386aeb50a235ddc4f0063cfbb8a7b66/4295e/static/bfc04ac72981166c740b189463e1f74c/40129/eth-diamond-black-white.jpg",
                                "height": 0,
                                "width": 0
                            },
                            "footer": {
                                "text": "Power by hibana2077",
                                "icon_url": "https://w7.pngwing.com/pngs/914/758/png-transparent-github-social-media-computer-icons-logo-android-github-logo-computer-wallpaper-banner-thumbnail.png",
                                "proxy_icon_url": "https://github.com/hibana2077"
                            },
                            "url": f"https://etherscan.io/tx/{key}"
                            }
                        ]
                    }
                send_discord_webhook(argparser.parse_args().discordwebhook, send_data)
            

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print(f"### closed ### {close_status_code} {close_msg}")

def on_open(ws):
    def run(*args):
        # subscribe to mined transactions
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_subscribe",
            "params": ["newHeads"]
        }
        ws.send(json.dumps(subscribe_message))
        time.sleep(1)  # give server a sec to respond

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        WS_BASE.format(argparser.parse_args().alchemytoken),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
