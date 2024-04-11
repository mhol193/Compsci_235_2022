import pytest
from flask import session
import html
import markupsafe

from music.adapters.database_repository import SqlAlchemyRepository

from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.user import User

from music.bp_browse import services as browse_services
from music.bp_search import services as search_services



# from music.bp_authentication import authentication as views_auth
# from music.bp_browse import views_browse
# from music.bp_users import users_views
# from music.bp_search import views_search


# ***********************************************
#   LOGIN LOGOUT REGISTER
# ***********************************************

def test_register(client):
    # Check that we retrieve the register page.
    with client:
        response_code = client.get('/authentication/register').status_code
        assert response_code == 200

        # Check that we can register a user successfully, supplying a valid user name and password.
        response = client.post(
            '/authentication/register',
            data={'user_name': 'gmicha', 'password': 'CarelessWhisper1984'}
        )
        assert response.status_code == 302
        assert response.headers['Location'] == '/authentication/login'

@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Username is required'),
        ('test', '', b'Password is required'),
        ('test', 'test', b'Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'),
        ))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    # Check that we can retrieve the login page.
    with client:
        status_code = client.get('/authentication/login').status_code
        assert status_code == 200

        # Check that a successful login generates a redirect to the homepage.
        response = auth.login()
        # assert session['user_name'] == 'thorke'
        assert response.status_code == 302
        assert response.headers['Location'] == '/alltracks1'

        # Check that a session has been created for the logged-in user.
    with client:
        client.get('/alltracks1')
        assert session['user_name'] == 'thorke'

def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_name' not in session

# ***********************************************
#   BROWSING TRACKS
# ***********************************************

def test_can_see_tracks_page_by_page(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_tracks = repo.get_tracks_from(0)
    # check all 286 pages
    for _pg_num in range(1, 287):
        response = client.get(f'/alltracks{_pg_num}')
        start_i = (_pg_num-1) * 7
        for t in all_tracks[start_i: start_i+7]:
            # only check first 10 char as some are trimmed
            assert markupsafe.escape(t.title[:10]) in response.text

def test_can_see_album_page_by_page(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_albums = repo.get_albums_from(0)
    # check all 62 pages
    for _pg_num in range(1, 62):
        response = client.get(f'/allalbums{_pg_num}')
        start_i = (_pg_num-1) * 7
        for a in all_albums[start_i: start_i+7]:
            # only check first 10 char as some are trimmed
            assert markupsafe.escape(a.title[:10]) in response.text

def test_can_see_artist_page_by_page(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_artists = repo.get_artists()
    # check all 34 pages
    for _pg_num in range(1, 34):
        response = client.get(f'/allartists{_pg_num}')
        start_i = (_pg_num-1) * 8
        for a in all_artists[start_i: start_i+8]:
            # only check first 10 char as some are trimmed
            assert markupsafe.escape(a.full_name[:10]) in response.text

def test_can_see_specific_album_tracks(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_albums = repo.get_albums_from(0)
    # for every album
    for album in all_albums:
        alb_id = album.album_id
        album_tracks = repo.get_tracks_of_album(Album(alb_id, ""))

        # get num of pages
        pages = len(album_tracks) // 7
        if len(album_tracks) % 7 != 0:
            pages += 1

        # for page of a single album
        for pg in range(pages):
            print(f"CHECKING ALBUM {alb_id} PAGE {pg+1}")
            response = client.get(f'/album{alb_id}/{pg+1}')
            start_i = (pg) * 7
            # check if the corresponding tracks are in the correct page
            for track in album_tracks[start_i: start_i+7]:
                assert markupsafe.escape(track.title[:10]) in response.text

def test_can_see_specific_artist_tracks(client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_artists = repo.get_artists()
    # for every artist
    for artist in all_artists:
        artist_id = artist.artist_id
        artist_tracks = repo.get_tracks_by_artist(Artist(artist_id, ""))

        # get num of pages
        pages = len(artist_tracks) // 7
        if len(artist_tracks) % 7 != 0:
            pages += 1
    
        # for page of a single artist
        for pg in range(pages):
            print(f"CHECKING ARTIST {artist_id} PAGE {pg+1}")
            response = client.get(f'/artist{artist_id}/{pg+1}')
            start_i = (pg) * 7
            # check if the corresponding tracks are in the correct page
            for track in artist_tracks[start_i: start_i+7]:
                assert markupsafe.escape(track.title[:10]) in response.text

# ***********************************************
#   FAVOURITE TRACKS
# ***********************************************

def test_can_add_and_remove_fav_track(auth, client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    with client:
        auth.login()
        all_tracks = repo.get_tracks_from(0)[:7]

        # adding tracks
        track_count = 0
        for track in all_tracks:
            # add track
            print("ADDING TRACK", track.title)
            response = client.get(f'add-fav-track{track.track_id}')
            assert response.status_code == 200
            assert "Added to your favourites!" in response.text
            track_count += 1
            # check track in fav tracks page
            response = client.get(f'myfavourites1')
            assert track.title[:10] in response.text
            curr_user = repo.get_user(session['user_name'])
            assert len(curr_user.liked_tracks) == track_count

        # removing
        for track in all_tracks:
            print("REMOVING TRACK", track.title)
            response = client.get(f'remove-fav-track{track.track_id}')
            assert response.status_code == 200
            assert "Removed from your favourites" in response.text
            track_count -= 1
            response = client.get(f'myfavourites1')
            assert track.title[:10] not in response.text
            curr_user = repo.get_user(session['user_name'])
            assert len(curr_user.liked_tracks) == track_count

# ***********************************************
#   REVIEWS
# ***********************************************        

def test_can_user_can_leave_review(auth, client):
    auth.login()
    # can retrive review page
    response = client.get('add-review2')
    assert response.status_code == 200
    
    # can post review and be redirected to track page
    form_data = {'rating_field': '4', 'text_area': "good song"}
    response = client.post('add-review2', data=form_data)
    assert response.headers['Location'] == '/track2/1'

    # can see added review
    response = client.get('/track2/1')
    assert "good song" in response.text
    assert "4 out of 5" in response.text

    # can add review with empty text
    form_data = {'rating_field': "1", 'text_area': ""}
    response = client.post('add-review2', data=form_data)
    assert response.headers['Location'] == '/track2/1'

    # empty review displays as <no text>
    response = client.get('/track2/1')
    assert markupsafe.escape("<no text>") in response.text
    assert "1 out of 5" in response.text

    # test others can see review
    auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
    response = client.get('/track2/1')
    assert markupsafe.escape("<no text>") in response.text
    assert "1 out of 5" in response.text
  
def test_user_own_review_is_displayed_first(auth, client, session_factory):
    repo = SqlAlchemyRepository(session_factory)

    with client:
        reviews = [
            ('thorke', 'cLQ^C#oFXloS'),
            ('fmerc', 'mvNNbc1eLA$i'),
            ('mjack', 'vpwJv4A7%#9b'),
            ('lam', 'f07Zsswc'),
            ('skolis', '4NC7adVF'),
        ]

        for i, r in enumerate(reviews):
            auth.login(user_name=r[0], password=r[1])
            form_data = {'rating_field': str(i+1), 'text_area': f"{r[0]} review"}
            client.post('add-review2', data=form_data)
            assert len(repo.get_reviews_by_track(Track(2, ''))) == i+1


        # check thorke review shows first
        auth.login()
        response = client.get('/track2/1')
        assert "thorke review" in response.text

        # check rest of reviews are shown latest to oldest
        for i in range(4, 0, -1):
            r = reviews[i]
            response = client.get(f'/track2/{(5-i) + 1}')
            assert r[0] in response.text
            assert f"{i+1} out of 5" in response.text

# ***********************************************
#   SEARCH
# ***********************************************

def test_can_see_search_page(auth, client, session_factory):
    repo = SqlAlchemyRepository(session_factory)
    search_by = ['Tracks', 'Albums', 'Artists']

    for _ in search_by:
        response = client.get(f'/search{_}')
        assert response.status_code == 200

        # check all genre filters are shown
        genres = repo.get_genres()
        for g in genres:
            assert g.name in response.text

def test_can_search_tracks_by_genres(auth, client, repo: SqlAlchemyRepository):
    genres = repo.get_genres()
    for g in genres:
        form_data = {'search_field': "the", g.name: "True"}
        response = client.post('/searchTracks', data=form_data)
        assert response.headers['Location'] == '/results1/1'
        results = search_services.get_next_results(0, 7)
        for r in results:
            assert r.title in response.text
            track = repo.get_track_by_id(r.track_id)
            assert g in track.genres

# ***********************************************
#   COOL FEATURE
# ***********************************************

def test_can_see_frienable_users(auth, client, repo: SqlAlchemyRepository):
    auth.login()
    response_pg1 = client.get('/findfriends1')
    response_pg2 = client.get('/findfriends2')
    assert response_pg1.status_code == 200
    assert response_pg2.status_code == 200


    friendable_users = repo.get_all_users().copy()
    friendable_users.remove(User('thorke', '', ''))

    for user in friendable_users:
        assert user.user_name in response_pg1.text \
            or user.user_name in response_pg2.text

def test_send_and_cancel_fiend_request(auth, client):
    with client:
        auth.login()
        curr_u_name = session['user_name']
        response = client.get('/add-friendfmerc')
        assert "Request sent!" in response.text

        # can't send request to same person twice
        response = client.get('/add-friendfmerc')
        assert "Request already sent!" in response.text

        # confirm fmerc recieved the request
        auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
        response = client.get('/myrequests1')
        assert 'thorke' in response.text

        # test thorke can cancel request
        auth.login()
        response = client.get('/findfriends1')
        assert 'fmerc' in response.text
        response = client.get('/cancel-requestfmerc')
        assert "Canceled request!" in response.text

        # confirm fmerc can't see request anymore 
        auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
        response = client.get('/myrequests1')
        assert 'thorke' not in response.text

def test_can_decline_request(auth, client):
    with client:
        # send request
        auth.login()
        response = client.get('/add-friendfmerc')
        assert "Request sent!" in response.text

        # decline request
        auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
        response = client.get('/decline-requestthorke')
        assert "Request declined" in response.text

        # confrim can fmerc can't see request anymore
        response = client.get('/myrequests1')
        assert 'thorke' not in response.text

def test_can_accept_request(auth, client):
    with client: 
        # send request
        auth.login()
        response = client.get('/add-friendfmerc')
        assert "Request sent!" in response.text

        # decline request
        auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
        response = client.get('accept-requestthorke')
        assert "Request accepted!" in response.text

        # check both can see each other as friends
        response = client.get('myfriends1')
        assert 'thorke' in response.text
        auth.login()
        response = client.get('myfriends1')
        assert 'fmerc' in response.text

def test_can_unfriend_eachother(auth, client):
    with client:
        # thorke adds fmerc as friend
        auth.login()
        response = client.get('/add-friendfmerc')

        # unfriend fmerc
        response = client.get('unfriendfmerc')
        assert "Unfriended fmerc" in response.text

        # check they are no longer friends
        response = client.get('/myfriends1')
        assert "fmerc" not in response.text
        auth.login(user_name='fmerc', password='mvNNbc1eLA$i')
        response = client.get('/myfriends1')
        assert "thorke" not in response.text






