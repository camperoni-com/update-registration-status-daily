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

def fetch_camps():
      #Get a list of all the camps
      headers = {
      'Content-type': 'application/json'
      }

      response = requests.get(camp_list_url, headers=headers)

      logger.info("Fetching camps:")
      logger.info(response.status_code)

      if((response.status_code // 100) ==  4):
            logger.critical("ERROR fetching camps: " + str(response.status_code))
            raise Exception("ERROR fetching camps: " + str(response.status_code))

      camps = json.loads(response.text)
      return camps

def close_camp(auth_key, camp_id):
      headers = {
            'Authorization': 'Token ' + auth_key,
            'Content-type': 'application/json'
        }

      payload = {
            "registration_status": "CLOSED"
        }

      response = requests.patch(camp_list_url + str(camp_id) + "/", data=json.dumps(payload), headers=headers)

      logger.debug(response.status_code)
      logger.debug(response.text)
      if((response.status_code // 100) ==  4):
            logger.error("ERROR changing info for camp: " + camp_id)
            logger.error(response.status_code)
            logger.error(response.text)

            # raise Exception("ERROR changing info for camp: " + camp_id)
            exception = Exception("ERROR changing info for camp: " + camp_id)
            sentry_sdk.capture_exception(exception)
            
            return False
      
      return True

def calculate_camps_to_close(camps):
      camps_to_close = []
      
      for camp in camps:
            camp_id = camp["id"]
            camp_name = camp["name"]
            camp_dates = camp["dates"]
            camp_status = camp["registration_status"]
            
            logger.debug(f"Camp {camp_id}: {camp_name} has status {camp_status} and dates {camp_dates}")
            
            if(camp_status=="CLOSED"):
                  logger.debug(f"Camp {camp_id}: {camp_name} is already closed. Skipping.")
                  continue

            if(camp_dates == None or camp_dates == []):
                  logger.debug(f"Camp {camp_id}: {camp_name} has no dates. Skipping.")
                  continue
            
            camp_datez = [ datetime.datetime.strptime(x, "%Y-%m-%d").date() for x in camp_dates ]
            date_max = max(camp_datez)
            
            today = datetime.datetime.now().date()
            
            if(today >= date_max):
                  logger.debug(f"Camp {camp_id}: {camp_name} is on or past its last date. Selected to close.")
                  logger.debug(f" - Last date: {date_max}. Dates: {camp_dates}")
                  camps_to_close.append(camp)

      logger.info('Finished calculating camps to close. Found ' + str(len(camps_to_close)) + ' camps to close.') 
      return camps_to_close

def close_camps(auth_key, camps_to_close):
      camps_closed = []
      camps_not_closed = []

      for camp in camps_to_close:
            camp_id = camp["id"]
            camp_name = camp["name"]
            logger.info(f"Closing camp {camp_id}: {camp_name}")

            response = close_camp(auth_key, camp_id)
            camp["closed"] = response

            if response:
                  camps_closed.append(camp)
                  logger.info(f"Camp {camp_id}: {camp_name} closed successfully.")
                  
            else:
                  logger.error(f"Camp {camp_id}: {camp_name} failed to close. Continuing...")
                  camps_not_closed.append(camp)
                  continue
            
            if EXECUTE_SAMPLE_ONLY and (random.random() < 0.3):
                  # Do something with 30% chance
                  # Add your code here
                  break

      return (camps_closed, camps_not_closed)

def gdrive_upload(camps_to_close_table, camps_closed_table, camps_not_closed_table):
      # Update the google drive and upload the list of camps that were closed
      try:
            pass
      except:
            logger.error("Google Drive upload failed.")
            raise Exception("Google Drive upload failed.")
      
      return

def calculate_camps_table(camps):

      if(len(camps) == 0):
            logger.debug("No camps in this list.")
            return ""

      camps_clean = []
      for camp in camps:
            camp_clean = {}
            id = camp["id"]
            name = camp["name"]
            
            camp_id_url = f"<a href=\"{camp_list_url}{id}\">{id}</a>"
            camp_name_url = f"<a href=\"{CAMPERONI_URL}/camps/{id}\">{name}</a>"

            camp_clean["id"] = camp_id_url
            camp_clean["name"] = camp_name_url
            camp_clean["dates"] = camp["dates"]

            camps_clean.append(camp_clean)

      camps_table = tabulate(camps_clean, headers="keys", tablefmt="unsafehtml")
      return camps_table

def calculate_html(camps_to_close, camps_closed, camps_not_closed, camps_closed_table):

      html_head = "<html><head></head><body>"
      html_footer = "</body></html>"
      
      html_content = "<h3>Camps to close: " + str(len(camps_to_close)) + "</h3>"
      html_content += "<h3>Camps closed: " + str(len(camps_closed)) + "</h3>"
      html_content += "<h3>Camps not closed: " + str(len(camps_not_closed)) + "</h3>"
      
      if len(camps_to_close) > len(camps_closed):
            html_content += "<h1>NOT ALL CAMPS WERE CLOSED</h1>"

      if len(camps_not_closed) > 0:
            html_content += "<h1>THERE ARE REMAINING CAMPS</h1>"

      html_content += "<h2>List of camps closed</h2>" + camps_closed_table

      html = html_head + html_content + html_footer
      return html
      
def email_update(html, camps_to_close_table, camps_closed_table, camps_not_closed_table):
      camps_to_close_table_data = b64encode(bytes(camps_to_close_table, 'utf-8')).decode('utf-8')
      camps_closed_table_data = b64encode(bytes(camps_closed_table, 'utf-8')).decode('utf-8')
      camps_not_closed_table_data = b64encode(bytes(camps_not_closed_table, 'utf-8')).decode('utf-8')
      
      email_recipients = EMAIL_RECIPIENTS.split(",")

      message = { 'from_email': 'email@camperoni.com',
            'from_name': 'Camperoni Team - Daily Update',
            'to': [
                  #       {
                  #       'email': 'email@camperoni.com',
                  # },
                  #       {
                  #       'email': 'tzikis@camperoni.com',
                  # },
            ],
            'subject': "Camperoni Daily Update - Closing old camps",
            'html': html,
            'attachments': [
                  {
                        'name': 'camps_to_close.html',
                        'type': 'text/html',
                        'content': camps_to_close_table_data
                  },
                  {
                        'name': 'camps_closed.html',
                        'type': 'text/html',
                        'content': camps_closed_table_data
                  },
                  {
                        'name': 'camps_not_closed.html',
                        'type': 'text/html',
                        'content': camps_not_closed_table_data
                  },
            ]
      }

      message['to'] = [{'email': recipient.strip()} for recipient in email_recipients]
      
      try:
            mailchimp = MailchimpTransactional.Client(MANDRILL_API_KEY)
            result = mailchimp.messages.send({"message": message})

            for email_response in result:
                  email_recipient = email_response["email"]

                  if(email_response["status"] != "sent" and email_response["status"] != "queued"):
                        logger.error("Emailing failed.")
                        logger.error(email_response)
                        exception = Exception(f"Emailing {email_recipient} failed.")
                        sentry_sdk.capture_exception(exception)

      except ApiClientError as error:
            logger.error('An exception occurred: {}'.format(error.text))
            sentry_sdk.capture_exception(error)

def main():
      auth_key = login()
      camps = fetch_camps()

      camps_to_close = calculate_camps_to_close(camps)
      (camps_closed, camps_not_closed) = close_camps(auth_key, camps_to_close)
      
      logger.info("Camps to close: " + str(len(camps_to_close)))
      logger.info("Camps closed: " + str(len(camps_closed)))
      logger.info("Camps not closed: " + str(len(camps_not_closed)))

      camps_to_close_table = calculate_camps_table(camps_to_close)

      camps_closed_table = calculate_camps_table(camps_closed)
      camps_not_closed_table = calculate_camps_table(camps_not_closed)

      email_html = calculate_html(camps_to_close, camps_closed, camps_not_closed, camps_closed_table)

      logger.info("Emailing updates...")
      email_update(email_html, camps_to_close_table, camps_closed_table, camps_not_closed_table)
      logger.info("Done")

      # logger.info("Uploading to Google Drive...")
      # gdrive_upload(camps_to_close_table, camps_closed_table, camps_not_closed_table)
      # logger.info("Done")

      logout(auth_key)
      return

if __name__ == "__main__":
      response = main()
