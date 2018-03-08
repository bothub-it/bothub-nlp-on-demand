import os
import django
import click

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bothub.settings')
django.setup()


@click.command()
@click.option('--service', type=click.Choice(['start_server']))
@click.argument('arg', required=False)
def start_service(service, arg):
    if service == 'start_server':
        from app.server import start_server
        start_server(arg)


if __name__ == '__main__':
    start_service()