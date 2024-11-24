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
    """Muestra la leaderboard ordenada con rangos, LP, victorias, derrotas y win rate."""
    await interaction.response.defer()  # Diferir la respuesta

    if not players:
        await interaction.followup.send("No hay jugadores registrados aún.", ephemeral=True)
        return

    leaderboard_data = []

    # Recopilar datos
    for player_tag in players.keys():
        rank_data = get_player_rank(player_tag)
        if rank_data:
            leaderboard_data.append({
                "name": player_tag,
                "url": f"<https://www.op.gg/summoners/euw/{player_tag.replace(' ', '-').replace('#', '-')}>",  # Enlace sin preview
                "tier": rank_data["tier"],
                "lp": int(rank_data["lp"].split()[0]) if rank_data["lp"].split()[0].isdigit() else 0,
                "win_rate": rank_data["win_rate"],
                "wins": rank_data["win_lose"].split("W")[0],
                "losses": rank_data["win_lose"].split("W")[1].replace("L", "").strip()
            })
        else:
            leaderboard_data.append({
                "name": player_tag,
                "url": f"<https://www.op.gg/summoners/euw/{player_tag.replace(' ', '-').replace('#', '-')}>",
                "tier": "No Rank",
                "lp": 0,
                "win_rate": "Win rate 0%",
                "wins": "0",
                "losses": "0"
            })

    # Ordenar por LP
    leaderboard_data.sort(key=lambda x: (-x["lp"], x["tier"]))

    # Generar mensaje
    leaderboard_message = "**🏆 Leaderboard:**\n\n"
    for idx, player in enumerate(leaderboard_data, start=1):
        leaderboard_message += (
            f"{idx}. [{player['name']}]({player['url']}) - **{player['tier']}** con **{player['lp']} LP**\n"
            f"   Estadísticas: 🟢 **{player['wins']}W** 🔴 **{player['losses']}L** "
            f"(**{player['win_rate']}**)\n\n"
        )

    # Enviar respuesta
    await interaction.followup.send(leaderboard_message)




bot.run(TOKEN)
