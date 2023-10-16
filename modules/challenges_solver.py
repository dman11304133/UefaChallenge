import base64
import json
import hashlib
import random
import time

from bs4 import BeautifulSoup
from modules import utils
from modules.CapSolver import CapSolver
from modules.utils import DEBUG, INFO, OOS, WARNING, ERROR, SUCCESS


class ChallengesSolver:
    def __init__(self, session, config, queueItHtml, q_page_url, thread_num=None):
        self.session = session
        self.queuePageUrl = q_page_url
        self.config = config
        self.thread_num = thread_num

        soup = BeautifulSoup(queueItHtml, "html.parser")

        self.userId = soup.find("meta", {"id": "queue-it_log"}).get("data-userid", "") or ""
        self.customerId = self.config["customerId"]
        self.eventId = self.config["eventId"]
        self.tags = {
            "powTag-CustomerId": self.customerId,
            "X-Queueit-Challange-CustomerId": self.customerId,
            "powTag-EventId": self.eventId,
            "X-Queueit-Challange-EventId": self.eventId,
            "powTag-UserId": self.userId,
            "X-Queueit-Challange-UserId": self.userId,
        }

    def solve(self):
        challenges = self.config.get("challenges", [])
        if challenges:
            utils.print_log(f"[{', '.join([it['name'] for it in challenges])}] challenges are present before queue. Solving", type=WARNING, thread_index=self.thread_num)
            solutions = []
            for challenge in challenges:
                name = challenge["name"]
                if name == "RecaptchaInvisible":
                    solution = self.solveRecaptcha(True)
                elif name == "ProofOfWork":
                    solution = self.solveProofOfWork()
                elif name == "Recaptcha":
                    solution = self.solveRecaptcha(False)
                elif name == "BotDetect":
                    solution = self.solveBotDetect()
                else:
                    raise ValueError("Unsupported Queue-It challenge")

                solutions.append(solution["sessionInfo"])

            return solutions
        else:
            utils.print_log("No challenges found")
            return []

    def solveRecaptcha(self, isInvisible, max_retries=10):
        for attempt in range(max_retries):
            try:
                start_time = int(time.time() * 1000)
                siteKey = "6LePTyoUAAAAADPttQg1At44EFCygqxZYzgleaKp"
                utils.print_log(f"Solving captcha with key [{siteKey}]. Invisible [{isInvisible}]", type=WARNING, thread_index=self.thread_num)
                
                details = self.get_challenge_details()
                utils.print_log(f"{self.queuePageUrl}")
                cap_solver = CapSolver(thread_num=self.thread_num)
                solution = cap_solver.solve_recaptcha(siteKey, self.queuePageUrl)
                challengePayload = self.generateChallengePayload(
                    "recaptcha-invisible" if isInvisible else "recaptcha",
                    details["challengeDetails"], 
                    details["sessionId"], 
                    solution, 
                    self.generate_stats(int(time.time() * 1000) - start_time)
                )
                
                # This will raise an exception if the verification fails
                verification_result = self.postChallengePayload(challengePayload)
                    
                # Check if verification was successful
                if verification_result and verification_result.get("isVerified"):
                    return verification_result

            except ValueError as e:
                utils.print_log(f"Retrying the entire Recaptcha solving process due to: {str(e)}. Attempt {attempt + 1}/{max_retries}", type=WARNING, thread_index=self.thread_num)
                continue  # Explicitly continue to the next iteration, though this is optional since it will continue naturally

        # If the code reaches here, all retries have failed
        raise ValueError("Failed to solve and verify recaptcha after maximum retries")


    def get_challenge_details(self):
        url = f"https://{self.config['reCaptchaHost']}/challengeapi/recaptchainvisible/challenge/"
        headers = {
            "x-queueit-challange-reason": "1",
            'X-Queueit-Challange-Customerid': self.customerId,
            'X-Queueit-Challange-Eventid': self.eventId,
            "X-Queueit-Challange-Hash": self.config["challengeApiChecksumHash"]
        }
        headers = {**utils.defaultHeaders(), **headers}
        response = self.session.post(url, headers=headers)
        return response.json()

    def solveProofOfWork(self):
        utils.print_log("Solving proof of work")
        url = f"https://{self.config['proofOfWorkHost']}/challengeapi/pow/challenge/{self.userId}"
        new_headers = {
            "powTag-CustomerId": self.customerId,
            "X-Queueit-Challange-CustomerId": self.customerId,
            "powTag-EventId": self.eventId,
            "X-Queueit-Challange-EventId": self.eventId,
            "powTag-UserId": self.userId,
            "X-Queueit-Challange-UserId": self.userId,
            "X-Queueit-Challange-reason": "1",
            "X-Queueit-Challange-Hash": self.config["challengeApiChecksumHash"],
            "powTag-Hash": self.config["challengeApiChecksumHash"],
            "referer": self.queuePageUrl,
        }
        headers = {**utils.defaultHeaders(), **new_headers}
        response = self.session.post(url, headers=headers)
        challenge_data_json = response.json()

        params = challenge_data_json["parameters"]

        solution = {
            "hash": self.solve_pow(params["zeroCount"], params["input"], params["complexity"]),
            "type": "HashChallenge"
        }

        if not solution:
            raise Exception("Failed to solve proof of work")

        stats = self.generate_stats(random.randint(2000, 8000))
        challenge_payload = {
            "challengeDetails": challenge_data_json["challengeDetails"],
            "challengeType": "proofofwork",
            "customerId": self.config["customerId"],
            "eventId": self.config["eventId"],
            "sessionId": challenge_data_json["sessionId"],
            "solution": solution["gRecaptchaResponse"],
            "stats": stats,
            "version": 6,
        }

        return self.postChallengePayload(challenge_payload)

    def solve_pow(self, zero_count, input, complexity):
        solutions = []
        postfix = 0

        while len(solutions) != zero_count:
            hash = hashlib.sha256(f"{input}{postfix}".encode()).hexdigest()

            if hash.startswith("0" * complexity):
                solutions.append({"hash": hash, "postfix": postfix})

            postfix += 1

        return solutions
    
    def solveBotDetect(self):
     utils.print_log(f"Solving BotDetect challenge", type=WARNING, thread_index=self.thread_num)
     startTime = int(time.time() * 1000)
     culture = self.config["culture"]

     additionalHeaders = {}
     if self.config.get("customerId"):
        additionalHeaders["x-queueit-challange-customerid"] = self.config["customerId"]
     if self.config.get("eventId"):
        additionalHeaders["x-queueit-challange-eventid"] = self.config["eventId"]
     if self.config.get("challengeApiChecksumHash"):
        additionalHeaders["x-queueit-challange-hash"] = self.config["challengeApiChecksumHash"]
     if self.config.get("challengesIssuedByReason"):
        additionalHeaders["x-queueit-challange-reason"] = f'{self.config["challengesIssuedByReason"]}'

     url = f"https://{self.config['botDetectHost']}/challengeapi/queueitcaptcha/challenge/{culture.lower()}"

     headers = {**utils.defaultHeaders(), **additionalHeaders}

     challengeDataJson = self.session.post(
        url,
        headers=headers
     ).json()

     if "imageBase64" not in challengeDataJson:
        utils.print_log(f"Incorrect numeric captcha payload: {challengeDataJson}", type=WARNING, thread_index=self.thread_num)
        raise ValueError("Incorrect numeric captcha (BotProtection) payload")

     solution = CapSolver(thread_num=self.thread_num).solve_image_captcha(challengeDataJson["imageBase64"])

     if solution is None:
        utils.print_log("Failed to get a solution from solveBotDetect.", type=WARNING, thread_index=self.thread_num)
        return None  # Handle this return in the calling function

     jsonPayload = {
        "challengeType": "botdetect",
        "challengeDetails": challengeDataJson["challengeDetails"],
        "customerId": self.config["customerId"],
        "eventId": self.config["eventId"],
        "sessionId": challengeDataJson["sessionId"],
        "solution": solution.upper(),
        "stats": self.generate_stats(int(time.time() * 1000) - startTime),
        "version": 6,
     }

     return self.postChallengePayload(jsonPayload)


    def postChallengePayload(self, bodyJson, max_retries=3):
        for attempt in range(max_retries):
            try:
                url = f"https://{self.config['botDetectHost']}{self.config['challengeVerifyEndpoint']}"
                base_headers = {
                    "x-requested-with": "XMLHttpRequest",
                    "referer": self.queuePageUrl
                }
                headers = {**utils.defaultHeaders(), **base_headers}

                response = self.session.post(url, json=bodyJson, headers=headers)
                responseJson = response.json()

                # If verification is successful, return the responseJson
                if responseJson.get("isVerified"):
                    return responseJson
                else:
                    # Log the failed attempt
                    utils.print_log(f"Failed to verify recaptcha solution. Response: {responseJson}", type=ERROR, thread_index=self.thread_num)
                    # Sleep for a short duration before retrying (adjust as needed)
                    time.sleep(2)
                    
            except Exception as e:
                # Log the exception (you can customize this log message)
                utils.print_log(f"Exception during verification: {str(e)}", type=ERROR, thread_index=self.thread_num)
            
            # Retry the verification by continuing to the next attempt
            continue

        # If all retry attempts fail, raise an exception
        raise ValueError("Failed to verify recaptcha solution after maximum retries")
 




    def generateChallengePayload(self, challengeType, challengeDetails, sessionId, solution, stats):
        return {
            "challengeDetails": challengeDetails,
            "challengeType": challengeType,
            "customerId": self.config["customerId"],
            "eventId": self.config["eventId"],
            "sessionId": sessionId,
            "solution": solution["gRecaptchaResponse"],
            "stats": stats,
            "version": 6,
        }

    def generate_stats(self, duration):
        return {
            "duration": duration,
            "tries": 1,
            "userAgent": utils.default_ua,
            "screen": "1920 x 1080",
            "browser": "Chrome",
            "browserVersion": "114.0.0.0",
            "isMobile": False,
            "os": "10",
            "osVersion": "Windows",
            "cookiesEnabled": True,
        }
