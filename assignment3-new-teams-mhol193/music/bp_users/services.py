from music.adapters.a_repository import AbstractRepository
from music.domainmodel import user

from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.user import User

from music.dtos.dto_track_out import DtoTrackOut
from music.dtos.dto_user_out import DtoUserOut

from typing import List

from flask import session

# ***********************************************
#   FAV TRACK SERVIVCES
# ***********************************************
def add_track_to_user_favs(track_id: int, user_name: str, repo: AbstractRepository) -> None:
    repo.add_favourite_track(user_name, track_id)

def remove_track_from_user_favs(track_id: int, user_name: str, repo: AbstractRepository) -> None:
    repo.remove_favourite_track(user_name, track_id)

def get_user_fav_tracks(user_name: str, start_index: int, no_of_tracks: int, repo: AbstractRepository) -> List[Track]:
    _u = repo.get_user(user_name)
    dtos = [DtoTrackOut(t, is_fav=True) for t in _u.liked_tracks]
    return dtos[start_index: start_index+no_of_tracks]

def get_fav_tracks_last_page_index(user_name: str, no_of_tracks: int, repo: AbstractRepository) -> int:
    fav_tracks = repo.get_user(user_name).liked_tracks
    last_pg_i = (len(fav_tracks) // no_of_tracks) * no_of_tracks
    if last_pg_i == len(fav_tracks):
        return last_pg_i - no_of_tracks
    else:
        return last_pg_i

# Used by other bp
def check_if_fav_track(track: Track, repo: AbstractRepository) -> bool:
    if 'user_name' in session: 
        fav_tracks = repo.get_user(session['user_name']).liked_tracks
        return (track in fav_tracks)
    else:
        return False

def get_track_rating(track: Track, repo: AbstractRepository) -> int:
    if 'user_name' in session:
        _r = repo.get_user_review_for_track(session['user_name'], track)
        return _r.rating if _r is not None else 0
    else:
        return 0

# ***********************************************
#   FRIEND SERVIVCES
# ***********************************************
friendable_users: List[User] = []
curr_requests: List[User] = []
curr_friends: List[User] = []

# Find Friends
def get_friendable_users(curr_user_name: str, repo: AbstractRepository) -> None:
    users = repo.get_all_users().copy()
    curr_user = repo.get_user(curr_user_name)

    for i in range(len(users)-1, -1, -1):
        user = users[i]
        # can't add yourself as a friend
        if user == curr_user:
            # print("removing curr user", user)
            users.remove(user)
        # can't add friends that have already requested you
        elif user in curr_user.requests:
            # print("removing requested user", user)
            users.remove(user)
        # can't re-add friends
        elif user in curr_user.friends:
            # print("removing friend", user)
            users.remove(user)

    users = [DtoUserOut(u, check_if_request_sent(curr_user_name, u.user_name, repo)) for u in users]
    global friendable_users
    friendable_users = users

def get_next_users(start_index: int, no_items_to_display: int) -> List[User]:
    return friendable_users[start_index: start_index + no_items_to_display]

def get_users_last_pg_num(num_items_to_display: int) -> int:
    no_of_users = len(friendable_users)
    _last_pg = (no_of_users // num_items_to_display)
    if no_of_users % num_items_to_display == 0:
        return _last_pg - 1
    else:
        return _last_pg


# Requests
def send_request_to_user(curr_u_name: str, request_u_name: str, repo: AbstractRepository) -> str:
    user_to_request = repo.get_user(request_u_name)
    curr_user = repo.get_user(curr_u_name)
    if curr_user in user_to_request.friends:
        return "User is already your friend!"
    elif curr_user in user_to_request.requests:
        return "Request already sent!"
    else:
        repo.send_request(user_to_request, curr_user)
        return "Request sent!"
    

def check_if_request_sent(curr_u_name: str, request_u_name: str, repo: AbstractRepository) -> bool:
    request_user = repo.get_user(request_u_name)
    curr_user = repo.get_user(curr_u_name)
    return curr_user in request_user.requests

def accept_request(curr_u_name: str, request_u_name: str, repo: AbstractRepository) -> str:
    user_sending_request = repo.get_user(request_u_name)
    curr_user = repo.get_user(curr_u_name)
    if user_sending_request in curr_user.requests:
        repo.add_friend(curr_user, user_sending_request)
        repo.add_friend(user_sending_request, curr_user)
        repo.remove_request(curr_user, user_sending_request)
    return "Request accepted!"

def decline_request(curr_u_name: str, request_u_name: str, repo: AbstractRepository) -> str:
    user_sending_request = repo.get_user(request_u_name)
    curr_user = repo.get_user(curr_u_name)
    if user_sending_request in curr_user.requests:
        repo.remove_request(curr_user, user_sending_request)
    return "Request declined"
   
def get_curr_requests(curr_u_name: str, repo: AbstractRepository) -> None:
    curr_user = repo.get_user(curr_u_name)
    global curr_requests
    curr_requests = curr_user.requests

def get_next_requests(start_index: int, no_items_to_display: int) -> List[User]:
    next_reqs = curr_requests[start_index: start_index + no_items_to_display]
    return [DtoUserOut(u) for u in next_reqs]

def get_requests_last_pg_num(num_items_to_display: int) -> int:
    no_of_requests = len(curr_requests)
    _last_pg = (no_of_requests // num_items_to_display)
    if no_of_requests % num_items_to_display == 0:
        return _last_pg - 1
    else:
        return _last_pg


# Current Friends
def get_curr_friends(curr_u_name: str, repo: AbstractRepository) -> None:
    curr_user = repo.get_user(curr_u_name)
    global curr_friends
    curr_friends = curr_user.friends

def get_next_friends(start_index: int, no_items_to_display: int) -> List[User]:
    next_friends = curr_friends[start_index: start_index + no_items_to_display]
    return [DtoUserOut(f) for f in next_friends]

def get_friends_last_pg_num(num_items_to_display: int) -> int:
    no_of_friends = len(curr_friends)
    _last_pg = (no_of_friends // num_items_to_display)
    if no_of_friends % num_items_to_display == 0:
        return _last_pg - 1
    else:
        return _last_pg

def unfriend(curr_u_name: str, friend_u_name: str, repo: AbstractRepository) -> None:
    curr_user = repo.get_user(curr_u_name)
    friend_user = repo.get_user(friend_u_name)
    repo.remove_friend(friend_user, curr_user)
    repo.remove_friend(curr_user, friend_user)
