import os
import random
import asyncio
import discord
import emoji
from io import BytesIO
from base64 import b64decode
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from huggingface_hub import InferenceClient


# ---------------------
# Cargar variables de entorno
# ---------------------
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("❌ No se encontró la variable de entorno DISCORD_TOKEN")

if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ No se encontró la variable de entorno HUGGINGFACE_API_KEY")


# ---------------------
# Clientes Hugging Face / OpenRouter
# ---------------------
hf_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HUGGINGFACE_API_KEY
)

hf_img_client = InferenceClient(HUGGINGFACE_API_KEY)


# ---------------------
# Emojis y temas
# ---------------------
ALL_EMOJIS = [e for e in emoji.EMOJI_DATA.keys()]

THEMES = {
    "chill": ["😎", "☮️", "🌊", "✨", "🌴", "🛋️", "🎵", "💫"],
    "chillimg": ["🎨", "🔥", "🌈", "💫", "🎭", "🖌️", "🖼️", "🌟"],
    "genimg": ["⚡", "🎉", "🥳", "🎮", "🧠", "💥", "🎆"]
}


# ---------------------
# Función principal de respuesta con emojis
# ---------------------
async def obtener_respuesta_stream(
    prompt: str,
    message: discord.Message,
    command="chill",
    image_url: str | None = None
):
    """Genera la respuesta del bot de manera streaming con emojis."""
    content_list: list[dict[str, str]] = [{"type": "text", "text": prompt}]
    if image_url:
        content_list.append({"type": "image_url", "image_url": image_url})

    messages = [
        {
            "role": "system",
            "content": (
                "Eres Chillbot, un bot estilo Rndgamer: relajado, directo, "
                "motivador, con humor inteligente, siempre chill 😎☮️."
            )
        },
        {"role": "user", "content": content_list}
    ]

    stream = hf_client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic",
        messages=messages,
        stream=True
    )

    respuesta_parcial = "🧠 *Chillbot dice:* "
    await message.edit(content=respuesta_parcial)

    buffer = ""
    mensajes_a_enviar = []

    async def editar_mensaje():
        nonlocal respuesta_parcial, buffer, mensajes_a_enviar
        theme_emojis = THEMES.get(command, ALL_EMOJIS)

        while True:
            if buffer:
                bloque = buffer
                buffer = ""

                # Añadir emojis según longitud
                if len(bloque) < 50:
                    densidad = 1
                elif len(bloque) < 150:
                    densidad = random.randint(1, 2)
                else:
                    densidad = random.randint(2, 5)

                if random.random() < 0.25:
                    bloque += "".join(random.choices(theme_emojis, k=densidad))

                respuesta_parcial += bloque

                # Dividir en mensajes si excede límite
                while len(respuesta_parcial) > 1900:
                    mensajes_a_enviar.append(respuesta_parcial[:1900])
                    respuesta_parcial = respuesta_parcial[1900:]

                if mensajes_a_enviar:
                    for msg_chunk in mensajes_a_enviar:
                        await message.channel.send(msg_chunk)
                    mensajes_a_enviar = []

                await message.edit(content=respuesta_parcial)
            await asyncio.sleep(0.05)

    editar_task = asyncio.create_task(editar_mensaje())

    try:
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                buffer += delta
    finally:
        editar_task.cancel()
        try:
            await editar_task
        except asyncio.CancelledError:
            pass

        if buffer:
            respuesta_parcial += buffer

        while len(respuesta_parcial) > 1900:
            await message.channel.send(respuesta_parcial[:1900])
            respuesta_parcial = respuesta_parcial[1900:]

        await message.edit(
            content=respuesta_parcial + "\n\n☮️ Siempre chill como Rndgamer 😌✨"
        )


# ---------------------
# Generación de imágenes robusta
# ---------------------
def generar_imagen(prompt: str) -> BytesIO:
    """
    Genera una imagen a partir de un prompt usando Hugging Face InferenceClient.
    Devuelve un BytesIO listo para enviar a Discord.
    Compatible con PIL.Image.Image o diccionario con 'image_base64'.
    """
    result = hf_img_client.text_to_image(prompt=prompt, width=512, height=512)
    buffer = BytesIO()

    if isinstance(result, Image.Image):
        result.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    if isinstance(result, dict) and "image_base64" in result:
        image_bytes = b64decode(result["image_base64"])
        buffer.write(image_bytes)
        buffer.seek(0)
        return buffer

    raise TypeError(f"Tipo de salida no soportado: {type(result)}")


# ---------------------
# Configuración Discord
# ---------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")


@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return

    content = msg.content.strip()

    # Comando de ayuda
    if content.startswith("!help"):
        ayuda = (
            "🧠 **Comandos de Chillbot:**\n"
            "• !chill <texto> → Respuesta chill con emojis.\n"
            "• !chillimg <texto> | <url_imagen> → Analiza imagen + texto.\n"
            "• !genimg <texto> → Genera una imagen desde texto.\n"
            "• !help → Muestra esta lista de comandos.\n\n"
            "☮️ Siempre chill como Rndgamer 😌✨"
        )
        await msg.channel.send(ayuda)
        return

    # Comando chill
    if content.startswith("!chill "):
        pregunta = content[len("!chill "):].strip()
        async with msg.channel.typing():
            mensaje = await msg.channel.send("🧠 *Chillbot dice:* ...")
            await obtener_respuesta_stream(pregunta, mensaje, command="chill")
        return

    # Comando chillimg
    if content.startswith("!chillimg "):
        try:
            texto, url_imagen = content[len("!chillimg "):].rsplit("|", 1)
            texto = texto.strip()
            url_imagen = url_imagen.strip()

            async with msg.channel.typing():
                mensaje = await msg.channel.send("🧠 *Chillbot dice:* ...")
                await obtener_respuesta_stream(
                    texto, mensaje, command="chillimg", image_url=url_imagen
                )
        except ValueError:
            await msg.channel.send("⚠️ Usa el formato: !chillimg <texto> | <url_imagen>")
        return

    # Comando genimg
    if content.startswith("!genimg "):
        prompt = content[len("!genimg "):].strip()
        async with msg.channel.typing():
            mensaje = await msg.channel.send("🎨 Generando imagen chill... 😎")
            imagen_bytes = generar_imagen(prompt)
            await msg.channel.send(
                file=discord.File(fp=imagen_bytes, filename="imagen.png")
            )
            await mensaje.delete()
        return


# ---------------------
# Iniciar bot
# ---------------------
client.run(DISCORD_TOKEN)
