import music.domainmodel as dm

from music.utilties.util_functions import format_duration_as_time, fix_broken_album_url

from typing import List

class DtoAlbumOut:
    def __init__(self, input_album: dm.Album, artist_name: str|None, list_of_tracks: List[dm.Track]) -> None:
        
        self.__album_id = input_album.album_id
        _title = input_album.title if input_album.title is not None else "<no title>"
        _ry = str(input_album.release_year) if input_album.release_year is not None else "<no release year>"
        _artist = artist_name if artist_name is not None else "<no artist>"

        self.__title = _title
        self.__artist_name = _artist
        
        # calculate duration
        _sum = 0
        for track in list_of_tracks:
            _sum += track.track_duration
        self.__album_duration = format_duration_as_time(_sum)

        # format track count
        self.__track_count = str(len(list_of_tracks)) + " track"
        if len(list_of_tracks) > 1:
            self.__track_count += "s"

        # get album art
        _img_url = list_of_tracks[0].track_img_url
        if _img_url is not None:
            self.__img_url = fix_broken_album_url(_img_url)
        else:
            self.__img_url = "no_url"

        # get release year
        self.__release_year = str(_ry)

        # get artist id
        _artist = list_of_tracks[0].artist
        if _artist is not None:
            self.__artist_id = _artist.artist_id


        

    @property
    def album_id(self) -> int:
        return self.__album_id
    
    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def release_year(self) -> str:
        return self.__release_year
    
    @property
    def artist_name(self) -> str:
        return self.__artist_name

    @property
    def track_count(self) -> int:
        return self.__track_count

    @property
    def album_duration(self) -> int:
        return self.__album_duration
    
    @property
    def img_url(self) -> str:
        return self.__img_url

    @property
    def genres(self) -> str:
        return self.__genres

    @property
    def artist_id(self) -> str:
        return self.__artist_id
