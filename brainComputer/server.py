from .utils.listener import Listener
from .utils.protocol import Hello, Config, Snapshot
from .utils.parser import Parsers, ParserContext
import json
import threading
import click
import pika

CONF_FIELDS = ['pose']


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', default='127.0.0.1', help="address of the server")
@click.option('--port', '-p', default='8000', help='port of the server')
@click.argument('publish')
def run_server(host, port, publish):
    try:
        port = int(port)
    except ValueError as e:
        print(f'bad port argument: {e}')
        return 1

    address = f'{host}:{port}'
    parsers_dict = Parsers.load_modules()
    with Listener(host, port) as listener:
        while True:
            con = listener.accept()
            handler = ConnectionHandler(con, parsers_dict)
            handler.start()  # start() invokes .run()


class ConnectionHandler(threading.Thread):
    def __init__(self, connection, parsers):
        super().__init__()
        self.connection = connection
        self.parsers = parsers
        # self.data_dir = data_dir
        # if data_dir.split("/")[-1] != '':
        #     self.data_dir += "/"

    def run(self):
        """ Handle the connection and then print to stdout
        :return:
        """
        try:
            conf = Config(CONF_FIELDS)
            with self.connection as con:
                hello = Hello.deserialize(con.receive())
                con.send(conf.serialize())
                snap_bytes = con.receive()
                import pdb; pdb.set_trace()  # DEBUG
                snap = Snapshot.deserialize(snap_bytes, CONF_FIELDS)

        except Exception as e:
            print("Abort connection to failed client.")

        # parse_context = ParserContext(self.data_dir, hello, snap)
        # for field_name, func_handler in self.parsers.items():
        #     if field_name in CONF_FIELDS:
        #         func_handler(parse_context, snap)


if __name__ == '__main__':
    # cli()  # TODO: this should be the only thing here.
    # DEBUG mode for testing Rabbitmq :

    queue_name = 'hello'
    message = "Hello World!"

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)

    print(" [x] Sent 'Hello World!'")
    connection.close()