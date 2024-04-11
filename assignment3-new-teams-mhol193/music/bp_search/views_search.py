from typing import List

from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SearchField, SubmitField, BooleanField, SelectMultipleField

import music.bp_search.services as services
import music.adapters.a_repository as repo
from music.domainmodel.genre import Genre

bp_search: Blueprint = Blueprint("bp_search", __name__)


# instructs endpoint whether to display tracks, albums, or artists
def convert_to_resource_id(input_str: str) -> int:
    match input_str:
        case 'Tracks':
            return 1
        case 'Albums':
            return 2
        case 'Artists':
            return 3


# Results page
keywords = None
genre_filters = None

# Search page
@bp_search.route('/search<string:search_by>', methods=['GET', 'POST'])
def search_data(search_by):
    # Building search form
    class SearchForm(FlaskForm):
        search_field = SearchField()
        submit_field = SubmitField("Search")
        search_by = SelectMultipleField("search for",
                                        choices=["Tracks", "Artists", "Albums"])

    # create unique checkbox for each genre
    for genre in services.get_all_genres(repo.repo_instance):
        setattr(SearchForm, genre.name,
                BooleanField(genre.name, id=genre.genre_id))

    search_form = SearchForm()

    # POST method
    if search_form.validate_on_submit():
        global genre_filters # holds ticked checkboxes
        global keywords # holds search keywords
        
        keywords = search_form.search_field.data.strip()
        genre_filters = []
        for genre in services.get_all_genres(repo.repo_instance):
            _filter = getattr(search_form, genre.name)
            if _filter.data: 
                genre_filters.append(Genre(_filter.id, _filter.name))

        # building redirection URL
        redirect_url = url_for('bp_search.list_results',
                               resource_id=convert_to_resource_id(search_by),
                               page_num=1)
        return redirect(redirect_url)

    # GET method
    else:
        return render_template('bp_search/search_form.html',
                               form=search_form,
                               search_by_param=search_by,
                               genres=services.get_all_genres(
                                   repo.repo_instance))


@bp_search.route('/results<int:resource_id>/<int:page_num>')
def list_results(resource_id: int, page_num: int):
    global keywords
    global genre_filters
    genres = genre_filters

    # only execute if new search request
    if keywords is not None and genre_filters is not None:
        if len(genres) == 0:  # if no filters selected apply all filters
            genres = services.get_all_genres(repo.repo_instance)
        # get results
        match resource_id:
            case 1:
                services.get_track_results(keywords, genres, repo.repo_instance)
            case 2:
                services.get_album_results(keywords, genres, repo.repo_instance)
            case 3:
                services.get_artist_results(keywords, genres, repo.repo_instance)
        # keywords = None
        genre_filters = None

    # display results
    match resource_id:
        case 1:
            start_index = (page_num - 1) * 7
            items_to_disp = services.get_next_results(start_index, 7)
            last_page_num = int(
                (services.get_results_last_page_index(
                    7, repo.repo_instance) / 7) + 1)
            return render_template("bp_search/search_results_tracks.html",
                                   tracks=items_to_disp,
                                   curr_page=page_num,
                                   last_page_num=last_page_num,
                                   search_keywords=keywords)
        case 2:
            start_index = (page_num - 1) * 7
            items_to_disp = services.get_next_results(start_index, 7)
            last_page_num = int((services.get_results_last_page_index(7,
                                           repo.repo_instance) / 7) + 1)
            return render_template("bp_search/search_results_albums.html",
                                   albums=items_to_disp,
                                   curr_page=page_num,
                                   last_page_num=last_page_num,
                                   search_keywords=keywords)
        case 3:
            start_index = (page_num - 1) * 8
            items_to_disp = services.get_next_results(start_index, 8)
            last_page_num = int((services.get_results_last_page_index(8,
                                           repo.repo_instance) / 8) + 1)
            return render_template("bp_search/search_results_artists.html",
                                   artists=items_to_disp,
                                   curr_page=page_num,
                                   last_page_num=last_page_num,
                                   search_keywords=keywords)
