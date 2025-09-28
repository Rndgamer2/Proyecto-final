import discord
from discord.ext import commands
import classifier
import database
import os
import uuid
from dotenv import load_dotenv

# Cargar claves del archivo .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

#Datos curiosos de los animales 
from animal_facts import animal_facts

# ✅ NUEVA FUNCIÓN PARA BUSCAR DATOS CURIOSOS
def obtener_dato_curioso(animal_detectado):
    clave = animal_detectado.lower().replace(" ", "_")
    if clave in animal_facts:
        return animal_facts[clave]
    
    # Búsqueda flexible por palabra clave
    for key in animal_facts:
        if key in clave or clave in key:
            return animal_facts[key]
    
    return "No tengo un dato curioso para este animal, pero prometo aprenderlo pronto 😉."


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'🐍 Bot conectado como {bot.user}')
    database.init_db()

@bot.command()
async def identificar2(ctx, *, nombre_animal: str):
    dato = obtener_dato_curioso(nombre_animal)
    await ctx.send(f"🐾 ¡Detectado! Parece ser un *{nombre_animal}*.\n📌 Dato curioso: {dato}")

@bot.command()
async def identificar(ctx):
    if not ctx.message.attachments:
        await ctx.send("📷 Por favor sube una imagen para identificar.")
        return

    attachment = ctx.message.attachments[0]
    extension = os.path.splitext(attachment.filename)[1]
    nombre_archivo = f"{uuid.uuid4()}{extension}"
    ruta = f"temp/{nombre_archivo}"
    
    await attachment.save(ruta)

    await ctx.send("🔍 Analizando la imagen, por favor espera unos segundos...")

    especie = classifier.clasificar_imagen(ruta)

    if especie == "Especie desconocida":
        await ctx.send("❌ No pude identificar la especie. Prueba con otra imagen más clara.")
    else:
        database.guardar_animal(ctx.author.id, especie, ruta)

        # 🔁 Incluye dato curioso aquí también
        dato = obtener_dato_curioso(especie)
        await ctx.send(
            f"✅ Especie detectada: **{especie}**. Imagen guardada en tu colección.\n"
            f"📌 Dato curioso: {dato}"
        )

@bot.command()
async def misanimales(ctx):
    especies = database.obtener_especies(ctx.author.id)
    if especies:
        lista = "\n".join(f"- {e}" for e in especies)
        await ctx.send(f"📚 Tienes registradas estas especies:\n{lista}")
    else:
        await ctx.send("🤷‍♂️ Aún no has registrado ninguna especie.")

@bot.command()
async def verespecie(ctx, *, especie: str):
    imagenes = database.obtener_imagenes_por_especie(ctx.author.id, especie)
    if not imagenes:
        await ctx.send("📭 No tienes imágenes de esa especie.")
        return

    await ctx.send(f"📂 Mostrando imágenes guardadas para: **{especie}**")
    for img in imagenes:
        await ctx.send(file=discord.File(img))

bot.run(DISCORD_TOKEN)  # Recuerda reemplazar esto por tu token real de forma segura


