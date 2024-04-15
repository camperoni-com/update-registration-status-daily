from setup import *

logger = logging.getLogger(__name__)

def login():
      #Log in as administration

      headers = {
      'Content-type': 'application/json'
      }

      payload = {
      "username": ADMIN_USERNAME,
      "password": ADMIN_PASSWORD,
      }

      response = requests.post(user_login_url, data=json.dumps(payload), headers=headers)

      logger.info("Login:")
      logger.info(response.status_code)
      logger.info(response.text)

      if((response.status_code // 100) ==  4):
            logger.critical("ERROR logging in as user: " + ADMIN_USERNAME)
            raise Exception("ERROR logging in as user: " + ADMIN_USERNAME)

      response_json = json.loads(response.text)
      auth_key = response_json["key"]
      logger.info("Auth key: " + auth_key)
      return auth_key

def logout(auth_key):
      #Logout
      headers = {
      'Authorization': 'Token ' + auth_key,
      'Content-type': 'application/json'
      }

      payload = {
      }

      response = requests.post(user_logout_url, data=json.dumps(payload), headers=headers)

      logger.info("Logout:")
      logger.info(response.status_code)
      logger.info(response.text)

      if((response.status_code // 100) ==  4):
            logger.critical("ERROR logging out as user: " + ADMIN_USERNAME)
            raise Exception("ERROR logging out as user: " + ADMIN_USERNAME)
