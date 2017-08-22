from app.helpers.Validator.ValidateUser import ValidateUser as vu


def Validator(table, action):
    if table=="user":
        if action=="edit":
            return vu.ValidateEditUser
        else: #create
            return vu.ValidateCreateUser
    elif table=="location":
        if action=="edit":
            return vu.ValidateEditLocation
        else: #create
            return vu.ValidateCreateLocation
    elif table=="visit":
        if action=="edit":
            return vu.ValidateEditVisit
        else: #create
            return vu.ValidateCreateVisit