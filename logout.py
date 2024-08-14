# coding=utf-8
import sys


class Logout:

    def __init__(self, main):
        self.main = main

        self.main.btnLogout.clicked.connect(self.exit_app)


    def exit_app(self, e):
        sys.exit(self.main.app.exit())