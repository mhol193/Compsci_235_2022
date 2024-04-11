import music.domainmodel as dm
from music.utilties.util_functions import fix_broken_album_url

import random
from typing import List

class DtoArtistOut:
    def __init__(self, artist: dm.Artist, list_of_tracks: List[dm.Track]):
        # trim name if too long
        _n = artist.full_name
        # if len(_n) > 14:
        #     self.__name = _n[:11] + "..."
        # else:
        self.__name = _n

        # get track count
        self.__track_count = str(len(list_of_tracks)) + " track"
        if len(list_of_tracks) > 1:
            self.__track_count += "s"
        
        # get genres
        _genres = list()
        for t in list_of_tracks:
            for g in t.genres:
                if g not in _genres:
                    _genres.append(g.name)
        # self.__genres = ", ".join(_genres)
        if len(_genres) == 0:
            self.__genres = "<no genre>"
        else:
            self.__genres = _genres[0]


        rand_i = random.randrange(0, len(list_of_tracks))
        rand_url = list_of_tracks[rand_i].track_img_url
        if rand_url is not None:
            self.__img_url = fix_broken_album_url(rand_url)
        else:
            self.__img_url = "no_url"

        self.__artist_id = artist.artist_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def track_count(self) -> int:
        return self.__track_count

    @property 
    def genres(self) -> str:
        return self.__genres

    @property
    def img_url(self) -> str:
        return self.__img_url

    @property
    def artist_id(self) -> str:
        return self.__artist_id
