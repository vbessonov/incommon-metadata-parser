import logging
import sys

import click

from incommon_metadata_parser.loader import MetadataLoader
from incommon_metadata_parser.parser import MetadataParser
from incommon_metadata_parser.storage import MetadataStorage


def excepthook(exception_type, exception_instance, exception_traceback):
    """
    Function called for uncaught exceptions
    :param exception_type: Type of an exception
    :param exception_instance: Exception instance
    :param exception_traceback: Exception traceback
    """

    logging.fatal(
        'Exception hook has been fired: {0}'.format(exception_instance),
        exc_info=(exception_type, exception_instance, exception_traceback,))


sys.excepthook = excepthook


@click.group()
@click.pass_context
def cli(*args, **kwargs):
    """
    incommon-metadata-parser is a tool designed for parsing InCommon Federation metadata
    and saving it in MongoDB for further analysis.
    """

    pass


@cli.command()
@click.option('--host', '-h', help='MongoDB host', type=str, default='localhost')
@click.option('--port', '-P', help='MongoDB port', type=int, default=27017)
@click.option('--user', '-u', help='MongoDB user', type=str, required=True)
@click.option('--password', '-p', help='MongoDB password', type=str, required=True)
def import_metadata(host, port, user, password):
    """
    Imports metadata into MongoDB instance
    """

    loader = MetadataLoader()
    parser = MetadataParser()
    storage = MetadataStorage(host, port, user, password)

    metadata = loader.load_metadata(MetadataLoader.IN_COMMON_METADATA_SERVICE_URL)
    service_providers = parser.parse(metadata)
    storage.save_service_providers(service_providers)
