import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from modules.queue import check_and_process_queue
import time  # Import the time module

import urllib3
from selenium.webdriver.common.keys import Keys

urllib3.disable_warnings()

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def fill_out_form_and_process_queue(driver, session, q_page_url, res_url):
    """Fills out the form and then processes the Queue-It page.

    Args:
        driver (webdriver.Firefox): The Selenium driver to use.
        session (requests.Session): The requests session to use.
        q_page_url (str): The URL of the Queue-It page.
        res_url (str): The URL of the response.

    Returns:
        None
    """

    # Navigate to the Queue-It page
    driver.get(q_page_url)

    try:
        # Click the "Create your UEFA account" link using By.LINK_TEXT
        create_account_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Create your UEFA account"))
        )
        create_account_link.click()
        time.sleep(1)
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-75074230944436030"]'))
        )
        email_input.send_keys("fergentius@test1.com")

        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-password-59919533498235100"]'))
        )
        password_input.send_keys("PasswordTest23%")

        firstName_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-130722358975432270"]'))
        )
        firstName_input.send_keys("Fergentius")

        lastName_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-30497114450394400"]'))
        )
        lastName_input.send_keys("Rosales")

        DD_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-88315185881230510"]'))
        )
        DD_input.send_keys("04")
        MM_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-105406014904922500"]'))
        )
        MM_input.send_keys("11")
        YY_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gigya-textbox-32538633360993784"]'))
        )
        YY_input.send_keys("1986")
        # Locate the checkbox element inside the div by class name

        # Find the <span> element by its text content

        checkbox = driver.find_element(By.XPATH, '//*[@id="gigya-register-form"]/div[1]/div[11]/label')

        driver.execute_script('arguments[0].click();', checkbox)

        checkbox = driver.find_element(By.XPATH, '//*[@id="gigya-register-form"]/div[1]/div[12]/label')

        # Check the checkbox
        checkbox.click()

        checkbox = driver.find_element(By.XPATH, '//*[@id="gigya-register-form"]/div[1]/div[13]/label')

        # Check the checkbox
        checkbox.click()

        dropdown_input = driver.find_element(By.XPATH,
                                             '//*[@id="gigya-register-form"]/div[1]/div[14]/div/div/div/input')

        # Click the input element to open the dropdown
        dropdown_input.click()

        # Locate the first option and click it
        first_option = driver.find_element(By.XPATH, '//li[@role="option"][1]')
        first_option.click()
        #form is filled out let click the link
        # Find the element by class name
        input_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="Create account"]'))
        )

        input_element.click()

        time.sleep(10)

        # Get the HTML of the Queue-It page

        driver.switch_to.frame(0)
        iframe_content = driver.page_source
        driver.switch_to.frame(0)

        queue_page_html = iframe_content

        #driver.switch_to.default_content()
        # Process the Queue-It page
        return queue_page_html

    except Exception as e:
        print(f"Error filling out form and processing queue: {str(e)}")

def test():
    threading_index = 1
    session = requests.session()
    proxies = {
        "https": "http://LemonClub3yOpDG4s-country-GB-session-LemonClub03120818:GLzo5FvI@packetstream.lemonclub.io:31112",
    }
    session.proxies = proxies

    # Get the path to the GeckoDriver executable
    geckodriver_path = f"{os.getcwd()}/geckodriver"

    # Create a new Service object for GeckoDriver
    service = Service(executable_path=geckodriver_path)

    # Create a new WebDriver object for Firefox
    driver = webdriver.Firefox(service=service)

    try:

        result = fill_out_form_and_process_queue(driver, session,
                                        q_page_url="https://idpassets.uefa.com/saml/ticket-login.html?mode=login&samlContext=eu1_8352704_45292c49-2da9-4298-ad06-91cb8475b6a6&spName=EURO%202024%20Lottery&locale=en",
                                        res_url="https://www.uefa.com/euro-2024/tickets/")
        q_page_url = "https://idpassets.uefa.com/saml/ticket-login.html?mode=login&samlContext=eu1_8352704_45292c49-2da9-4298-ad06-91cb8475b6a6&spName=EURO%202024%20Lottery&locale=en",
        res_url="https://www.uefa.com/euro-2024/tickets/"

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


        _ = check_and_process_queue(threading_index, session, result, q_page_url, res_url, 0)
        print(
            f"QueueITAccepted-SDFrts345E-V3_liverpoolfcmatchtixq={session.cookies.get('QueueITAccepted-SDFrts345E-V3_liverpoolfcmatchtixq')}")

    except Exception as e:
        print(f"Error in test: {e}")
    finally:
        driver.quit()


if __name__ == '__main__':
    test()
