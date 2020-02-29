from brainComputer.utils.readers import ReaderBinary, ReaderProtobuf
from brainComputer.utils.connection import Connection
from brainComputer.utils.protocol import Hello, Config
import json


def upload_sample(host: str, port: int, path: str):
    try:
        reader = ReaderProtobuf(path)
        hello = Hello(reader.user)
        for snapshot in reader:
            with Connection.connect(host, port) as con:
                con.send(hello.serialize())
                conf = Config.deserialize(con.receive())
                con.send(snapshot.serialize(conf.fields))
    except Exception as error:
        print(f'ERROR: {error}')
        return 1
