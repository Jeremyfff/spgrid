from helper.util import *
import configparser
import datetime
import os
import threading
import time


if __name__ == "__main__":
    app = App(version="2.0.1")
    app.run()
    print(app.output)
    if app.exit_task is not None:
        if type(app.exit_task) == list:
            print(f"find {len(app.exit_task)} tasks")
            for i in range(len(app.exit_task)):
                task = app.exit_task[i]
                kwargs = app.exit_kwargs[i]
                task.__call__(*kwargs)
        else:
            app.exit_task.__call__(*app.exit_kwargs)

