import click
from .utils.reader import ReaderBinary
from .utils.connection import Connection
from .utils.protocol import Hello, Config


@click.command(name='upload')
@click.option('--address', '-a', default='127.0.0.1:5000', help="address of the server")
@click.option('--user', '-u', help='user ID.')
@click.option('--thought', '-t', help='an arbitrary string to send to the server.')
def upload_thought(address, data_path):
    ip, port = address.split(":")
    try:
        reader = ReaderBinary(data_path)
        hello = Hello(reader.user)
        for snapshot in reader:
            with Connection.connect(host=ip, port=port) as con:
                con.send(hello.serialize())
                conf_fields = Config.deserialize(con.receive())
                con.send(snapshot.serialize(conf_fields))
    except Exception as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    pass
