import json
import time
import urllib
import re
from urllib.parse import unquote
from modules import challenges_solver, utils
from modules.utils import DEBUG, INFO

configStartTexts = [
    "window.queueViewModel = new QueueIt.Queue.InQueueView({",
    "var queueViewModel = new QueueIt.Queue.SoftblockViewModel({"
]

def is_present(index, html_src):
    try:
        if html_src is None:
            return False

        result = "id=\"hlThisIsQueueIt\"" in html_src \
                 or "<title>Queue-it</title>" in html_src \
                 or "<title>reCAPTCHA</title>" in html_src \
                 or "queueit.js" in html_src \
                 or any(config_start_text in html_src for config_start_text in configStartTexts)

        utils.print_log(f"QueueIt check result is [{result}]", DEBUG, index)

        return result
    except Exception as e:
        raise e

def get_config(html_src):
    try:
        if not html_src:
            return None
        config_start_text = next((text for text in configStartTexts if text in html_src), None)
        if not config_start_text:
            return None

        config_json = utils.extract_json_string(html_src, config_start_text)
        if not config_json:
            return None
        config_json = config_json.replace("'", "\"")

        lines = config_json.split("\n")

        lines = [line for line in lines if "messageFeed:" not in line]

        decode_uri_regex = r"decodeURIComponent\((.*)\)"
        lines = [re.sub(decode_uri_regex, lambda match: urllib.parse.unquote(match.group(1)), line) if "decodeURIComponent" in line else line for line in lines]
        joined_json = "\n".join(lines)
        quoted_string = re.sub(r'(\b\w+\b)(?=\s*:)', r'"\1"', joined_json)
        config_dict = json.loads(quoted_string)
        return config_dict
    except Exception as e:
        utils.print_log(f"An error occurred while parsing config object. [{e}]")
        return None

def enter_queue(session, queue_page_html, q_page_url, thread_num):
    try:
        html = queue_page_html
        config = get_config(html)
        queue_page_url = q_page_url

        if not config:
            return None

        challenge_sessions = challenges_solver.ChallengesSolver(session, config, queue_page_html, queue_page_url, thread_num=thread_num).solve()

        if config.get("inqueueUrl"):
            return {
                "queueId": "",
                "checkUrl": "",
                "updateIntervalMs": 0,
                "customUrlParams": unquote(str(challenge_sessions[0])),
                "layoutVersion": 1,
                "layoutName": "",
                "isBeforeOrIdle": False,
                "targetUrl": unquote(f"https://{config['proofOfWorkHost']}{config['inqueueUrl']}"),
            }
        else:
            url_base = f"https://{config['proofOfWorkHost']}/spa-api/queue/{config['customerId']}/{config['eventId']}/"
            target_url = config['targetUrl']
            url = url_base + "enqueue"

            if config.get("culture"):
                url += f"?cid={config['culture'].lower()}"

            layout_name = config['inqueueInfo']['layoutName']

            payload = {
                "customUrlParams": config['customUrlParams'],
                "layoutName": layout_name,
                "Referrer": f"{urllib.parse.urlparse(target_url).scheme}://{urllib.parse.urlparse(target_url).netloc}/",
                "targetUrl": target_url,
            }
            if config.get("inqueueInfo") and config['inqueueInfo'].get("texts") and config['inqueueInfo']['texts'].get("toppanelIFrameSrc"):
                payload["QueueitEnqueueToken"] = config['inqueueInfo']['texts']['toppanelIFrameSrc'].split("&qet=")[1]

            if len(challenge_sessions) > 0:
                payload["challengeSessions"] = challenge_sessions
            headers = {
                "x-queueit-qpage-referral": payload["Referrer"],
                "X-Requested-With": "XMLHttpRequest",
                "Referer": queue_page_url
            }
            headers = {**utils.defaultHeaders(), **headers}
            response_json = session.post(
                url,
                json=payload,
                headers=headers
            ).json()

            if response_json.get("challengeFailed") is True:
                raise Exception(f"Failed to enqueue. Response: [{json.dumps(response_json)}]")
            return {
                "queueId": response_json.get("queueId", ""),
                "checkUrl": f"{url_base}{response_json.get('queueId', '')}/status",
                "updateIntervalMs": 0,
                "customUrlParams": config['customUrlParams'],
                "layoutVersion": config['inqueueInfo']['layoutVersion'],
                "layoutName": layout_name,
                "isBeforeOrIdle": config.get("isBeforeOrIdle", False),
                "targetUrl": target_url,
            }
    except Exception as e:
        raise e

def check_queue(client, queue_details, event_custom_info=None):
    try:
        if queue_details.get("checkUrl"):
            response_json = client.post(
                queue_details["checkUrl"],
                json={
                    "customUrlParams": queue_details["customUrlParams"],
                    "isBeforeOrIdle": queue_details["isBeforeOrIdle"],
                    "isClientRedayToRedirect": True,
                    "layoutName": queue_details["layoutName"],
                    "layoutVersion": queue_details["layoutVersion"],
                    "targetUrl": queue_details["targetUrl"],
                }
            )

            if "isRedirectToTarget" in response_json and not response_json["isRedirectToTarget"]:
                raise Exception("Queue is expired or incorrect token is specified")

            if "updateInterval" in response_json:
                queue_details["updateIntervalMs"] = response_json["updateInterval"]
            queue_details["redirectUrl"] = response_json.get("redirectUrl")
        else:
            queue_details["redirectUrl"] = queue_details["targetUrl"]
        return queue_details
    except Exception as e:
        raise e

def check_and_process_queue(index, session, queue_page_html, q_page_url, queue_url, time_limit=0, event_custom_info=None, thread_num=None):
    try:
        html = queue_page_html
        final_url = None  # Initializing the URL that will be returned

        if is_present(index, html):  # assuming is_present is a utility function
            start_time = time.time()
            utils.print_log("QueueIt page is present. Starting the wait process", utils.DEBUG, index)

            queue_details = enter_queue(session, html, q_page_url, thread_num)  # assuming enter_queue is a utility function

            if not queue_details:
                return None

            update_interval_ms = queue_details["updateIntervalMs"]

            while True:
                try:
                    queue_details = check_queue(session, queue_details, event_custom_info)  # assuming check_queue is a utility function
                    update_interval_ms = queue_details["updateIntervalMs"]

                    if "redirectUrl" in queue_details and queue_details["redirectUrl"] is not None:
                        break
                except Exception as e:
                    utils.print_log(f"An exception occurred while requesting QueueIt status {e}", "ERROR", index)

                if time_limit > 0 and time.time() - start_time >= time_limit:
                    message = f"Failed to process queue in specified time limit [{time_limit}]. Stopping waiting"
                    utils.print_log(message, utils.WARNING, index)
                    raise Exception(message)

                utils.print_log(f"Queue is not finished. Waiting [{update_interval_ms}]ms before the next status request", utils.INFO, index)
                utils.sleep_ms(update_interval_ms)  # assuming sleep_ms is a utility function

            utils.print_log(f"Redirect URL is provided: [{queue_details['redirectUrl']}]", utils.INFO, index)

            if "checkUrl" in queue_details and queue_details["checkUrl"] != "":
                session.get(queue_details["redirectUrl"], headers=utils.defaultHeaders(), verify=False)
            else:
                headers = {
                    "referer": queue_url
                }
                headers = {**utils.defaultHeaders(), **headers}
                params = queue_details['customUrlParams'].replace("'", '"')

                url = f"{queue_details['redirectUrl']}&scv={urllib.parse.quote(params)}"

                res = session.get(url, headers=headers, verify=False)
                res_text = res.text
                
                if "decodeURIComponent('" in res_text:
                    decodeURI = unquote(res_text.split("decodeURIComponent('")[1].split("');")[0])
                else:
                    # Handle unexpected format
                    #utils.print_log(f"Unexpected response format: {res_text}", utils.WARNING, index)
                    return None

                redirect_url = f"{urllib.parse.urlparse(queue_url).scheme}://{urllib.parse.urlparse(queue_url).netloc}{decodeURI}"

                headers = {
                    "referer": url
                }
                headers = {**utils.defaultHeaders(), **headers}
                res = session.get(redirect_url, headers=headers, allow_redirects=False, verify=False)

                if "Location" in res.headers:
                    final_url = res.headers["Location"]
                else:
                    # Handle the case where Location header isn't present.
                    utils.print_log(f"No 'Location' header in response. Full headers: {res.headers}", utils.WARNING, index)
                    return None

                headers = {
                    "referer": final_url
                }
                headers = {**utils.defaultHeaders(), **headers}
                res = session.get(final_url, headers=headers, timeout=5, verify=False)
                utils.print_log(f"Last status code: {res.status_code}", utils.INFO, index)

        return final_url
    except Exception as e:
        utils.print_log(f"An error occurred: {e}", "ERROR", index)
        raise e
