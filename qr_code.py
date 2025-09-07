import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

st.set_page_config(page_title="QR Code App", page_icon="🔗", layout="wide")

# ---------------- Cabeçalho ----------------
col1, col2, col3, col4 = st.columns([0.5, 1, 0.5, 0.5])
with col2:
    st.title(":blue[Estufa IOT]")
    st.title("Projeto Integrador 6")
with col3:
    st.image("Code.png", width=150)

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["🖼️ Gerar QR Codes (JPG - A4)", "📷 Ler QR Codes"])

# ---------------- TAB 1 ----------------
with tab1:
    st.header("🖼️ Gerador de QR Codes em JPG (Formato A4)")

    st.write("Selecione a quantidade de QR Codes desejada:")

    qtd_escolhida = None
    for qtd in [4, 8, 12, 16]:
        if st.checkbox(f"{qtd} QR Codes"):
            qtd_escolhida = qtd

    if qtd_escolhida:
        nomes = st.multiselect(
            f"Selecione exatamente {qtd_escolhida} nomes:",
            [
                # Frutíferas
                "TOMATE", "MORANGO", "PIMENTÃO", "BERINJELA", "PEPINO", "MELÃO", "MELANCIA", "UVA",
                "ABACAXI", "MARACUJÁ", "COCO", "BANANA",

                # Hortaliças
                "ALFACE", "COUVE", "ESPINAFRE", "RÚCULA", "CENOURA", "BETERRABA", "CEBOLINHA",
                "SALSA", "COENTRO", "BRÓCOLIS", "COUVE-FLOR",

                # Flores ornamentais
                "ROSA", "ORQUÍDEA", "GIRASSOL", "LÍRIO", "CRAVO", "VIOLETA",

                # Ervas aromáticas e medicinais
                "HORTELÃ", "ALECRIM", "MANJERICÃO", "TOMILHO", "ERVA-DOCE", "CAMOMILA", "LAVANDA",
            ],
            max_selections=qtd_escolhida,
        )

        if st.button("Gerar JPG (A4)"):
            if len(nomes) != qtd_escolhida:
                st.warning(f"⚠️ Você deve selecionar exatamente {qtd_escolhida} nomes.")
            else:
                # Dimensão A4 em pixels (300 DPI)
                a4_width, a4_height = 2480, 3508

                # Layout por quantidade
                layout_map = {
                    4: (2, 2),
                    8: (2, 4),
                    12: (3, 4),
                    16: (4, 4),
                }

                cols, rows = layout_map[qtd_escolhida]

                # Calcular tamanho dos QR codes
                qr_size = min(
                    (a4_width - (cols + 1) * 100) // cols,
                    (a4_height - (rows + 1) * 150) // rows,
                )

                final_img = Image.new("RGB", (a4_width, a4_height), "white")
                draw = ImageDraw.Draw(final_img)

                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    font = ImageFont.load_default()

                for i, nome in enumerate(nomes):
                    # Gerar QR Code
                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(nome)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                    qr_img = qr_img.resize((qr_size, qr_size))

                    col = i % cols
                    row = i // cols
                    x = 100 + col * (qr_size + 100)
                    y = 100 + row * (qr_size + 150)

                    # Colar QR
                    final_img.paste(qr_img, (x, y))

                    # Texto abaixo do QR
                    text_x = x + qr_size // 2
                    text_y = y + qr_size + 50
                    draw.text((text_x, text_y), nome, font=font, fill="black", anchor="mm")

                # Mostrar imagem no app
                st.image(final_img, caption="Folha A4 com QR Codes")

                # Baixar JPG
                buf = BytesIO()
                final_img.save(buf, format="JPEG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="⬇️ Baixar JPG (A4)",
                    data=byte_im,
                    file_name="qrcodes_A4.jpg",
                    mime="image/jpeg",
                )

# ---------------- TAB 2 ----------------
with tab2:
    st.header("📷 Leitor de QR Code com OpenCV")

    uploaded_file = st.file_uploader("Carregue uma imagem com QR Code", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None and data:
            n_lines = len(bbox)
            for i in range(n_lines):
                pt1 = tuple(map(int, bbox[i][0]))
                pt2 = tuple(map(int, bbox[(i + 1) % n_lines][0]))
                cv2.line(img, pt1, pt2, color=(255, 0, 0), thickness=2)

            st.image(img, channels="BGR", caption="QR Code Detectado")
            st.success(f"📌 Conteúdo do QR Code: {data}")
        else:
            st.warning("⚠️ Nenhum QR Code detectado nessa imagem.")
