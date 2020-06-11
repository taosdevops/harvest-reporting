import click

from reporting.config import ConfigHelp
from reporting.utils import load_yaml, truncate


@click.group()
@click.option(
    "-b",
    "--bearer-token",
    envvar="BEARER_TOKEN",
    required=True,
    help=ConfigHelp.bearer_token_help,
)
@click.option(
    "--account-id",
    envvar="HARVEST_ACCOUNT_ID",
    required=True,
    help=ConfigHelp.config_path_help,
)
@click.option(
    "--config-path",
    envvar="HARVEST_CONFIG",
    default=None,
    help=ConfigHelp.account_id_help,
)
@click.option(
    "--send-grid",
    envvar="SENDGRID_API_KEY",
    required=True,
    help=ConfigHelp.sendgrid_api_help,
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

    ctx.obj = HarvestAPIClient(bearer_token, account_id, config)


@main.command()
@click.pass_obj
def list_clients(client: HarvestAPIClient):
    """ Returns a list of clients in table format """
    template = "{id:<9} {name}"
    click.echo("ID      | Name")

    for client in client.list_clients():
        click.echo(str.format(template, name=client["name"], id=client["id"]))


@main.command()
@click.argument("client_id")
@click.pass_obj
def get_client(harvest_client: HarvestAPIClient, client_id):
    """ Returns data regarding client """
    client = harvest_client.get_client_by_id(client_id)
    clientName = client["name"]

    hours_used = harvest_client.get_client_time_used(client_id)
    total_hours = harvest_client.get_client_time_allotment(clientName)
    hours_left = total_hours - hours_used

    used = truncate(hours_used, 2)
    left = truncate(hours_left, 2)

    percent = used / total_hours * 100
