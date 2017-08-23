from app.helpers.ReturnAdapter.AdaptReturnUser import AdaptReturnUser as aur
from app.helpers.ReturnAdapter.AdaptReturnLocation import AdaptReturnLocation as alr


def AdaptReturn(resource, action):
    if resource=="user":
        if action=="visits":
            return aur.UserVisits
    elif resource=="location":
        if action=="avg":
            return alr.LocationAVG
