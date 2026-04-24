import threading
from queue import Empty, Queue
import tkinter as tk
from tkinter import messagebox, scrolledtext

from assistente_leilao.automation.action import inserir_valores
from assistente_leilao.automation.browser import Browser
from assistente_leilao.core.monitor import monitorar
from assistente_leilao.core.validator import validar_nome, validar_timeout, validar_url
from assistente_leilao.logs.activity_log import registrar_acao


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistente de Lances")
        self.geometry("600x620")
        self.configure(bg="#f0f0f0")

        self.monitor_browser = None
        self.action_browser = None
        self.monitor_thread = None
        self.action_thread = None
        self.action_queue = None
        self.stop_event = None
        self.nome_usuario = None
        self.monitorando = False
        self.ui_queue = Queue()

        self.after(100, self.processar_fila_ui)
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.tela_login()

    def tela_login(self):
        self.limpar_tela()

        tk.Label(self, text="Assistente de Lances", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=40)
        tk.Label(self, text="Seu nome:", bg="#f0f0f0").pack()

        self.entrada_nome = tk.Entry(self, font=("Arial", 12), width=30)
        self.entrada_nome.pack(pady=8)

        tk.Button(self, text="Entrar", command=self.confirmar_login).pack()

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

        tk.Label(self, text="URL do leilão:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(20, 0))
        self.e_url = tk.Entry(self, width=60)
        self.e_url.pack(padx=30)

        tk.Label(self, text="XPath do preço:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_xpath = tk.Entry(self, width=60)
        self.e_xpath.pack(padx=30)

        tk.Label(self, text="Regex do preço (alternativo):", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_regex = tk.Entry(self, width=60)
        self.e_regex.pack(padx=30)

        tk.Label(self, text="Intervalo de verificação (segundos):", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_timeout = tk.Entry(self, width=10)
        self.e_timeout.insert(0, "10")
        self.e_timeout.pack(anchor="w", padx=30)

        frame_botoes = tk.Frame(self, bg="#f0f0f0")
        frame_botoes.pack(pady=14)

        self.btn_iniciar = tk.Button(frame_botoes, text="Iniciar", bg="green", fg="white", command=self.iniciar)
        self.btn_iniciar.grid(row=0, column=0, padx=6)

        self.btn_parar = tk.Button(frame_botoes, text="Parar", bg="red", fg="white", state="disabled", command=self.parar)
        self.btn_parar.grid(row=0, column=1, padx=6)

        self.log = scrolledtext.ScrolledText(self, height=8, state="disabled", bg="#1e1e1e", fg="white")
        self.log.pack(padx=30, pady=10, fill="x")

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
            messagebox.showerror("Erro", f"Não foi possível iniciar o navegador: {e}")
            return

        registrar_acao(self.nome_usuario, f"monitoramento iniciado em {url}")
        self.adicionar_log("Monitoramento iniciado...")
        self.btn_iniciar.config(state="disabled")
        self.btn_parar.config(state="normal")
        self.monitorando = True
        self.stop_event = threading.Event()
        self.action_queue = Queue()

        def callback(preco_antigo, preco_novo):
            self.enfileirar_ui(self.adicionar_log, f"Preço mudou: R${preco_antigo:.2f} -> R${preco_novo:.2f}")
            registrar_acao(self.nome_usuario, f"preço mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
            self.action_queue.put((preco_antigo, preco_novo))

        def status_callback(mensagem):
            self.enfileirar_ui(self.adicionar_log, mensagem)

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
        self.btn_parar.config(state="disabled")

    def adicionar_log(self, mensagem):
        self.log.config(state="normal")
        self.log.insert("end", mensagem + "\n")
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
        self.btn_iniciar.config(state="normal")
        self.btn_parar.config(state="disabled")

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


def iniciar_gui():
    app = App()
    app.mainloop()
