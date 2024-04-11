from music.domainmodel.user import User

from music.utilties.util_functions import fix_broken_album_url, format_duration_as_time

class DtoUserOut:
    def __init__(self, input_user: User, is_req: bool = False) -> None:
        self.__profile_photo: str = input_user.profile_photo
        self.__user_name: str = input_user.user_name
        self.__is_request: bool = is_req
        self.__friend_count: int = len(input_user.friends)
        self.__fav_tracks_count: int = len(input_user.liked_tracks)


    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def profile_photo(self) -> str:
        return self.__profile_photo

    @property
    def is_request(self) -> bool:
        return self.__is_request

    @property
    def friend_count(self) -> int:
        return self.__friend_count

    @property
    def fav_tracks_count(self) -> int:
        return self.__fav_tracks_count

