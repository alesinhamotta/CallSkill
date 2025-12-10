import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import threading

# SUA CHAVE OPENAI
client = OpenAI(api_key="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")

engine = pyttsx3.init()
engine.setProperty('rate', 175)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 mulher, 1 homem

CENARIOS = [
    "chip pré-pago suspenso por falta de recarga",
    "fibra cortada por falta de pagamento",
    "pedir segunda via de fatura",
    "mudar titularidade de linha pós",
    "controle acabou todos os dados",
    "cliente reclamão que odeia tudo",
    "quer fazer portabilidade pra Alive",
    "quer pacote adicional de dados"
]

class CallSkillSimulador:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Call Skill – Treinamento Vivo/Alive")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")
        self.usuario = "Alessandra"
        self.conversa = []
        self.cenario = random.choice(CENARIOS)
        self.janela_chamada()

    def falar(self, texto):
        def run():
            engine.say(texto)
            engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()  # <-- não trava mais

    def janela_chamada(self):
        j = self.root
        j.configure(bg="white")

        tk.Label(j, text="TOQUE! CHAMADA ENTRANDO...", font=("Arial", 20, "bold"), fg="red", bg="white").pack(pady=30)
        tk.Label(j, text=f"Cenário: {self.cenario.upper()}", font=("Arial", 14, "italic"), bg="white").pack(pady=10)

        chat = scrolledtext.ScrolledText(j, height=28, font=("Consolas", 12), bg="#f8f9fa")
        chat.pack(pady=20, padx=20, fill="both", expand=True)
        chat.tag_config("you", foreground="#1a73e8", font=("Consolas", 12, "bold"))
        chat.tag_config("client", foreground="#d93025")
        chat.tag_config("upsell", foreground="#0f9d58", font=("Consolas", 12, "bold"))

        # primeira fala do cliente
        prompt = f"Você é cliente da Alive. Problema: {self.cenario}. Nunca dê a solução sozinho, só reclame ou peça ajuda. Fale em português brasileiro natural."
        resposta = self.chamar_ia(prompt)
        self.falar(resposta)
        chat.insert("end", f"Cliente: {resposta}\n\n", "client")
        self.conversa.append({"role": "user", "content": resposta})

        def responder_com_voz():
            r = sr.Recognizer()
            r.energy_threshold = 100
            r.dynamic_energy_threshold = False

            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                chat.insert("end", "🎤 FALE AGORA!\n", "you")
                chat.see("end")
                j.update()
                try:
                    audio = r.listen(source, timeout=30, phrase_time_limit=25)
                except:
                    chat.insert("end", "Não ouvi nada...\n\n")
                    return

            try:
                texto = r.recognize_google(audio, language="pt-BR")
                chat.insert("end", f"Você ({self.usuario}): {texto}\n\n", "you")
                self.conversa.append({"role": "assistant", "content": texto})

                resposta = self.chamar_ia("Continue como cliente. Nunca resolva o problema sozinho. Só reclame ou peça ajuda. Português brasileiro.")
                self.falar(resposta)
                chat.insert("end", f"Cliente: {resposta}\n\n", "client")
                self.conversa.append({"role": "user", "content": resposta})

                if any(p in texto.lower() for p in ["plano","fibra","chip","migração","controle","pós"]):
                    chat.insert("end", "UPSELL → Migração para Controle Médio +10GB R$30/mês!\n\n", "upsell")

            except:
                chat.insert("end", "Não entendi... repete?\n\n")

        tk.Button(j, text="RESPONDER COM VOZ", command=responder_com_voz,
                  bg="#1a73e8", fg="white", font=("Arial", 16, "bold"), height=2, width=30).pack(pady=30)

        def finalizar():
            feedback = self.chamar_ia("Você é supervisor da Alive. Analise o atendimento. Pontos positivos, negativos e dicas em português.")
            messagebox.showinfo("FEEDBACK", feedback)
            self.root.destroy()

        tk.Button(j, text="FINALIZAR CHAMADA", command=finalizar,
                  bg="#db4437", fg="white", font=("Arial", 16, "bold")).pack(pady=20)

    def chamar_ia(self, prompt):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}] + self.conversa,
                temperature=0.8,
                max_tokens=400
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Erro: {e}"

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CallSkillSimulador()
    app.run()