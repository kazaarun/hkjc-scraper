from bs4 import BeautifulSoup
import pandas as pd
import urllib.request, json
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_results(date, race):
    print(date, race)
    option = webdriver.ChromeOptions()

    option.add_argument("--disable-gpu")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-infobars")
    option.add_argument("--start-maximized")
    option.add_argument("--disable-notifications")
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome('chromedriver', options=option)
    url = 'https://racing.hkjc.com/racing/information/english/Racing/LocalResults.aspx?RaceDate=' + date + '&RaceNo=' + race
    print(url)
    try:
        wd.get(url)
        table_found = WebDriverWait(wd, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".table_bd.f_tac.f_fs13.f_fl"))
        )

        print(table_found)
        soup = BeautifulSoup(wd.page_source, "html.parser")
        table = soup.find_all('table', "table_bd f_tac f_fs13 f_fl")[0]
        print(soup)
        print(table)
    except TimeoutException:
        try:
            url = url.rpartition('&')
            wd.get(url[0])
            table_found = WebDriverWait(wd, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".table_bd.f_tac.f_fs13.f_fl"))
            )
            soup = BeautifulSoup(wd.page_source, "html.parser")
            table = soup.find_all('table', "table_bd f_tac f_fs13 f_fl")[0]
        except TimeoutException:
            return 'dateError'
        return 'raceError'
    divdf = pd.read_html(str(table), thousands=None)[0]['Dividend']
    divdf['Dividend (HK$)'] = divdf['Dividend (HK$)'].str.replace(',', '')
    divdf['Dividend (HK$)'] = pd.to_numeric(divdf['Dividend (HK$)'], errors='coerce')
    print(divdf)
    bets = json.loads(urllib.request.urlopen("https://jsonkeeper.com/b/3UGD").read())['bets']
    betdf = pd.DataFrame(
        [{'pool': pool, 'bet': key, 'amount': value} for pool, b in bets.items() for key, value in b.items()])
    betlst =betdf
    betdf['pool'] = betdf['pool'].replace(['qin', 'qpl'], ['QUINELLA', 'QUINELLA PLACE'])
    betdf = betdf.merge(divdf, how='left', left_on=['pool', 'bet'], right_on=['Pool', 'Winning Combination']).drop(
        columns=['Pool', 'Winning Combination'])
    betdf['p/l'] = betdf['amount'] * ((betdf['Dividend (HK$)'] - 1) / 10)
    betdf['p/l'] = betdf['p/l'].fillna(-betdf['amount'])
    betdf['Dividend (HK$)'] = betdf['Dividend (HK$)'].fillna(0)
    return [betdf.to_records(index=False).tolist(), divdf.fillna('').to_records(index=False).tolist(), betlst.to_records(index=False).tolist(), betdf['p/l'].sum()]
