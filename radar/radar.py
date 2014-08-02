import logging
import json
import urllib.parse
import urllib.request
import re


URL_IMAKOKO_LATEST = "http://imakoko-gps.appspot.com/api/latest"
URL_QUERY_ADDRESS = "http://geoapi.heartrails.com/api/json"


def get_user_location(user):
    url = URL_IMAKOKO_LATEST + "?user={}".format(user)
    latest = urllib.request.urlopen(url).read()
    # logging.debug(latest)

    decoded = latest.decode('utf-8')
    # logging.debug(decoded)

    cleansed = re.sub(r'^\(|\)$', '', decoded)
    # logging.debug(sanitized)

    latest_obj = json.loads(cleansed)
    logging.debug("target user location:{}".format(latest_obj))

    return latest_obj


def get_address(latitude, longitude):
    address_obj = None

    try:
        url = URL_QUERY_ADDRESS + "?method=searchByGeoLocation&x=" + longitude + "&y=" + latitude
        logging.debug("trying to resolve address:{}".format(url))
        address = urllib.request.urlopen(url).read()
        decoded = address.decode('utf-8')
        address_obj = json.loads(decoded)['response']['location'][0]
        logging.debug("resolved address:{}".format(address_obj))
    except Exception as error:
        logging.error("failed to resolve address:{}".format(error))

    return address_obj
