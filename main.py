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

# Orden jerárquico de los rangos en League of Legends
tier_order = {
    "Challenger": 9, "Grandmaster": 8, "Master": 7, "Diamond": 6,
    "Platinum": 5, "Gold": 4, "Silver": 3, "Bronze": 2, "Iron": 1,
    "Unranked": 0  # Unranked es el rango más bajo
}


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
    players[player_tag] = interaction.user.id
    save_players(players)
    print(f"Jugador añadido: {player_tag}")
    await interaction.response.send_message(
        f"{interaction.user.mention} ha añadido al jugador: {player_tag}",
        ephemeral=True
    )


@bot.tree.command(name="leaderboard", description="Muestra la lista de jugadores registrados y sus estadísticas.")
async def leaderboard(interaction: discord.Interaction):
    """Muestra la leaderboard ordenada con rangos, LP, victorias, derrotas y win rate."""
    await interaction.response.defer()  # Diferir la respuesta

    if not players:
        print("No hay jugadores registrados aún.")
        await interaction.followup.send("No hay jugadores registrados aún.", ephemeral=True)
        return

    leaderboard_data = []

    # Paso 1: Recolectar información de los jugadores
    print("Recolectando información de los jugadores...")
    for player_tag in players.keys():
        rank_data = get_player_rank(player_tag)
        print(f"Datos obtenidos para {player_tag}: {rank_data}")
        if rank_data:
            tier_split = rank_data["tier"].split()
            main_tier = tier_split[0] if len(tier_split) > 0 else "Unranked"
            sub_tier = int(tier_split[1]) if len(tier_split) > 1 and tier_split[1].isdigit() else 0

            # Corregir tier_rank usando nombres en mayúsculas
            tier_rank = tier_order.get(main_tier.capitalize(), 0)

            leaderboard_data.append({
                "name": player_tag,
                "url": f"<https://www.op.gg/summoners/euw/{player_tag.replace(' ', '-').replace('#', '-')}>",
                "tier": rank_data["tier"],
                "main_tier": main_tier,
                "tier_rank": tier_rank,  # Asignar valor correcto
                "sub_tier": sub_tier,  # Nivel dentro del rango
                "lp": int(rank_data["lp"].split()[0]) if rank_data["lp"].split()[0].isdigit() else 0,
                "win_rate": rank_data["win_rate"],
                "wins": rank_data["win_lose"].split("W")[0],
                "losses": rank_data["win_lose"].split("W")[1].replace("L", "").strip()
            })
        else:
            leaderboard_data.append({
                "name": player_tag,
                "url": f"<https://www.op.gg/summoners/euw/{player_tag.replace(' ', '-').replace('#', '-')}>",
                "tier": "Unranked",
                "main_tier": "Unranked",
                "tier_rank": 0,  # Valor más bajo para Unranked
                "sub_tier": 0,
                "lp": 0,
                "win_rate": "Win rate 0%",
                "wins": "0",
                "losses": "0"
            })

    # Paso 2: Ordenar los datos recolectados
    print("Datos antes de ordenar:")
    for player in leaderboard_data:
        print(player)

    leaderboard_data.sort(key=lambda x: (-x["tier_rank"], x["sub_tier"], -x["lp"]))

    print("Datos después de ordenar:")
    for player in leaderboard_data:
        print(player)

    # Paso 3: Generar el mensaje de la leaderboard
    leaderboard_message = "**🏆 Leaderboard:**\n\n"
    for idx, player in enumerate(leaderboard_data, start=1):
        leaderboard_message += (
            f"{idx}. [{player['name']}]({player['url']}) - **{player['tier']}** con **{player['lp']} LP**\n"
            f"   Estadísticas: 🟢 **{player['wins']}W** 🔴 **{player['losses']}L** "
            f"(**{player['win_rate']}**)\n\n"
        )

    # Paso 4: Enviar el mensaje
    await interaction.followup.send(leaderboard_message)


bot.run(TOKEN)
