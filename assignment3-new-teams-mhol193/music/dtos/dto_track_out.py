from music.domainmodel.track import Track

from music.utilties.util_functions import fix_broken_album_url, format_duration_as_time

class DtoTrackOut:
    def __init__(self, input_track: Track, is_fav: bool = False, user_rating: int = 0) -> None:
        _track_name = input_track.title if input_track.title is not None else "<no title>"
        _duration = input_track.track_duration if input_track.track_duration is not None else 0
        _album_name = input_track.album.title if input_track.album is not None else "<no album>"
        _artist_name = input_track.artist.full_name if input_track.artist is not None else "<no artist>"

        self.__track_id: int = input_track.track_id
        self.__title: str = _track_name
        self.__album_title: str = _album_name
        self.__artist_name: str = _artist_name
        self.__is_favourite: bool = is_fav
        self.__user_rating: int = user_rating

        # format duration as MM:SS
        self.__track_duration = format_duration_as_time(_duration)

        # get track art
        _img_url = input_track.track_img_url
        if _img_url is not None:
            self.__track_img_url = fix_broken_album_url(_img_url)
        else:
            self.__track_img_url = "no_url"


        # get album id
        if input_track.album is not None:
            self.__album_id = input_track.album.album_id


        # get artist id
        if input_track.artist is not None:
            self.__artist_id = input_track.artist.artist_id



    @property
    def title(self) -> str:
        return self.__title

    @property
    def album_title(self) -> str:
        return self.__album_title

    @property
    def artist_name(self) -> str:
        return self.__artist_name

    @property
    def track_duration(self) -> str:
        return self.__track_duration

    @property
    def track_img_url(self) -> str:
        return self.__track_img_url
    
    @property
    def album_id(self) -> int:
        return self.__album_id

    @property
    def artist_id(self) -> int:
        return self.__artist_id

    @property
    def is_favourite(self) -> bool:
        return self.__is_favourite

    @property 
    def track_id(self) -> int:
        return self.__track_id

    @property 
    def user_rating(self) -> int:
        return self.__user_rating