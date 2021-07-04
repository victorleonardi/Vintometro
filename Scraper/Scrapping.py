from asyncio.windows_events import NULL
from logging import info
from typing import Counter
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import pathlib
from datetime import datetime
import asyncio
from aiomultiprocess import Pool
from multiprocessing import Manager
import time
from math import *
import pandas as pd

# Adicionar a tag de terror
tags = {
    "Indie": 492,
    "Ação": 19,
    "Casual": 597,
    "Aventura": 21,
    "RPG": 122,
    "Atmosférico": 4166,
    "2D": 3871,
    "Boa Trama": 1742,
    "Quebra-cabeças": 1664,
    "Um Jogador": 4182,
    "Estratégia": 9,
    "Simulação": 599,
    "Multijogador": 3859,
    "Arcade": 1773,
    "Gráficos Pixelados": 3964,
    "Terror": 1667
}

info_list = []

today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
Counter = 1

tagged_games = pd.DataFrame()


async def get_html(tag, page=1):
    html_body = ""
    itens = f'https://store.steampowered.com/search/?tags={tags[tag]}&query&start={page}&count=100'
    async with ClientSession() as session:
        async with session.get(itens) as response:
            html_body = await response.read()
    return html_body


def collect_data(html_body, update_df=False, tag=None, info_list=None):
    s_info = ''
    soup = BeautifulSoup(html_body, "html.parser")
    html_parsered = soup.find_all(
        "a", class_=lambda value: value and value.startswith('search_result_row ds_collapse_flag'))
    num_of_games_string = soup.find(
        'div', id='search_results_filtered_warning').text[1:]
    num_of_games = num_of_games_string.split('results')[0]
    num_of_games = num_of_games.replace(',', '')
    if update_df != False:
        for infos in html_parsered:
            name = infos.find(class_='title').text
            image = infos.find('img')['src']
            price_analyse_discount = infos.find('div',
                                                class_='col search_price discounted responsive_secondrow')
            full_price_analyse = infos.find('div',
                                            class_='col search_price responsive_secondrow')
            if price_analyse_discount is not None:
                if 'Free' not in price_analyse_discount.text:
                    price = 'R$' + \
                        price_analyse_discount.text[2:-20].split('R$ ')[1]
                else:
                    price = "Free to Play"
            elif full_price_analyse is not None and price_analyse_discount is None:
                if 'R$' in full_price_analyse.text:
                    price = 'R$' + \
                        full_price_analyse.text[2:-20].split('R$ ')[1]
                else:
                    price = 'Free to Play'
            else:
                price = 'Releasing Soon'
            s_info = f'{name}(.){image}(.){price}(.){tag}'
            info_list.append(s_info)
    return num_of_games


async def loop_through(tuple_info):
    tag, page, info_list = tuple_info
    html_body = await get_html(tag, page)
    collect_data(html_body, True, tag, info_list)


async def make_dic_complete(tuple_info):
    tag, info_list = tuple_info
    html_body = await get_html(tag)
    try:
        num_of_games = collect_data(html_body)
        rest = int(num_of_games) % 100
        limit = int((int(num_of_games) - rest)/4)
        print(limit)
        print(tag)
        async with Pool() as pool:
            await pool.map(loop_through, [(tag, page, info_list) for page in range(0, limit, 100)])
            pool.terminate()
            await pool.join()
        pool.terminate()
    except:
        global Counter
        make_ref_file('HTML Error' + str(Counter), html_body)
        Counter += 1


def make_ref_file(name_file, html_body):
    output_dir = pathlib.Path().resolve() / "referência"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name_file}.html"
    output_file.write_text(html_body.decode(), encoding="utf-8")


async def main(tags, info_list):
    async with Pool(processes=3) as pool:
        await pool.map(make_dic_complete, [(tag, info_list) for tag in tags])
        pool.terminate()
        await pool.join()


async def main_analyses(tags, info_list):
    for tag in tags:
        await make_dic_complete((tag, info_list))


def scrape() -> pd.DataFrame:
    t1 = time.perf_counter()
    tagged_games = pd.DataFrame()
    with Manager() as manager:
        info_list = manager.list()
        keys = list(tags.keys())
        for key in range(0, len(keys)-4, 4):
            asyncio.run(
                main_analyses(
                    [keys[key], keys[key+1], keys[key+2], keys[key+3]], info_list
                )
            )
        unpack_info = [info_list[i] for i in range(len(info_list))]
        for package in unpack_info:
            tagged_games = tagged_games.append(
                {
                    'Date': today,
                    'Game': package.split('(.)')[0],
                    'Image': package.split('(.)')[1],
                    'Price': package.split('(.)')[2],
                    'Tag': package.split('(.)')[3]
                }, ignore_index=True)
        print(tagged_games.head())
        m_df = tagged_games.groupby(
            'Game').Tag.apply(tuple).reset_index()
        tagged_games.drop(columns='Tag', inplace=True)
        tagged_games = m_df.merge(
            tagged_games, copy=False, how='inner', on='Game')
        tagged_games.drop_duplicates('Game', inplace=True)
        tagged_games.Tag.apply(str)
        tagged_games.to_csv(
            r'C:\Users\Bia\Documents\Projetos Python\Vintometro\Data_Storage\Data_Storage_df.csv')
        t2 = time.perf_counter()
        print(t2-t1)
# Preciso definir os tipos de colunas!
