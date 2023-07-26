'''
Author: hibana2077 hibana2077@gmail.com
Date: 2023-07-24 11:00:18
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2023-07-26 22:37:01
FilePath: \ST_LAB\lab\get_whale\page_parse.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

import asyncio
import traceback
import pandas as pd
from webfunction import http_get
from bs4 import BeautifulSoup
from ccxt import binance

BLOCKINFO_URL_BASE = 'https://etherscan.io/block/{}'
BLOCKTXS_URL_BASE = 'https://etherscan.io/txs?block={}&p={}'
BLOCKTXSIFO_URL_BASE = 'https://etherscan.io/tx/{}'

"""
func:
    - get_block_info
    - get_block_txs_info
    - check_big_whale

usage:
# print(asyncio.run(get_block_info(17755956)))
# data = asyncio.run(get_block_txs_info(17755956))
# erc20,eth = asyncio.run(check_big_whale(data, 1))
# print(erc20)
# print(eth)
# note : AttributeError
"""

async def get_block_info(block: int) -> dict:
    """
    Returns the block info of the specified block number.

    Args:
        block (int): The block number.

    Returns:
        dict: The block info of txs and contract internal txs.
    """
    page = await http_get(BLOCKINFO_URL_BASE.format(block))
    soup = BeautifulSoup(page, 'html.parser')
    block_info = {}
    block_info['block'] = block
    block_info['total_txs'], block_info['total_contract_internal_txs'] = map(lambda x: int(x.text.split()[0]),soup.find('div', id='ContentPlaceHolder1_div_tx_fieldvalue').find_all('a'))
    return block_info

async def get_block_txs_info(block_num:int) -> pd.DataFrame:
    """
    Returns the txs info of the specified block number.

    Args:
        block_num (int): The block number.

    Returns:
        pd.DataFrame: The txs info of the specified block number.
    """
    try:
        first_page = await http_get(BLOCKTXS_URL_BASE.format(block_num, 1))
        soup = BeautifulSoup(first_page, 'html.parser')
        total_pages = int(soup.find('span', class_='page-link text-nowrap').text.split()[-1])
        #一次性獲取所有頁面的資料
        joblist = [http_get(BLOCKTXS_URL_BASE.format(block_num, page)) for page in range(1, total_pages + 1)]
        pages = await asyncio.gather(*joblist)
        #解析數據:紀錄下有Transfer的交易，分ETH不為0的交易和ETH為0的交易
        txs = []
        for page in pages:
            soup = BeautifulSoup(page, 'html.parser')
            #pd.read_html()會自動將table轉換成DataFrame
            table = soup.find('div', id='ContentPlaceHolder1_divTransactions')
            table = table.find('div', class_ = 'table-responsive')
            table = pd.read_html(str(table))
            #drop Unnamed: 0 Unnamed: 4 Unnamed: 6 Block
            table = table[0].drop(columns=['Unnamed: 0', 'Unnamed: 4', 'Unnamed: 6', 'Block'])
            #rename Unnamed: 9 to GasFee
            table = table.rename(columns={'Unnamed: 9': 'GasFee'})
            txs.append(table)
        txs = pd.concat(txs)
        txs = txs.reset_index(drop=True)
        #value == 0 and method is Transfer
        txs['ERC20 TokenTransfer'] = txs['Value'].apply(lambda x: True if x.split()[0] == '0' else False) & txs['Method'].apply(lambda x: True if x == 'Transfer' else False)
        return txs
    except Exception as e:
        print("below is the error message")
        traceback.print_exc()
        raise AttributeError

async def check_big_whale(txs: pd.DataFrame, tokenthreshold:float) -> list:
    """
    Returns the big whale information of the specified txs.

    Args:
        txs (pd.DataFrame): The txs information.
        tokenthreshold (float): The threshold value for the token.

    Returns:
        list: The big whale information of the specified txs.
    """
    try:
        eth_price = binance().fetch_ticker('ETH/USDT')['last']
        txs['Value'] = txs['Value'].astype(str)
        txs['Value'] = txs['Value'].apply(lambda x: x.replace(',', ''))
        print(txs['Value'].dtype)
        txs['Value'] = txs['Value'].apply(lambda x: float(x.split()[0]))
        #ERC token transfer
        erc20_txs = txs[txs['ERC20 TokenTransfer'] == True]
        #ETH transfer
        eth_txs = txs[(txs['Method'] == 'Transfer') & (txs['ERC20 TokenTransfer'] == False) & (txs['Value'] * eth_price >= tokenthreshold)]
        
        #check erc20
        txn_hash = erc20_txs['Txn Hash'].tolist()
        joblist = [http_get(BLOCKTXSIFO_URL_BASE.format(hash)) for hash in txn_hash]
        pages = await asyncio.gather(*joblist)
        token_temp_data = {}#key:txhash
        for page in pages:
            soup = BeautifulSoup(page, 'html.parser')
            #get txn_hash as key
            txn_hash = soup.find('span', id='spanTxHash').text
            #get transfer record
            transfer_list = list()
            area = soup.find('div', class_="d-flex flex-column gap-3 overflow-y-auto scrollbar-custom")
            if area is None:
                print('Possible error: no transfer record')
                continue
            all_lines = area.find_all('div', class_="row-count d-flex align-items-baseline")
            for line in all_lines:
                line_content = line.find('span', class_="d-inline-flex flex-wrap align-items-center")
                all_spans = list(map(lambda x: x.text, line_content.find_all('span')))
                temp_data = {
                    "from": all_spans[1],
                    "to": all_spans[3],
                    "value": all_spans[5],
                    "notional": float(all_spans[6].replace('(',"").replace(')',"").replace('$',"").replace(",","")) if all_spans[6][2].isdigit() else 0,
                    "currency": all_spans[-1].replace('.', '')
                }
                if temp_data['notional'] == 0:
                    #get a
                    if line.find('a', type="button") is None:continue
                    temp_data['notional'] = line.find('a', type="button").text.replace('$',"").replace(",","")
                    temp_data['notional'] = float(temp_data['notional'])
                transfer_list.append(temp_data) if temp_data['notional'] >= tokenthreshold else None
            if len(transfer_list) != 0:token_temp_data[txn_hash] = transfer_list

        erc20_txs = token_temp_data
        #check eth
        
        new_eth_txs = dict()
        for _, row in eth_txs.iterrows():
            txn_hash = row['Txn Hash']
            new_eth_txs[txn_hash] = {
                "from": row['From'],
                "to": row['To'],
                "value": row['Value'],
                "notional": row['Value'] * eth_price,
                "currency": 'ETH'
            }

        return [erc20_txs, new_eth_txs]
    except Exception as e:
        print("below is the error message")
        traceback.print_exc()
        raise AttributeError


# print(asyncio.run(get_block_info(17755956)))
# data = asyncio.run(get_block_txs_info(17755956))
# erc20,eth = asyncio.run(check_big_whale(data, 1))
# print(erc20)
# print(eth)
# note : AttributeError