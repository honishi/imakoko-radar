import os
import logging
import logging.config
import configparser
import time


import radar
from twython import Twython


CHECK_INTERVAL = 60
RESTART_INTERVAL = 60
CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) + "/main.configuration"


def init_logger():
    logging.config.fileConfig(CONFIG_FILE)
    logging.info("logger initialized.")


def get_configuration():
    logging.info("using config file: " + CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    target_users = config.get('imakoko', 'target_users').split(',')

    configurations = []

    for target_user in target_users:
        user_config = {}
        user_config['user'] = target_user
        user_config['message'] = config.get(target_user, 'message')
        user_config['imakoko_url'] = config.get(target_user, 'imakoko_url')
        user_config['consumer_key'] = config.get(target_user, 'consumer_key')
        user_config['consumer_secret'] = config.get(target_user, 'consumer_secret')
        user_config['access_key'] = config.get(target_user, 'access_key')
        user_config['access_secret'] = config.get(target_user, 'access_secret')

        configurations.append(user_config)
        logging.debug("loaded configuration:{}".format(user_config))

    return configurations


def tweet(configuration, location):
    address = radar.get_address(location['lat'], location['lon'])

    address_info = None
    if address is not None:
        address_info = "({}{}{}付近)".format(
            address['prefecture'], address['city'], address['town'])

    message = "{} {} {}".format(configuration['message'],
                                address_info,
                                configuration['imakoko_url'])

    try:
        twitter = Twython(configuration['consumer_key'],
                          configuration['consumer_secret'],
                          configuration['access_key'],
                          configuration['access_secret'])
        twitter.update_status(status=message)
    except Exception as error:
        logging.error("caught exception in tweet:{}".format(error))


def main():
    init_logger()
    configurations = get_configuration()

    while True:
        try:
            previous_location = {}
            initial_check = True

            while True:
                for configuration in configurations:
                    user = configuration['user']
                    logging.info("*** checking for {}".format(user))

                    locations = radar.get_user_location(user)['points']
                    logging.info("locations:{}".format(locations))

                    location = None
                    if 0 < len(locations):
                        location = locations[0]

                    # debug
                    """
                    if initial_check:
                        location = None
                    """

                    if not initial_check:
                        if previous_location[user] is None and location is not None:
                            # detected user activity start
                            tweet(configuration, location)

                    previous_location[user] = location

                if initial_check:
                    initial_check = False

                logging.info("*** sleeping for {} seconds...".format(CHECK_INTERVAL))
                time.sleep(CHECK_INTERVAL)
        except Exception as error:
            logging.error("caught exception in main loop:{}".format(error))
            logging.debug("restart loop after {} seconds".format(RESTART_INTERVAL))
            time.sleep(RESTART_INTERVAL)


if __name__ == '__main__':
    main()
