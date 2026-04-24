import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from core.monitor import monitorar
from core.validator import validar_url, validar_timeout, validar_nome
from automation.browser import Browser
from automation.action import inserir_valores
from logs.activity_log import registrar_acao


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistente de Lances")
        self.geometry("600x620")
        self.configure(bg="#f0f0f0")

        self.browser = None
        self.nome_usuario = None
        self.monitorando = False

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

        self.browser = Browser()
        self.browser.iniciar()
        self.browser.abrir_url(url)
        driver = self.browser.obter_driver()

        registrar_acao(self.nome_usuario, f"monitoramento iniciado em {url}")
        self.adicionar_log("Monitoramento iniciado...")
        self.btn_iniciar.config(state="disabled")
        self.btn_parar.config(state="normal")
        self.monitorando = True

        def callback(preco_antigo, preco_novo):
            self.adicionar_log(f"Preço mudou: R${preco_antigo:.2f} → R${preco_novo:.2f}")
            registrar_acao(self.nome_usuario, f"preço mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
            inserir_valores(driver, preco_antigo, preco_novo)

        t = threading.Thread(
            target=monitorar,
            kwargs=dict(driver=driver, xpath=xpath, regex=regex, timeout=timeout, callback=callback),
            daemon=True
        )
        t.start()

    def parar(self):
        if self.browser:
            self.browser.fechar()
            self.browser = None
        self.monitorando = False
        registrar_acao(self.nome_usuario, "monitoramento encerrado")
        self.adicionar_log("Monitoramento encerrado.")
        self.btn_iniciar.config(state="normal")
        self.btn_parar.config(state="disabled")

    def adicionar_log(self, mensagem):
        self.log.config(state="normal")
        self.log.insert("end", mensagem + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()


def iniciar_gui():
    app = App()
    app.mainloop()