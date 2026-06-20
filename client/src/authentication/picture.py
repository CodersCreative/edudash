from PySide6.QtCore import QThread, pyqtSignal
import requests

from constants import SERVER_URL
from utils import get_project_root


class FetchProfilePictureThread(QThread):
    fetched = pyqtSignal(str)

    def __init__(self, id, *args, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs)

    def run(self):
        default = f"{get_project_root()}src/assets/icons/account.svg"
        try:
            response = requests.get(
                SERVER_URL + "profile/picture",
                json={"id": self.id},
                timeout=5,
                stream=True,
            )
            response.raise_for_status()
            filename = f"{get_project_root()}src/assets/user_data/profiles/{self.id}"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                self.fetched.emit(filename)
            self.fetched.emit(default)
        except Exception:
            self.fetched.emit(default)
