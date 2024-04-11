from music.domainmodel.user import User
from music.domainmodel.review import Review

from music.utilties.util_functions import format_duration_as_time, fix_broken_album_url

from typing import List

class DtoReviewOut:
    def __init__(self, user: User, list_of_reviews: List[Review]) -> None:
        
        self.__user = user
        self.__reviews = list_of_reviews  

    @property
    def user(self) -> User:
        return self.__user
    
    @property
    def list_of_reviews(self) -> List[Review]:
        return self.__reviews
    