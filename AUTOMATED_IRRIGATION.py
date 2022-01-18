from bs4 import BeautifulSoup as bs
import requests
import random
from time import sleep
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import timeit

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"
min=1 #Default it has to be 60
hrs=1 #Default it has to be 3600
req=40 #Depens on crop Planted

def get_weather_data(url):
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(url)
    global temp, rain, humid, region1,dayhour
    # create a new soup
    soup = bs(html.text, "html.parser")
    region1 = soup.find("div", attrs={"id": "wob_loc"}).text
    # extract temperature now
    temp = soup.find("span", attrs={"id": "wob_tm"}).text
    # get the day and hour now
    dayhour = soup.find("div", attrs={"id": "wob_dts"}).text
    # get the precipitation
    rain = soup.find("span", attrs={"id": "wob_pp"}).text
    # get the % of humidity
    humid = soup.find("span", attrs={"id": "wob_hm"}).text
    
def getsoilmoisture():
    global soilmoist
    soilmoist = random.randint(20,60)
    return soilmoist

def publish(time,time1):
    host='demo.thingsboard.io'
    access_token='HlqYwKsrsx6cU79Qlnn1'
    sensor_data={}
    for i in range(10): 
     client=mqtt.Client()
     client.username_pw_set(access_token)
     sensor_data['Last Watered']=time
     sensor_data['Watered Time']=time1
     client.connect(host,1883,100)
     client.publish('v1/devices/me/telemetry',json.dumps(sensor_data),1)
     client.disconnect()

def start():
        time=0
        global soilmoist
        if(humid<20 or temp>40):
            sleep(10*min)
        if(rain>80):
            return 
        else:
         print('start watering')
         start = timeit.default_timer()
         while(soilmoist<req):
            sleep(min*10)
            soilmoist=getsoilmoisture()
         print('stop watering')
         stop = timeit.default_timer()
         time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
         print("Watered At:", time)
         time1 = int(stop - start)
         print('watered for',time1)
         publish(time,time1)

           

if __name__ == "__main__":
   URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
   region = 'kadiri'
   URL += f"+{region}"
    # get data
   while(True):
    get_weather_data(URL)
    getsoilmoisture()
    # print data
    temp=int(temp)
    rain=int(rain[:-1])
    humid=int(humid[:-1])
    print("\nRegion:",region1)
    print("Local Time:",dayhour)
    print("Temperature:",temp)
    print("Precipitation:", rain)
    print("Humidity:", humid)
    print("Soil Moisture:", soilmoist)
    if(soilmoist<req):
         start()
    sleep(4*hrs)
    

   

