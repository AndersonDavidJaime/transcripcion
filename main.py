import os
os.system('apt-get install -y ffmpeg')
import streamlit as st
import requests
import base64
import tempfile
import sounddevice as sd
import soundfile as sf
from io import BytesIO
import subprocess

st.title("🎤 Audio ↔ Texto ↔ Voz con AWS")

API_URL = "https://pqawnl4myd.execute-api.us-east-1.amazonaws.com/default/funcion_traduccir"

st.header("Audio a texto")


# ---------------------------
# Upload de archivos
# ---------------------------
uploaded_file = st.file_uploader("sube un archivo de audio (.wav, .mp3 o .aac)", type=["wav", "mp3", "aac"])
audio_bytes = None

if uploaded_file:
    try:
        # Guardar el archivo subido temporalmente
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        temp_file.close()

        # Convertir a WAV si es necesario
        wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        if uploaded_file.type == "audio/aac" or uploaded_file.name.endswith(".aac"):
            # Convertir AAC a WAV usando ffmpeg
            subprocess.run(["ffmpeg", "-i", temp_file.name, wav_file.name])
        else:
            # Si es WAV o MP3, simplemente leerlo
            wav_file.name = temp_file.name

        # Leer el archivo WAV
        data, samplerate = sf.read(wav_file.name)
        audio_bytes = open(wav_file.name, "rb").read()

    except Exception as e:
        st.error(f"Formato no soportado. Usa WAV, MP3 o AAC. Error: {str(e)}")


# ---------------------------
# Procesar audio
# ---------------------------
if audio_bytes:
    if st.button("Procesar audio"):
        payload = {"audio_base64": base64.b64encode(audio_bytes).decode("utf-8")}
        with st.spinner("Procesando audio..."):
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("🎯 Transcripción:")
                    st.write(data.get("transcript", "No se obtuvo texto"))

                    st.subheader("🔊 Audio generado con Polly:")
                    audio_stream = base64.b64decode(data.get("audio_base64", ""))
                    if audio_stream:
                        st.audio(audio_stream, format="audio/mp3")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error al llamar la API: {e}")

# ---------------------------
# Texto a voz
# ---------------------------
st.header("De texto a voz")
text_input = st.text_area("Escribe el texto que quieras convertir a voz")

if st.button("Generar Audio de Texto", key="text_to_speech"):
    if text_input.strip():
        payload = {"text_input": text_input}
        with st.spinner("Generando audio..."):
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    audio_stream = base64.b64decode(data.get("audio_base64", ""))
                    if audio_stream:
                        st.audio(audio_stream, format="audio/mp3")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error al llamar la API: {e}")
    else:
        st.warning("Por favor, ingresa algún texto.")
