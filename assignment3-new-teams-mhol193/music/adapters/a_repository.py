import abc
from typing import List

import music.domainmodel as dm
from music.domainmodel.user import User

repo_instance = None

class AbstractRepository(abc.ABC):
# ***********************************************
#   TRACK OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def add_track(self, track: dm.Track):
        raise NotImplementedError

    @abc.abstractmethod
    def get_tracks_from(self, start_index: int) -> List[dm.Track]:
        """Gets all tracks from start_index"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_num_tracks(self, start_index: int) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tracks_by_genres(self, keyword: str, genres: List[dm.Genre]) -> \
    List[dm.Track]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_track_by_id(self, id: int) -> dm.Track:
        raise NotImplementedError


# ***********************************************
#   ALBUM OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def add_album(self, album: dm.Album):
        raise NotImplementedError

    @abc.abstractmethod
    def get_albums_from(self, start_index: int) -> List[dm.Album]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tracks_of_album(self, album: dm.Album) -> List[dm.Track]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_albums_by_genres(self, genres: List[dm.Genre]) -> List[dm.Album]:
        raise NotImplementedError


# ***********************************************
#   ARTIST OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def add_artist(self, artist: dm.Artist):
        raise NotImplementedError

    @abc.abstractmethod
    def get_artists(self) -> List[dm.Artist]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tracks_by_artist(self, artist: dm.Artist) -> List[dm.Track]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_artists_by_genres(self, genres: List[dm.Genre]) -> List[dm.Artist]:
        raise NotImplementedError


# ***********************************************
#   GENRE OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def add_genre(self, genre: dm.Genre):
        raise NotImplementedError

    @abc.abstractmethod
    def get_genres(self) -> List[dm.Genre]:
        raise NotImplementedError


# ***********************************************
#   REVIEW OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def get_reviews_by_track(self, track: dm.Track) -> List[dm.Review]:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_user_review_for_track(self, u_name: str, track: dm.Track) -> dm.Review:
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: dm.Review) -> None:
        raise NotImplementedError


# ***********************************************
#   USER OPERATIONS
# ***********************************************
    @abc.abstractmethod
    def add_user(self, user: User):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_users(self) -> List[User]:
        raise NotImplementedError

# ***********************************************
#   FAV TRACK SERVIVCES
# ***********************************************
    
    @abc.abstractmethod
    def add_favourite_track(self, track_id: int, user_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_favourite_track(self, track_id: int, user_name: str):
        raise NotImplementedError


# ***********************************************
#   FRIEND SERVIVCES
# ***********************************************
    def send_request(self, curr_user: User, request_user: User):
        raise NotImplementedError

    def remove_request(self, curr_user: User, request_user: User):
        raise NotImplementedError

    def add_friend(self, curr_user: User, request_user: User):
        raise NotImplementedError

    def remove_friend(self, curr_user: User, request_user: User):
        raise NotImplementedError