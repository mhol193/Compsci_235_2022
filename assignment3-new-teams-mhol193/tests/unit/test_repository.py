from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User

from music.adapters.database_repository import SqlAlchemyRepository 

# TRACK TESTS
def test_repo_can_get_tracks_from_given_index(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    
    tracks_from_0 = repo.get_tracks_from(0)
    tracks_from_10 = repo.get_tracks_from(10)
    tracks_from_1000 = repo.get_tracks_from(1000)
    tracks_from_2000 = repo.get_tracks_from(2000)

    assert len(tracks_from_0) == 2000
    assert len(tracks_from_10) == 1990
    assert len(tracks_from_1000) == 1000
    # out of bounds start_index should return empty list
    assert len(tracks_from_2000) == 0

def test_repo_can_get_track_by_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    track = repo.get_track_by_id(134)
    # equality is based on track_id
    assert track == Track(134, "test track")

def test_repo_can_get_tracks_by_genre_filters(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # check if no filters returns all tracks
    all_tracks = repo.get_tracks_from(0)
    tracks_w_no_filter = repo.get_tracks_by_genres()
    assert all_tracks == tracks_w_no_filter

    # check if 1 filter works
    filtered_tracks = repo.get_tracks_by_genres([Genre(41, "Electroacoustic"), ])
    assert len(filtered_tracks) == 2

    # check if 2 filters work
    filters = [Genre(41, "Electroacoustic"), Genre(43, "Radio Art")]
    filtered_tracks = repo.get_tracks_by_genres(filters)
    assert len(filtered_tracks) == 3

    # check if tracks with 2 genres are not counted twice
    filters = [Genre(33, "Psych-Folk"), Genre(107, "Ambient")]
    filtered_tracks = repo.get_tracks_by_genres(filters)
    assert len(filtered_tracks) == 11


# ALBUM TESTS
def test_repo_can_get_albums_from_given_index(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    alb_from_0 = repo.get_albums_from(0)
    assert len(alb_from_0) == 427

    alb_from_427 = repo.get_albums_from(427)
    assert len(alb_from_427) == 0

def test_repo_can_get_album_tracks(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    album = Album(1, "AWOL - A Way Of Life")
    tracks = repo.get_tracks_of_album(album)
    assert len(tracks) == 4

def test_repo_can_get_album_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    album = Album(4, "Niris")
    genres = repo.get_genres_of_album(album)
    assert len(genres) == 2
    assert all(g in genres for g in [Genre(76, "Experimental Pop"), Genre(103, "Singer-Songwriter")])

def test_repo_can_get_albums_by_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # check if no filters returns all albums
    all_albums = repo.get_albums_from(0)
    albums_w_no_filter = repo.get_albums_by_genres()
    assert all_albums == albums_w_no_filter

    # check if 1 filter works
    filtered_tracks = repo.get_albums_by_genres([Genre(41, "Electroacoustic"), ])
    assert len(filtered_tracks) == 1

    # check if 2 filters work
    filters = [Genre(41, "Electroacoustic"), Genre(43, "Radio Art")]
    filtered_tracks = repo.get_albums_by_genres(filters)
    assert len(filtered_tracks) == 2

    # check if albums with 2 genres are not counted twice
    filters = [Genre(33, "Psych-Folk"), Genre(107, "Ambient")]
    filtered_tracks = repo.get_albums_by_genres(filters)
    assert len(filtered_tracks) == 6


# ARTIST TESTS
def test_repo_can_get_tracks_by_artist(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # non-existent artist should return empty list
    tracks = repo.get_tracks_by_artist(Artist(5000, "random artist"))
    assert tracks == []

    # Artist "AWOL" should return 4 tracks
    tracks = repo.get_tracks_by_artist(Artist(1, "AWOL"))
    assert all(t in tracks for t in [Track(2, ""), Track(3, ""), Track(5, ""), Track(134, "")])

    # Artst 522 should return 15 tracks
    tracks = repo.get_tracks_by_artist(Artist(522, "AWOL"))
    assert len(tracks) == 15

    # Artist "Nicky Cook" should return 13 tracks
    tracks = repo.get_tracks_by_artist(Artist(4, ""))
    assert len(tracks) == 13

def test_repo_can_get_artist_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genres_of_artist(Artist(1, "AWOL"))
    assert genres == [Genre(21, "hip-hop"), ]

    # artist with multiple tracks and genres does not add duplicate genres
    genres = repo.get_genres_of_artist(Artist(10, "Lucky Dragons"))
    assert len(genres) == 2
    assert all(g in genres for g in [Genre(22, "Audio Collage"), Genre(15, "Electronic")])

def test_repo_can_get_artists_by_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # check no filters returns all artists
    artists = repo.get_artists_by_genres()
    assert len(artists) == 263

     # check if 1 filter works
    artists = repo.get_artists_by_genres([Genre(41, "Electroacoustic"), ])
    assert len(artists) == 1
    assert artists ==[Artist(126, "EKG")]

    # check if albums with 2 genres are not counted twice
    filters = [Genre(43, "Radio Art"), Genre(41, "Electroacoustic")]
    artists = repo.get_artists_by_genres(filters)
    assert len(artists) == 2
    assert all(a in artists for a in [Artist(126, "EKG"), Artist(1700, "")])


# REVIEW TESTS
def test_repo_can_get_user_review_for_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    track = Track(1, "")
    track.track_duration = 0
    track.track_img_url = ''
    review1 = Review(track, "test review", 5, User("user1", "password", 'bear.png'))
    review2 = Review(track, "test review", 5, User("user2", "password", 'bear.png'))
    repo.add_review(review1)
    repo.add_review(review2)

    # should only return first review
    repo_review = repo.get_user_review_for_track("user1", Track(1, ""))
    assert repo_review == review1

    # test random user returns None
    repo_review = repo_review = repo.get_user_review_for_track("user3", Track(1, ""))
    assert repo_review == None

def test_repo_can_get_all_reviews_for_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    track = Track(1, "")
    track.track_duration = 0
    track.track_img_url = ''
    review1 = Review(track, "test review", 5, User("user1", "password", 'bear.png'))
    review2 = Review(track, "test review", 5, User("user2", "password", 'bear.png'))
    repo.add_review(review1)
    repo.add_review(review2)

    # should return both reviews
    reviews = repo.get_reviews_by_track(Track(1, ""))
    assert any(r in [review1, review2] for r in reviews)     


# USER TESTS
def test_repo_can_get_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User("thorke", "", "bear.png")
    repo_user = repo.get_user('thorke')
    assert repo_user == user

    # should not return None if user doesn't exist
    repo_user = repo.get_user('random user')
    assert repo_user is None

def test_repo_can_add_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('user1', "", 'bear.png')
    repo.add_user(user)
    assert user == repo.get_user('user1')
