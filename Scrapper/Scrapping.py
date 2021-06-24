from asyncio.windows_events import NULL
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import pathlib
import asyncio
from aiomultiprocess import Pool
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

tagged_games = pd.DataFrame(columns='Games')


async def get_html(tag, page=1):
    html_body = ""
    itens = f'https://store.steampowered.com/search/?sort_by=Released_DESC&tags={tags[tag]}&category1=998,996&query&start={page}&count=100'
    async with ClientSession() as session:
        async with session.get(itens) as response:
            html_body = await response.read()
    return html_body


def collect_data(html_body, dic_games=NULL):
    soup = BeautifulSoup(html_body, "html.parser")
    html_parsered = soup.find_all(
        "a", class_=lambda value: value and value.startswith('search_result_row ds_collapse_flag'))
    num_of_games_string = soup.find(
        'div', id='search_results_filtered_warning').text[2:]
    num_of_games = num_of_games_string.split('results')[0]
    num_of_games = num_of_games.replace(',', '')
    if dic_games != NULL:
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
            dic_games[name] = [image, price]
    return num_of_games


# Por algum motivo, não está coletando o valor total que deveria
async def loop_through(tag, total_games):
    dic_games = {}
    pages = int(total_games)
    for page in range(0, pages, 100):
        html_body = await get_html(tag, page)
        collect_data(html_body, dic_games)
    return dic_games  # Inserir o tratamento com dataframe aqui! Mas, antes, atualizar Github


async def make_dic_complete(tag):
    html_body = await get_html(tag)
    num_of_games = collect_data(html_body)
    async with Pool() as pool:
        print(tag)
        dic_games = await pool.starmap(loop_through, [(tag, num_of_games)])
        pool.terminate()
        await pool.join()
        tagged_games[tag] = dic_games


async def make_dic_complete_analyses(tag):
    html_body = await get_html(tag)
    num_of_games = collect_data(html_body)
    dic_games = await loop_through(tag, num_of_games)
    # Trabalhar com um data frame, não mais dicionário
    tagged_games[tag] = dic_games


def make_ref_file(name_file, html_body):
    output_dir = pathlib.Path().resolve() / "referência"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name_file}.html"
    output_file.write_text(html_body.decode(), encoding="utf-8")


"""if __name__ == '__main__':
    t1 = time.perf_counter()
    for tag in tags:
        asyncio.run(make_dic_complete(tag))
    t2 = time.perf_counter()
    print(t2-t1, "\n", tagged_games)"""

asyncio.run(make_dic_complete_analyses('Indie'))

"""t1 = time.perf_counter()
games_Indie = asyncio.run(main("Indie"))
t2 = time.perf_counter()
print(t2-t1)
games_Aventura = asyncio.run(main('Aventura'))
t3 = time.perf_counter()
print(t3-t2)"""
