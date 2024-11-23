import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from opgg_scraper import get_player_rank
from data_manager import load_players, save_players

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Configurar el bot con comandos de barra
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Lista de jugadores (cargada al iniciar)
players = load_players()

@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot se conecta"""
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

@bot.tree.command(name="add", description="Añade un jugador a la leaderboard.")
async def add_player(interaction: discord.Interaction, player_tag: str):
    """Añade un jugador a la leaderboard"""
    # if interaction.user.id in players:
    #     await interaction.response.send_message(
    #         f"{interaction.user.mention}, ya estás registrado como: {players[interaction.user.id]}",
    #         ephemeral=True
    #     )
    #     return

    players[player_tag] = interaction.user.id
    save_players(players)
    await interaction.response.send_message(
        f"{interaction.user.mention} ha añadido al jugador: {player_tag}",
        ephemeral=True
    )

@bot.tree.command(name="leaderboard", description="Muestra la lista de jugadores registrados y sus estadísticas.")
async def leaderboard(interaction: discord.Interaction):
    """Muestra la leaderboard con rangos, LP, victorias, derrotas y win rate"""

    # Diferir la respuesta para evitar el timeout de 3 segundos
    await interaction.response.defer()

    if not players:
        await interaction.followup.send("No hay jugadores registrados aún.", ephemeral=True)
        return

    leaderboard_message = "**Leaderboard:**\n"
    print(players)
    for player_tag in players.keys():
        rank_data = get_player_rank(player_tag)
        print(player_tag)
        if rank_data:
            leaderboard_message += (
                f"\n{player_tag} - {rank_data['tier']} "
                f"con {rank_data['lp']}\n"
                f"Estadísticas: {rank_data['win_lose']} ({rank_data['win_rate']})\n"
            )

        else:
            leaderboard_message += f"{player_tag} - No se pudo obtener información.\n"

    # Enviar el mensaje final como seguimiento
    await interaction.followup.send(leaderboard_message)


bot.run(TOKEN)
