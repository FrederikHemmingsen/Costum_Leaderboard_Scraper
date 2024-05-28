import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template
import schedule
import time
from threading import Thread

app = Flask(__name__)

def scrape_data():
    url = 'https://www.velocidrone.com/weekly_time_trial/current'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    return df

def filter_danish_times(df):
    danish_times = df[df['Country'] == 'Denmark']
    return danish_times

def save_filtered_data():
    data = scrape_data()
    danish_times = filter_danish_times(data)
    danish_times.to_csv('danish_times.csv', index=False)

@app.route('/')
def index():
    df = pd.read_csv('danish_times.csv')
    data = df.to_dict(orient='records')
    return render_template('index.html', data=data)

def schedule_scraping():
    schedule.every().hour.do(save_filtered_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    save_filtered_data()
    scraper_thread = Thread(target=schedule_scraping)
    scraper_thread.daemon = True
    scraper_thread.start()
    app.run(debug=True, host='0.0.0.0')
