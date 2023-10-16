import os
import csv
import random
import time
from datetime import datetime
from colorama import Fore, Style
import re

# Constants
DEBUG = "DEBUG"
ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"
SUCCESS = "SUCCESS"
OOS = "OOS"

class UnrecoverableAccountException(Exception):
    pass

# Default user agent and headers
default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'
default_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "dnt": "1",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Avast Secure Browser";v="101"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": default_ua,
}

def defaultHeaders():
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "dnt": "1",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Avast Secure Browser";v="101"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": 'document',
        "sec-fetch-mode": 'navigate',
        "sec-fetch-site": 'none',
        "sec-fetch-user": '?1',
        "upgrade-insecure-requests": '1',
        "user-agent": default_ua,
    }

def get_main_domain_from_url(event_url):
    try:
        host = event_url.split("//")[-1].split("/")[0]
        host_split_items = host.split(".")
        return f"{host_split_items[-2]}.{host_split_items[-1]}"
    except Exception as e:
        raise e

def site_main_header():
    try:
        new_headers = defaultHeaders()
        new_headers["referer"] = 'https://www.ticketmaster.com/'
        return new_headers
    except Exception as e:
        raise e

def get_custom_headers(additional_headers, type="site"):
    try:
        new_headers = defaultHeaders() if type != "site" else site_main_header()
        new_headers.update(additional_headers)
        return new_headers
    except Exception as e:
        raise e

def print_log(message, type=DEBUG, thread_index=""):
    try:
        current_time = datetime.utcnow()
        print_message = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] [Thread-{thread_index}] [{type}] {message}"

        # log_file_path = os.path.join(os.path.dirname(__file__), './../logs/main.log')
        # with open(log_file_path, "a+") as log_file:
        #     log_file.write(f"{print_message}\n")

        log_level = {
            DEBUG: lambda msg: print(Fore.MAGENTA + Style.BRIGHT + msg),
            INFO: lambda msg: print(Fore.BLUE + Style.BRIGHT + msg),
            OOS: lambda msg: print(Fore.CYAN + Style.BRIGHT + msg),
            WARNING: lambda msg: print(Fore.YELLOW + Style.BRIGHT + msg),
            ERROR: lambda msg: print(Fore.RED + Style.BRIGHT + msg),
            SUCCESS: lambda msg: print(Fore.GREEN + Style.BRIGHT + msg)
        }
        log_level.get(type, lambda msg: print(msg))(print_message)
    except Exception as e:
        raise e

def sleep_ms(ms):
    print_log(f"Waiting for [{ms}] milliseconds.")
    time.sleep(ms / 1000.0)

def get_random_item(items):
    try:
        if not items:
            return None
        return random.choice(items)
    except Exception as e:
        raise e

def get_proxy():
    try:
        proxy_data = ""
        with open("proxies.txt", "r") as proxy_file:
            proxy_data = proxy_file.read()

        proxy_list = proxy_data.replace('"', "").replace("\r", "").split("\n")
        proxy = None
        while not proxy or len(proxy) < 4:
            proxy = random.choice(proxy_list).split(":")

        print_log(f"Got proxy: {proxy}")
        return proxy
    except Exception as e:
        raise e

def get_proxy_url():
    try:
        if os.environ.get("PROXY") == "local":
            return "http://127.0.0.1:8080"
        else:
            proxy = get_proxy()
            return f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
    except Exception as e:
        raise e


def write_queue_log(data):
    csv_file_path = os.path.join(os.path.dirname(__file__), './../logs/queueLog.csv')

    if not os.path.exists(csv_file_path):
        header = ['Timestamp', 'EventId', 'QueueNumber', 'AheadOfYou', 'Email']
        with open(csv_file_path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

    with open(csv_file_path, "a", newline='') as csv_file:
        writer = csv.writer(csv_file)
        for item in data:
            writer.writerow(item)

    print_log('Data inserted into CSV file.')

def extract_json_string(html, start_text_with_char):
    try:
        if html is None:
            return None

        opening_bracket_char = start_text_with_char[-1]

        closing_bracket_char = "}" if opening_bracket_char == "{" else "]"

        start_index = html.find(start_text_with_char)
        if start_index < 0:
            print(f"Text [{start_text_with_char}] is not found in the specified HTML. Exiting")
            return None

        first_bracket_position = start_index + start_text_with_char.find(opening_bracket_char)

        current_pos = first_bracket_position + 1
        open_brackets = 1
        close_brackets = 0

        while open_brackets > close_brackets and current_pos < len(html):
            if html[current_pos] == opening_bracket_char:
                open_brackets += 1
            elif html[current_pos] == closing_bracket_char:
                close_brackets += 1
            current_pos += 1

        result = None if open_brackets != close_brackets else html[first_bracket_position:current_pos]

        return result
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")
        return None

def get_item_with_key_containing_text(items, search_text):
    try:
        if not items:
            return None

        for item in items:
            for key, value in item.items():
                if search_text.lower() in key.lower():
                    return item

        return None
    except Exception as e:
        raise e

def extract_token(data):
    token_regexp = r'<input name="__RequestVerificationToken" type="hidden" value="(.+?)" /></form>'
    match = re.search(token_regexp, data)
    
    if match:
        return match.group(1)  # The token
    return None

# for extracting the values in the signin callback
def extract_input_fields(data):
    """
    Extracts all input fields from the provided HTML content using regex.

    Args:
    - data (str): The HTML content to extract input fields from.

    Returns:
    - dict: A dictionary containing the names and values of the input fields.
    """
    input_regexp = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']+)["\'][^>]*>'
    matches = re.findall(input_regexp, data)

    return {name: value for name, value in matches}
