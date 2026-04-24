import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from core import scraper
from core.monitor import monitorar
from core.validator import validar_url, validar_timeout, validar_nome_usuario
from automation.browser import criar_driver, abrir_pagina, fechar_driver
from automation.action import registrar_em_pagina_alvo
from logs.activity_log import definir_usuario, registrar_acao


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("assistente de lances")
        self.geometry("600x580")
        self.configure(bg="#f0f0f0")

        self.driver = None
        self.monitorando = False

        self.tela_login()

    def tela_login(self):
        self.limpar_tela()

        tk.Label(self, text="assistente de lances", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=40)
        tk.Label(self, text="seu nome:", bg="#f0f0f0").pack()

        self.entrada_nome = tk.Entry(self, font=("Arial", 12), width=30)
        self.entrada_nome.pack(pady=8)

        tk.Button(self, text="entrar", command=self.confirmar_login).pack()

    def confirmar_login(self):
        nome = self.entrada_nome.get().strip()
        ok, msg = validar_nome_usuario(nome)
        if not ok:
            messagebox.showerror("erro", msg)
            return
        definir_usuario(nome)
        self.tela_principal()

    def tela_principal(self):
        self.limpar_tela()

        tk.Label(self, text="url do leilao:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(20, 0))
        self.e_url = tk.Entry(self, width=60)
        self.e_url.pack(padx=30)

        tk.Label(self, text="xpath do preco:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_xpath = tk.Entry(self, width=60)
        self.e_xpath.pack(padx=30)

        tk.Label(self, text="regex do preco (alternativo):", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_regex = tk.Entry(self, width=60)
        self.e_regex.pack(padx=30)

        tk.Label(self, text="url da pagina alvo:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_url_alvo = tk.Entry(self, width=60)
        self.e_url_alvo.pack(padx=30)

        tk.Label(self, text="xpath do campo de texto na pagina alvo:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_campo_alvo = tk.Entry(self, width=60)
        self.e_campo_alvo.pack(padx=30)

        tk.Label(self, text="xpath do botao na pagina alvo:", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_botao_alvo = tk.Entry(self, width=60)
        self.e_botao_alvo.pack(padx=30)

        tk.Label(self, text="intervalo de verificacao (segundos):", bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10, 0))
        self.e_timeout = tk.Entry(self, width=10)
        self.e_timeout.insert(0, "10")
        self.e_timeout.pack(anchor="w", padx=30)

        frame_botoes = tk.Frame(self, bg="#f0f0f0")
        frame_botoes.pack(pady=14)

        self.btn_iniciar = tk.Button(frame_botoes, text="iniciar", bg="green", fg="white", command=self.iniciar)
        self.btn_iniciar.grid(row=0, column=0, padx=6)

        self.btn_parar = tk.Button(frame_botoes, text="parar", bg="red", fg="white", state="disabled", command=self.parar)
        self.btn_parar.grid(row=0, column=1, padx=6)

        self.log = scrolledtext.ScrolledText(self, height=6, state="disabled", bg="#1e1e1e", fg="white")
        self.log.pack(padx=30, pady=10, fill="x")

    def iniciar(self):
        url = self.e_url.get().strip()
        xpath = self.e_xpath.get().strip() or None
        regex = self.e_regex.get().strip() or None
        url_alvo = self.e_url_alvo.get().strip()
        campo_alvo = self.e_campo_alvo.get().strip()
        botao_alvo = self.e_botao_alvo.get().strip()
        timeout = self.e_timeout.get().strip()

        ok, msg = validar_url(url)
        if not ok:
            messagebox.showerror("erro", msg)
            return

        ok, timeout, msg = validar_timeout(timeout)
        if not ok:
            messagebox.showerror("erro", msg)
            return

        self.driver = criar_driver()
        abrir_pagina(self.driver, url)

        registrar_acao("monitoramento iniciado")
        self.adicionar_log("monitoramento iniciado...")
        self.btn_iniciar.config(state="disabled")
        self.btn_parar.config(state="normal")

        def callback(preco_antigo, preco_novo):
            self.adicionar_log(f"preco mudou: R${preco_antigo:.2f} -> R${preco_novo:.2f}")
            registrar_acao(f"preco mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
            registrar_em_pagina_alvo(self.driver, url_alvo, campo_alvo, botao_alvo, preco_antigo, preco_novo)

        t = threading.Thread(
            target=monitorar,
            kwargs=dict(driver=self.driver, xpath=xpath, regex=regex, timeout=timeout, callback=callback),
            daemon=True
        )
        t.start()

    def parar(self):
        if self.driver:
            fechar_driver(self.driver)
            self.driver = None
        registrar_acao("monitoramento encerrado")
        self.adicionar_log("monitoramento encerrado.")
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