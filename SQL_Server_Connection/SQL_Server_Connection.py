# Preciso aprender com o Bruno como fazer a conexão entre arquivos de pastas diferentes.
import pyodbc
import pandas as pd
import sqlalchemy
from sqlalchemy import engine
# import Scrapping Ver como é feita a conexão de import


def save_dataframe_as_table(df: pd.DataFrame, table_name: str):
    engine = sqlalchemy.create_engine(
        'mssql+pyodbc://DESKTOP-SCIEEGO\Bia:@Price_DataBase101')
    conn = engine.connect()
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print('Values Inserted')
