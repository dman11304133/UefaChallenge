import json
from bs4 import BeautifulSoup
import requests
import urllib3
from modules.queue import check_and_process_queue
from modules.CapSolver import CapSolver
import multiprocessing
from faker import Faker
fake = Faker()
urllib3.disable_warnings()
import random
"""
This code generates a valid liverpool queueit token, that allows us to scrape the site.
use this as an initial building block to build your account generator
for proxies, see proxies.txt
for datadome cookie api: https://takionapi.tech/incapsula/sensor/www.eticketing.co.uk?api_key=TAKION_API_1QUY8PC5G3FY9FST

to get you started, i would initialize proxies with session using this:
def initialize_session(proxy):
    try:
        session = requests.Session()
        update_session_proxy(session, proxy)
        return session
    except Exception as e:
        print(f"Error initializing session: {e}")
        return None
"""


def make_registration_request(session, regToken):
    url = 'https://idp.uefa.com/accounts.register'
    BrowserAgents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit / 536.30.1 (KHTML, like Gecko) Version / 6.0.5 Safari / 536.30.1',
        'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit / 536.29.13 (KHTML, like Gecko) Version / 6.0.4 Safari / 536.29.13',
        'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit / 534.57.2 (KHTML, like Gecko) Version / 5.1.7 Safari / 534.57.2',
        'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit / 536.26.17 (KHTML, like Gecko) Version / 6.0.2 Safari / 536.26.17',
        'Mozilla / 5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit / 124 (KHTML, like Gecko) Safari / 125',
    ]

    cookies_str = "; ".join(f"{cookie.name}={cookie.value}" for cookie in session.cookies)

    headers = {
        'authority': 'idp.uefa.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookies_str,  # Replace with your actual cookie value
        'origin': 'https://idpassets.uefa.com',
        'referer': 'https://idpassets.uefa.com/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': 'Android',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random.choice(BrowserAgents),  # Replace with your actual user-agent
    }

    print(headers);
    capsolver = CapSolver()

    captcha_solution = None
    while captcha_solution is None:
        # Use the solve_recaptcha method to solve the reCAPTCHA
        capchaUrl = "hhttps://idpassets.uefa.com/saml/ticket-login.html?mode=login&samlContext=eu1_8352704_4e13e8de-4267-44bf-9839-ae3772b53bc8&spName=EURO%202024%20Lottery&locale=en"
        site_key = "6LehfZUbAAAAAJhue_6BVqqxLulLiXLP0rEgpdRH"
        captcha_solution = capsolver.solve_recaptcha(page_url=url, site_key=site_key)
        if captcha_solution is None:
            print("Failed to solve reCAPTCHA. Retrying...")
    profile_data = {
        'firstName': fake.first_name(),
        'lastName': fake.last_name(),
        'birthDay': fake.day_of_month(),
        'birthMonth': fake.month(),
        'birthYear': fake.random_int(min=1960, max=2005),
        'email': fake.email(),
    }
    data = {
        'email': fake.email(),
        'password': fake.password(),
        'regToken': regToken,  # Use the regToken variable provided
        'regSource': 'UEFA Ticketing Web',
        'profile': json.dumps(profile_data),
        'preferences': '{"terms":{"uefacom":{"term_1":{"isConsentGranted":true}}},"nationalFootballAssociation":{"consent_1":{"isConsentGranted":true,"entitlements":"BLR"}}}',
        'displayedPreferences': '{"terms.uefacom.term_1":{"docVersion":1,"docDate":null},"nationalFootballAssociation.consent_1":{"docVersion":1,"docDate":null}}',
        'data': '{"ticketing":{"ticketsDeliveryEmail":"fergentius@gmail2.com"},"subscriptions":{"subscribeToAll":true},"accounts":{"acquisition":{"regSource":"UEFA Ticketing Web","regDate":"2023-10-16T13:51:46.406Z","regCampaign":"https://idpassets.uefa.com/saml/ticket-login.html?spName=EURO%202024%20Lottery","regRedirectURL":"https://idpassets.uefa.com/saml/ticket-login.html?spName=EURO%202024%20Lottery"}}}',
        'captchaType': 'invisible',
        'captchaToken': captcha_solution.get('gRecaptchaResponse'),
        'lang': 'en',
        'finalizeRegistration': 'true',
        'targetEnv': 'jssdk',
        'sessionExpiration': '0',
        'include': 'profile,data,emails,loginIDs,subscriptions,preferences',
        'includeUserInfo': 'true',
        'subscriptions': '{"newsletters":{"UNTFNews":{"email":{"isSubscribed":true}},"UEFATicketing":{"email":{"isSubscribed":true}},"UELNews":{"email":{"isSubscribed":true}},"UCLNews":{"email":{"isSubscribed":true}},"UEFANews":{"email":{"isSubscribed":true}},"GamingAll":{"email":{"isSubscribed":true}},"UEFAWomenFootball":{"email":{"isSubscribed":true}}},"sponsors":{"all":{"email":{"isSubscribed":true}}}}'
    }
    json_data = json.dumps(data, indent=4)

    # Print the generated JSON data
    print(json_data)
    response = session.post(url, headers=headers, data=data, verify=False)
    print(response.text)

    if response.status_code == 200:
        print(f"Response Code - {response.status_code}")
        print(f"Account created: {fake.email()}:{fake.password()}")
        with open('accounts.txt', 'a') as accounts_file:
            accounts_file.write(f"{fake.email()}:{fake.password()}\n")
    else:
        print(response.text)
        print(f"Failed to create account for {fake.email()}")

def test():
    threading_index = 1
    session = requests.session()
    proxies = {
        "https": "http://LemonClub3yOpDG4s-country-GB-session-LemonClub03120818:GLzo5FvI@packetstream.lemonclub.io:31112",
    }
    session.proxies = proxies
    q_page_url = "https://liverpoolfc.queue-it.net/softblock/?c=liverpoolfc&e=liverpoolfcmatchtixq&t=https%3A%2F%2Fticketing.liverpoolfc.com%2Fen-gb%2Fcategories%2Fhome-tickets&cid=en-GB&enqueuetoken=eyJ0eXAiOiJRVDEiLCJlbmMiOiJBRVMyNTYiLCJpc3MiOjE2OTU2NTIxMTkxMDIsImV4cCI6MTY5NTY1MjM1OTEwMiwidGkiOiJjMTE5YzJiYS1mNjcxLTRlMGQtODdjNy0zMTZkMjNmNzQ4OTYiLCJjIjoibGl2ZXJwb29sZmMiLCJlIjoibGl2ZXJwb29sZmNtYXRjaHRpeHEiLCJpcCI6IjEwLjMzLjIzMy41NiJ9.2QMeptN9YeXKKUph9eWYuw.V3mPsdM5ZYQeu8BHI4VS6jfTVe-LUH0aXbMc1yIzz-I&rticr=0"
    # q_page_url = "https://ticketmastersportuk.queue-it.net/softblock/?c=ticketmastersportuk&e=arsenal&t=https%3A%2F%2Fwww.eticketing.co.uk%2Farsenal%2FAuthentication%2FCallback%2FAfterSignInInternalPostback%3FreturnUrl%3D%252Farsenal%252F&cid=en-GB&rticr=0"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "te": "trailers"
    }
    res = session.get(q_page_url, headers=headers, verify=False)
    _ = check_and_process_queue(threading_index, session, res.text, q_page_url, res.url, 0)
    print(f"QueueITAccepted-SDFrts345E-V3_liverpoolfcmatchtixq={session.cookies.get('QueueITAccepted-SDFrts345E-V3_liverpoolfcmatchtixq')}")

    # Make a request to the URL
    response = session.get(
        "https://idp.uefa.com/accounts.initRegistration?APIKey=3_WhoQ5kSze6W6uz1oBpBfDNQkMRYi8y2RC32TGpY6XKRxlOeTTLjY-qIrnw4hJaLV&source=showScreenSet&sdk=js_canary&authMode=cookie&pageURL=https%3A%2F%2Fidpassets.uefa.com%2Fsaml%2Fticket-login.html%3Flocale%3Den%26mode%3Dlogin%26samlContext%3Deu1_8352704_4e13e8de-4267-44bf-9839-ae3772b53bc8%26spName%3DEURO%25202024%2520Lottery&sdkBuild=15468&format=json",
        headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()

        # Extract the regToken value
        regToken = response_json.get("regToken")

        # Check if regToken is not None
        if regToken is not None:
            # Store the regToken in a variable for further use
            your_variable = regToken
            result = make_registration_request(session, regToken)
            if result is not None:
            # Process the result as needed
                 print(result)
            else:
                print("Registration request failed")

        else:
            print("regToken not found in the response")
    else:
        print(f"Request to URL failed with status code: {response.status_code}")
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")



if __name__ == '__main__':
    #test()
    # Set the desired number of accounts
    processes = []

    # Create a separate process for each account
    for _ in range(1):
        process = multiprocessing.Process(target=test())
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()



