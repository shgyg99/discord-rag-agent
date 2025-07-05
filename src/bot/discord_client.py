import os
import discord
from dotenv import load_dotenv
from aiohttp_socks import ProxyConnector
import asyncio
from ..utils.logger import setup_logger
from ..rag.agent import RAGAgent
from discord import app_commands, Embed, Colour
import random


logger = setup_logger('rag_agent')
rag_agent = RAGAgent()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

CHAT_RESPONSES = [
    "Hi there! How can I help you today? 🙂",
    "Hello! Feel free to ask me questions using /ask command!",
    "Hey! I'm here to help. Use /ask to query the documentation.",
]

intents = discord.Intents.default()
intents.message_content = True

class RAGBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._first_sync = True
        
    async def setup_hook(self):
        if self._first_sync:
            guild_id = os.getenv('DISCORD_GUILD_ID')
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
            else:
                await self.tree.sync()
            self._first_sync = False

async def start_bot():
    client = RAGBot()

    @client.event
    async def on_ready():
        print(f'✅ Bot ready: {client.user}')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if isinstance(message.channel, discord.DMChannel) or client.user in message.mentions:
            await message.channel.send(random.choice(CHAT_RESPONSES))

    async def process_query(ctx, query: str):
        try:
            answer = rag_agent.query(query)
            sources = rag_agent.retriever.retrieve(query)
            
            embed = Embed(title="📚 Answer", description=answer, color=Colour.blue())
            
            if sources:
                sources_text = ""
                for i, source in enumerate(sources, 0):  # Start from 0
                    source_text = source[:5000] + "..." if len(source) > 5000 else source
                    sources_text += f"{i}. {source_text}\n"
                embed.add_field(name="Sources", value=sources_text[:3000], inline=False)
            
            response = await ctx.followup.send(embed=embed) if isinstance(ctx, discord.Interaction) else await ctx.channel.send(embed=embed)
            await response.add_reaction("👍")
            await response.add_reaction("👎")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            error_msg = "Sorry, I encountered an error processing your request."
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(error_msg, ephemeral=True)
            else:
                await ctx.channel.send(error_msg)

    @client.tree.command(name="ask", description="Ask a question")
    async def ask(interaction: discord.Interaction, question: str):
        await interaction.response.defer(thinking=True)
        await process_query(interaction, question)

    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        embed = Embed(title="🤖 Help", color=Colour.green())
        embed.add_field(name="Commands", value="/ask `<question>` - Ask a question\n/help - Show this message", inline=False)
        embed.add_field(name="Feedback", value="React with 👍 or 👎", inline=False)
        await interaction.response.send_message(embed=embed)

    connector = ProxyConnector.from_url(os.getenv('PROXY_URL'))
    client.http.connector = connector
    await client.start(TOKEN)

def run_discord_bot():
    asyncio.run(start_bot())

if __name__ == '__main__':
    try:
        run_discord_bot()
    except KeyboardInterrupt:
        print("Shutting down...")
