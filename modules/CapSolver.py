import yaml
from modules import utils
import capsolver

class CapSolver:
    def __init__(self, thread_num=None):
        # Load the API key from the config file
        with open('config.yml', 'r') as config_file:
            config_data = yaml.safe_load(config_file)
        self.apiKey = config_data.get('CAPSOLVER_API_KEY', 'DEFAULT_API_KEY')
        self.siteKey = '6LePTyoUAAAAADPttQg1At44EFCygqxZYzgleaKp'  # recaptcha sitekey found on site
        self.thread_num = thread_num
        capsolver.api_key = self.apiKey

    def solve_recaptcha(self, site_key=None, page_url=None):
        try:
            print(page_url)
            site_key = site_key or self.siteKey
            solution = capsolver.solve({
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteURL": page_url,
                "websiteKey": site_key,
            })
            utils.print_log(f"Got reCAPTCHA response from CapSolver. Solution: {solution}", utils.SUCCESS, thread_index=self.thread_num)
            return solution
        except Exception as e:
            utils.print_log(f"Failed to solve reCAPTCHA: {e}", utils.ERROR, thread_index=self.thread_num)
            return None

    def solve_image_captcha(self, base64_string, module="queueit"):
        try:
            solution = capsolver.solve({
                "type": "ImageToTextTask",
                "module": module,
                "body": base64_string
            })
            utils.print_log(f"Got imageCaptcha response from CapSolver. Solution text: [{solution['text']}]", utils.SUCCESS, thread_index=self.thread_num)
            return solution['text']
        except Exception as e:
            utils.print_log(f"Failed to get imageCaptcha response from CapSolver. [{e}]", utils.ERROR, thread_index=self.thread_num)
            return None
