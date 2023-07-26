'''
Author: hibana2077 hibana2077@gmail.com
Date: 2023-07-21 11:11:52
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2023-07-26 22:29:05
FilePath: \ST_LAB\lab\get_whale\webfunction.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

import asyncio
import aiohttp
from fake_useragent import UserAgent

__doc__ = """
This module provides functions for sending HTTP GET and POST requests and returning the response text.

Functions:
    http_get(url: str) -> str:
        Sends an HTTP GET request to the specified URL and returns the response text.
    http_post(url: str, data: dict) -> str:
        Sends an HTTP POST request with the specified data to the specified URL and returns the response text.
    run(joblist: list) -> list:
        Runs the specified list of jobs and returns a list of response texts.
    help() -> str:
        Returns the module's documentation string.

example:

    import asyncio
    import webfunction

    if __name__ == '__main__':
        joblist = [
            webfunction.http_get('https://api.etherscan.io/api?module=account&action=balance&address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae&tag=latest&apikey=APIKEY'),
            webfunction.http_get('https://api.etherscan.io/api?module=account&action=balance&address=0x75e89d5979E4f6Fba9F97c104c2F0AFB3F1dcB88&tag=latest&apikey=APIKEY')
        ]
        datas = asyncio.run(webfunction.run(joblist))
        for data in datas:
            print(data)
"""

async def http_get(url: str) -> str:
    """
    Sends an HTTP GET request to the specified URL and returns the response text.

    Args:
        url (str): The URL to send the request to.

    Returns:
        str: The response text.
    """
    UA = UserAgent().random
    headers = {'User-Agent': UA, 'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print(resp.status)
            print(resp.reason)
            return await resp.text()

async def http_post(url: str, data: dict) -> str:
    """
    Sends an HTTP POST request with the specified data to the specified URL and returns the response text.

    Args:
        url (str): The URL to send the request to.
        data (dict): The data to include in the request.

    Returns:
        str: The response text.
    """
    UA = UserAgent().random
    headers = {'User-Agent': UA}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            print(resp.status)
            print(resp.reason)
            return await resp.text()

async def run(joblist: list) -> list:
    """
    Runs the specified list of jobs and returns a list of response texts.

    Args:
        joblist (list): The list of jobs to run.

    Returns:
        list: The list of response texts.
    """
    loop = asyncio.get_event_loop()
    futures = [loop.create_task(job) for job in joblist]
    return await asyncio.gather(*futures)

def help()->str:
    """
    Returns the module's documentation string.

    Returns:
        str: The module's documentation string.
    """
    return __doc__