#!/usr/bin/env python3
"""
FenixBot - Bot Discord com sistema de tickets
Versão melhorada com tratamento de erros e configuração via ambiente
"""

import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import json
import os
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class FenixBot(commands.Bot):
    """Bot Discord personalizado com funcionalidades de ticket"""
    
    def __init__(self):
        # Configuração de intents (sem privileged intents)
        intents = discord.Intents.default()
        # Não usando message_content para evitar privileged intents
        
        super().__init__(
            command_prefix=os.getenv("BOT_PREFIX", "!"),
            intents=intents,
            help_command=None
        )
        
        self.config_file = "config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Carrega configuração do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    logger.info("Configuração carregada com sucesso")
                    return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            
        # Configuração padrão
        default_config = {
            "categoria_produtos": None,
            "categoria_parcerias": None,
            "canal_logs": None,
            "cargo_staff": None,
            "ticket_counter": 1
        }
        logger.info("Usando configuração padrão")
        return default_config
        
    def save_config(self):
        """Salva configuração no arquivo JSON"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                logger.debug("Configuração salva")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            
    async def setup_hook(self):
        """Configuração inicial do bot"""
        logger.info("Configurando bot...")
        
        # Adiciona comandos
        await self.setup_commands()
        
        # Sincroniza comandos slash
        try:
            synced = await self.tree.sync()
            logger.info(f"Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos: {e}")
            
    async def on_ready(self):
        """Evento disparado quando o bot está pronto"""
        logger.info(f"Bot conectado como {self.user}")
        logger.info(f"Conectado a {len(self.guilds)} servidor(es)")
        
        # Atualiza status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servidores | !ajuda"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        logger.info("FenixBot está online e pronto!")
        
    async def on_error(self, event, *args, **kwargs):
        """Tratamento global de erros"""
        logger.error(f"Erro no evento {event}: {args}", exc_info=True)
        
    async def on_command_error(self, ctx, error):
        """Tratamento de erros de comandos"""
        logger.error(f"Erro no comando {ctx.command}: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignora comandos não encontrados
            
        await ctx.send(f"❌ Ocorreu um erro: {str(error)}")
        
    async def start(self):
        """Inicia o bot com o token do ambiente"""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN não encontrado nas variáveis de ambiente")
            
        await super().start(token, reconnect=True)


# ===========================
# Modal: Solicitar Produto
# ===========================
class ModalProduto(Modal, title="🎨 Solicitar Produto Personalizado"):
    nome_produto = TextInput(
        label="Nome do Produto",
        placeholder="Ex: Logo, Banner, Miniatura...",
        required=True
    )
    descricao = TextInput(
        label="Descrição do Pedido",
        placeholder="Descreva como deseja a arte, cores, temas, referências...",
        style=discord.TextStyle.long,
        max_length=1000,
        required=True
    )
    prazo = TextInput(
        label="Prazo Desejado",
        placeholder="Ex: 3 dias, 1 semana...",
        required=True
    )

    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            categoria_id = self.bot.config["categoria_produtos"]
            categoria = guild.get_channel(categoria_id) if categoria_id else None

            if not categoria:
                return await interaction.followup.send(
                    "⚠️ Categoria de produtos não configurada. Contacte a administração.", 
                    ephemeral=True
                )

            numero = self.bot.config["ticket_counter"]
            self.bot.config["ticket_counter"] += 1
            self.bot.save_config()

            # Cria canal do ticket
            canal = await guild.create_text_channel(
                name=f"produto-{self.user.name}-{numero}",
                category=categoria,
                topic=f"Produto: {self.nome_produto.value} | Prazo: {self.prazo.value}"
            )

            # Configura permissões
            await canal.set_permissions(self.user, read_messages=True, send_messages=True)
            staff = guild.get_role(self.bot.config["cargo_staff"])
            if staff:
                await canal.set_permissions(staff, read_messages=True, send_messages=True)
            await canal.set_permissions(guild.default_role, read_messages=False)

            # Embed de boas-vindas
            embed_boas_vindas = discord.Embed(
                title="📦 Pedido Recebido com Sucesso!",
                description=f"Olá {self.user.mention}, bem-vindo ao atendimento de **produtos personalizados**!\n\n"
                            f"Seu pedido foi registrado e em breve um membro da equipe irá te atender.\n\n"
                            f"🔍 **Detalhes do Pedido:**\n"
                            f"» **Produto:** `{self.nome_produto.value}`\n"
                            f"» **Descrição:** {self.descricao.value}\n"
                            f"» **Prazo:** `{self.prazo.value}`\n\n"
                            f"📌 Aguarde pacientemente. Agradecemos pela colaboração!",
                color=0xFF5733
            )
            embed_boas_vindas.set_author(name="Fênix Bots", icon_url=guild.icon.url if guild.icon else None)
            embed_boas_vindas.set_thumbnail(url="https://i.imgur.com/KeVqZJX.png")
            embed_boas_vindas.set_footer(text="Fênix Bots • Subzin, Akashi & Santana © 2025")
            embed_boas_vindas.timestamp = discord.utils.utcnow()

            view = PainelTicket(canal, self.user, self.bot)
            await canal.send(embed=embed_boas_vindas, view=view)

            # Log do sistema
            await self._log_ticket(guild, "📦 Novo Pedido de Produto", canal, {
                "Produto": self.nome_produto.value,
                "Prazo": self.prazo.value
            })

            await interaction.followup.send(
                f"✅ Pedido registrado! Acesse: {canal.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar ticket de produto: {e}")
            await interaction.followup.send(
                "❌ Erro interno. Tente novamente ou contacte a administração.",
                ephemeral=True
            )

    async def _log_ticket(self, guild, title, canal, details):
        """Envia log do ticket"""
        log_channel = guild.get_channel(self.bot.config["canal_logs"])
        if log_channel:
            try:
                log_embed = discord.Embed(
                    title=title,
                    description=f"**Cliente:** {self.user.mention}\n**Canal:** {canal.mention}",
                    color=discord.Color.orange()
                )
                
                for key, value in details.items():
                    log_embed.add_field(name=key, value=value, inline=True)
                    
                log_embed.set_thumbnail(url=self.user.display_avatar.url)
                log_embed.set_footer(text="Fênix Bots • Sistema de Tickets")
                await log_channel.send(embed=log_embed)
            except Exception as e:
                logger.error(f"Erro ao enviar log: {e}")


# ===========================
# Modal: Solicitar Parceria
# ===========================
class ModalParceria(Modal, title="🤝 Solicitar Parceria Oficial"):
    link_servidor = TextInput(
        label="Link do Servidor",
        placeholder="Cole aqui o convite do seu servidor...",
        required=True
    )

    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            categoria_id = self.bot.config["categoria_parcerias"]
            categoria = guild.get_channel(categoria_id) if categoria_id else None

            if not categoria:
                return await interaction.followup.send(
                    "⚠️ Categoria de parcerias não configurada. Contacte a administração.", 
                    ephemeral=True
                )

            numero = self.bot.config["ticket_counter"]
            self.bot.config["ticket_counter"] += 1
            self.bot.save_config()

            canal = await guild.create_text_channel(
                name=f"parceria-{self.user.name}-{numero}",
                category=categoria,
                topic=f"Parceria solicitada por {self.user}"
            )

            # Permissões
            await canal.set_permissions(self.user, read_messages=True, send_messages=True)
            staff = guild.get_role(self.bot.config["cargo_staff"])
            if staff:
                await canal.set_permissions(staff, read_messages=True, send_messages=True)
            await canal.set_permissions(guild.default_role, read_messages=False)

            # Embed de boas-vindas
            embed_boas_vindas = discord.Embed(
                title="🤝 Parceria Solicitada",
                description=f"Olá {self.user.mention}, obrigado por se interessar pela **parceria oficial**!\n\n"
                            "Deixe abaixo o link do seu servidor para análise.\n\n"
                            "✅ **Requisitos para parceria:**\n"
                            "• 200+ membros\n"
                            "• Nenhuma regra do Discord quebrada\n"
                            "• Sem conteúdo NSFW\n"
                            "• Sem racismo ou nazismo\n"
                            "• Ambiente limpo e organizado",
                color=0x5865F2
            )
            embed_boas_vindas.set_author(name="Fênix Bots", icon_url=guild.icon.url if guild.icon else None)
            embed_boas_vindas.set_footer(text="Fênix Bots • Subzin, Akashi & Santana © 2025")
            embed_boas_vindas.timestamp = discord.utils.utcnow()

            view = PainelTicket(canal, self.user, self.bot)
            await canal.send(embed=embed_boas_vindas, view=view)

            # Log
            await self._log_parceria(guild, canal)

            await interaction.followup.send(
                f"✅ Parceria solicitada! Acesse: {canal.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar ticket de parceria: {e}")
            await interaction.followup.send(
                "❌ Erro interno. Tente novamente ou contacte a administração.",
                ephemeral=True
            )

    async def _log_parceria(self, guild, canal):
        """Envia log da parceria"""
        log_channel = guild.get_channel(self.bot.config["canal_logs"])
        if log_channel:
            try:
                log_embed = discord.Embed(
                    title="🤝 Nova Solicitação de Parceria",
                    description=f"**Cliente:** {self.user.mention}\n"
                                f"**Canal:** {canal.mention}\n"
                                f"**Link do Servidor:** [Clique aqui]({self.link_servidor.value})",
                    color=discord.Color.purple()
                )
                log_embed.set_thumbnail(url=self.user.display_avatar.url)
                log_embed.set_footer(text="Fênix Bots • Sistema de Tickets")
                await log_channel.send(embed=log_embed)
            except Exception as e:
                logger.error(f"Erro ao enviar log: {e}")


# ===========================
# Botões do Painel Inicial
# ===========================
class PainelInicial(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📦 Produtos", style=discord.ButtonStyle.primary, emoji="🎨", custom_id="produtos_btn")
    async def produtos(self, interaction: discord.Interaction, button: Button):
        modal = ModalProduto(interaction.user, interaction.client)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🤝 Parcerias", style=discord.ButtonStyle.success, emoji="💼", custom_id="parcerias_btn")
    async def parcerias(self, interaction: discord.Interaction, button: Button):
        modal = ModalParceria(interaction.user, interaction.client)
        await interaction.response.send_modal(modal)


# ===========================
# Painel do Ticket (Fechar)
# ===========================
class PainelTicket(View):
    def __init__(self, channel, owner, bot):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner = owner
        self.bot = bot

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="❌", custom_id="fechar_ticket_btn")
    async def fechar(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "🚫 Apenas a equipe pode fechar este ticket.", ephemeral=True
            )

        view = ConfirmarFechamento(self.channel, self.owner, self.bot)
        await interaction.response.send_message(
            "⚠️ Tem certeza que deseja fechar este ticket?",
            view=view,
            ephemeral=True
        )


# ===========================
# Confirmação de Fechamento
# ===========================
class ConfirmarFechamento(View):
    def __init__(self, channel, owner, bot):
        super().__init__(timeout=30)
        self.channel = channel
        self.owner = owner
        self.bot = bot

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.danger, emoji="✅", custom_id="confirmar_fechamento")
    async def confirmar(self, interaction: discord.Interaction, button: Button):
        try:
            # Salvar transcript
            mensagens = []
            async for msg in self.channel.history(limit=100, oldest_first=True):
                tempo = msg.created_at.strftime("%H:%M")
                conteudo = msg.content or "(sem texto)"
                if msg.attachments:
                    conteudo += " [arquivo]"
                mensagens.append(f"[{tempo}] {msg.author}: {conteudo}")

            os.makedirs("transcripts", exist_ok=True)
            caminho = f"transcripts/transcript-{self.channel.id}.txt"
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(f"📁 TRANSCRIPT - {self.channel.name}\n")
                f.write(f"Fechado por: {interaction.user}\n")
                f.write(f"Data: {discord.utils.utcnow().strftime('%d/%m/%Y %H:%M')}\n\n")
                f.write("\n".join(mensagens))

            # Embed de fechamento
            embed_fechado = discord.Embed(
                title="🎫 Ticket Fechado",
                description=f"O ticket foi fechado por {interaction.user.mention}.\n\n"
                            "Se precisar de mais ajuda, abra um novo ticket!\n\n"
                            "Agradecemos pela preferência! 🌟",
                color=0x2ECC71
            )
            embed_fechado.set_footer(text="Fênix Bots • Subzin, Akashi & Santana © 2025")
            embed_fechado.timestamp = discord.utils.utcnow()

            # Enviar log
            log_channel = interaction.guild.get_channel(self.bot.config["canal_logs"])
            if log_channel:
                try:
                    with open(caminho, "rb") as f:
                        file = discord.File(f)
                        await log_channel.send(
                            embed=discord.Embed(
                                title="📁 Ticket Fechado",
                                description=f"Canal: {self.channel.mention}\nFechado por: {interaction.user.mention}",
                                color=0xFFD700
                            ).set_footer(text="Fênix Bots • Tickets"),
                            file=file
                        )
                except Exception as e:
                    logger.error(f"Erro ao enviar transcript: {e}")

            await interaction.response.send_message("✅ Ticket fechado!", ephemeral=True)
            await self.channel.send(embed=embed_fechado)
            
            # Aguarda um pouco antes de deletar
            await asyncio.sleep(3)
            await self.channel.delete()
            
        except Exception as e:
            logger.error(f"Erro ao fechar ticket: {e}")
            await interaction.response.send_message(
                "❌ Erro ao fechar ticket. Tente novamente.",
                ephemeral=True
            )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="cancelar_fechamento")
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("✅ Fechamento cancelado.", ephemeral=True)


# ===========================
# Comandos de Configuração
# ===========================
@discord.app_commands.command(name="config", description="Configura o bot")
@discord.app_commands.default_permissions(administrator=True)
async def config_bot(interaction: discord.Interaction):
    """Comando para configurar o bot"""
    embed = discord.Embed(
        title="🔧 Configuração do FenixBot",
        description="Use os comandos abaixo para configurar o bot:",
        color=0x00FF00
    )
    
    embed.add_field(
        name="Configurar Categoria de Produtos",
        value="`/set_categoria_produtos <id_categoria>`",
        inline=False
    )
    
    embed.add_field(
        name="Configurar Categoria de Parcerias", 
        value="`/set_categoria_parcerias <id_categoria>`",
        inline=False
    )
    
    embed.add_field(
        name="Configurar Canal de Logs",
        value="`/set_canal_logs <id_canal>`",
        inline=False
    )
    
    embed.add_field(
        name="Configurar Cargo Staff",
        value="`/set_cargo_staff <id_cargo>`",
        inline=False
    )
    
    embed.add_field(
        name="Criar Painel de Tickets",
        value="`/painel`",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Adiciona comandos ao bot
async def add_commands(bot):
    """Adiciona comandos ao bot"""
    bot.add_command(config_bot)
    
    @bot.command(name="painel")
    @commands.has_permissions(administrator=True)
    async def criar_painel(ctx):
        """Cria o painel de tickets"""
        embed = discord.Embed(
            title="🎫 Sistema de Tickets - Fênix Bots",
            description="Bem-vindo ao nosso sistema de atendimento!\n\n"
                        "🎨 **Produtos Personalizados**\n"
                        "Solicite logos, banners, miniaturas e outros designs!\n\n"
                        "🤝 **Parcerias Oficiais**\n"
                        "Interesse em fazer parceria conosco?\n\n"
                        "Clique nos botões abaixo para abrir um ticket:",
            color=0x5865F2
        )
        embed.set_author(name="Fênix Bots", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_thumbnail(url="https://i.imgur.com/KeVqZJX.png")
        embed.set_footer(text="Fênix Bots • Subzin, Akashi & Santana © 2025")
        
        view = PainelInicial()
        await ctx.send(embed=embed, view=view)
        
    # Comandos de configuração
    @bot.command(name="set_categoria_produtos")
    @commands.has_permissions(administrator=True)
    async def set_categoria_produtos(ctx, categoria_id: int):
        bot.config["categoria_produtos"] = categoria_id
        bot.save_config()
        await ctx.send(f"✅ Categoria de produtos configurada: <#{categoria_id}>")
        
    @bot.command(name="set_categoria_parcerias")
    @commands.has_permissions(administrator=True)
    async def set_categoria_parcerias(ctx, categoria_id: int):
        bot.config["categoria_parcerias"] = categoria_id
        bot.save_config()
        await ctx.send(f"✅ Categoria de parcerias configurada: <#{categoria_id}>")
        
    @bot.command(name="set_canal_logs")
    @commands.has_permissions(administrator=True)
    async def set_canal_logs(ctx, canal_id: int):
        bot.config["canal_logs"] = canal_id
        bot.save_config()
        await ctx.send(f"✅ Canal de logs configurado: <#{canal_id}>")
        
    @bot.command(name="set_cargo_staff")
    @commands.has_permissions(administrator=True)
    async def set_cargo_staff(ctx, cargo_id: int):
        bot.config["cargo_staff"] = cargo_id
        bot.save_config()
        await ctx.send(f"✅ Cargo de staff configurado: <@&{cargo_id}>")

# Adiciona método à classe FenixBot
FenixBot.setup_commands = lambda self: add_commands(self)
