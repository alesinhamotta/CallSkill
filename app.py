import streamlit as st
import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import random

# SUA CHAVE OPENAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
engine = pyttsx3.init()
engine.setProperty('rate', 175)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 = mulher, 1 = homem

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

# Login simples
if 'logged_in' not in st.session_state:
    st.title("Call Skill - Login")
    nome = st.text_input("Digite seu nome")
    if st.button("Entrar", key="login"):
        if nome.strip():
            st.session_state.logged_in = True
            st.session_state.usuario = nome.strip().title()
            st.rerun()
else:
    st.title(f"Call Skill – {st.session_state.usuario}")

    # Botão nova chamada
    if st.button("ATENDER NOVA CHAMADA", key="nova_chamada"):
        st.session_state.conversa = []
        st.session_state.cenario = random.choice(CENARIOS)

        prompt = f"Você é cliente da Alive. Problema: {st.session_state.cenario}. Nunca dê a solução, só reclame ou peça ajuda. Fale em português brasileiro natural."
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        ).choices[0].message.content.strip()

        engine.say(resposta)
        engine.runAndWait()

        st.session_state.conversa.append({"role": "user", "content": resposta})
        st.rerun()

    # Mostra a conversa
    if 'conversa' in st.session_state:
        st.write(f"**Cenário:** {st.session_state.cenario.upper()}")
        for msg in st.session_state.conversa:
            if msg["role"] == "user":
                st.write(f"**Cliente:** {msg['content']}")
            else:
                st.write(f"**Você:** {msg['content']}")

        # BOTÃO RESPONDER COM VOZ
        if st.button("RESPONDER COM VOZ", key="responder_voz"):
            with st.spinner("OUVINDO... fale agora!"):
                r = sr.Recognizer()
                r.energy_threshold = 100
                r.dynamic_energy_threshold = False

                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    try:
                        audio = r.listen(source, timeout=30, phrase_time_limit=25)
                        texto = r.recognize_google(audio, language="pt-BR")
                    except sr.WaitTimeoutError:
                        st.error("Não ouvi nada... tenta de novo?")
                        st.stop()
                    except sr.UnknownValueError:
                        st.error("Não entendi... fala mais perto ou devagar!")
                        st.stop()
                    except Exception as e:
                        st.error(f"Erro no microfone: {e}")
                        st.stop()

            st.session_state.conversa.append({"role": "assistant", "content": texto})
            st.success(f"Você disse: {texto}")

            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.conversa + [{"role": "system", "content": "Continue como cliente. Nunca resolva o problema sozinho. Só reclame ou peça ajuda. Português brasileiro."}],
                temperature=0.7
            ).choices[0].message.content.strip()

            engine.say(resposta)
            engine.runAndWait()
            st.session_state.conversa.append({"role": "user", "content": resposta})
            st.rerun()

        # Botão finalizar
        if st.button("FINALIZAR CHAMADA", key="finalizar"):
            feedback = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.conversa + [{"role": "system", "content": "Analise como supervisor da Alive. Dê pontos positivos, negativos e dicas em português."}],
                temperature=0.7
            ).choices[0].message.content.strip()
            st.success("FEEDBACK GERADO!")
            st.write(f"### Feedback:\n{feedback}")