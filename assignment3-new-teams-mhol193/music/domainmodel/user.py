from music.domainmodel.track import Track


class User:

    def __init__(self, user_name: str, password: str, profile_photo: str):

        if type(user_name) is str:
            self.__user_name = user_name.lower().strip()
        else:
            raise ValueError("user_name must be a string!")

        if isinstance(password, str) and len(password) >= 8:
            self.__password = password
        else:
            self.__password = None

        self.__profile_photo = profile_photo
        
        self.__liked_tracks: list[Track] = []
        self.__friends: list[User] = []
        self.__requests: list[User] = []

    
    @property
    def profile_photo(self) -> str:
        return self.__profile_photo

    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def password(self) -> str:
        return self.__password

    @property
    def liked_tracks(self) -> list:
        return self.__liked_tracks

    def add_liked_track(self, track: Track):
        if not isinstance(track, Track) or track in self.__liked_tracks:
            return
        self.__liked_tracks.append(track)

    def remove_liked_track(self, track: Track):
        if not isinstance(track, Track) or track not in self.__liked_tracks:
            return
        self.__liked_tracks.remove(track)

    @property
    def friends(self) -> list:
        return self.__friends

    def add_friend(self, user):
        if isinstance(user, self.__class__) and user not in self.__friends:
            self.__friends.append(user)

    def remove_friend(self, user):
        if isinstance(user, self.__class__) and user in self.__friends:
            self.__friends.remove(user)

    @property
    def requests(self) -> list:
        return self.__requests

    def add_request(self, user) -> None:
        if not isinstance(user, self.__class__):
            raise ValueError("requests must be of type User")
        elif user not in self.requests:
            self.__requests.append(user)

    def remove_request(self, user) -> None:
        if not isinstance(user, self.__class__):
            raise ValueError("requests must be of type User")
        elif user not in self.__requests:
            raise ValueError("user not in requests")
        else:
            self.__requests.remove(user)

    def __repr__(self):
        return f'<User {self.__user_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.user_name == other.user_name

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return self.user_name < other.user_name

    def __hash__(self):
        return hash(self.user_name)
