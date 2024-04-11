from pathlib import Path

from music.adapters.a_repository import AbstractRepository
from music.adapters.csv_data_importer import load_users, load_tracks, load_albums


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool):
    load_users(data_path, repo)
    albums = load_albums(data_path, repo)
    load_tracks(albums, data_path, repo)



    