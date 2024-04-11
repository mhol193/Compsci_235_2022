from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship, synonym

# import domain model
from music.domainmodel.track import Track
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.user import User
from music.domainmodel.review import Review 

# global variable giving access to the MetaData (schema) information of the database
metadata = MetaData()

genres_table = Table(
    'genres', metadata,
    Column('genre_id', Integer, primary_key=True),
    Column('name', String(255), nullable=False)
)

artists_table = Table(
    'artists', metadata,
    Column('artist_id', Integer, primary_key=True),
    Column('name', String(255), unique=True, nullable=False)
)

albums_table = Table(
    'albums', metadata,
    Column('album_id', Integer, primary_key=True),
    Column('title', String(255), nullable=False),
    Column('album_url', String(255), nullable=False),
    Column('album_type', String(255), nullable=False),
    Column('release_year', String(255), nullable=False)
)

tracks_table = Table(
    'tracks', metadata,
    Column('track_id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), unique=False, nullable=False),
    Column('artist_id', ForeignKey('artists.artist_id')),
    Column('album_id', ForeignKey('albums.album_id')),
    Column('track_duration', Integer, nullable=False),
    Column('track_img_url', Integer, nullable=False)
)

users_table = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False), 
    Column('password', String(255), nullable=False), 
    Column('profile_photo', String(255), nullable=False)
)

reviews_table = Table(
    'reviews', metadata,
    Column('review_id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.user_id')),
    Column('track_id', ForeignKey('tracks.track_id')),
    Column('review_text', String(1024), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

user_liked_table = Table(
    'user_liked', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.user_id')),
    Column('track_id', ForeignKey('tracks.track_id'))
)

track_genres_table = Table(
    'track_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('track_id', ForeignKey('tracks.track_id')),
    Column('genre_id', ForeignKey('genres.genre_id')) 
)

user_requests_table = Table(
    'user_requests', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.user_id')),
    Column('request_id', ForeignKey('users.user_id')) 
)

user_friends_table = Table(
    'user_friends', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.user_id')),
    Column('friend_id', ForeignKey('users.user_id')) 
)


def map_model_to_tables():
    mapper(User, users_table, properties={
        '_User__user_name': users_table.c.name,
        '_User__password': users_table.c.password,
        '_User__profile_photo': users_table.c.profile_photo,
        '_User__reviews': relationship(Review, backref='_Review__user'),
        '_User__liked_tracks': relationship(Track, secondary=user_liked_table, back_populates='_Track__users'),
        '_User__requests': relationship(User, secondary=user_requests_table,
                                        primaryjoin=users_table.c.user_id==user_requests_table.c.user_id,
                                        secondaryjoin=users_table.c.user_id==user_requests_table.c.request_id),
        '_User__friends': relationship(User, secondary=user_friends_table,
                                        primaryjoin=users_table.c.user_id==user_friends_table.c.user_id,
                                        secondaryjoin=users_table.c.user_id==user_friends_table.c.friend_id)
    })
    mapper(Track, tracks_table, properties={
        '_Track__track_id': tracks_table.c.track_id,
        '_Track__title': tracks_table.c.title,
        '_Track__track_duration': tracks_table.c.track_duration,
        '_Track__album': relationship(Album),
        '_Track__artist': relationship(Artist),
        '_Track__genres': relationship(Genre, secondary=track_genres_table),
        '_Track__track_img_url': tracks_table.c.track_img_url,
        '_Track__reviews': relationship(Review, backref='_Review__track'),
        '_Track__users': relationship(User, secondary=user_liked_table, back_populates='_User__liked_tracks')
    })
    mapper(Album, albums_table, properties={
        '_Album__album_id': albums_table.c.album_id,
        '_Album__title': albums_table.c.title,
        '_Album__album_type': albums_table.c.album_type,
        '_Album__album_url': albums_table.c.album_url,
        '_Album__release_year': albums_table.c.release_year
    })
    mapper(Artist, artists_table, properties={
        '_Artist__artist_id': artists_table.c.artist_id,
        '_Artist__full_name': artists_table.c.name,
    })
    mapper(Genre, genres_table, properties={
        '_Genre__genre_id': genres_table.c.genre_id,
        '_Genre__name': genres_table.c.name,
        '_Genre__tracks': relationship(Track, secondary=track_genres_table, back_populates='_Track__genres')
    })
    mapper(Review, reviews_table, properties={
        '_Review__id': reviews_table.c.review_id,
        '_Review__review_text': reviews_table.c.review_text,
        '_Review__rating': reviews_table.c.rating,
        '_Review__timestamp': reviews_table.c.timestamp
    })


    