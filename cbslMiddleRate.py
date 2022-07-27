import requests
from pathlib import Path
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import re
import pandas as pd


url =  'https://www.cbsl.gov.lk/en/middle-exchange-rate-and-variation-margin'

def get_middle_rate(url):
    # retrieve the latest pdf file
    try:
        pdf_content = requests.get(url, stream=True).content
        pdf = PdfReader(BytesIO(pdf_content))
        text = pdf.getPage(0).extractText()

        match_date = re.search("\d{2}.\d{2}.\d{4}", text)
        match_middle_rate = re.search("(?<=required to use )(.*)(?=as the middle)", text)
        upper_margin = re.search("(?<=upper margin at)(.*)(?=\n)?(?=and the low)?(.*)?", text)
        lower_margin = re.search("(?<=lower margin at)(.*)(?=of the)", text)
        
        return {
            "Date": match_date.group(0),
            "MiddleRate": match_middle_rate.group(0),
            "UpperMargin": upper_margin.group(0),
            "LowerMargin": lower_margin.group(0)
        }
    except Exception as e:
        print(e)
        return None
    
           

html = requests.get(url).text
bs = BeautifulSoup(html, 'html.parser')

# //*[@id="article-12453"]/div/div/div/div/p[2]
article = bs.find('div', id='article-12453')
# latest_file_url = article.find_all('p')[6].find('a')['href']
ps = article.find_all('p')

rates = []

try:
    option = int(input("Do you want to see the latest rate or download all rates \n Type 1 - for latest rate \n Type 2 - for all rates in a CSV file \n>>"))
    
    if option == 1:
        url = ps[2].find('a')['href']
        data =  get_middle_rate(url)
        print(data['Date'], data['MiddleRate'], data['UpperMargin'], data['LowerMargin'])
        
    elif option == 2:
        for i, p in enumerate(ps):
            if i == 0:
                continue
            url = p.find('a')['href']
            data =  get_middle_rate(url)
            if data is not None:
                rates.append(data)        
        df = pd.DataFrame(rates)
        df.to_csv('middle_rate.csv', index=False)
        print("Successfully downloaded")
        
except Exception as e:
    print("error", e)
