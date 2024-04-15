from setup import *

if (GDRIVE_PARENT_FOLDER is not None) and (GDRIVE_CREDENTIALS is not None):
    from io import BytesIO

    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)

def get_drive_service(credentials_json):
    scopes = ['https://www.googleapis.com/auth/drive']

    service_account_info = json.loads(credentials_json)
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)

    drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)

    return drive_service

def get_or_create_folder(parent_folder_id, drive_service):

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and name = '{today}_close'"

    # Check if today's date folder exists
    response = drive_service.files().list(
        q=query,
        spaces='drive',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields='files(id, name)').execute()
    folders = response.get('files', [])

    # If the folder exists, return its ID
    if folders:
        return folders[0]['id']
    else:
        # If not, create the folder
        folder_metadata = {
            'name': f"{today}_close",
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id', supportsAllDrives=True).execute()
        return folder.get('id')

def upload_file_to_drive(drive_service, data, file_prefix, folder_id):

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    time = datetime.datetime.now().strftime('%H:%M:%S')

    # Convert DataFrame to an Excel file in memory
    file_name = f'{file_prefix}_{today}_{time}.html'
    data_buffer = BytesIO()

    data_buffer.write(data.encode('utf-8'))
    data_buffer.seek(0)

    # Upload Excel file to Google Drive
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'mimeType': 'text/html'
    }

    media = MediaIoBaseUpload(data_buffer,
                              mimetype='text/html',
                              resumable=True)

    request = drive_service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True)
    response = request.execute()

    return response


def gdrive_upload(camps_to_close_table, camps_closed_table, camps_not_closed_table):
    if (GDRIVE_PARENT_FOLDER is not None) and (GDRIVE_CREDENTIALS is not None):
        logger.info("Uploading to Google Drive...")

        # Update the google drive and upload the list of camps that were closed
        try:
            drive_service = get_drive_service(GDRIVE_CREDENTIALS)

            folder_id = get_or_create_folder(GDRIVE_PARENT_FOLDER, drive_service)
            logger.debug(f"Folder ID: {folder_id}")

            response = upload_file_to_drive(drive_service, camps_to_close_table, 'camps_to_close', folder_id)
            logger.debug(f"File camps_to_close response: {response}")

            response = upload_file_to_drive(drive_service, camps_closed_table, 'camps_closed', folder_id)
            logger.debug(f"File camps_closed response: {response}")

            response = upload_file_to_drive(drive_service, camps_not_closed_table, 'camps_not_closed', folder_id)
            logger.debug(f"File camps_not_closed response: {response}")

        except Exception as e:
            logger.error("Google Drive upload failed.")
            logger.error(e)
            # exception = Exception("Google Drive upload failed.")
            # sentry_sdk.capture_exception(exception)
            sentry_sdk.capture_exception(e)
        logger.info("Done")
    else:
        logger.info("Skipping Google Drive upload...")
