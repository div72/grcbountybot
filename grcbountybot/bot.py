import os

from octomachinery.routing import process_event_actions
from octomachinery.routing.decorators import process_webhook_payload
from octomachinery.runtime.context import RUNTIME_CONTEXT

from grcbountybot.shell import Shell
from grcbountybot.wallet import Wallet

ADMINS = [*map(int, os.environ['BOT_ADMINS'].split(';'))]
shell = Shell(trigger=os.environ['BOT_TRIGGER'])
wallet = Wallet(url=os.environ['WALLET_URL'],
                rpc_user=os.environ['WALLET_RPC_USER'],
                rpc_password=os.environ['WALLET_RPC_PASSWORD'])


@shell.command(name='createbounty')
async def create_bounty(*, ctx):
    account = f'{ctx.repository.full_name}#{ctx.issue.number}'
    address = await wallet.getaccountaddress(account)
    body = f'Bounty created! Address: `{address}`'
    await ctx.api.post(ctx.issue.comments_url, preview_api_version='squirrel-girl', data={'body': body})


@shell.command(name='claimbounty')
async def claim_bounty(address: str, *, ctx):
    if ctx.comment.user.id in ADMINS:
        account = f'{ctx.repository.full_name}#{ctx.issue.number}'
        addresses = await wallet.getaddressesbyaccount(account)
        amount = 0.0
        for addr in addresses:
            amount += await wallet.getreceivedbyaddress(addr)
        if amount:
            tx = await wallet.sendtoaddress(address, amount)
            body = f'Sent {amount} GRC to `{address}` (tx: `{tx}`)'
        else:
            body = 'Sorry, no GRC to send'
        await ctx.api.post(ctx.issue.comments_url, preview_api_version='squirrel-girl', data={'body': body})


@process_event_actions('issue_comment', {'created'})
@process_webhook_payload
async def on_comment(comment, issue, *args, **kwargs):
    github = RUNTIME_CONTEXT.app_installation_client
    if comment['user']['type'] == 'User':  # Ignore bots
        if response := await shell.parse_command(comment['body'], api=github, comment=comment, issue=issue, **kwargs):
            await github.post(
                issue['comments_url'],
                preview_api_version='squirrel-girl',
                data={'body': response},
            )
