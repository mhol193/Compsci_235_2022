import pytest
from flask import session

# import service layers
from music.bp_authentication import services as auth_services
from music.bp_browse import services as browse_services
from music.bp_search import services as search_services
from music.bp_users import services as users_services

# import domain model
from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.review import Review
from music.domainmodel.genre import Genre
from music.domainmodel.user import User



from music.bp_authentication.services import AuthenticationException
from music.adapters.database_repository import SqlAlchemyRepository



# BP AUTHENTICATION TESTS

def test_can_add_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    new_user_name = 'jz'
    new_password = 'abcd1A23'
    auth_services.add_user(new_user_name, new_password, repo)

    user_as_dict = auth_services.get_user(new_user_name, repo)
    assert user_as_dict['user_name'] == new_user_name

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')

def test_cannot_add_user_with_existing_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    user_name = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(user_name, password, repo)

def test_authentication_with_valid_credentials(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, repo)

    try:
        auth_services.authenticate_user(new_user_name, new_password, repo)
    except AuthenticationException:
        assert False

def test_authentication_with_invalid_credentials(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_user_name, '0987654321', repo)


# BP BROWSE TESTS
# tracks
def test_services_can_get_next_7_tracks(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    with client:
        # get session context
        client.get('/alltracks1')
        dto_tracks = browse_services.get_next_seven_tracks(0, repo)
        assert len(dto_tracks) == 7

    tracks_list = [Track(2, ''), Track(3, ''), 
                    Track(5, ''), Track(10, ''), 
                    Track(20, ''), Track(26, ''), 
                    Track(30, '')]

    # Services returns trackDTO while tracks_list has Track objects,
    # so we test for equality by comparing track_ids
    for i, track_dto in enumerate(dto_tracks):
        assert track_dto.track_id == tracks_list[i].track_id

def test_services_can_get_correct_track_last_page_index(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    last_pg_i = browse_services.get_tracks_last_page_index(repo)
    # There are 2000 tracks. Each page displays 7 tracks.
    # Therefore, index for first track on the last page should be 1995
    assert last_pg_i == 1995
    # 2000 % 7 = 5, so there should be 5 tracks on the last page
    last_pg_tracks = repo.get_tracks_from(last_pg_i)
    assert len(last_pg_tracks) == 5

# albums
def test_services_can_get_next_7_albums(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    repo_next_albums = browse_services.get_next_seven_albums(0, repo)
    assert len(repo_next_albums) == 7

def test_services_can_get_correct_album_last_page_index(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    last_pg_i = browse_services.get_albums_last_page_index(repo)
    # There are 427 albums. Each page displays 7 albums.
    # 427 is divisble by 7, so index for first track on the last page should be 420
    assert last_pg_i == 420
    # 427 % 7 = 0, so there should be 7 albums on the last page
    last_pg_albums = repo.get_albums_from(last_pg_i)
    assert len(last_pg_albums) == 7

def test_services_can_get_next_7_tracks_of_album(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    with client:
        client.get('/album71/1')
        dto_tracks = browse_services.get_next_seven_tracks_of_album(71, 0, repo)
        assert len(dto_tracks) == 7

    tracks_list = [Track(156, ''), Track(157, ''), 
                    Track(158, ''), Track(159, ''), 
                    Track(160, ''), Track(161, ''), 
                    Track(162, '')]

    for i, track_dto in enumerate(dto_tracks):
        assert track_dto.track_id == tracks_list[i].track_id

# artists
def test_services_can_get_next_8_artists(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    # test returns 8 artists
    next_artists = browse_services.get_next_eight_artists(0, repo)
    assert len(next_artists) == 8
    
    # test can return less than 8 artists on last page
    next_artists = browse_services.get_next_eight_artists(257, repo)
    assert len(next_artists) < 8

def test_services_can_get_artists_last_pg_num(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    last_pg_num = browse_services.get_artists_last_page_num(repo)
    # There are 263 artists. Each page displays 8 artists.
    # So last page should be 263 // 8 = 32 (0 is first page)
    assert last_pg_num == 32

def test_services_can_get_next_7_tracks_of_artist(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    with client:
        client.get('/artist4/1')
        dto_tracks = browse_services.get_next_seven_tracks_of_artist(4, 0, repo)
        assert len(dto_tracks) == 7

        dto_tracks = browse_services.get_next_seven_tracks_of_artist(4, 7, repo)
        assert len(dto_tracks) == 6

# reviews testing done in e2e

# BP SEARCH TESTS
def test_services_can_get_track_by_exact_keyword(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    search_services.get_track_results("the appLemen", None, repo)
    top_result = search_services.get_next_results(0, 1)
    assert top_result[0].track_id == 556

def test_services_can_get_track_by_typo_keyword(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    search_services.get_track_results("the appemen", None, repo)
    top_result = search_services.get_next_results(0, 1)
    assert top_result[0].track_id == 556

def test_services_can_get_album_by_exact_keyword(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    search_services.get_album_results("AWoL - a way of life", None, repo)
    top_result = search_services.get_next_results(0, 1)
    assert top_result[0].album_id == 1

def test_services_can_get_artist_by_exact_keyword(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    search_services.get_artist_results("kurt vile", None, repo)
    top_result = search_services.get_next_results(0, 1)
    assert top_result[0].artist_id == 6

def test_services_can_search_only_selected_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    genre = Genre(21, 'hiphop')
    search_services.get_track_results("The", [genre, ], repo)
    results = search_services.get_next_results(0, 21)
    for r in results:
        track = repo.get_track_by_id(r.track_id)
        assert genre in track.genres

# BP USER TESTS
def test_services_can_get_friendable_users(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    users_services.get_friendable_users('thorke', repo)
    results = users_services.get_next_users(0, 14)
    assert len(results) == len(repo.get_all_users()) - 1
    assert all(not u.user_name == 'thorke' for u in results)

def test_services_can_send_friend_request(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    req_user = repo.get_user('fmerc')
    assert User('thorke', '', '') not in req_user.requests
    users_services.send_request_to_user('thorke', 'fmerc', repo)
    assert User('thorke', '', '') in req_user.requests
    assert User('thorke', '', '') not in req_user.friends
    message = users_services.send_request_to_user('thorke', 'fmerc', repo)
    assert len(req_user.requests) == 1
    assert message == "Request already sent!"

def test_services_can_accept_friend_request(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    users_services.send_request_to_user('thorke', 'fmerc', repo)
    users_services.accept_request('fmerc', 'thorke', repo)
    curr_user = repo.get_user('fmerc')
    req_user = repo.get_user('thorke')
    assert req_user not in curr_user.requests
    assert curr_user in req_user.friends
    assert req_user in curr_user.friends

def test_services_can_decline_friend_request(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    users_services.send_request_to_user('thorke', 'fmerc', repo)
    users_services.decline_request('fmerc', 'thorke', repo)
    curr_user = repo.get_user('fmerc')
    req_user = repo.get_user('thorke')
    assert req_user not in curr_user.requests
    assert curr_user not in req_user.friends
    assert req_user not in curr_user.friends

def test_services_can_remove_friend(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    users_services.send_request_to_user('thorke', 'fmerc', repo)
    users_services.accept_request('fmerc', 'thorke', repo)
    curr_user = repo.get_user('fmerc')
    req_user = repo.get_user('thorke')
    assert curr_user in req_user.friends
    users_services.unfriend('fmerc', 'thorke', repo)
    assert req_user not in curr_user.friends
    assert curr_user not in req_user.friends


