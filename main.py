import os
import asyncio
from datetime import datetime

import discord
from fastapi import FastAPI
from fastapi.responses import JSONResponse

TOKEN = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1457588380174127299"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
app = FastAPI()

bot_pronto = asyncio.Event()

@client.event
async def on_ready():
    print("Bot logado como:", client.user)
    bot_pronto.set()

def fmt_data(dt: datetime):
    try:
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return str(dt)

async def buscar_no_canal(nome: str, limite: int = 2000):
    nome = (nome or "").strip()
    if nome == "":
        return []

    canal = client.get_channel(CHANNEL_ID)
    if canal is None:
        canal = await client.fetch_channel(CHANNEL_ID)

    resultados = []

    async for msg in canal.history(limit=limite, oldest_first=False):
        conteudo = msg.content or ""
        if nome.lower() in conteudo.lower():
            resultados.append({
                "mensagem": conteudo,
                "autor": str(msg.author),
                "data": fmt_data(msg.created_at),
                "id": str(msg.id)
            })

    return resultados

@app.on_event("startup")
async def iniciar_bot():
    if TOKEN == "":
        print("DISCORD_TOKEN vazio.")
        return
    asyncio.create_task(client.start(TOKEN))

@app.get("/buscar")
async def buscar(nome: str = ""):
    if TOKEN == "":
        return JSONResponse({"ok": False, "erro": "DISCORD_TOKEN não configurado."})

    try:
        await asyncio.wait_for(bot_pronto.wait(), timeout=25)
    except:
        return JSONResponse({"ok": False, "erro": "Bot não ficou pronto a tempo."})

    try:
        resultados = await buscar_no_canal(nome)
        return JSONResponse({"ok": True, "resultados": resultados})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})

@app.get("/")
async def home():
    return {"ok": True, "msg": "API online"}
