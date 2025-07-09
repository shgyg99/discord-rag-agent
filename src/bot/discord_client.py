import os
import time
import discord
from dotenv import load_dotenv
from aiohttp_socks import ProxyConnector
import asyncio
from ..utils.logger import setup_logger
from ..rag.agent import RAGAgent
from discord import app_commands, Embed, Colour
import random
from prometheus_client import start_http_server, Counter, Gauge

logger = setup_logger('rag_agent')
rag_agent = RAGAgent()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

request_count = Counter('request_count', 'Number of requests processed')
error_count = Counter('error_count', 'Number of errors encountered')
query_processing_latency = Gauge('query_processing_latency', 'Latency of query processing in ms')
positive_feedback_count = Counter('positive_feedback_count', 'Number of positive feedback received')
negative_feedback_count = Counter('negative_feedback_count', 'Number of negative feedback received') 


start_http_server(9091)


CHAT_RESPONSES = [
    "Hi there! How can I help you today? 🙂",
    "Hello! Feel free to ask me questions using /ask command!",
    "Hey! I'm here to help. Use /ask to query the documentation.",
]

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

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


    @client.event
    async def on_reaction_add(reaction, user):
        # Ignore bot's own reactions
        if user == client.user:
            return
            
        # Only process reactions on bot's messages
        if reaction.message.author == client.user:
            if str(reaction.emoji) == '👍':
                positive_feedback_count.inc()
                await reaction.message.channel.send(f"Thank you for your positive feedback {user.mention}! 😊")
                
            elif str(reaction.emoji) == '👎':
                negative_feedback_count.inc()
                feedback_message = (
                    f"I'm sorry my answer wasn't helpful {user.mention}!\n"
                    "Please try asking your question more specifically or use the `/ask` command again."
                )
                await reaction.message.channel.send(feedback_message)

    async def process_query(ctx, query: str):
        request_count.inc()
        start_time = time.time()
        try:
            # دریافت پاسخ از RAG Agent
            answer = rag_agent.query(query)
            
            # اگر پاسخ خیلی کوتاه باشد، ساختار پیش‌فرض را اضافه می‌کنیم
            if len(answer) < 100:
                answer = (
                    "🤖 **Answer**\n"
                    f"{answer}\n\n"
                    "📚 **Sources**\n"
                    "- Context from knowledge base\n"
                    "🔗 **Related Links**\n"
                    "- [AI PM Bootcamp Playlist](https://youtube.com/playlist?list=example)"
                )
            
            # بررسی طول پاسخ برای تقسیم به چند embed در صورت نیاز
            if len(answer) <= 4096:  # حداکثر طول مجاز embed
                embed = Embed(description=answer, color=Colour.blue())
                if isinstance(ctx, discord.Interaction):
                    response = await ctx.followup.send(embed=embed)
                else:
                    response = await ctx.channel.send(embed=embed)
            else:
                # اگر پاسخ خیلی طولانی است، آن را به چند بخش تقسیم می‌کنیم
                chunks = [answer[i:i+2000] for i in range(0, len(answer), 2000)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        embed = Embed(
                            title=f"📚 Answer (Part {i+1}/{len(chunks)})",
                            description=chunk,
                            color=Colour.blue()
                        )
                        if isinstance(ctx, discord.Interaction):
                            response = await ctx.followup.send(embed=embed)
                        else:
                            response = await ctx.channel.send(embed=embed)
                    else:
                        embed = Embed(
                            description=chunk,
                            color=Colour.blue()
                        )
                        if isinstance(ctx, discord.Interaction):
                            await ctx.followup.send(embed=embed)
                        else:
                            await ctx.channel.send(embed=embed)
            
            # افزودن واکنش‌ها به اولین پیام
            await response.add_reaction("👍")
            await response.add_reaction("👎")

            end_time = time.time()
            query_processing_latency.set((end_time - start_time) * 1000)

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            error_msg = (
                "Sorry, I encountered an error processing your request.\n"
                "Please try again or ask more specifically."
            )
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(error_msg, ephemeral=True)
            else:
                await ctx.channel.send(error_msg)
            error_count.inc()

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
