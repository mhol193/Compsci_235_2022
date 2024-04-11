from flask import Blueprint
from flask import render_template, session, redirect, url_for

from music.domainmodel.track import Track
from music.domainmodel.review import Review

# Repo and Services layer
import music.bp_browse.services as services
import music.adapters.a_repository as repo
from music.bp_authentication.authentication import login_required

# WTF forms
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import RadioField, SubmitField, TextAreaField


bp_browse: Blueprint = Blueprint("bp_browse", __name__)

# TODO: rating stars
@bp_browse.route('/alltracks<int:page_num>', methods=["GET"])
def list_tracks(page_num: int):
    start_index = (page_num-1) * 7
    tracks_to_disp = services.get_next_seven_tracks(start_index, repo.repo_instance)
    last_page_num = int((services.get_tracks_last_page_index(repo.repo_instance) / 7) + 1)

    return render_template("bp_browse/browse_tracks.html", 
                            tracks=tracks_to_disp, 
                            curr_page=page_num,
                            last_page_num=last_page_num)

@bp_browse.route('/allalbums<int:page_num>', methods=["GET"])
def list_albums(page_num: int):
    start_index = (page_num-1) * 7
    albums_to_disp = services.get_next_seven_albums(start_index, repo.repo_instance)
    last_page_num = int((services.get_albums_last_page_index(repo.repo_instance)/7) + 1)

    return render_template("bp_browse/browse_albums.html",
                            albums=albums_to_disp,
                            curr_page= page_num,
                            last_page_num=last_page_num)

@bp_browse.route('/allartists<int:page_num>', methods=["GET"])
def list_artists(page_num: int):
    start_index = (page_num-1) * 8
    artists_to_disp = services.get_next_eight_artists(start_index, repo.repo_instance)
    last_page_num = int(services.get_artists_last_page_num(repo.repo_instance) + 1)

    return render_template("bp_browse/browse_artists.html",
                            artists=artists_to_disp,
                            curr_page= page_num,
                            last_page_num=last_page_num)


# TODO: rating stars
@bp_browse.route('/album<int:resource_id>/<int:page_num>', methods=["GET"])
def list_album_tracks(resource_id:int, page_num: int):
    start_index = (page_num-1) * 7
    tracks_to_disp = services.get_next_seven_tracks_of_album(resource_id, start_index, repo.repo_instance)
    last_page_num = int((services.get_last_pg_index_of_single_album(resource_id, repo.repo_instance) / 7) + 1)

    return render_template("bp_browse/browse_single_album.html", 
                            tracks=tracks_to_disp, 
                            curr_page=page_num,
                            last_page_num=last_page_num)

# TODO: rating stars
@bp_browse.route('/artist<int:resource_id>/<int:page_num>', methods=["GET"])
def list_artist_tracks(resource_id:int, page_num: int):
    start_index = (page_num-1) * 7
    tracks_to_disp = services.get_next_seven_tracks_of_artist(resource_id, start_index, repo.repo_instance)
    last_page_num = int((services.get_last_pg_index_of_single_artist(resource_id, repo.repo_instance) / 7) + 1)

    return render_template("bp_browse/browse_single_artist.html", 
                            tracks=tracks_to_disp, 
                            curr_page=page_num,
                            last_page_num=last_page_num)




@bp_browse.route('/track<int:resource_id>/<int:page_num>', methods=["GET"])
def track_page(resource_id: int, page_num: int):
    track_dto = services.get_track(resource_id, repo.repo_instance)

    services.get_reviews(track_dto.track_id, repo.repo_instance)
    review = services.get_next_review(page_num-1)

    return render_template('bp_browse/browse_track_page.html',
                            track=track_dto,
                            review=review,
                            curr_page=page_num,
                            resource_id=resource_id,
                            last_page_num=services.get_reviews_last_pg())

@bp_browse.route('/add-review<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_review(track_id: int):

    # Building review form
    class ReviewForm(FlaskForm):
        rating_field = RadioField("Rating", choices=['1', '2', '3', '4', '5'], validators=[DataRequired(), ])
        text_area = TextAreaField("Review text", validators=[Length(max=400), ])
        submit_field = SubmitField("Submit")

    review_form = ReviewForm()
    track_dto = services.get_track(track_id, repo.repo_instance)
    if review_form.validate_on_submit():
        text = review_form.text_area.data
        rating = int(review_form.rating_field.data)
        services.create_review(text, rating, track_dto.track_id, repo.repo_instance)
        return redirect( url_for('bp_browse.track_page', resource_id=track_dto.track_id, page_num=1) )


    return render_template('bp_browse/add_review.html', 
                    form=review_form,
                    track=track_dto)