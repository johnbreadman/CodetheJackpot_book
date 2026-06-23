"""
Code the Jackpot - 3.1 Why Historical Data Matters: Randomness and Repeatability
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 3.1 Why Historical Data Matters: Randomness and Repeatability
# ======================================================================
import warnings
import pandas as pd
import requests
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)

def scrape_historical_draws(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    draw_rows = soup.find_all('tr')
    extracted_data = []
    for row in draw_rows:
        date_link = row.find('a')
        if date_link and '/results/' in date_link['href']:
            date = date_link['href'].split('/')[-1]
            numbers_list = row.find('ul', class_='balls small')
            if numbers_list:
                numbers = [span.text for span in numbers_list.find_all('span')]
                extracted_data.append({'date': date, 'numbers': ', '.join(numbers)})
    return extracted_data

total_scraped_data = []
for year in range(2012, 2025):
    url = f"https://www.euro-jackpot.net/results-archive-{year}"
    scraped_data = scrape_historical_draws(url)
    total_scraped_data.extend(scraped_data)

data_list = []
for draw in total_scraped_data:
    numbers = draw['numbers'].split(', ')
    if len(numbers) == 7:
        new_row = {
            'Date': draw['date'],
            'st1': numbers[0], 'st2': numbers[1], 'st3': numbers[2],
            'st4': numbers[3], 'st5': numbers[4],
            'n1': numbers[5], 'n2': numbers[6]}
        data_list.append(new_row)

df = pd.DataFrame(data_list)
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
df.sort_values(by='Date', inplace=True)
df.reset_index(drop=True, inplace=True)
df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')

def scrape_winners_for_date(date):
    url = f'https://www.euro-jackpot.net/results/{date}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tbody = soup.find('tbody')
    prize_data = []
    for tr in tbody.find_all('tr'):
        prize_category = tr.find('td').text.strip()
        number_of_winners = tr.find_all('td')[-1].text.strip()
        prize_data.append({'Prize Category': prize_category, 'Number of Winners': number_of_winners})
    return prize_data

category_mapping = {
    'Match 5 and 2 Euro Numbers': '5and2',
    'Match 5 and 1 Euro Number': '5and1',
    'Match 5': '5',
    'Match 4 and 2 Euro Numbers': '4and2',
    'Match 4 and 1 Euro Number': '4and1',
    'Match 4': '4',
    'Match 3 and 2 Euro Numbers': '3and2',
    'Match 3 and 1 Euro Number': '3and1',
    'Match 2 and 2 Euro Numbers': '2and2',
    'Match 3': '3',
    'Match 1 and 2 Euro Numbers': '1and2',
    'Match 2 and 1 Euro Number': '2and1',
    'Total': 'Total'
}

for col in category_mapping.values():
    df[col] = 0

for index, row in df.iterrows():
    date = row['Date']
    winners_data = scrape_winners_for_date(date)
    for winner in winners_data:
        prize_category = winner['Prize Category']
        number_of_winners = winner['Number of Winners']
        column_name = category_mapping.get(prize_category)
        if column_name:
            df.at[index, column_name] = number_of_winners

prize_category_columns = list(category_mapping.values())

for column in prize_category_columns:
    df[column] = df[column].replace({',': '', '-': '0'}, regex=True)
    df[column] = df[column].astype(int)

df['Total'] = df[prize_category_columns[:-1]].sum(axis=1)
df.to_csv('data/historical_draws.csv')

import warnings
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

category_mapping = {
    'Match 5 and 2 Euro Numbers': '5and2',
    'Match 5 and 1 Euro Number': '5and1',
    'Match 5': '5',
    'Match 4 and 2 Euro Numbers': '4and2',
    'Match 4 and 1 Euro Number': '4and1',
    'Match 4': '4',
    'Match 3 and 2 Euro Numbers': '3and2',
    'Match 3 and 1 Euro Number': '3and1',
    'Match 2 and 2 Euro Numbers': '2and2',
    'Match 3': '3',
    'Match 1 and 2 Euro Numbers': '1and2',
    'Match 2 and 1 Euro Number': '2and1',
    'Match 1 and 1 Euro Number': '1and1',
    'Total': 'Total'
}

url = "https://www.euro-jackpot.net/results"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
link = soup.find('a', href=lambda href: href and '/results/' in href)

if link:
    first_result_link = link['href']
    new_url = "https://www.euro-jackpot.net" + first_result_link
    new_response = requests.get(new_url)
    new_soup = BeautifulSoup(new_response.text, 'html.parser')

numbers_list = new_soup.find('ul', class_='balls')
if numbers_list:
    numbers = [span.text for span in numbers_list.find_all('span')]
    if len(numbers) == 7:
        new_row = {
            'Date': first_result_link.split('/')[-1],
            'st1': numbers[0], 'st2': numbers[1], 'st3': numbers[2],
            'st4': numbers[3], 'st5': numbers[4],
            'n1': numbers[5], 'n2': numbers[6]}

tbody = new_soup.find('tbody')
prize_data = []
for tr in tbody.find_all('tr'):
    prize_category = tr.find('td').text.strip()
    number_of_winners = tr.find_all('td')[-1].text.strip()
    prize_data.append({'Prize Category': prize_category,
                       'Number of Winners': number_of_winners})

for prize in prize_data:
    category = prize['Prize Category']
    winners = prize['Number of Winners']
    mapped_category = category_mapping.get(category, 'Unknown Category')
    new_row[mapped_category] = winners

df = pd.read_csv('data/historical_draws.csv', index_col=0)
new_row_df = pd.DataFrame([new_row])

for column in new_row_df.columns[1:]:
    new_row_df[column] = new_row_df[column].replace({',': '', '-': '0'}, regex=True)
    new_row_df[column] = new_row_df[column].astype(int)

df = pd.concat([df, new_row_df], ignore_index=True)
df.to_csv('data/historical_draws.csv')


# ======================================================================
# Windows: Task Scheduler Example
# ======================================================================
"C:\Path\To\Python.exe" "D:\Scripts\update_lottery_dataset.py"

0 23:30 * * 2,5 /usr/bin/python3 /home/user/scripts/update_lottery_dataset.py

df[['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'En0', 'En1', 'En2']]=0

def co_common(st1, st2):

    return len(set(st1).intersection(set(st2)))

def count_common_values(df):

    counts = [0] * 6

    last_row = df.iloc[-1].tolist()

    for i in range(len(df) - 1):

        row = df.iloc[i].tolist()

        common = co_common(last_row, row)

        counts[common] += 1

    return counts

def count_common_values_n(df):

    counts = [0] * 3

    last_row = df.iloc[-1].tolist()

    for i in range(len(df) - 1):

        row = df.iloc[i].tolist()

        common = co_common(last_row, row)

        counts[common] += 1

    return counts

and this loop

for i in range(1, len(df)):

       df1=df_n.loc[ :i, 'st1':'st5']

       counts =count_common_values(df1)

       for j in range(len(counts)):

             df.loc[i,f'E{j}'] = counts[j]


        <w:t xml:space="preserve">

       df2=df_n.loc[ :i, 'n1':'n2']

       counts_n =count_common_values_n(df2)

       for j in range(len(counts_n)):

            df.loc[i,f'En{j}'] = counts_n[j]

# Saving the historical dataset in a csv file

df.to_csv('data/historical_draws.csv')

# Importing the required libraries

import create

import subprocess

import warnings

import pandas as pd

import numpy as np

import requests

import functions

from bs4 import BeautifulSoup

from datetime import datetime

pd.set_option('display.max_columns', 500)

pd.set_option('display.max_rows', 500)

# Winners category mapping

category_mapping = {

    'Match 5 and 2 Euro Numbers': '5and2',

    'Match 5 and 1 Euro Number': '5and1',

    'Match 5': '5',

    'Match 4 and 2 Euro Numbers': '4and2',

    'Match 4 and 1 Euro Number': '4and1',

    'Match 4': '4',

    'Match 3 and 2 Euro Numbers': '3and2',

    'Match 3 and 1 Euro Number': '3and1',

    'Match 2 and 2 Euro Numbers': '2and2',

    'Match 3': '3',

    'Match 1 and 2 Euro Numbers': '1and2',

    'Match 2 and 1 Euro Number': '2and1',

    'Match 1 and 1 Euro Number': '1and1',

    'Total': 'Total'

}

def co_common(st1, st2):

    return len(set(st1).intersection(set(st2)))

def count_common_values(df, new_row):

    counts = [0] * 6

    last_row = new_row.loc[0, :].tolist()

    for i in range(len(df)):

        row = df.iloc[i].tolist()

        common = co_common(last_row, row)

        counts[common] += 1

    return counts

def count_common_values_n(df, new_row):

    counts = [0] * 3

    last_row = new_row.loc[0, :].tolist()

    for i in range(len(df)):

        row = df.iloc[i].tolist()

        common = co_common(last_row, row)

        counts[common] += 1

    return counts

# date='15-10-2024' for specific date

#url = f'https://www.euro-jackpot.net/results/{date}'

#use the above lines if you want to download and update with draw from specific date

url = "https://www.euro-jackpot.net/results"

response = requests.get(url)

# Parsing the HTML content of the page

soup = BeautifulSoup(response.text, 'html.parser')

link = soup.find('a', href=lambda href: href and '/results/' in href)

if link:

    # If a matching link is found, extract the 'href' attribute

    first_result_link = link['href']

    new_url = "https://www.euro-jackpot.net"+first_result_link

    new_response = requests.get(new_url)

    new_soup = BeautifulSoup(new_response.text, 'html.parser')

    # Finding the <ul class="balls small"> for numbers

    numbers_list = new_soup.find('ul', class_='balls')

    if numbers_list:

        # Extracting all numbers from the list

        numbers = [span.text for span in numbers_list.find_all('span')]

        if len(numbers) == 7:

            new_row = {

                'Date': first_result_link.split('/')[-1],

                'st1': numbers[0],

                'st2': numbers[1],

                'st3': numbers[2],

                'st4': numbers[3],

                'st5': numbers[4],

                'n1': numbers[5],

                'n2': numbers[6]}

    tbody = new_soup.find('tbody')

    prize_data = []

    # Iterate through each <tr> within the <tbody>

    for tr in tbody.find_all('tr'):

        # Extracting the prize category from the first <td>

        prize_category = tr.find('td').text.strip()

        # Extracting the number of winners from the last <td>

        number_of_winners = tr.find_all('td')[-1].text.strip()

        # Storing the extracted data

        prize_data.append({'Prize Category': prize_category,

                          'Number of Winners': number_of_winners})

    for prize in prize_data:

        category = prize['Prize Category']

        winners = prize['Number of Winners']

        # Default to 'Unknown Category' if not found

        mapped_category = category_mapping.get(category, 'Unknown Category')

        new_row[mapped_category] = winners

df = pd.read_csv('data/historical_draws.csv', index_col=0)

# Convert the dictionary to a DataFrame first

new_row_df = pd.DataFrame([new_row])

for column in new_row_df.columns[1:]:

    new_row_df[column] = new_row_df[column].replace({',': '', '-': '0'}, regex=True)

    new_row_df[column] = new_row_df[column].astype(int)

# add to new row the results of the count common numbers columns and their values

new_row_df[['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'En0', 'En1', 'En2']] = 0

new_row_df[['E0', 'E1', 'E2', 'E3', 'E4', 'E5']] = count_common_values(

    df[['st1', 'st2', 'st3', 'st4', 'st5']], new_row_df[['st1', 'st2', 'st3', 'st4', 'st5']])

new_row_df[['En0', 'En1', 'En2']] = count_common_values_n(

    df[['n1', 'n2']], new_row_df[['n1', 'n2']])

# Use pd.concat to append the new row DataFrame to the existing DataFrame

df = pd.concat([df, new_row_df], ignore_index=True)

print(df)

df.to_csv('data/historical_draws.csv')
