#!/usr/bin/env python
""" This module start server """
import tornado.ioloop
import tornado.escape

from tornado.web import Application, url
from app.handlers.bot_trainer import BotTrainerRequestHandler
from app.handlers.message import MessageRequestHandler


def make_app():  # pragma: no cover
    return Application([
        url(r'/v1/message', MessageRequestHandler),
        url(r'/v1/train', BotTrainerRequestHandler)
    ])


def start_server(port):  # pragma: no cover
    global app
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()