from setup import *

logger = logging.getLogger(__name__)

def gdrive_upload(camps_to_close_table, camps_closed_table, camps_not_closed_table):
      logger.info("Uploading to Google Drive...")
      logger.info("Done")

      # Update the google drive and upload the list of camps that were closed
      try:
            pass
      except:
            logger.error("Google Drive upload failed.")
            raise Exception("Google Drive upload failed.")
      
      return

