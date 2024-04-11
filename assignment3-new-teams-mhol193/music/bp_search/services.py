from typing import List

from music.adapters.a_repository import AbstractRepository
from music.domainmodel import track
import music.dtos as dtos
import music.domainmodel as dm

from music.dtos.dto_album_out import DtoAlbumOut
from music.dtos.dto_artist_out import DtoArtistOut

import smart_match


def get_all_genres(_repo: AbstractRepository):
    return _repo.get_genres()


search_results: List[dtos.DtoTrackOut] | List[dtos.DtoAlbumOut] | List[
    dtos.DtoArtistOut] = []


def get_track_results(keywords: str, genres: List[dm.Genre],
                      repo: AbstractRepository) -> None:
    global search_results
    _results = repo.get_tracks_by_genres(genres)
    _ranked_results = []
    # calc rank for each track based on similarity to search keyword
    for t in _results:
        rank = smart_match.similarity(keywords, t.title)
        if rank > 0.1:
            _ranked_results.append((rank, t))
    # sort tracks by rank 
    _ranked_results.sort(key=lambda x: x[0], reverse=True)
    # place first 2 pages global variable for display
    search_results = [dtos.DtoTrackOut(t[1]) for t in _ranked_results][:14]


def get_album_results(keywords: str, genres: List[dm.Genre],
                      repo: AbstractRepository) -> None:
    global search_results
    _results = repo.get_albums_by_genres(genres)
    _ranked_results = []
    # calc rank for each album based on similarity to search keyword
    for a in _results:
        rank = smart_match.similarity(keywords, a.title)
        if rank > 0.1:
            _ranked_results.append((rank, a))
    # sort albums by rank 
    _ranked_results.sort(key=lambda x: x[0], reverse=True)
    # convert each album to dto form
    albs_to_display = []
    for _ in _ranked_results:
        _album = _[1]
        try:
            tracks = repo.get_tracks_of_album(_album)
            artist = tracks[0].artist
            if artist is not None:
                artist = artist.full_name
            albs_to_display.append(DtoAlbumOut(_album, artist, tracks))
        except IndexError:
            print("ERROR", _album)
    # place in global variable for display
    search_results = albs_to_display[:14]


def get_artist_results(keywords: str, genres: List[dm.Genre],
                       repo: AbstractRepository) -> None:
    global search_results
    _results = repo.get_artists_by_genres(genres)
    _ranked_results = []
    # calc rank for each artist based on similarity to search keyword
    for a in _results:
        rank = smart_match.similarity(keywords, a.full_name)
        if rank > 0.1:
            _ranked_results.append((rank, a))
    # sort artists by rank
    _ranked_results.sort(key=lambda x: x[0], reverse=True)
    # convert each artist to dto form
    artists_to_display = []
    for _ in _ranked_results:
        _artist = _[1]
        tracks = repo.get_tracks_by_artist(_artist)
        artists_to_display.append(DtoArtistOut(_artist, tracks))
    # place in global variable for display
    search_results = artists_to_display[:14]





def get_next_results(start_index: int, no_of_items: int):
    items_to_disp = search_results[start_index: start_index + no_of_items]
    return items_to_disp


def get_results_last_page_index(no_of_tracks: int, repo: AbstractRepository):
    last_pg_i = (len(search_results) // no_of_tracks) * no_of_tracks
    if last_pg_i == len(search_results):
        return last_pg_i - no_of_tracks
    else:
        return last_pg_i
