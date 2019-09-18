import click
from hreporting.harvest_client import HarvestClient
from hreporting.utils import truncate, print_verify


@click.group()
@click.option("-b", "--bearer-token", envvar="BEARER_TOKEN", required=True)
@click.option("--account-id", envvar="HARVEST_ACCOUNT_ID", required=True)
# @click.option("--config-path", envvar="HARVEST_ACCOUNT_ID", required=True)
@click.pass_context
def main(ctx, bearer_token, account_id):
    ctx.obj = HarvestClient(bearer_token, account_id)


@main.command()
@click.pass_obj
def list_clients(client: HarvestClient):
    template = "{id:<9} {name}"
    click.echo("ID      | Name")
    # print(clients)
    for client in client.list_clients():
        click.echo(str.format(template, name=client["name"], id=client["id"]))


@main.command()
@click.argument("client_id")
@click.pass_obj
def get_client(harvest_client: HarvestClient, client_id):
    client = harvest_client.get_client_by_id(client_id)
    clientName = client["name"]

    hours_used = harvest_client.get_client_time_used(client_id)
    total_hours = harvest_client.get_client_time_allotment(clientName)
    hours_left = total_hours - hours_used

    used = truncate(hours_used, 2)
    left = truncate(hours_left, 2)

    percent = used / total_hours * 100

    print_verify(used, clientName, percent, left)
