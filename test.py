from numpy import copy, dtype
import pandas as pd
from SQL_Server_Connection.SQL_Server_Connection import save_dataframe_as_table
from datetime import datetime

today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

print(today)

df = pd.read_csv(
    r'C:\Users\Bia\Documents\Projetos Python\Vintometro\Data_Storage\Data_Storage_df.csv', dtype={
        'Game': 'str',
        'Image': str,
        'Price': str,
        'Tag': 'str'
    })
print(df)

df.drop(columns='Unnamed: 0', inplace=True)

save_dataframe_as_table(df, 'Teste')
# df2.to_csv(
#    r'C:\Users\Bia\Documents\Projetos Python\Vintometro\Data Storage\Data_Storage_df_teste.csv')
# print(df2)
# Aplicar no código principal
