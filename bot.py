import properties
import tables
import os
import csv
import discord
import asyncio
from discord import app_commands

# get first row of a csv
claimable_things: set[str] = set()
with open("roles.csv") as file:
    reader = csv.reader(file)
    claimable_things = set(map( lambda x : x[0], reader ))

print(f'{len(claimable_things)} claims found')

# give player_properties a mutex lock since multiple coroutines may mutate player_properties
player_properties = properties.deserialize_properties()
player_properties_lock = asyncio.locks.Lock()

async def async_serialize_properties():
    async with player_properties_lock:
        properties.serialize_properties(player_properties)

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
    await interaction.response.send_message(f'started...')
    if guild:
        for role in claimable_things: 
            await guild.create_role(name=role, reason=cool_reason)
    await interaction.response.edit_message(f'ok done')

@client.tree.command(
    name = "deleteroles",
    description="get rid of them all"
)
async def delete_roles(interaction: discord.Interaction):
    guild = interaction.guild
    cool_reason = f'{interaction.user.display_name} asked for it'
    await interaction.response.send_message(f'started...')
    if guild:
        for role in guild.roles: 
            if role.name in claimable_things:
                role.delete(reason=cool_reason)
    await interaction.response.edit_message(f'ok done')

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
    search = claim_name.lower()
    possibile_claims = list(filter(lambda claim : claim.lower().startswith(search),  claimable_things))
    if len(possibile_claims) > 1:
        await interaction.response.send_message(f'fool! too many: {possibile_claims}')
        return
    if len(possibile_claims) == 0:
        await interaction.response.send_message(f'could not find claim {claim_name}.')
        return
    claim = possibile_claims[0]
    for role in interaction.guild.roles:
        if role.name == claim:
            await who.add_roles(role)
            await interaction.response.send_message(f'made {who.display_name} a {claim}')
            return

@client.tree.command(
    name="removeclaim",
    description="removes someones claim"
)
async def remove_claim(interaction: discord.Interaction, who: discord.Member):
    # fail if person already has a claim
    for role in who.roles:
        if role.name in claimable_things:
            await who.remove_roles(role)
            await interaction.response.send_message(f'removed claim {role.name} from {who.display_name}.')
            return
    await interaction.response.send_message(f'{who.display_name} has no claim!')

@client.tree.command(
    name="view-property",
    description="looks at someone elses property"
)
async def view_others_properties(interaction: discord.Interaction, who: discord.Member):
    # find claim
    for role in who.roles:
        if role.name in claimable_things:
            async with player_properties_lock:
                if role.name in player_properties:
                    owned = player_properties[role.name]
                    await interaction.response.send_message(f'```{tables.table_properties(owned)}```')
                else:
                    await interaction.response.send_message(f'{role.name} ({who}) has no properties.')
            return
    await interaction.response.send_message(f'{who.display_name} has no claim!')

@client.tree.command(
    name="give-property",
    description="give someone a property"
)
async def give_property(interaction: discord.Interaction, 
                        who: discord.Member, 
                        property_name: str,
                        property_type: str,
                        product: str,
                        size: int,
                        location: str,
                        value: float,
                        income: float):
    # find claim
    for role in who.roles:
        if role.name in claimable_things:
            new = properties.PlayerProperty()
            new.name = property_name
            new.property_type = property_type
            new.product = product
            new.size = size
            new.location = location
            new.value = value
            new.income = income
            async with player_properties_lock:
                if role.name in player_properties:
                    player_properties[role.name].append(new)
                else:
                    player_properties[role.name] = [new]
            await interaction.response.send_message(f'added {property_type} named {property_name} to {role.name} ({who})')
            asyncio.create_task(async_serialize_properties())
            return
    await interaction.response.send_message(f'{who.display_name} has no claim!')


client.run(os.getenv('BOT_TOKEN'))