from db import DataBase, Data
from app import App


def main():
    db = DataBase(Data())
    app = App(db)
    app.start()


if __name__ == '__main__':
    main()
