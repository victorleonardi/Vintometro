from Scraper.Scrapping import scrape
from SQL_Server_Connection.SQL_Server_Connection import save_dataframe_as_table
import pandas as pd
import resource


if __name__ == '__main__':
    scrape()
    df = pd.read_csv(resource.directory)
    df.drop(columns='Unnamed: 0', inplace=True)
    save_dataframe_as_table(df, 'Steam_Price_Over_Time')
