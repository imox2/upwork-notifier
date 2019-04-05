#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 17:25:35 2019

@author: imox
"""

from bs4 import BeautifulSoup as bs #to parse the html we get , to extract the data we need
from selenium import webdriver #will give us a browser which we control by code and go to the desired page and get html
import datetime  
from slackclient import SlackClient


setting = {}
setting['chrome_path'] = "/Users/imox/ahlat/webdriverio-test/chromedriver";

def get_time_data(url):
	browser = webdriver.Chrome(setting['chrome_path']);
	browser.get(url_to_hit)
	html=browser.page_source


	soup = bs(html)

	final_time_list = []

	time_list = soup.findAll('time');

	for time_tag in time_list:
	    temp_dict = {}

	    temp_dict['data-eo-relative'] = time_tag['data-eo-relative']
	    temp_dict['datetime'] = time_tag['datetime']
	    temp_dict['datetext'] = time_tag.text
	    final_time_list.append(temp_dict);

	browser.close();

	return final_time_list;

def find_user_id_based_on_email(sc,email="talhaanwar.anwar@gmail.com"):
        users = sc.api_call('users.list')
        users = users['members']
        user_found = 0

        for user in users:
            if 'email' in user['profile']:
                if user['profile']['email']==email:
                    user_found = user['id']
                    break
                
        return user_found
    
def send_message_to_user(msg):
    token = "xoxb-368337695024-599092697542-H9xXwC8Vwqp3uFDrljeSUrZ8"
    sc = SlackClient(token) 
    user_id = find_user_id_based_on_email(sc)
    print("Got user id:"+user_id)
    
    if user_id!=0:
        channel_info = sc.api_call('im.open', user=user_id)
        channel_id = channel_info['channel']['id']
        print("Got channel id:"+channel_id)
        sc.api_call("chat.postMessage", as_user="true:", channel=channel_id, text=msg)

def get_latest_post(time_data,time=60):
    
    number_of_found_records = 0;
    current_gmt_time = datetime.datetime.utcnow()
    gmt_time_before = current_gmt_time - datetime.timedelta(minutes = time)
    
    for time_dict in time_data:
        
        datetime_obj = datetime.datetime.strptime(time_dict['datetime'], "%Y-%m-%dT%H:%M:%S+00:00")
        
        if gmt_time_before<=datetime_obj<current_gmt_time:
            number_of_found_records+=1
            
    return number_of_found_records
        
    
    
##main callers##



url_to_hit = "https://www.upwork.com/o/jobs/browse/?q=scraping&sort=recency"
time_data = get_time_data(url_to_hit)

print(time_data)
msg = "";
number_of_post = 0;
send_msg_to_slack = 0;

if len(time_data)>0:
    number_of_post = get_latest_post(time_data,120)
    if number_of_post > 0:
        msg = "Upwork received "+str(number_of_post)+" new queries for scraping"
        send_msg_to_slack = 1;

else:
    msg = "Upwork notifier seems broken and getting no data. Kindly check out the script once"
    send_msg_to_slack = 1;
    

if send_msg_to_slack==1:
    send_message_to_user(msg)






