from typing import List, Set
import pathlib
import csv
import random

from werkzeug.security import generate_password_hash

from music.adapters.a_repository import AbstractRepository
from music.adapters.csvdatareader import TrackCSVReader

# import domain model
from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.user import User
from music.domainmodel.review import Review


class MemoryRepository(AbstractRepository):

    def __init__(self) -> None:
        self.__tracks: List[Track] = list()
        self.__artists: List[Artist] = list()
        self.__albums: List[Album] = list()
        self.__genres: List[Genre] = list()
        self.__users: List[User] = list()
        self.__reviews: List[Review] = list()

# ***********************************************
#   TRACK OPERATIONS
# ***********************************************
    def get_tracks_from(self, start_index: int) -> List[Track]:
        if start_index < len(self.__tracks):
            return self.__tracks[start_index:]
        else:
            return []

    def get_num_tracks(self, start_index: int) -> int:
        return len(self.__tracks[start_index:])

    def get_tracks_by_genres(self, genre_filters: List[Genre]=None) -> List[Track]:
        if genre_filters is None:
            return self.__tracks
        output_tracks = list()
        for track in self.__tracks:
            if any(g in track.genres for g in genre_filters):
                output_tracks.append(track)
        return output_tracks

    def get_track_by_id(self, id: int) -> Track | None:
        for t in self.__tracks:
            if t.track_id == id:
                return t


# ***********************************************
#   ALBUM OPERATIONS
# ***********************************************
    def get_albums_from(self, start_index: int) -> List[Album]:
        if start_index < len(self.__albums):
            return self.__albums[start_index:]
        else:
            return []

    def get_tracks_of_album(self, album: Album) -> List[Track]:
        _tracks: Track = []
        for track in self.__tracks:
            if track.album == album:
                _tracks.append(track)
        return _tracks

    def get_genres_of_album(self, album: Album) -> List[Genre]:
        tracks = self.get_tracks_of_album(album)
        genres = set()
        for track in tracks:
            [genres.add(g) for g in track.genres]
        return list(genres)
   
    def get_albums_by_genres(self, genre_filters: List[Genre] = None) -> List[Album]:
        if genre_filters is None:
           return self.__albums
        output_albums = list()
        for album in self.__albums:
            _genres = self.get_genres_of_album(album)
            if any(g in _genres for g in genre_filters):
                output_albums.append(album)
        return output_albums
      

# ***********************************************
#   ARTIST OPERATIONS
# ***********************************************
    def get_artists(self) -> List[Artist]:
        return self.__artists

    def get_tracks_by_artist(self, artist: Artist) -> List[Track]:
        tracks = list()
        for track in self.__tracks:
            if track.artist == artist:
                tracks.append(track)
        return tracks

    def get_genres_of_artist(self, artist: Artist) -> List[Genre]:
        tracks = self.get_tracks_by_artist(artist)
        genres = set()
        for track in tracks:
            [genres.add(g) for g in track.genres]
        return list(genres)
    
    def get_artists_by_genres(self, genre_filters: List[Genre] = None) -> List[Artist]:
        if genre_filters is None:
            return self.__artists
        output_artists = set()
        for artist in self.__artists:
            _genres = self.get_genres_of_artist(artist)
            if any(g in _genres for g in genre_filters):
                output_artists.add(artist)
        return list(output_artists)


# ***********************************************
#   GENRE OPERATIONS
# ***********************************************
    def get_genres(self) -> List[Genre]:
        return self.__genres


# ***********************************************
#   REVIEW OPERATIONS
# ***********************************************
    def get_reviews_by_track(self, track: Track) -> List[Review]:
        output = [r for r in self.__reviews if r.track == track]
        return output

    def get_user_review_for_track(self, u_name: str, track: Track) -> Review:
        for r in self.__reviews:
            if r.user.user_name == u_name and r.track == track:
                return r

    def add_review(self, review: Review) -> None:
        if isinstance(review, Review) and review not in self.__reviews:
            self.__reviews.append(review)
        elif review in self.__reviews:
            self.__reviews.remove(review)
            self.__reviews.append(review)


# ***********************************************
#   USER OPERATIONS
# ***********************************************
    def add_user(self, user: User):
        if isinstance(user, User) and user not in self.__users:
            self.__users.append(user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__users if user.user_name == user_name), None)

    def get_all_users(self) -> List[User]:
        return self.__users


# ***********************************************
#   UTILITY OPERATIONS
# ***********************************************
    def populate_from_csv(self):
        albums_file = pathlib.Path().cwd() / "music/adapters/data/raw_albums_excerpt.csv"
        tracks_file = pathlib.Path().cwd() / "music/adapters/data/raw_tracks_excerpt.csv"
        users_file = pathlib.Path().cwd() / "music/adapters/data"

        csvreader = TrackCSVReader(str(albums_file), str(tracks_file))
        csvreader.read_csv_files()
        
        self.__tracks = csvreader.dataset_of_tracks
        self.__albums = list(csvreader.dataset_of_albums)
        self.__artists = list(csvreader.dataset_of_artists)
        self.__genres = list(csvreader.dataset_of_genres)
        load_users(users_file, self)

        # print("MEMORY REPO POPULATED")
        # print("SIZE OF TRACKS DATASET =", len(self.__tracks))
        # print("SIZE OF ALBUMS DATASET =", len(self.__albums))
        # print("SIZE OF ARTISTS DATASET =", len(self.__artists))
        # print("SIZE OF GENRES DATASET =", len(self.__genres))
        # print("SIZE OF REVIEWS DATASET =", len(self.__reviews))
        # print("SIZE OF USERS DATASET =", len(self.__users))



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

def load_users(data_path: pathlib.Path, repo: MemoryRepository):
    users = dict()

    users_filename = str(pathlib.Path(data_path) / "users.csv")
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

def populate(data_path: pathlib.Path, repo: MemoryRepository):
    # Load users into the repository.
    users = load_users(data_path, repo)


        