from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session

from music.adapters.a_repository import AbstractRepository
from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.user import User
from music.domainmodel.review import Review


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()


# ***********************************************
#   TRACK OPERATIONS
# ***********************************************
    def add_track(self, track: Track):
        with self._session_cm as scm:
            scm.session.merge(track)
            scm.commit()

    def get_tracks_from(self, start_index: int) -> List[Track]:
        tracks = self._session_cm.session.query(Track).all()
        if start_index < len(tracks):
            return tracks[start_index:]
        else:
            return []

    def get_num_tracks(self, start_index: int) -> int:
        tracks = self._session_cm.session.query(Track).all()
        return len(tracks[start_index:])

    def get_tracks_by_genres(self, genre_filters: List[Genre]=None) -> List[Track]:
        tracks = self._session_cm.session.query(Track).all()
        if genre_filters is None:
            return tracks
        output_tracks = list()
        for track in tracks:
            if any(g in track.genres for g in genre_filters):
                output_tracks.append(track)
        return output_tracks

    def get_track_by_id(self, id: int) -> Track | None:
        tracks = self._session_cm.session.query(Track).all()
        for t in tracks:
            if t.track_id == id:
                return t


# ***********************************************
#   ALBUM OPERATIONS
# ***********************************************
    def add_album(self, album: Album):
        with self._session_cm as scm:
            scm.session.merge(album)
            scm.commit()

    def get_albums_from(self, start_index: int) -> List[Album]:
        albums = self._session_cm.session.query(Album).all()
        if start_index < len(albums):
            return albums[start_index:]
        else:
            return []

    def get_tracks_of_album(self, album: Album) -> List[Track]:
        tracks = self._session_cm.session.query(Track).all()
        _tracks: Track = []
        for track in tracks:
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
        albums = self._session_cm.session.query(Album).all()
        if genre_filters is None:
           return albums
        output_albums = list()
        for album in albums:
            _genres = self.get_genres_of_album(album)
            if any(g in _genres for g in genre_filters):
                output_albums.append(album)
        return output_albums
      

# ***********************************************
#   ARTIST OPERATIONS
# ***********************************************
    def add_artist(self, artist: Artist):
        with self._session_cm as scm:
            scm.session.merge(artist)
            scm.commit()

    def get_artists(self) -> List[Artist]:
        artists = self._session_cm.session.query(Artist).all()
        return artists

    def get_tracks_by_artist(self, artist: Artist) -> List[Track]:
        tracks = self._session_cm.session.query(Track).all()
        _tracks = list()
        for track in tracks:
            if track.artist == artist:
                _tracks.append(track)
        return _tracks

    def get_genres_of_artist(self, artist: Artist) -> List[Genre]:
        tracks = self.get_tracks_by_artist(artist)
        genres = set()
        for track in tracks:
            [genres.add(g) for g in track.genres]
        return list(genres)
    
    def get_artists_by_genres(self, genre_filters: List[Genre] = None) -> List[Artist]:
        artists = self._session_cm.session.query(Artist).all()
        if genre_filters is None:
            return artists
        output_artists = set()
        for artist in artists:
            _genres = self.get_genres_of_artist(artist)
            if any(g in _genres for g in genre_filters):
                output_artists.add(artist)
        return list(output_artists)


# ***********************************************
#   GENRE OPERATIONS
# ***********************************************
    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.merge(genre)
            scm.commit()

    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres


# ***********************************************
#   REVIEW OPERATIONS
# ***********************************************
    def get_reviews_by_track(self, track: Track) -> List[Review]:
        reviews = self._session_cm.session.query(Review).all()
        output = [r for r in reviews if r.track == track]
        return output

    def get_user_review_for_track(self, u_name: str, track: Track) -> Review:
        reviews = self._session_cm.session.query(Review).all()
        for r in reviews:
            if r.user.user_name == u_name and r.track == track:
                return r

    def add_review(self, review: Review) -> None:
        with self._session_cm as scm:
            scm.session.merge(review)
            scm.commit()


# ***********************************************
#   USER OPERATIONS
# ***********************************************
    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.merge(user)
            scm.commit()

    def get_user(self, user_name: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == user_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def get_all_users(self) -> List[User]:
        users = self._session_cm.session.query(User).all()
        return users


# ***********************************************
#   FAV TRACK SERVIVCES
# ***********************************************

    def add_favourite_track(self, track_id: int, user_name: str) -> None:
        with self._session_cm as scm:
            user = scm.session.get(User, user_name)
            track = scm.session.get(Track, track_id)
            user.add_liked_track(track)
            scm.commit()

    def remove_favourite_track(self, track_id: int, user_name: str) -> None:
        with self._session_cm as scm:
            user = scm.session.get(User, user_name)
            track = scm.session.get(Track, track_id)
            user.remove_liked_track(track)
            scm.commit()


# ***********************************************
#   FRIEND SERVIVCES
# ***********************************************

    def send_request(self, curr_user: User, request_user: User):
        with self._session_cm as scm:
            curr_user.add_request(request_user)
            scm.commit()

    def remove_request(self, curr_user: User, request_user: User):
        with self._session_cm as scm:
            curr_user.remove_request(request_user)
            scm.commit()

    def add_friend(self, curr_user: User, request_user: User):
        with self._session_cm as scm:
            curr_user.add_friend(request_user)
            scm.commit()

    def remove_friend(self, curr_user: User, request_user: User):
        with self._session_cm as scm:
            curr_user.remove_friend(request_user)
            scm.commit()
