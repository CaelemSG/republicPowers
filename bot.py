import os
import csv
import discord
from discord import app_commands

# get first row of a csv
claimable_things: set[str] = set()
with open("roles.csv") as file:
    reader = csv.reader(file)
    claimable_things = set(map( lambda x : x[0], reader ))

print(claimable_things)

MY_GUILD = discord.Object(id=os.getenv('REPLICATE_GUILD'))

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # thank you example docs
    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command(
    name = "makeroles",
    description="make a million roles"
)
async def make_roles(interaction: discord.Interaction):
    guild = interaction.guild
    cool_reason = f'{interaction.user.display_name} asked for it'
    if guild:
        for role in claimable_things: 
            await guild.create_role(name=role, reason=cool_reason)
    await interaction.response.send_message(f'ok done')

@client.tree.command(
    name="giveclaim",
    description="give someone a claim"
)
async def give_claim(interaction: discord.Interaction, who: discord.Member, claim_name: str):
    # fail if person already has a claim
    for role in who.roles:
        if role.name in claimable_things:
            await interaction.response.send_message(f'{who.display_name} already has claim {role.name}!')
            return
    possibile_claims = list(filter(lambda claim : claim.startswith(claim_name),  claimable_things))
    if len(possibile_claims) > 1:
        await interaction.response.send_message(f'fool! too many: {possibile_claims}')
        return
    claim = interaction[0]
    for role in interaction.guild.roles:
        if role.name == claim:
            await who.add_roles(role)
            await interaction.response.send_message(f'made {who.display_name} a {claim}')
            return
        
client.run(os.getenv('BOT_TOKEN'))