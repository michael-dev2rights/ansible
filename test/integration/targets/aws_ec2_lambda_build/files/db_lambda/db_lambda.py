from __future__ import print_function
from sqlalchemy import func, select
from sqlalchemy import Column, MetaData, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sys import argv
import json
import os

# SECURITY CONSIDERATIONS
#
# This lambda is designed and tested only for triggering from within it's account.  It
# accepts and attempts to write to any given database endpoint.  Don't expose it for
# public use.
#

password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
user = os.environ["DB_USER"]
port = os.environ["DB_PORT"]
name = os.environ["DB_NAME"]
url_template = 'postgresql://{}:{}@{}:{}/{}'
url = url_template.format(user, password, host, port, name)
db_con = create_engine(url, client_encoding='utf8')
db_meta = MetaData(bind=db_con, reflect=True)

rows = 172


def handler(event, context):
    """
    The handler function is the function which gets called each time
    the lambda is run.
    """
    # printing goes to the cloudwatch log allowing us to simply debug the lambda if we can find
    # the log entry.
    print("got event:\n" + json.dumps(event))

    # if the name parameter isn't present this can throw an exception
    # which will result in an amazon chosen failure from the lambda
    # which can be completely fine.

    command = event["command"]

    commands = {
        "ping": ping,
        "verify_initial_data": verify_initial_data,
        "initial_data": initial_data,
    }

    # we can use environment variables as part of the configuration of the lambda
    # which can change the behaviour of the lambda without needing a new upload

    return commands[command](event)


def ping(event):
    return {"return": "pong"}


def verify_initial_data(event):
    try:
        table = db_meta.tables['fake_data_table']
    except KeyError:
        return {"return": "failed - no table"}
    s = select([func.count("*")], from_obj=[table])
    count = s.execute().scalar()
    if count == rows:
        return {"return": "true"}
    else:
        return {"return": "failed - wrong number of rows: " + str(count)}


Base = declarative_base()


class FakePersonObject(Base):
    __tablename__ = 'fake_data_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)


def initial_data(event):
    try:
        table = db_meta.tables['fake_data_table']
        table.drop(db_con)
    except KeyError:
        pass
    Base.metadata.create_all(db_con)
    session = sessionmaker(bind=db_con)
    s = session()
    for i in range(0, 172):
        john = FakePersonObject(name='john')
        s.add(john)
    s.commit()
    return {"return": "maybe I created it; maybe not"}


def main():
    """
    This main function will normally never be called during normal
    lambda use.  It is here for testing the lambda program only.
    """
    try:
        event_json = argv[1]
        event = json.loads(event_json)
    except IndexError:
        event = {"command": "verify_initial_data"}
    context = None
    print(handler(event, context))


if __name__ == '__main__':
    main()
