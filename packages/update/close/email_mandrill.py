from setup import *

from base64 import b64encode

logger = logging.getLogger(__name__)

if email_isenabled():
      import mailchimp_transactional as MailchimpTransactional
      from mailchimp_transactional.api_client import ApiClientError

def email_update(html, camps_to_close_table, camps_closed_table, camps_not_closed_table):
      if email_isenabled():
            logger.info("Emailing updates...")
            send_email_mandrill(html, camps_to_close_table, camps_closed_table, camps_not_closed_table)
            logger.info("Done")
      else:
            logger.info("Skipping email...")


def send_email_mandrill(html, camps_to_close_table, camps_closed_table, camps_not_closed_table):

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


