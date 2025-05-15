import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload,MediaIoBaseDownload
from dotenv import load_dotenv
from io import BytesIO
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

def upload_file_to_drive(file_obj, filename, mimetype):
    query = f"name = '{filename}' and trashed = false"
    existing_files = drive_service.files().list(q=query, fields="files(id, name, webViewLink)").execute().get("files", [])

    if existing_files:
        # File already exists — return existing file info
        return {
            'status': 'already_exists',
            'id': existing_files[0]['id'],
            'webViewLink': existing_files[0].get('webViewLink') or f"https://drive.google.com/file/d/{existing_files[0]['id']}/view",
            'message': f"File '{filename}' already exists. Using existing file."
        }
    media = MediaIoBaseUpload(file_obj, mimetype=mimetype, resumable=True)
    file_metadata = {'name': filename}
    
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    # return uploaded_file
    return {
        'status': 'uploaded',
        'id': uploaded_file['id'],
        'webViewLink': uploaded_file['webViewLink'],
        'message': f"File '{filename}' uploaded successfully."
    }

def download_file_from_drive(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh 

# def list_files_from_drive():
#     result = drive_service.files().list(
#         pageSize=20,
#         fields="files(id, name, webViewLink)"
#     ).execute()
#     return result.get("files", [])
def list_files_from_drive():
    files = []
    page_token = None

    while True:
        response = drive_service.files().list(
            pageSize=100,
            fields="nextPageToken, files(id, name, webViewLink)",
            pageToken=page_token
        ).execute()

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

    return files
