import os

from octomachinery.app.server.runner import run as run_app

import grcbountybot.bot


def main():
    run_app(name='grcbountybot',
            version='0.0.1',
            url='https://github.com/div72/grcbountybot')


if __name__ == '__main__':
    main()
