from app.helpers.Validator.ValidateUser import ValidateUser as vu
from app.helpers.Validator.ValidateLocation import ValidateLocation as vl
from app.helpers.Validator.ValidateVisit import ValidateVisit as vv

def Validator(table, action):
    if table=="user":
        if action=="edit":
            return vu.ValidateEditUser
        else: #create
            return vu.ValidateCreateUser
    elif table=="location":
        if action=="edit":
            return vl.ValidateEditLocation
        else: #create
            return vl.ValidateCreateLocation
    elif table=="visit":
        if action=="edit":
            return vv.ValidateEditVisit
        else: #create
            return vv.ValidateCreateVisit