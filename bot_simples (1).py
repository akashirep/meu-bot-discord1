#!/usr/bin/env python3
"""
FenixBot - Bot Discord simplificado com sistema de tickets
Versão sem privileged intents
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

class FenixBotSimples(commands.Bot):
    """Bot Discord simplificado"""
    
    def __init__(self):
        # Intents básicos apenas
        intents = discord.Intents.default()
        
        super().__init__(
            command_prefix="$",  # Prefix diferente para evitar conflitos
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
        logger.info("Configurando bot simples...")
        
        # Adiciona comandos slash
        @discord.app_commands.command(name="config", description="Mostra configuração do bot")
        @discord.app_commands.default_permissions(administrator=True)
        async def config_cmd(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🔧 Configuração do FenixBot",
                description="Use os comandos slash abaixo:",
                color=0x00FF00
            )
            embed.add_field(name="Configurar Produtos", value="`/set_produtos <categoria_id>`", inline=False)
            embed.add_field(name="Configurar Parcerias", value="`/set_parcerias <categoria_id>`", inline=False)
            embed.add_field(name="Configurar Logs", value="`/set_logs <canal_id>`", inline=False)
            embed.add_field(name="Criar Painel", value="`/painel`", inline=False)
            await interaction.response.send_message(embed=embed)
            
        @discord.app_commands.command(name="set_produtos", description="Configura categoria de produtos")
        @discord.app_commands.default_permissions(administrator=True)
        async def set_produtos(interaction: discord.Interaction, categoria_id: str):
            try:
                cat_id = int(categoria_id)
                self.config["categoria_produtos"] = cat_id
                self.save_config()
                await interaction.response.send_message(f"✅ Categoria de produtos: <#{cat_id}>")
            except:
                await interaction.response.send_message("❌ ID inválido!", ephemeral=True)
                
        @discord.app_commands.command(name="set_parcerias", description="Configura categoria de parcerias")
        @discord.app_commands.default_permissions(administrator=True)
        async def set_parcerias(interaction: discord.Interaction, categoria_id: str):
            try:
                cat_id = int(categoria_id)
                self.config["categoria_parcerias"] = cat_id
                self.save_config()
                await interaction.response.send_message(f"✅ Categoria de parcerias: <#{cat_id}>")
            except:
                await interaction.response.send_message("❌ ID inválido!", ephemeral=True)
                
        @discord.app_commands.command(name="set_logs", description="Configura canal de logs")
        @discord.app_commands.default_permissions(administrator=True)
        async def set_logs(interaction: discord.Interaction, canal_id: str):
            try:
                ch_id = int(canal_id)
                self.config["canal_logs"] = ch_id
                self.save_config()
                await interaction.response.send_message(f"✅ Canal de logs: <#{ch_id}>")
            except:
                await interaction.response.send_message("❌ ID inválido!", ephemeral=True)
                
        @discord.app_commands.command(name="painel", description="Cria painel de tickets")
        @discord.app_commands.default_permissions(administrator=True)
        async def painel_cmd(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🎫 Sistema de Tickets - Fênix Bots",
                description="Bem-vindo ao sistema de atendimento!\n\n"
                           "🎨 **Produtos Personalizados**\n"
                           "Logos, banners, miniaturas e designs!\n\n"
                           "🤝 **Parcerias Oficiais**\n"
                           "Parcerias com nosso servidor!\n\n"
                           "Clique nos botões para abrir ticket:",
                color=0x5865F2
            )
            embed.set_footer(text="Fênix Bots • 2025")
            
            view = PainelTickets(self)
            await interaction.response.send_message(embed=embed, view=view)
        
        # Adiciona comandos à árvore
        self.tree.add_command(config_cmd)
        self.tree.add_command(set_produtos)
        self.tree.add_command(set_parcerias)
        self.tree.add_command(set_logs)
        self.tree.add_command(painel_cmd)
        
        # Sincroniza comandos
        try:
            synced = await self.tree.sync()
            logger.info(f"Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos: {e}")
            
    async def on_ready(self):
        """Evento quando bot fica online"""
        logger.info(f"Bot conectado como {self.user}")
        logger.info(f"Conectado a {len(self.guilds)} servidor(es)")
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servidores"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        logger.info("FenixBot simples está online!")
        
    async def start(self):
        """Inicia o bot"""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN não encontrado")
            
        await super().start(token, reconnect=True)


# Views e Modals
class PainelTickets(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="📦 Produtos", style=discord.ButtonStyle.primary, custom_id="produtos_btn")
    async def produtos(self, interaction: discord.Interaction, button: Button):
        modal = ModalProdutoSimples(interaction.user, self.bot)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🤝 Parcerias", style=discord.ButtonStyle.success, custom_id="parcerias_btn")
    async def parcerias(self, interaction: discord.Interaction, button: Button):
        modal = ModalParceriaSimples(interaction.user, self.bot)
        await interaction.response.send_modal(modal)


class ModalProdutoSimples(Modal, title="🎨 Solicitar Produto"):
    nome = TextInput(label="Nome do Produto", placeholder="Ex: Logo, Banner...", required=True)
    descricao = TextInput(label="Descrição", style=discord.TextStyle.long, required=True)
    prazo = TextInput(label="Prazo", placeholder="Ex: 3 dias", required=True)

    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        categoria_id = self.bot.config["categoria_produtos"]
        
        if not categoria_id:
            return await interaction.followup.send("❌ Categoria não configurada!", ephemeral=True)
            
        categoria = guild.get_channel(categoria_id)
        if not categoria:
            return await interaction.followup.send("❌ Categoria inválida!", ephemeral=True)

        numero = self.bot.config["ticket_counter"]
        self.bot.config["ticket_counter"] += 1
        self.bot.save_config()

        # Cria canal
        canal = await guild.create_text_channel(
            name=f"produto-{self.user.name}-{numero}",
            category=categoria
        )

        # Permissões
        await canal.set_permissions(self.user, read_messages=True, send_messages=True)
        await canal.set_permissions(guild.default_role, read_messages=False)

        # Mensagem
        embed = discord.Embed(
            title="📦 Produto Solicitado",
            description=f"Olá {self.user.mention}!\n\n"
                       f"**Produto:** {self.nome.value}\n"
                       f"**Descrição:** {self.descricao.value}\n"
                       f"**Prazo:** {self.prazo.value}",
            color=0xFF5733
        )
        await canal.send(embed=embed)
        await interaction.followup.send(f"✅ Ticket criado: {canal.mention}", ephemeral=True)


class ModalParceriaSimples(Modal, title="🤝 Solicitar Parceria"):
    servidor = TextInput(label="Link do Servidor", required=True)

    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        categoria_id = self.bot.config["categoria_parcerias"]
        
        if not categoria_id:
            return await interaction.followup.send("❌ Categoria não configurada!", ephemeral=True)
            
        categoria = guild.get_channel(categoria_id)
        if not categoria:
            return await interaction.followup.send("❌ Categoria inválida!", ephemeral=True)

        numero = self.bot.config["ticket_counter"]
        self.bot.config["ticket_counter"] += 1
        self.bot.save_config()

        # Cria canal
        canal = await guild.create_text_channel(
            name=f"parceria-{self.user.name}-{numero}",
            category=categoria
        )

        # Permissões
        await canal.set_permissions(self.user, read_messages=True, send_messages=True)
        await canal.set_permissions(guild.default_role, read_messages=False)

        # Mensagem
        embed = discord.Embed(
            title="🤝 Parceria Solicitada",
            description=f"Olá {self.user.mention}!\n\n"
                       f"**Link:** {self.servidor.value}\n\n"
                       "Aguarde análise da equipe!",
            color=0x5865F2
        )
        await canal.send(embed=embed)
        await interaction.followup.send(f"✅ Ticket criado: {canal.mention}", ephemeral=True)