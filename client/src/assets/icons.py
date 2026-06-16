from dataclasses import dataclass
from PySide6.QtGui import QIcon

from utils import get_project_path

@dataclass
class Icons:
    calculate : QIcon
    check : QIcon
    code : QIcon
    experiment : QIcon
    fire : QIcon
    language : QIcon
    orbit : QIcon
    stories : QIcon
    delete : QIcon
    add : QIcon
    cancel : QIcon
    export_notes : QIcon
    facebook : QIcon
    google : QIcon
    linkedin : QIcon
    bin : QIcon
    add_file : QIcon
    edit : QIcon
    file_plus_outline : QIcon
    file_plus_tinted : QIcon
    home_outline : QIcon
    home_tinted : QIcon
    notifications_outline : QIcon
    notifications_tinted : QIcon
    search : QIcon
    select_all : QIcon
    select : QIcon
    settings_outline : QIcon
    settings_tinted : QIcon
    x : QIcon


def get_path(name : str):
    return f"{get_project_path()}/src/assets/icons/" + name;
def get_default_icons() -> Icons:


    return Icons(
        calculate=QIcon(get_path("calculate.svg")),
        check=QIcon(get_path("check.svg")),
        code=QIcon(get_path("code.svg")),
        experiment=QIcon(get_path("experiment.svg")),
        fire=QIcon(get_path("fire.svg")),
        language=QIcon(get_path("language.svg")),
        orbit=QIcon(get_path("orbit.svg")),
        stories=QIcon(get_path("stories.svg")),
        delete=QIcon(get_path("delete.svg")),
        add=QIcon(get_path("add.svg")),
        cancel=QIcon(get_path("cancel.svg")),
        export_notes=QIcon(get_path("export_notes.svg")),
        facebook=QIcon(get_path("facebook.png")),
        google=QIcon(get_path("google.png")),
        linkedin=QIcon(get_path("linkedin.png")),
        bin=QIcon(get_path("bin.svg")),
        add_file=QIcon(get_path("add-file.svg")),
        edit=QIcon(get_path("edit.svg")),
        file_plus_outline=QIcon(get_path("file-plus-outline.svg")),
        file_plus_tinted=QIcon(get_path("file-plus-tinted.svg")),
        home_outline=QIcon(get_path("home-outline.svg")),
        home_tinted=QIcon(get_path("home-tinted.svg")),
        notifications_outline=QIcon(get_path("notifications-outline.svg")),
        notifications_tinted=QIcon(get_path("notifications-tinted.svg")),
        search=QIcon(get_path("search.svg")),
        select_all=QIcon(get_path("select-all.svg")),
        select=QIcon(get_path("select.svg")),
        settings_outline=QIcon(get_path("settings-outline.svg")),
        settings_tinted=QIcon(get_path("settings-tinted.svg")),
        x=QIcon(get_path("x.svg")),
    );

icons : Icons = get_default_icons();
