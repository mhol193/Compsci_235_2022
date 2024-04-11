from typing import List, Tuple
from flask import session

from music.adapters.a_repository import AbstractRepository

from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.review import Review

from music.dtos.dto_album_out import DtoAlbumOut
from music.dtos.dto_track_out import DtoTrackOut
from music.dtos.dto_artist_out import DtoArtistOut

from music.bp_users.services import check_if_fav_track, get_track_rating

# TRACK SERVICES
def get_track(track_id: int, repo: AbstractRepository):
    t = repo.get_track_by_id(track_id)
    return DtoTrackOut(t, is_fav=check_if_fav_track(t, repo), user_rating=get_track_rating(t, repo))

def get_next_seven_tracks(start_index: int, repo: AbstractRepository) -> List[Track]:
    _remaining_tracks = repo.get_tracks_from(start_index)[:7]
    _dtos = []
    for t in _remaining_tracks:
        dto = DtoTrackOut(t, 
                        is_fav=check_if_fav_track(t, repo),
                        user_rating=get_track_rating(t, repo))
        _dtos.append(dto)
    return _dtos

def get_tracks_last_page_index(repo: AbstractRepository) -> int:
    _last_pg_i = (repo.get_num_tracks(0) // 7) * 7
    
    if len(repo.get_tracks_from(_last_pg_i)) == 0:
        return _last_pg_i - 7
    else:
        return _last_pg_i


# ALBUM SERVICES
def get_next_seven_albums(start_index: int, repo: AbstractRepository) -> List[DtoAlbumOut]:
    next_albums = repo.get_albums_from(start_index)[:7]
    dtos = []

    for _album in next_albums:
        try:
            tracks = repo.get_tracks_of_album(_album)
            artist = tracks[0].artist
            if artist is not None:
                artist = artist.full_name
            dtos.append(DtoAlbumOut(_album, artist, tracks))
        except IndexError:
            print("ERROR", _album)

    return dtos

def get_albums_last_page_index(repo: AbstractRepository) -> int:
    _last_pg_i = (len(repo.get_albums_from(0)) // 7) * 7
    if len(repo.get_albums_from(_last_pg_i)) == 0:
        return _last_pg_i - 7
    else:
        return _last_pg_i

def get_next_seven_tracks_of_album(album_id: int, start_index: int, repo: AbstractRepository) -> List[DtoTrackOut]:
    tracks = repo.get_tracks_of_album(Album(album_id, ""))
    next_tracks = tracks[start_index: start_index+7]
    dtos = []
    for t in next_tracks:
        dto = DtoTrackOut(t, 
                        is_fav=check_if_fav_track(t, repo),
                        user_rating=get_track_rating(t, repo))
        dtos.append(dto)
    return dtos

def get_last_pg_index_of_single_album(album_id: int, repo: AbstractRepository) -> int:
    tracks = repo.get_tracks_of_album(Album(album_id, ""))
    last_pg_i = (len(tracks) // 7) * 7
    if len(tracks[last_pg_i:]) == 0:
        return last_pg_i - 7
    else:
        return last_pg_i


# ARTIST SERVICES
def get_next_eight_artists(start_index: int, repo: AbstractRepository) -> List[DtoArtistOut]:
    next_artists = repo.get_artists()[start_index: start_index+8]
    dtos = []

    for _ in next_artists:
        artist_tracks = repo.get_tracks_by_artist(_)
        dtos.append(DtoArtistOut(_, artist_tracks))

    return dtos

def get_artists_last_page_num(repo: AbstractRepository) -> int:
    data_artists = repo.get_artists()
    _last_pg = (len(data_artists) // 8)
    if len(data_artists) % 8 == 0:
        return _last_pg - 1
    else:
        return _last_pg

def get_next_seven_tracks_of_artist(artist_id: int, start_index: int, repo: AbstractRepository) -> List[DtoTrackOut]:
    tracks = repo.get_tracks_by_artist(Artist(artist_id, ""))
    next_tracks = tracks[start_index: start_index+7]
    dtos = []
    for t in next_tracks:
        dto = DtoTrackOut(t, 
                        is_fav=check_if_fav_track(t, repo),
                        user_rating=get_track_rating(t, repo))
        dtos.append(dto)
    return dtos

def get_last_pg_index_of_single_artist(artist_id: int, repo: AbstractRepository) -> int:
    tracks = repo.get_tracks_by_artist(Artist(artist_id, ""))
    last_pg_i = (len(tracks) // 7) * 7
    if len(tracks[last_pg_i:]) == 0:
        return last_pg_i - 7
    else:
        return last_pg_i


# REVIEW SERVICES
reviews: List[Review] = []
def get_reviews(track_id: int, repo: AbstractRepository) -> None:
    global reviews
    track = repo.get_track_by_id(track_id)

    # Order reviews by descending timestamp
    reviews = repo.get_reviews_by_track(track)
    reviews.reverse()

    # Move any reviews written by current user to start
    if 'user_name' in session:
        for index, r in enumerate(reviews):
            if r.user.user_name == session['user_name']:
                user_review = reviews.pop(index)
                reviews.insert(0, user_review)
                break

def get_next_review(index: int) -> Review | None:
    try:
        return reviews[index]
    except IndexError:
        return None

def get_reviews_last_pg() -> int:
    return len(reviews)

def create_review(r_text: str, r_rating: int, track_id: int, repo: AbstractRepository):
    if r_text == "":
        r_text = "<no text>"
    curr_user = repo.get_user(session['user_name'])
    track = repo.get_track_by_id(track_id)
    review = Review(track, r_text, r_rating, curr_user)
    repo.add_review(review)
