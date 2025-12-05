import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import pyttsx3
import speech_recognition as sr

# Voz do cliente - agora funciona 100%
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

BOOK_PLANOS = {
    "Pré-Pago Básico": {"sugestao": "Migração para Controle Médio: +10GB por R$30/mês com desconto!"},
    "Fibra 500Mbps": {"sugestao": "Combo Fibra 500MB + Chip 50GB: R$149/mês. Ativação e-SIM grátis!"},
    "e-SIM Pré": {"sugestao": "Ativação e-SIM R$5 + migração para Pós com +20GB!"},
}

CLIENTES_TIPOS = {
    "Ignorante": {"frase": "Ei, resolve logo isso! Internet cortada, paguei ontem e nada!", "personalidade": "Impaciente"},
    "Legal": {"frase": "Oi, tudo bem? Minha internet foi cortada, mas já paguei. Pode ajudar?", "personalidade": "Cooperativo"},
    "Idoso": {"frase": "Alô? Minha internet parou, filha. Eu paguei, mas não entendo esses computadores...", "personalidade": "Lento"},
    "Jovem": {"frase": "Galera, net caiu de novo. Paguei via app, mas tá sem sinal. Fixa aí!", "personalidade": "Tech"},
}

class CallSkillSimulador:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Call Skill - Treinamento Alive")
        self.root.geometry("700x650")
        self.root.configure(bg="#f0f0f0")
        self.usuario = None
        self.login_tela()

    def login_tela(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text="CALL SKILL", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#1a73e8").pack(pady=50)
        tk.Label(self.root, text="Treinamento Realista para Atendentes Alive", font=("Arial", 14), bg="#f0f0f0").pack(pady=20)
        nome = simpledialog.askstring("Login", "Digite seu nome:")
        if nome:
            self.usuario = nome.strip().title()
            messagebox.showinfo("Sucesso!", f"Olá, {self.usuario}! Vamos treinar?")
            self.dashboard()

    def dashboard(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text=f"Atendente: {self.usuario}", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=40)
        tk.Button(self.root, text="ATENDER NOVA CHAMADA", command=self.simular_chamada,
                  bg="#0f9d58", fg="white", font=("Arial", 16, "bold"), height=3, width=30).pack(pady=40)

    def simular_chamada(self):
        tipo = random.choice(list(CLIENTES_TIPOS.keys()))
        cliente = CLIENTES_TIPOS[tipo]
        plano = random.choice(list(BOOK_PLANOS.keys()))

        j = tk.Toplevel(self.root)
        j.title(f"Chamada - {tipo}")
        j.geometry("900x750")
        j.configure(bg="white")

        tk.Label(j, text="TOQUE! CHAMADA ENTRANDO...", font=("Arial", 18, "bold"), fg="red", bg="white").pack(pady=20)

        chat = tk.Text(j, height=22, width=105, font=("Consolas", 11), bg="#f8f9fa")
        chat.pack(pady=10, padx=20)
        chat.tag_config("upsell", foreground="#0f9d58", font=("Consolas", 11, "bold"))
        chat.tag_config("you", foreground="#1a73e8", font=("Consolas", 11, "bold"))
        chat.insert("end", f"Tipo: {cliente['personalidade']} | Plano: {plano}\n\n")

        engine.say(cliente['frase'])
        engine.runAndWait()
        chat.insert("end", f"Cliente: {cliente['frase']}\n\n")

        def falar():
            try:
                with sr.Microphone(device_index=12) as source:
                    r = sr.Recognizer()
                    r.energy_threshold = 100
                    r.dynamic_energy_threshold = False
                    r.adjust_for_ambient_noise(source, duration=0.3)
                    chat.insert("end", "🎤 FALE AGORA!\n")
                    chat.see("end")
                    j.update()
                    audio = r.listen(source, timeout=15, phrase_time_limit=12)

                texto = r.recognize_google(audio, language="pt-BR")
                chat.insert("end", f"Você ({self.usuario}): {texto}\n\n", "you")

                resp = random.choice(["Tá bom, pode consultar.", "Um minutinho.", "Vou verificar agora."])
                engine.say(resp)
                engine.runAndWait()
                chat.insert("end", f"Cliente: {resp}\n\n")

                if any(p in texto.lower() for p in ["cpf", "olhar", "ver", "consultar"]):
                    chat.insert("end", f"UPSELL → {BOOK_PLANOS[plano]['sugestao']}\n\n", "upsell")

            except Exception as e: 
                chat.insert("end", f"Erro: {e}\n\n")

        tk.Button(j, text="RESPONDER COM VOZ", command=falar, bg="#1a73e8", fg="white", font=("Arial", 14, "bold")).pack(pady=20)

        tk.Button(j, text="FINALIZAR CHAMADA", command=j.destroy, bg="#db4437", fg="white", font=("Arial", 14, "bold")).pack(pady=20)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CallSkillSimulador()
    app.run()