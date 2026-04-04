from enum import Enum

class ApplicationStatus(Enum):
    NOT_APPLIED = 0
    APPLIED = 1
    INTERVIEWING = 2
    OFFER = 3
    REJECTED = 4
