#!/usr/bin/env python3
"""
FenixBot - Versão final simplificada
"""

import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import json
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

class FenixBotFinal(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
        self.config = {
            "categoria_produtos": None,
            "categoria_parcerias": None,
            "ticket_counter": 1
        }
        self.load_config()
        
    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    logger.info("Config carregada")
        except:
            pass
        
    def save_config(self):
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
            
    async def setup_hook(self):
        logger.info("Configurando bot final...")
        
        # Comandos simples
        @discord.app_commands.command(name="setup", description="Configurar bot")
        @discord.app_commands.default_permissions(administrator=True)
        async def setup_cmd(interaction: discord.Interaction, categoria_produtos: str, categoria_parcerias: str):
            """Configura as categorias de uma vez"""
            try:
                prod_id = int(categoria_produtos)
                parc_id = int(categoria_parcerias)
                
                self.config["categoria_produtos"] = prod_id
                self.config["categoria_parcerias"] = parc_id
                self.save_config()
                
                embed = discord.Embed(
                    title="✅ Configuração Completa!",
                    description=f"**Produtos:** <#{prod_id}>\n**Parcerias:** <#{parc_id}>",
                    color=0x00FF00
                )
                await interaction.response.send_message(embed=embed)
            except:
                await interaction.response.send_message("❌ IDs inválidos! Use apenas números.", ephemeral=True)
                
        @discord.app_commands.command(name="painel", description="Criar painel de tickets")
        @discord.app_commands.default_permissions(administrator=True)
        async def painel_cmd(interaction: discord.Interaction):
            """Cria o painel profissional de tickets"""
            if not self.config["categoria_produtos"] or not self.config["categoria_parcerias"]:
                return await interaction.response.send_message("❌ Configure primeiro com `/setup`!", ephemeral=True)
                
            embed = discord.Embed(
                title="🌟 FÊNIX BOTS - SISTEMA DE ATENDIMENTO",
                description="═══════════════════════════════════\n\n"
                           "**🎯 NOSSOS SERVIÇOS PREMIUM**\n\n"
                           "🎨 **PRODUTOS PERSONALIZADOS**\n"
                           "┣ 🖼️ Logos profissionais\n"
                           "┣ 🎬 Banners para YouTube/Twitch\n"
                           "┣ 📸 Thumbnails chamativas\n"
                           "┣ 🎭 Avatars únicos\n"
                           "┗ 🎪 Designs exclusivos\n\n"
                           "🤝 **PARCERIAS ESTRATÉGICAS**\n"
                           "┣ 💼 Parcerias comerciais\n"
                           "┣ 🌐 Cross-promotion\n"
                           "┣ 🚀 Colaborações especiais\n"
                           "┗ 📈 Crescimento mútuo\n\n"
                           "═══════════════════════════════════\n"
                           "**📞 PRONTO PARA COMEÇAR?**\n"
                           "Clique nos botões abaixo para abrir seu atendimento:",
                color=0x00D4FF
            )
            embed.set_author(
                name="Fênix Bots - Atendimento Premium", 
                icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
            )
            embed.set_thumbnail(url="https://i.imgur.com/KeVqZJX.png")
            embed.add_field(
                name="⚡ ATENDIMENTO RÁPIDO", 
                value="Resposta em até 24h", 
                inline=True
            )
            embed.add_field(
                name="🎨 QUALIDADE PREMIUM", 
                value="Designs profissionais", 
                inline=True
            )
            embed.add_field(
                name="💰 PREÇOS JUSTOS", 
                value="Valores acessíveis", 
                inline=True
            )
            embed.set_footer(
                text="Fênix Bots © 2025 • Subzin, Akashi & Santana • Qualidade Garantida ✨",
                icon_url="https://i.imgur.com/KeVqZJX.png"
            )
            embed.timestamp = discord.utils.utcnow()
            
            view = PainelView(self)
            await interaction.response.send_message(embed=embed, view=view)
            
        self.tree.add_command(setup_cmd)
        self.tree.add_command(painel_cmd)
        
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ {len(synced)} comandos sincronizados")
        except Exception as e:
            logger.error(f"Erro sync: {e}")
            
    async def on_ready(self):
        logger.info(f"🟢 {self.user} online!")
        logger.info(f"📊 {len(self.guilds)} servidores")
        
        # Status diferente para deploy vs desenvolvimento
        is_deployed = os.getenv('REPLIT_DEPLOYMENT') == '1'
        activity_name = "24/7 • Fênix Bots" if is_deployed else "tickets • dev"
        
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name),
            status=discord.Status.online
        )
        
    async def start(self):
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("Token não encontrado")
        await super().start(token, reconnect=True)


class PainelView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="🎨 PRODUTOS PREMIUM", 
        style=discord.ButtonStyle.primary, 
        custom_id="btn_produtos",
        emoji="🎨"
    )
    async def produtos_btn(self, interaction: discord.Interaction, button: Button):
        modal = ProdutoModal(self.bot)
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="🤝 PARCERIAS VIP", 
        style=discord.ButtonStyle.success, 
        custom_id="btn_parcerias",
        emoji="🤝"
    )
    async def parcerias_btn(self, interaction: discord.Interaction, button: Button):
        modal = ParceriaModal(self.bot)
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(
        label="📊 PORTFÓLIO", 
        style=discord.ButtonStyle.secondary, 
        custom_id="btn_portfolio",
        emoji="📊"
    )
    async def portfolio_btn(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="📊 PORTFÓLIO FÊNIX BOTS",
            description="**🎨 CONFIRA NOSSOS TRABALHOS:**\n\n"
                       "┣ 🖼️ **500+** Logos criados\n"
                       "┣ 🎬 **300+** Banners entregues\n" 
                       "┣ 📸 **200+** Thumbnails produzidas\n"
                       "┗ 🏆 **95%** Taxa de satisfação\n\n"
                       "🌟 **CLIENTES SATISFEITOS:**\n"
                       "• Streamers verificados\n"
                       "• Empresas parceiras\n"
                       "• Criadores de conteúdo\n\n"
                       "📞 **Solicite seu orçamento gratuito!**",
            color=0x9966FF
        )
        embed.set_footer(text="Fênix Bots • Qualidade Premium desde 2025")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ProdutoModal(Modal, title="🎨 Produto Personalizado"):
    produto = TextInput(label="Produto", placeholder="Ex: Logo, Banner, Thumbnail")
    detalhes = TextInput(label="Detalhes", style=discord.TextStyle.long, placeholder="Descreva o que deseja...")
    prazo = TextInput(label="Prazo", placeholder="Ex: 3 dias")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        categoria = guild.get_channel(self.bot.config["categoria_produtos"])
        
        if not categoria:
            return await interaction.followup.send("❌ Categoria não configurada!", ephemeral=True)

        # Cria ticket
        numero = self.bot.config["ticket_counter"]
        self.bot.config["ticket_counter"] += 1
        self.bot.save_config()

        canal = await guild.create_text_channel(
            name=f"produto-{interaction.user.name}-{numero}",
            category=categoria
        )

        # Permissões
        await canal.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await canal.set_permissions(guild.default_role, read_messages=False)

        # Embed do ticket
        embed = discord.Embed(
            title="🎨 NOVO PEDIDO DE PRODUTO PREMIUM",
            description="═══════════════════════════════════\n\n"
                       f"**👤 CLIENTE VIP:** {interaction.user.mention}\n"
                       f"**📅 DATA:** {discord.utils.format_dt(discord.utils.utcnow(), 'F')}\n\n"
                       f"**🎨 PRODUTO SOLICITADO:**\n"
                       f"```{self.produto.value}```\n\n"
                       f"**📝 DETALHES E ESPECIFICAÇÕES:**\n"
                       f"```{self.detalhes.value}```\n\n"
                       f"**⏰ PRAZO SOLICITADO:**\n"
                       f"```{self.prazo.value}```\n\n"
                       "═══════════════════════════════════\n"
                       "**🔥 STATUS:** Aguardando atendimento da equipe\n"
                       "**⚡ PRIORIDADE:** Normal\n"
                       "**💼 CATEGORIA:** Produtos Premium",
            color=0x00FF88
        )
        embed.set_author(name="Sistema de Tickets - Fênix Bots", icon_url="https://i.imgur.com/KeVqZJX.png")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🎯 PRÓXIMOS PASSOS", value="• Nossa equipe analisará seu pedido\n• Enviaremos um orçamento personalizado\n• Início da produção após aprovação", inline=False)
        embed.set_footer(text="Fênix Bots © 2025 • Ticket #" + str(numero), icon_url="https://i.imgur.com/KeVqZJX.png")
        embed.timestamp = discord.utils.utcnow()
        
        welcome_msg = f"🎉 **Bem-vindo ao atendimento Premium!** {interaction.user.mention}\n\n💎 **Obrigado por escolher a Fênix Bots!** Nossa equipe especializada já foi notificada e em breve entrará em contato para dar início ao seu projeto exclusivo!"
        
        await canal.send(welcome_msg, embed=embed)
        await interaction.followup.send(f"✅ Ticket criado: {canal.mention}", ephemeral=True)


class ParceriaModal(Modal, title="🤝 Parceria Oficial"):
    servidor = TextInput(label="Link do Servidor", placeholder="Cole o convite do seu servidor")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            categoria = guild.get_channel(self.bot.config["categoria_parcerias"])
            
            if not categoria:
                return await interaction.followup.send("❌ Categoria não configurada!", ephemeral=True)

            # Cria ticket
            numero = self.bot.config["ticket_counter"]
            self.bot.config["ticket_counter"] += 1
            self.bot.save_config()

            canal = await guild.create_text_channel(
                name=f"parceria-{interaction.user.name}-{numero}",
                category=categoria
            )

            # Permissões
            await canal.set_permissions(interaction.user, read_messages=True, send_messages=True)
            await canal.set_permissions(guild.default_role, read_messages=False)

            # Embed do ticket
            embed = discord.Embed(
                title="🤝 NOVA SOLICITAÇÃO DE PARCERIA VIP",
                description="═══════════════════════════════════\n\n"
                           f"**👤 PARCEIRO POTENCIAL:** {interaction.user.mention}\n"
                           f"**📅 DATA:** {discord.utils.format_dt(discord.utils.utcnow(), 'F')}\n\n"
                           f"**🔗 SERVIDOR PARA ANÁLISE:**\n"
                           f"```{self.servidor.value}```\n\n"
                           "═══════════════════════════════════\n"
                           "**📋 CHECKLIST DE REQUISITOS:**\n"
                           "┣ 📊 **200+ membros ativos**\n"
                           "┣ 🛡️ **Moderação ativa**\n"
                           "┣ 🔒 **Ambiente organizado**\n"
                           "┣ ✅ **Conteúdo apropriado**\n"
                           "┣ 📝 **Regras claras**\n"
                           "┗ 🌟 **Engajamento da comunidade**\n\n"
                           "**🔥 STATUS:** Em análise pela equipe\n"
                           "**⚡ PRAZO:** Resposta em até 48h\n"
                           "**💼 TIPO:** Parceria Estratégica",
                color=0x9932CC
            )
            embed.set_author(name="Departamento de Parcerias - Fênix Bots", icon_url="https://i.imgur.com/KeVqZJX.png")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.add_field(
                name="🚀 BENEFÍCIOS DA PARCERIA", 
                value="• Cross-promotion nos servidores\n• Divulgação mútua de conteúdo\n• Eventos colaborativos\n• Crescimento conjunto da comunidade", 
                inline=False
            )
            embed.set_footer(text="Fênix Bots © 2025 • Parceria #" + str(numero), icon_url="https://i.imgur.com/KeVqZJX.png")
            embed.timestamp = discord.utils.utcnow()
            
            welcome_msg = f"🤝 **Solicitação de Parceria Recebida!** {interaction.user.mention}\n\n🌟 **Agradecemos seu interesse em fazer parceria conosco!** Nossa equipe de parcerias analisará seu servidor e entrará em contato em breve com feedback detalhado."
            
            await canal.send(welcome_msg, embed=embed)
            await interaction.followup.send(f"✅ Ticket criado: {canal.mention}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar ticket de parceria: {e}")
            await interaction.followup.send("❌ Erro ao criar ticket. Tente novamente!", ephemeral=True)