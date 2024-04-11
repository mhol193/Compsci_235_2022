from flask import Blueprint, render_template, session

import music.bp_users.services as services
import music.adapters.a_repository as repo

from music.bp_authentication.authentication import login, login_required
from music.domainmodel.user import User


bp_users = Blueprint(
    'bp_users', __name__)

# fav tracks
@bp_users.route('/add-fav-track<int:track_id>')
@login_required
def add_track_to_fav(track_id: int):
    if 'user_name' in session:
        services.add_track_to_user_favs(track_id, session['user_name'], repo.repo_instance)
        return render_template('bp_users/display_message.html', message="Added to your favourites!")


@bp_users.route('/remove-fav-track<int:track_id>')
@login_required
def remove_track_from_fav(track_id: int):
    if 'user_name' in session:
        services.remove_track_from_user_favs(track_id, session['user_name'], repo.repo_instance)
        return render_template('bp_users/display_message.html', message="Removed from your favourites")


@bp_users.route('/myfavourites<int:page_num>')
@login_required
def list_favourites(page_num: int):
    curr_user = session['user_name']
    start_index = (page_num - 1) * 7
    items_to_disp = services.get_user_fav_tracks(curr_user, start_index,
                                                7, repo.repo_instance)
    last_pg_i = services.get_fav_tracks_last_page_index(curr_user, 7, 
                                                        repo.repo_instance)
    last_page_num = int((last_pg_i / 7) + 1)

    return render_template("bp_users/fav_tracks.html",
                    tracks=items_to_disp,
                    curr_page=page_num,
                    last_page_num=last_page_num)


# Friending
@bp_users.route('/add-friend<string:friend_u_name>')
@login_required
def friend_request(friend_u_name: str):
    message = services.send_request_to_user(session['user_name'],
                                    friend_u_name,
                                    repo.repo_instance)
    return render_template('bp_users/display_message.html', message=message)

@bp_users.route('/cancel-request<string:request_u_name>')
@login_required
def cancel_request(request_u_name: str):
    message = services.decline_request(request_u_name, 
                            session['user_name'], 
                            repo.repo_instance)
    return render_template('bp_users/display_message.html', 
                            message="Canceled request!")

@bp_users.route('/accept-request<string:request_u_name>')
@login_required
def accept_request(request_u_name: str):
    message = services.accept_request(session['user_name'], 
                            request_u_name, 
                            repo.repo_instance)
    return render_template('bp_users/display_message.html', message=message)

@bp_users.route('/decline-request<string:request_u_name>')
@login_required
def decline_request(request_u_name: str):
    message = services.decline_request(session['user_name'], 
                            request_u_name, 
                            repo.repo_instance)
    return render_template('bp_users/display_message.html', message=message)

@bp_users.route('/unfriend<string:friend_u_name>')
@login_required
def unfriend_user(friend_u_name: str):
    services.unfriend(session['user_name'], friend_u_name, repo.repo_instance)
    return render_template('bp_users/display_message.html', message=f"Unfriended {friend_u_name}")


@bp_users.route('/myfriends<int:page_num>')
@login_required
def list_friends(page_num: int):
    start_index = (page_num - 1) * 7
    services.get_curr_friends(session['user_name'], 
                              repo.repo_instance)
    items_to_disp = services.get_next_friends(start_index, 7)
    last_pg_i = services.get_friends_last_pg_num(7)
    last_page_num = int((last_pg_i / 7) + 1)

    return render_template("bp_users/friends.html",
                    selected_tab="curr_friends",
                    users=items_to_disp,
                    curr_page=page_num,
                    last_page_num=last_page_num)

@bp_users.route('/myrequests<int:page_num>')
@login_required
def list_requests(page_num: int):
    curr_user = session['user_name']
    services.get_curr_requests(curr_user, repo.repo_instance)
    start_index = (page_num - 1) * 7
    items_to_disp = services.get_next_requests(start_index, 7)
    last_page_num = services.get_requests_last_pg_num(7) + 1

    return render_template("bp_users/friends.html",
                    selected_tab="requests",
                    users=items_to_disp,
                    curr_page=page_num,
                    last_page_num=last_page_num)

@bp_users.route('/findfriends<int:page_num>')
@login_required
def list_users(page_num: int):
    curr_user = session['user_name']
    services.get_friendable_users(curr_user, repo.repo_instance)
    start_index = (page_num - 1) * 7
    items_to_disp = services.get_next_users(start_index, 7)
    last_page_num = services.get_users_last_pg_num(7) + 1

    return render_template("bp_users/friends.html",
                    selected_tab="find_friends",
                    users=items_to_disp,
                    curr_page=page_num,
                    last_page_num=last_page_num)
