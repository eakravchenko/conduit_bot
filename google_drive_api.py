from apiclient import discovery
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import client, file, tools
from googleapiclient.http import MediaIoBaseDownload
import io

# define path variables
credentials_file_path = './credentials/credentials.json'
clientsecret_file_path = './credentials/client_secret.json'

# define API scope
SCOPE = 'https://www.googleapis.com/auth/drive'

# define store
store = file.Storage(credentials_file_path)
credentials = store.get()
# get access token
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
    credentials = tools.run_flow(flow, store)

# define API service
http = credentials.authorize(Http())
drive_service = discovery.build('drive', 'v3', http=http)

IS_FOLDER = "mimeType='application/vnd.google-apps.folder'"


def get_mathcenter_folder_id(service) -> str:
    try:
        response = service.files().list(q=IS_FOLDER + " and name='Матцентр 2027'",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                               'files(id, name)',
                                        ).execute()
        file_list = response.get('files', [])
        if not file_list:
            print("This folder doesn't exist")

        for file in response.get('files', []):
            return file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None


def get_current_grade_folder_id(service, grade_folder_name: str) -> str:
    parent_id = get_mathcenter_folder_id(service)
    try:

        response = service.files().list(q=f"'{parent_id}' in parents and name='{grade_folder_name}'",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                               'files(id, name)').execute()
        file_list = response.get('files', [])
        if not file_list:
            print("This folder doesn't exist")

        for file in response.get('files', []):
            return file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None


def get_ser_file(service, grade_folder_name: str, ser_name: str):

    """
    :param service: диск, к которому адресованы все запросы
    :param grade_folder_name: Имя папки с классом, например "7 класс" или "Лагерь после 6 класса"
    :param ser_name: Часть имени серии, например "13" или "МБ1"
    :return:
    """

    current_grade_folder_id = get_current_grade_folder_id(service, grade_folder_name)

    series_folder_id: str

    try:
        response = service.files().list(q=f"'{current_grade_folder_id}' in parents and name='Серии'",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                               'files(id, name)').execute()
        file_list = response.get('files', [])
        if not file_list:
            print("This folder doesn't exist")

        for file in response.get('files', []):
            series_folder_id = file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    current_ser_folder_id: str

    try:
        response = service.files().list(q=f"'{series_folder_id}' in parents and name contains '{ser_name}'",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                               'files(id, name)').execute()
        file_list = response.get('files', [])
        if not file_list:
            print("This folder doesn't exist")

        for file in response.get('files', []):
            current_ser_folder_id = file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    pdf_ser_file_id: str

    try:
        response = service.files().list(q=f"'{current_ser_folder_id}' in parents and name contains 'ser {ser_name}"
                                          f".pdf'",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                               'files(id, name)').execute()
        file_list = response.get('files', [])
        if not file_list:
            print("This folder doesn't exist")

        for file in response.get('files', []):
            pdf_ser_file_id = file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None


    try:
        request = service.files().get_media(fileId=pdf_ser_file_id)
        fh = io.FileIO(f'ser {ser_name}.pdf', 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()



    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None




if __name__ == '__main__':
    service = discovery.build('drive', 'v3', credentials=credentials)
    get_ser_file(service, '7 класс', '13')
