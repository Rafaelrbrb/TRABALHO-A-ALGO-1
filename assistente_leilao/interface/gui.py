import threading
from datetime import datetime
from queue import Empty, Queue
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, scrolledtext

from assistente_leilao.automation.action import inserir_valores
from assistente_leilao.automation.browser import Browser
from assistente_leilao.core.monitor import monitorar
from assistente_leilao.core.validator import validar_nome, validar_timeout, validar_url
from assistente_leilao.logs.activity_log import registrar_acao


class App(tk.Tk):
    BG = "#f3ede4"
    SURFACE = "#fbf8f2"
    SURFACE_ALT = "#ece1d2"
    BORDER = "#d8c8b7"
    TEXT = "#251d17"
    MUTED = "#6f6255"
    ACCENT = "#295f5a"
    ACCENT_HOVER = "#214e4a"
    ACCENT_SOFT = "#d8e9e6"
    DANGER = "#9b4b38"
    DANGER_HOVER = "#823d2d"
    DANGER_SOFT = "#f1ddd5"
    WARNING = "#9c6a27"
    WARNING_SOFT = "#efe2c7"
    LOG_BG = "#1f1a17"
    LOG_FG = "#f5ecdf"

    def __init__(self):
        super().__init__()
        self._configurar_fontes()
        self.title("Assistente de Lances")
        self.geometry("980x690")
        self.minsize(760, 540)
        self.configure(bg=self.BG)

        self.monitor_browser = None
        self.action_browser = None
        self.monitor_thread = None
        self.action_thread = None
        self.action_queue = None
        self.stop_event = None
        self.nome_usuario = None
        self.monitorando = False
        self.ui_queue = Queue()
        self.log = None
        self.status_badge = None
        self.status_title = None
        self.status_detail = None
        self.user_badge = None
        self.header_frame = None
        self.header_badges = None
        self.header_description = None
        self.main_scroll_canvas = None
        self.main_scroll_body = None
        self.main_scroll_window = None
        self.main_content = None
        self.form_card = None
        self.activity_card = None
        self.form_description = None
        self.url_description = None
        self.regex_description = None
        self.hint_label = None
        self.xpath_description = None
        self.timeout_description = None

        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.bind_all("<Button-5>", self._on_mousewheel_linux)
        self.after(100, self.processar_fila_ui)
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.tela_login()

    def _configurar_fontes(self):
        heading_family = self._escolher_fonte(
            "Helvetica",
            "Arial",
            "Segoe UI",
        )
        body_family = self._escolher_fonte(
            "Helvetica",
            "Arial",
            "Segoe UI",
        )
        mono_family = self._escolher_fonte(
            "Menlo",
            "SF Mono",
            "Courier New",
            "Courier",
        )

        self.font_eyebrow = (body_family, 10, "bold")
        self.font_title = (heading_family, 24, "bold")
        self.font_heading = (heading_family, 16, "bold")
        self.font_subheading = (heading_family, 12, "bold")
        self.font_body = (body_family, 11)
        self.font_body_bold = (body_family, 11, "bold")
        self.font_small = (body_family, 10)
        self.font_button = (body_family, 11, "bold")
        self.font_log = (mono_family, 11)

    def _escolher_fonte(self, *candidatas):
        disponiveis = set(tkfont.families())
        for fonte in candidatas:
            if fonte in disponiveis:
                return fonte
        return "TkDefaultFont"

    def _resetar_grid_raiz(self):
        for coluna in range(3):
            self.grid_columnconfigure(coluna, weight=0)
        for linha in range(4):
            self.grid_rowconfigure(linha, weight=0)

    def _criar_card(self, parent):
        return tk.Frame(
            parent,
            bg=self.SURFACE,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            bd=0,
        )

    def _criar_entry(self, parent, width=40):
        return tk.Entry(
            parent,
            width=width,
            font=self.font_body,
            bg="#ffffff",
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
        )

    def _criar_botao(self, parent, texto, command, bg, hover):
        botao = tk.Button(
            parent,
            text=texto,
            command=command,
            font=self.font_button,
            bg=bg,
            fg="#ffffff",
            activebackground=hover,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=18,
            pady=12,
            highlightthickness=0,
        )

        botao.base_bg = bg
        botao.hover_bg = hover
        botao.base_fg = "#ffffff"

        def ao_entrar(_event):
            if str(botao["state"]) != "disabled":
                botao.configure(bg=botao.hover_bg)

        def ao_sair(_event):
            if str(botao["state"]) != "disabled":
                botao.configure(bg=botao.base_bg)

        botao.bind("<Enter>", ao_entrar)
        botao.bind("<Leave>", ao_sair)
        return botao

    def _definir_estado_botao(self, botao, habilitado: bool):
        if botao is None:
            return

        if habilitado:
            botao.configure(
                state="normal",
                bg=botao.base_bg,
                fg=botao.base_fg,
                activebackground=botao.hover_bg,
                cursor="hand2",
            )
            return

        botao.configure(
            state="disabled",
            bg=self.SURFACE_ALT,
            fg=self.MUTED,
            activebackground=self.SURFACE_ALT,
            cursor="arrow",
        )

    def definir_status(self, titulo: str, descricao: str, tone: str = "idle"):
        estilos = {
            "idle": {"bg": self.SURFACE_ALT, "fg": self.MUTED},
            "active": {"bg": self.ACCENT_SOFT, "fg": self.ACCENT},
            "warning": {"bg": self.WARNING_SOFT, "fg": self.WARNING},
            "error": {"bg": self.DANGER_SOFT, "fg": self.DANGER},
        }
        estilo = estilos.get(tone, estilos["idle"])

        if self.status_badge is not None:
            self.status_badge.configure(
                text=titulo.upper(),
                bg=estilo["bg"],
                fg=estilo["fg"],
            )

        if self.status_title is not None:
            self.status_title.configure(text=titulo, fg=self.TEXT)

        if self.status_detail is not None:
            self.status_detail.configure(text=descricao, fg=self.MUTED)

    def _criar_area_rolavel(self):
        container = tk.Frame(self, bg=self.BG)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.main_scroll_canvas = tk.Canvas(
            container,
            bg=self.BG,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.main_scroll_canvas.yview,
        )
        self.main_scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_scroll_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns", pady=18, padx=(0, 10))

        self.main_scroll_body = tk.Frame(self.main_scroll_canvas, bg=self.BG)
        self.main_scroll_window = self.main_scroll_canvas.create_window(
            (0, 0),
            window=self.main_scroll_body,
            anchor="nw",
        )

        self.main_scroll_body.bind("<Configure>", self._ao_configurar_scroll_body)
        self.main_scroll_canvas.bind("<Configure>", self._ao_configurar_scroll_canvas)

        return self.main_scroll_body

    def _ao_configurar_scroll_body(self, _event):
        if self.main_scroll_canvas is not None:
            self.main_scroll_canvas.configure(
                scrollregion=self.main_scroll_canvas.bbox("all")
            )

    def _ao_configurar_scroll_canvas(self, event):
        if self.main_scroll_canvas is None or self.main_scroll_window is None:
            return

        largura = max(event.width, 1)
        self.main_scroll_canvas.itemconfigure(self.main_scroll_window, width=largura)
        self._atualizar_layout_principal(largura)

    def _on_mousewheel(self, event):
        if self.main_scroll_canvas is None:
            return

        if self.log is not None and str(event.widget).startswith(str(self.log)):
            return

        delta = 0
        if event.delta > 0:
            delta = -1
        elif event.delta < 0:
            delta = 1

        if delta != 0:
            self.main_scroll_canvas.yview_scroll(delta, "units")

    def _on_mousewheel_linux(self, event):
        if self.main_scroll_canvas is None:
            return

        if self.log is not None and str(event.widget).startswith(str(self.log)):
            return

        if event.num == 4:
            self.main_scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.main_scroll_canvas.yview_scroll(1, "units")

    def _atualizar_layout_principal(self, largura=None):
        if self.main_content is None or self.header_frame is None:
            return

        if largura is None:
            if self.main_scroll_canvas is not None:
                largura = self.main_scroll_canvas.winfo_width()
            else:
                largura = self.winfo_width()

        largura = max(int(largura), 1)
        compacto = largura < 1120

        if compacto:
            self.header_badges.grid_configure(
                row=3,
                column=0,
                rowspan=1,
                sticky="w",
                padx=0,
                pady=(16, 0),
            )
            self.user_badge.grid_configure(row=0, column=0, sticky="w", pady=0, padx=0)
            self.status_badge.grid_configure(row=0, column=1, sticky="w", pady=0, padx=(10, 0))

            self.main_content.grid_columnconfigure(0, weight=1)
            self.main_content.grid_columnconfigure(1, weight=0)
            self.form_card.grid_configure(row=0, column=0, padx=0, pady=(0, 18), sticky="ew")
            self.activity_card.grid_configure(row=1, column=0, padx=0, pady=(0, 0), sticky="nsew")
        else:
            self.header_badges.grid_configure(
                row=0,
                column=1,
                rowspan=3,
                sticky="ne",
                padx=(24, 0),
                pady=0,
            )
            self.user_badge.grid_configure(row=0, column=0, sticky="e", padx=0, pady=0)
            self.status_badge.grid_configure(row=1, column=0, sticky="e", padx=0, pady=(10, 0))

            self.main_content.grid_columnconfigure(0, weight=5)
            self.main_content.grid_columnconfigure(1, weight=4)
            self.form_card.grid_configure(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
            self.activity_card.grid_configure(row=0, column=1, padx=(12, 0), pady=0, sticky="nsew")

        largura_texto = max(320, largura - 130)
        largura_form = max(320, min(540, largura_texto - 60 if compacto else 520))
        largura_status = max(300, min(380, largura_texto - 80))

        if self.header_description is not None:
            self.header_description.configure(wraplength=min(640, largura_texto))
        if self.form_description is not None:
            self.form_description.configure(wraplength=largura_form)
        if self.url_description is not None:
            self.url_description.configure(wraplength=largura_form)
        if self.regex_description is not None:
            self.regex_description.configure(wraplength=largura_form)
        if self.hint_label is not None:
            self.hint_label.configure(wraplength=largura_form)
        if self.xpath_description is not None:
            self.xpath_description.configure(wraplength=largura_form)
        if self.timeout_description is not None:
            self.timeout_description.configure(wraplength=largura_form)
        if self.status_detail is not None:
            self.status_detail.configure(wraplength=largura_status)

    def tela_login(self):
        self.limpar_tela()
        self._resetar_grid_raiz()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        wrapper = tk.Frame(self, bg=self.BG)
        wrapper.grid(row=0, column=0, sticky="nsew", padx=32, pady=32)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        card = self._criar_card(wrapper)
        card.grid(row=0, column=0, sticky="", padx=40, pady=20)
        card.grid_columnconfigure(0, weight=1)

        conteudo = tk.Frame(card, bg=self.SURFACE)
        conteudo.grid(row=0, column=0, padx=38, pady=36, sticky="nsew")
        conteudo.grid_columnconfigure(0, weight=1)

        tk.Label(
            conteudo,
            text="PAINEL LOCAL",
            bg=self.SURFACE,
            fg=self.ACCENT,
            font=self.font_eyebrow,
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            conteudo,
            text="Assistente de Lances",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_title,
        ).grid(row=1, column=0, sticky="w", pady=(8, 10))

        tk.Label(
            conteudo,
            text="Monitoramento simples, com leitura contínua de preço e ação automática quando houver alteração.",
            bg=self.SURFACE,
            fg=self.MUTED,
            justify="left",
            wraplength=460,
            font=self.font_body,
        ).grid(row=2, column=0, sticky="w", pady=(0, 26))

        tk.Label(
            conteudo,
            text="Nome do operador",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        ).grid(row=3, column=0, sticky="w")

        self.entrada_nome = self._criar_entry(conteudo, width=30)
        self.entrada_nome.grid(row=4, column=0, sticky="ew", pady=(8, 8), ipady=10)
        self.entrada_nome.focus_set()

        tk.Label(
            conteudo,
            text="Esse nome aparece apenas nos registros locais de atividade.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_small,
        ).grid(row=5, column=0, sticky="w", pady=(0, 24))

        btn_entrar = self._criar_botao(
            conteudo,
            "Entrar no Painel",
            self.confirmar_login,
            self.ACCENT,
            self.ACCENT_HOVER,
        )
        btn_entrar.grid(row=6, column=0, sticky="ew")

    def confirmar_login(self):
        nome = self.entrada_nome.get().strip()
        erro = validar_nome(nome)
        if erro:
            messagebox.showerror("Erro", erro)
            return
        self.nome_usuario = nome
        registrar_acao(self.nome_usuario, "sessão iniciada via GUI")
        self.tela_principal()

    def tela_principal(self):
        self.limpar_tela()
        self._resetar_grid_raiz()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        principal = self._criar_area_rolavel()
        principal.grid_columnconfigure(0, weight=1)

        header = tk.Frame(principal, bg=self.BG)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(26, 10))
        header.grid_columnconfigure(0, weight=1)
        self.header_frame = header

        tk.Label(
            header,
            text="MONITORAMENTO",
            bg=self.BG,
            fg=self.ACCENT,
            font=self.font_eyebrow,
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header,
            text="Painel do leilão",
            bg=self.BG,
            fg=self.TEXT,
            font=self.font_title,
        ).grid(row=1, column=0, sticky="w", pady=(6, 8))

        self.header_description = tk.Label(
            header,
            text="Configure a origem do preço, acompanhe o histórico e interrompa o processo com segurança quando precisar.",
            bg=self.BG,
            fg=self.MUTED,
            font=self.font_body,
            justify="left",
            wraplength=640,
        )
        self.header_description.grid(row=2, column=0, sticky="w")

        badges = tk.Frame(header, bg=self.BG)
        badges.grid(row=0, column=1, rowspan=3, sticky="ne", padx=(24, 0))
        self.header_badges = badges

        self.user_badge = tk.Label(
            badges,
            text=f"Operador: {self.nome_usuario}",
            bg=self.SURFACE_ALT,
            fg=self.TEXT,
            font=self.font_small,
            padx=14,
            pady=8,
        )
        self.user_badge.grid(row=0, column=0, sticky="e")

        self.status_badge = tk.Label(
            badges,
            text="PRONTO",
            bg=self.SURFACE_ALT,
            fg=self.MUTED,
            font=self.font_small,
            padx=14,
            pady=8,
        )
        self.status_badge.grid(row=1, column=0, sticky="e", pady=(10, 0))

        content = tk.Frame(principal, bg=self.BG)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(10, 28))
        content.grid_columnconfigure(0, weight=5)
        content.grid_columnconfigure(1, weight=4)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        self.main_content = content

        form_card = self._criar_card(content)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form_card.grid_columnconfigure(0, weight=1)
        self.form_card = form_card

        tk.Label(
            form_card,
            text="CONFIGURAÇÃO",
            bg=self.SURFACE,
            fg=self.ACCENT,
            font=self.font_eyebrow,
        ).grid(row=0, column=0, sticky="w", padx=26, pady=(26, 0))

        tk.Label(
            form_card,
            text="Parâmetros do monitor",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_heading,
        ).grid(row=1, column=0, sticky="w", padx=26, pady=(8, 6))

        self.form_description = tk.Label(
            form_card,
            text="Use XPath como caminho principal e deixe a regex como alternativa quando o HTML for mais instável.",
            bg=self.SURFACE,
            fg=self.MUTED,
            wraplength=480,
            justify="left",
            font=self.font_body,
        )
        self.form_description.grid(row=2, column=0, sticky="w", padx=26, pady=(0, 22))

        tk.Label(
            form_card,
            text="URL do leilão",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        ).grid(row=3, column=0, sticky="w", padx=26)

        self.e_url = self._criar_entry(form_card)
        self.e_url.grid(row=4, column=0, sticky="ew", padx=26, pady=(8, 6), ipady=10)
        self.e_url.focus_set()

        self.url_description = tk.Label(
            form_card,
            text="Cole a página que contém o valor a ser observado.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_small,
            justify="left",
            wraplength=500,
        )
        self.url_description.grid(row=5, column=0, sticky="w", padx=26, pady=(0, 18))

        selectors = tk.Frame(form_card, bg=self.SURFACE)
        selectors.grid(row=6, column=0, sticky="ew", padx=26)
        selectors.grid_columnconfigure(0, weight=1)

        tk.Label(
            selectors,
            text="XPath do preço",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        ).grid(row=0, column=0, sticky="w")

        self.e_xpath = self._criar_entry(selectors)
        self.e_xpath.grid(row=1, column=0, sticky="ew", pady=(8, 6), ipady=10)

        self.xpath_description = tk.Label(
            selectors,
            text="Preferência principal para leitura do valor na página.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_small,
            justify="left",
            wraplength=500,
        )
        self.xpath_description.grid(row=2, column=0, sticky="w", pady=(0, 18))

        tk.Label(
            selectors,
            text="Intervalo (s)",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        ).grid(row=3, column=0, sticky="w")

        self.e_timeout = self._criar_entry(selectors, width=10)
        self.e_timeout.insert(0, "10")
        self.e_timeout.grid(row=4, column=0, sticky="ew", pady=(8, 6), ipady=10)

        self.timeout_description = tk.Label(
            selectors,
            text="Tempo entre verificações do monitor.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_small,
            justify="left",
            wraplength=500,
        )
        self.timeout_description.grid(row=5, column=0, sticky="w", pady=(0, 18))

        tk.Label(
            form_card,
            text="Regex alternativa",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        ).grid(row=7, column=0, sticky="w", padx=26, pady=(4, 0))

        self.e_regex = self._criar_entry(form_card)
        self.e_regex.grid(row=8, column=0, sticky="ew", padx=26, pady=(8, 6), ipady=10)

        self.regex_description = tk.Label(
            form_card,
            text="Útil quando o preço não está em um elemento estável ou precisa ser capturado direto do HTML.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_small,
            wraplength=500,
            justify="left",
        )
        self.regex_description.grid(row=9, column=0, sticky="w", padx=26, pady=(0, 20))

        hint = tk.Label(
            form_card,
            text="Dica: se você tiver um XPath confiável, deixe a regex vazia. Se a página mudar com frequência, use a regex como plano B.",
            bg=self.SURFACE_ALT,
            fg=self.TEXT,
            font=self.font_small,
            justify="left",
            wraplength=500,
            padx=14,
            pady=12,
        )
        hint.grid(row=10, column=0, sticky="ew", padx=26)
        self.hint_label = hint

        frame_botoes = tk.Frame(form_card, bg=self.SURFACE)
        frame_botoes.grid(row=11, column=0, sticky="ew", padx=26, pady=(22, 26))
        frame_botoes.grid_columnconfigure(0, weight=1)
        frame_botoes.grid_columnconfigure(1, weight=1)

        self.btn_iniciar = self._criar_botao(
            frame_botoes,
            "Iniciar Monitoramento",
            self.iniciar,
            self.ACCENT,
            self.ACCENT_HOVER,
        )
        self.btn_iniciar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_parar = self._criar_botao(
            frame_botoes,
            "Parar",
            self.parar,
            self.DANGER,
            self.DANGER_HOVER,
        )
        self.btn_parar.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._definir_estado_botao(self.btn_parar, False)

        activity_card = self._criar_card(content)
        activity_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        activity_card.grid_columnconfigure(0, weight=1)
        activity_card.grid_rowconfigure(4, weight=1)
        self.activity_card = activity_card

        tk.Label(
            activity_card,
            text="ATIVIDADE",
            bg=self.SURFACE,
            fg=self.ACCENT,
            font=self.font_eyebrow,
        ).grid(row=0, column=0, sticky="w", padx=26, pady=(26, 0))

        tk.Label(
            activity_card,
            text="Linha do tempo",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_heading,
        ).grid(row=1, column=0, sticky="w", padx=26, pady=(8, 6))

        self.status_title = tk.Label(
            activity_card,
            text="Pronto",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=self.font_subheading,
        )
        self.status_title.grid(row=2, column=0, sticky="w", padx=26, pady=(6, 4))

        self.status_detail = tk.Label(
            activity_card,
            text="Preencha os campos ao lado e inicie o monitoramento quando estiver tudo certo.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=self.font_body,
            justify="left",
            wraplength=360,
        )
        self.status_detail.grid(row=3, column=0, sticky="w", padx=26, pady=(0, 18))

        self.log = scrolledtext.ScrolledText(
            activity_card,
            height=16,
            state="disabled",
            bg=self.LOG_BG,
            fg=self.LOG_FG,
            insertbackground=self.LOG_FG,
            relief="flat",
            bd=0,
            wrap="word",
            font=self.font_log,
            padx=14,
            pady=14,
        )
        self.log.grid(row=4, column=0, sticky="nsew", padx=26, pady=(0, 26))

        self.definir_status(
            "Pronto",
            "Preencha os campos ao lado e inicie o monitoramento quando estiver tudo certo.",
            "idle",
        )
        self.after_idle(self._atualizar_layout_principal)

    def iniciar(self):
        if self.monitorando:
            return

        url = self.e_url.get().strip()
        xpath = self.e_xpath.get().strip()
        regex = self.e_regex.get().strip()
        timeout_str = self.e_timeout.get().strip()

        erro_url = validar_url(url)
        if erro_url:
            messagebox.showerror("Erro", erro_url)
            return

        erro_timeout = validar_timeout(timeout_str)
        if erro_timeout:
            messagebox.showerror("Erro", erro_timeout)
            return

        if not xpath and not regex:
            messagebox.showerror("Erro", "Informe pelo menos XPath ou Regex.")
            return

        timeout = int(timeout_str)

        self.monitor_browser = Browser()

        try:
            self.monitor_browser.iniciar()
            self.monitor_browser.abrir_url(url)
            driver = self.monitor_browser.obter_driver()
        except Exception as e:
            self.monitor_browser.fechar()
            self.monitor_browser = None
            self.definir_status(
                "Erro ao iniciar",
                "Não foi possível abrir o navegador com a configuração atual.",
                "error",
            )
            messagebox.showerror("Erro", f"Não foi possível iniciar o navegador: {e}")
            return

        registrar_acao(self.nome_usuario, f"monitoramento iniciado em {url}")
        self.adicionar_log("Monitoramento iniciado...")
        self.definir_status(
            "Monitorando",
            "Acompanhando alterações de preço e registrando qualquer mudança detectada.",
            "active",
        )
        self._definir_estado_botao(self.btn_iniciar, False)
        self._definir_estado_botao(self.btn_parar, True)
        self.monitorando = True
        self.stop_event = threading.Event()
        self.action_queue = Queue()

        def callback(preco_antigo, preco_novo):
            self.enfileirar_ui(self.adicionar_log, f"Preço mudou: R${preco_antigo:.2f} -> R${preco_novo:.2f}")
            registrar_acao(self.nome_usuario, f"preço mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
            self.action_queue.put((preco_antigo, preco_novo))

        def status_callback(mensagem):
            self.enfileirar_ui(self.adicionar_log, mensagem)
            if mensagem.startswith("Erro durante"):
                self.enfileirar_ui(
                    self.definir_status,
                    "Erro no monitoramento",
                    "O processo foi interrompido por uma falha inesperada. Revise os campos e tente novamente.",
                    "error",
                )
            elif "preço inicial" in mensagem:
                self.enfileirar_ui(
                    self.definir_status,
                    "Leitura não encontrada",
                    "O valor inicial não foi localizado. Ajuste XPath ou regex antes de tentar de novo.",
                    "warning",
                )

        self.action_thread = threading.Thread(target=self.processar_acoes, daemon=True)
        self.action_thread.start()

        self.monitor_thread = threading.Thread(
            target=monitorar,
            kwargs=dict(
                driver=driver,
                xpath=xpath,
                regex=regex,
                timeout=timeout,
                callback=callback,
                stop_event=self.stop_event,
                status_callback=status_callback,
            ),
            daemon=True,
        )
        self.monitor_thread.start()
        self.acompanhar_monitoramento()

    def parar(self):
        if not self.monitorando:
            return

        if self.stop_event is not None:
            self.stop_event.set()

        self.adicionar_log("Encerrando monitoramento...")
        self.definir_status(
            "Encerrando",
            "Aguardando o fechamento seguro do monitoramento e das ações pendentes.",
            "warning",
        )
        self._definir_estado_botao(self.btn_parar, False)

    def adicionar_log(self, mensagem):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.config(state="normal")
        self.log.insert("end", f"[{timestamp}] {mensagem}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def enfileirar_ui(self, funcao, *args, **kwargs):
        self.ui_queue.put((funcao, args, kwargs))

    def processar_fila_ui(self):
        try:
            while True:
                funcao, args, kwargs = self.ui_queue.get_nowait()
                funcao(*args, **kwargs)
        except Empty:
            pass

        try:
            self.after(100, self.processar_fila_ui)
        except tk.TclError:
            return

    def obter_action_browser(self) -> Browser:
        if self.action_browser is None:
            self.action_browser = Browser()
            self.action_browser.iniciar()
        return self.action_browser

    def executar_acao(self, preco_antigo, preco_novo):
        try:
            action_browser = self.obter_action_browser()
            inserir_valores(action_browser.obter_driver(), preco_antigo, preco_novo)
        except Exception as e:
            registrar_acao(self.nome_usuario, f"falha na ação automática: {e}")
            self.enfileirar_ui(self.adicionar_log, f"Falha ao executar ação automática: {e}")

    def processar_acoes(self):
        while True:
            if self.stop_event is not None and self.stop_event.is_set():
                if self.action_queue is None or self.action_queue.empty():
                    break

            try:
                item = self.action_queue.get(timeout=0.2)
            except Empty:
                continue

            try:
                preco_antigo, preco_novo = item
                self.executar_acao(preco_antigo, preco_novo)
            finally:
                self.action_queue.task_done()

    def acompanhar_monitoramento(self):
        if self.monitor_thread is None and self.action_thread is None:
            return

        monitor_ativo = self.monitor_thread is not None and self.monitor_thread.is_alive()
        acao_ativa = self.action_thread is not None and self.action_thread.is_alive()

        if monitor_ativo or acao_ativa:
            self.after(200, self.acompanhar_monitoramento)
            return

        self.finalizar_monitoramento()

    def finalizar_monitoramento(self):
        if not self.monitorando:
            return

        if self.monitor_browser:
            self.monitor_browser.fechar()
            self.monitor_browser = None

        if self.action_browser:
            self.action_browser.fechar()
            self.action_browser = None

        self.monitor_thread = None
        self.action_thread = None
        self.action_queue = None
        self.stop_event = None
        self.monitorando = False

        registrar_acao(self.nome_usuario, "monitoramento encerrado")
        self.definir_status(
            "Pronto",
            "Monitoramento encerrado. Ajuste os campos se quiser iniciar uma nova rodada.",
            "idle",
        )
        self._definir_estado_botao(self.btn_iniciar, True)
        self._definir_estado_botao(self.btn_parar, False)

    def ao_fechar(self):
        if self.monitorando:
            if self.stop_event is not None:
                self.stop_event.set()
            self.after(200, self.tentar_fechar_janela)
            return

        if self.monitor_browser:
            self.monitor_browser.fechar()
            self.monitor_browser = None

        if self.action_browser:
            self.action_browser.fechar()
            self.action_browser = None

        self.destroy()

    def tentar_fechar_janela(self):
        monitor_ativo = self.monitor_thread is not None and self.monitor_thread.is_alive()
        acao_ativa = self.action_thread is not None and self.action_thread.is_alive()

        if monitor_ativo or acao_ativa:
            self.after(200, self.tentar_fechar_janela)
            return

        self.finalizar_monitoramento()
        self.destroy()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.status_badge = None
        self.status_title = None
        self.status_detail = None
        self.user_badge = None
        self.log = None
        self.header_frame = None
        self.header_badges = None
        self.header_description = None
        self.main_scroll_canvas = None
        self.main_scroll_body = None
        self.main_scroll_window = None
        self.main_content = None
        self.form_card = None
        self.activity_card = None
        self.form_description = None
        self.url_description = None
        self.regex_description = None
        self.hint_label = None
        self.xpath_description = None
        self.timeout_description = None


def iniciar_gui():
    app = App()
    app.mainloop()
