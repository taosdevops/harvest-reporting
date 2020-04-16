import click

from hreporting import config
from hreporting.harvest_client import HarvestClient
from hreporting.utils import load_yaml, print_verify, truncate


@click.group()
@click.option(
    "-b",
    "--bearer-token",
    envvar="BEARER_TOKEN",
    required=True,
    help=config.strings.bearer_token_help,
)
@click.option(
    "--account-id",
    envvar="HARVEST_ACCOUNT_ID",
    required=True,
    help=config.strings.config_path_help,
)
@click.option(
    "--config-path",
    envvar="HARVEST_CONFIG",
    default=None,
    help=config.strings.account_id_help,
)
@click.option(
    "--send-grid",
    envvar="SENDGRID_API_KEY",
    required=True,
    help=config.strings.sendgrid_api_help,
)
@click.pass_context
def main(ctx, bearer_token, account_id, config_path):
    if config_path:
        try:
            config = load_yaml(config_path)
        except Exception as e:
            click.echo(e, err=True)
            config = {}
    else:
        config = {}

    ctx.obj = HarvestClient(bearer_token, account_id, config)


@main.command()
@click.pass_obj
def list_clients(client: HarvestClient):
    """ Returns a list of clients in table format """
    template = "{id:<9} {name}"
    click.echo("ID      | Name")

    for client in client.list_clients():
        click.echo(str.format(template, name=client["name"], id=client["id"]))


@main.command()
@click.argument("client_id")
@click.pass_obj
def get_client(harvest_client: HarvestClient, client_id):
    """ Returns data regarding client """
    client = harvest_client.get_client_by_id(client_id)
    clientName = client["name"]

    hours_used = harvest_client.get_client_time_used(client_id)
    total_hours = harvest_client.get_client_time_allotment(clientName)
    hours_left = total_hours - hours_used

    used = truncate(hours_used, 2)
    left = truncate(hours_left, 2)

    percent = used / total_hours * 100

    print_verify(used, clientName, percent, left)
