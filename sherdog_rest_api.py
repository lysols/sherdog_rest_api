#!/usr/bin/python2.7

from flask import Flask
from lxml import html
import urllib2
import json

app = Flask(__name__)


@app.route('/mma/events', methods=['GET'])
def get_upcoming_mma_events():
    """
    :return: calls construct_events_json and returns json of upcoming mma events via GET
    """
    json_to_return = construct_events_json()
    return json_to_return


@app.route('/mma/event/<int:post_id>', methods=['GET'])
def get_mma_card_details(post_id):
    """
    :param post_id: the event_id json field as returned by the mma/events REST endpoint
    :return: returns a string of the fights on the MMA event, seperated by commas, via GET
    """
    upcoming_events_json = json.loads(construct_events_json())
    for x in upcoming_events_json["mma_events"]:
        if upcoming_events_json["mma_events"][x]["event_id"] == post_id:
                # big time hackery going on here, needs redone to return some sort of json
                requested_events_url = upcoming_events_json["mma_events"][x]["event_url"]
                print requested_events_url
                page_data_tree = request_website_data(requested_events_url)
                fight_card = page_data_tree.xpath(".//meta[@itemprop='name']/@content")
                return upcoming_events_json["mma_events"][x]["event_name"] + " - " + ', '.join(fight_card)


def request_website_data(target_url):
        """
        :return: Queries a website to return the data from it
        """
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(target_url).read()
        page_data_tree = html.fromstring(response)
        return page_data_tree


def sherdog_website_parser(page_data_tree, value1, value2, value3, value4):
        """
        :param page_data_tree: the HTML data to be parsed
        :param value1: xpath value 1, e.g. "span" or "a"
        :param value2: xpath value 2, e.g. "itemprop"
        :param value3: xpath value 3, e.g. "location" or "url"
        :param value4: xpath value 4, e.g. "text" or "context"
        :return: uses list comprehension to return a list of ten matches
        """
        construct_parse_string = './/%s[@%s="%s"]/%s' % (value1, value2, value3, value4)
        parsed_data = page_data_tree.xpath(construct_parse_string)
        return [parsed_data[i] for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]


def construct_events_json():
        """
        :return: returns a json  with event_id, event_name, event_location, event_time, and event_sherdog_events_url fields
        """

        target_url = "http://www.sherdog.com/events"
        parser_data_tree = request_website_data(target_url)
        events_list = sherdog_website_parser(parser_data_tree, "a", "itemprop", "url", "text()")
        events_location_list = sherdog_website_parser(parser_data_tree, "span", "itemprop", "location", "text()")
        events_url_list = sherdog_website_parser(parser_data_tree, "a", "itemprop", "url", "@href")
        events_times_list = sherdog_website_parser(parser_data_tree, "meta", "itemprop", "startDate", "@content")

        events_dict = {}
        events_dict['mma_events'] = {}
        event_id_build_counter = 1
        generic_build_counter = 0

        for event_item in events_list:
                events_dict['mma_events'][event_item] = {}
                events_dict['mma_events'][event_item]["event_id"] = event_id_build_counter
                events_dict['mma_events'][event_item]["event_name"] = events_list[generic_build_counter]
                events_dict['mma_events'][event_item]["event_location"] = events_location_list[generic_build_counter]
                events_dict['mma_events'][event_item]["event_time"] = events_times_list[generic_build_counter].split("T")[0]
                events_dict['mma_events'][event_item]["event_url"] = target_url + events_url_list[generic_build_counter]
                event_id_build_counter += 1
                generic_build_counter += 1

        return json.dumps(events_dict)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

