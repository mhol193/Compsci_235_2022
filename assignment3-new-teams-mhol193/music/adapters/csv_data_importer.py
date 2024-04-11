import os
import csv
import ast
from pathlib import Path
from datetime import date, datetime

from werkzeug.security import generate_password_hash

from music.adapters.a_repository import AbstractRepository
from music.adapters.csvdatareader import TrackCSVReader

from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.user import User
from music.domainmodel.review import Review


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def create_track_object(track_row):
    track = Track(int(track_row['track_id']), track_row['track_title'])
    track.track_url = track_row['track_url']
    track.track_img_url = track_row['track_image_file']
    track_duration = round(float(
        track_row['track_duration'])) if track_row['track_duration'] is not None else 0
    if type(track_duration) is int:
        track.track_duration = track_duration
    return track


def create_artist_object(track_row):
    artist_id = int(track_row['artist_id'])
    artist = Artist(artist_id, track_row['artist_name'])
    return artist


def create_album_object(row):
    album_id = int(row['album_id'])
    album = Album(album_id, row['album_title'])
    album.album_url = row['album_url']
    album.album_type = row['album_type']

    album.release_year = int(
        row['album_year_released']) if row['album_year_released'].isdigit() else 0

    return album
    


def extract_genres(track_row: dict):
    # List of dictionaries inside the string.
    track_genres_raw = track_row['track_genres']
    # Populate genres. track_genres can be empty (None)
    genres = []
    if track_genres_raw:
        try:
            genre_dicts = ast.literal_eval(
                track_genres_raw) if track_genres_raw != "" else []

            for genre_dict in genre_dicts:
                genre = Genre(
                    int(genre_dict['genre_id']), genre_dict['genre_title'])
                genres.append(genre)
        except Exception as e:
            print(track_genres_raw)
            print(f'Exception occurred while parsing genres: {e}')
    return genres

def load_albums(data_path: Path, repo: AbstractRepository):
    albums: list[Album] = []
    albums_file = str(Path(data_path) / "raw_albums_excerpt.csv")
    if not os.path.exists(albums_file):
        print(f"path {albums_file} does not exist!")

    # encoding of unicode_escape is required to decode successfully
    with open(albums_file, encoding="unicode_escape") as album_csv:
        reader = csv.DictReader(album_csv)
        for row in reader:
            album_id = int(
                row['album_id']) if row['album_id'].isdigit() else row['album_id']
            if type(album_id) is not int:
                print(f'Invalid album_id: {album_id}')
                print(row)
                continue
            album = create_album_object(row)
            repo.add_album(album)
            albums.append(album)

    return albums

def read_tracks_file(data_path: Path, repo: AbstractRepository):
    tracks_file = str(Path(data_path) / "raw_tracks_excerpt.csv")
    if not os.path.exists(tracks_file):
        print(f"path {tracks_file} does not exist!")
        return
    track_rows = []
    # encoding of unicode_escape is required to decode successfully
    with open(tracks_file, encoding='unicode_escape') as track_csv:
        reader = csv.DictReader(track_csv)
        for track_row in reader:
            track_rows.append(track_row)
    return track_rows


def load_users(data_path: Path, repo: AbstractRepository):
    users_filename = str(Path(data_path) / "users.csv")
    users = dict()
    user_list = []

    for data_row in read_csv_file(users_filename):
        user = User(
            user_name=data_row[1],
            password=generate_password_hash(data_row[2]),
            profile_photo = data_row[3]
        )
        repo.add_user(user)
        users[data_row[0]] = user
        user_list.append(user)
    return users

def load_tracks(albums: list[Album], data_path: Path, repo: AbstractRepository):
    track_rows: list = read_tracks_file(data_path, AbstractRepository)

    for track_row in track_rows:
        track = create_track_object(track_row)
        artist = create_artist_object(track_row)
        track.artist = artist
        

        # Extract track_genres attributes and assign genres to the track.
        track_genres = extract_genres(track_row)
        for genre in track_genres:
            track.add_genre(genre)


        if track_row['album_id'].isdigit():
            album_id = int(track_row['album_id']) 
            for a in albums:
                if a.album_id == album_id:
                    track.album = a
        else:
            track.album = None
    
        # Populate datasets for Artist, Genre and Album
        if artist not in repo.get_artists():
            repo.add_artist(artist)

        for genre in track_genres:
            if genre not in repo.get_genres():
                repo.add_genre(genre)

        repo.add_track(track)

