from asyncio.windows_events import NULL
from logging import info
from typing import Counter
from aiohttp import ClientSession
import aiomultiprocess
from bs4 import BeautifulSoup
import pathlib
import asyncio
from aiomultiprocess import Pool
from multiprocessing import Manager
import time
from math import *
import pandas as pd

# Adicionar a tag de terror
tags = {
    "Indie": 492,
    "Casual": 597,
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
    "Gráficos Pixelados": 3964
}

tags_2 = {
    "Indie": 492,
    "Casual": 597,
    "RPG": 122
}

info_list = []

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

            info_list.append(name)
            info_list.append(image)
            info_list.append(price)
            info_list.append(tag)
    return num_of_games


# Por algum motivo, não está coletando o valor total que deveria
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


async def make_dic_complete_analyses(tuple_info):
    tag, info_list = tuple_info
    html_body = await get_html(tag)
    num_of_games = collect_data(html_body)
    rest = int(num_of_games) % 100
    limit = int((int(num_of_games) - rest)/4)
    for page in range(0, limit, 100):
        await loop_through((tag, page, info_list))


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


if __name__ == '__main__':
    with Manager() as manager:
        info_list = manager.list()
        t1 = time.perf_counter()
        asyncio.run(
            main_analyses(
                tags_2, info_list
            )
        )
        unpack_info = (
            [info_list[i] for i in range(0, len(info_list), 4)],
            [info_list[i] for i in range(1, len(info_list), 4)],
            [info_list[i] for i in range(2, len(info_list), 4)],
            [info_list[i] for i in range(3, len(info_list), 4)]
        )
        # desempacotar as informações de uma lista.
        for position in range(len(unpack_info[0])):
            if unpack_info[2][position]:
                tagged_games = tagged_games.append(
                    {
                        'Games': unpack_info[0][position],
                        'Image': unpack_info[1][position],
                        'Price': unpack_info[2][position],
                        'Tag': unpack_info[3][position]
                    }, ignore_index=True)
            elif unpack_info[2][position] == None:
                tagged_games = tagged_games.append(
                    {
                        'Games': unpack_info[0][position],
                        'Image': unpack_info[1][position],
                        'Price': "Nan",
                        'Tag': "Nan"
                    }, ignore_index=True)
        print(tagged_games.head())
        tagged_games.to_csv(
            r'C:\Users\Bia\Documents\Projetos Python\Vintometro\Test_df\Test df.csv')  # Não consigo abrir o arquivo csv para avaliar os dados

        t2 = time.perf_counter()
        print(t2-t1)
