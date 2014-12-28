#!/usr/bin/python2.7

from flask import Flask
import urllib2
from lxml import html
import json

app = Flask(__name__)

@app.route('/mma/events', methods=['GET'])
def get_tasks():
    json_to_return = construct_events_json()
    return json_to_return

@app.route('/mma/event/<int:post_id>', methods=['GET'])
def show_card(post_id):
    upcoming_events_json = json.loads(construct_events_json())
    for x in upcoming_events_json["mma_events"]:
	if upcoming_events_json["mma_events"][x]["event_id"] == post_id:
		requested_event_url = upcoming_events_json["mma_events"][x]["event_url"]
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		response = opener.open(requested_event_url).read()
		tree = html.fromstring(response)
		fight_card = tree.xpath(".//meta[@itemprop='name']/@content")
		return upcoming_events_json["mma_events"][x]["event_name"] +" - " + ', '.join(fight_card)
	

url = 'http://www.sherdog.com/events'

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
response = opener.open(url).read()
tree = html.fromstring(response)

mma_events = tree.xpath('//a[@itemprop="url"]/text()')
mma_event_locations = tree.xpath('//span[@itemprop="location"]/text()')
mma_event_times = tree.xpath('//span[@class="date"]/text()')

events_times_list = []
for meta in tree.cssselect('meta'):
	prop = meta.get('itemprop')
	if prop == 'startDate':
		events_times_list.append(meta.get('content'))

events_url_list = []
for a in tree.cssselect('a'):
        prop = a.get('itemprop')
        if prop == 'url':
                events_url_list.append(a.get('href'))

events_list = mma_events
events_list = [events_list[i] for i in [0,1,2,3,4,5,6,7,8,9]]

events_location_list = mma_event_locations
events_location_list = [events_location_list[i] for i in [0,1,2,3,4,5,6,7,8,9]]

events_times_list = [events_times_list[i] for i in [0,1,2,3,4,5,6,7,8,9]]


def construct_events_json():	
	events_dict = {}
	events_dict['mma_events'] = {}
	build_counter = 0
	for event_item in events_list:
		events_dict['mma_events'][event_item] = {}
		events_dict['mma_events'][event_item]["event_id"] = build_counter
		events_dict['mma_events'][event_item]["event_name"] = events_list[build_counter]
		events_dict['mma_events'][event_item]["event_location"] = events_location_list[build_counter]
		events_dict['mma_events'][event_item]["event_time"] = events_times_list[build_counter].split("T")[0]
		events_dict['mma_events'][event_item]["event_url"] = url + events_url_list[build_counter]
		build_counter = build_counter + 1
	return json.dumps(events_dict)





if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
		
