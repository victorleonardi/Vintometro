from asyncio.windows_events import NULL
from typing import Counter
from aiohttp import ClientSession
import aiomultiprocess
from bs4 import BeautifulSoup
import pathlib
import asyncio
from aiomultiprocess import Pool, pool
import time
from math import *
import pandas as pd

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
    "Gráficos Pixelados": 3964
}

tagged_games = pd.DataFrame()

info_list = ([], [], [], [])

Counter = 1


async def get_html(tag, page=1):
    html_body = ""
    itens = f'https://store.steampowered.com/search/?sort_by=Released_DESC&tags={tags[tag]}&query&start={page}&count=100'
    async with ClientSession() as session:
        async with session.get(itens) as response:
            html_body = await response.read()
    return html_body


def collect_data(html_body, update_df=False, tag=None):
    #make_ref_file('IndiePage', html_body)
    soup = BeautifulSoup(html_body, "html.parser")
    html_parsered = soup.find_all(
        "a", class_=lambda value: value and value.startswith('search_result_row ds_collapse_flag'))
    num_of_games_string = soup.find(
        'div', id='search_results_filtered_warning').text[1:]  # Rever essa informação, vindo errado.
    num_of_games = num_of_games_string.split('results')[0]
    num_of_games = num_of_games.replace(',', '')
    if update_df != False:
        for infos in html_parsered:
            name = infos.find(class_='title').text
            image = infos.find('img')['src']
            try:
                price_analyse = infos.find(
                    class_='col search_price discounted responsive_secondrow').text
                if len(price_analyse) == 1:
                    price = 'R$' + price_analyse[2:-20].split('R$ ')
                else:
                    price = 'R$' + price_analyse[2:-20].split('R$ ')[1]
                # Usar um .split("R$ ") e tratar como uma lista que o primeiro argumento é o preço cheio, enquanto o segundo, a promoção.
            except:
                price = 'Releasing Soon'
            info_list[0].append(name)
            info_list[1].append(image)
            info_list[2].append(price)
            info_list[3].append(tag)
    return num_of_games


# Por algum motivo, não está coletando o valor total que deveria
async def loop_through(tuple_info):
    tag, page = tuple_info
    html_body = await get_html(tag, page)
    collect_data(html_body, True, tag)


async def make_dic_complete(tag):
    html_body = await get_html(tag)
    try:
        num_of_games = collect_data(html_body)
        print(tag)
        async with Pool(processes=3) as pool:
            await pool.map(loop_through, [(tag, page) for page in range(0, int(num_of_games), 100)])
            pool.terminate()
            await pool.join()
        pool.terminate()
    except:
        global Counter
        make_ref_file('HTML Error' + Counter, html_body)
        Counter += 1


async def make_dic_complete_analyses(tag):
    info_list = ([], [], [])
    html_body = await get_html(tag)
    num_of_games = collect_data(html_body)
    print(num_of_games)
    await loop_through(tag, num_of_games, info_list)
    tagged_games['Games'] = info_list[0]
    tagged_games['Image'] = info_list[1]
    tagged_games['Price'] = info_list[2]
    tagged_games.to_csv(
        r'C:\Users\Bia\Documents\Projetos Python\Vintometro\Test_df\Test df.csv')


def make_ref_file(name_file, html_body):
    output_dir = pathlib.Path().resolve() / "referência"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name_file}.html"
    output_file.write_text(html_body.decode(), encoding="utf-8")


async def main(tags):
    async with Pool(processes=3) as pool:
        await pool.map(make_dic_complete, tags)
        pool.terminate()
        await pool.join()

if __name__ == '__main__':
    t1 = time.perf_counter()
    asyncio.run(
        main(
            list(
                tags.keys()
            )
        )
    )
    t2 = time.perf_counter()
    print(t2-t1, "\n", tagged_games)
"""
t1 = time.perf_counter()
asyncio.run(make_dic_complete_analyses('Indie'))
t2 = time.perf_counter()
print(t2-t1)

t1 = time.perf_counter()
games_Indie = asyncio.run(main("Indie"))
t2 = time.perf_counter()
print(t2-t1)
games_Aventura = asyncio.run(main('Aventura'))
t3 = time.perf_counter()
print(t3-t2)"""
