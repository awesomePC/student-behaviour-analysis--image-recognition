from gdown import download

def download_drive_checkpoint(file_id, output):
    try:
        # download from google drive
        url = f'https://drive.google.com/uc?id={file_id}'
        print("downloading file from google drive.")
        download(url, output, quiet=False)
        return True
    except Exception as e:
        print(e)
        print("Error while downloading file from google drive. Manually add model checkpoint.")
        return False