from abc import ABCMeta

# TODO: сделать интерфейс для работы с базой данных (чтобы если что переписать для другой базы)
# см книжку

class BaseDB(ABCMeta):
    def __init__(self):
        pass

    def connect(self):
        pass

    def get_item_from_table(self, table, item_id):
        pass

    def set_item_into_table(self, table, item):
        pass