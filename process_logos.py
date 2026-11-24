import os
from PIL import Image

SRC_DIR = r"C:\Users\lucas\.gemini\antigravity\brain\0bcae2b5-5bdf-472a-b9d7-b8f6798c564b\.user_uploaded"
DST_DIR = r"C:\Users\lucas\.gemini\antigravity\scratch\nexa_senai\static\images"

# 1. PROCESSAR LOGO BRANCO (Fundo Preto -> Transparente)
img_white_path = os.path.join(SRC_DIR, "media_1795195226551_92664182.png")
if os.path.exists(img_white_path):
    img = Image.open(img_white_path).convert("RGBA")
    # Encontra bounding box de pixels não-pretos (threshold > 30)
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    diff = Image.new("L", img.size)
    pixels = img.load()
    diff_pixels = diff.load()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = pixels[x, y]
            brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
            diff_pixels[x, y] = brightness if brightness > 30 else 0

    bbox = diff.getbbox()
    if bbox:
        # Adiciona pequena margem
        x1 = max(0, bbox[0] - 10)
        y1 = max(0, bbox[1] - 10)
        x2 = min(w, bbox[2] + 10)
        y2 = min(h, bbox[3] + 10)
        cropped = img.crop((x1, y1, x2, y2))
        
        # Converte preto para transparente com suavização
        cropped_rgba = cropped.convert("RGBA")
        c_pixels = cropped_rgba.load()
        cw, ch = cropped_rgba.size
        for x in range(cw):
            for y in range(ch):
                r, g, b, a = c_pixels[x, y]
                alpha = int(max(r, g, b))
                # Força o branco puro onde há texto/ícone
                if alpha > 30:
                    c_pixels[x, y] = (255, 255, 255, min(255, int(alpha * 1.2)))
                else:
                    c_pixels[x, y] = (0, 0, 0, 0)
        
        out_white = os.path.join(DST_DIR, "logo_nexa_white.png")
        cropped_rgba.save(out_white, "PNG")
        print("Logo branco processado:", out_white, cropped_rgba.size)

# 2. PROCESSAR LOGO VERMELHO (Fundo Branco -> Transparente)
img_red_path = os.path.join(SRC_DIR, "media_1795195306615_ae8e9e6d.png")
if os.path.exists(img_red_path):
    img = Image.open(img_red_path).convert("RGBA")
    w, h = img.size
    diff = Image.new("L", img.size)
    pixels = img.load()
    diff_pixels = diff.load()
    for x in range(w):
        for y in range(h):
            r, g, b, a = pixels[x, y]
            # Detecta se não é branco
            if r < 240 or g < 240 or b < 240:
                diff_pixels[x, y] = 255
            else:
                diff_pixels[x, y] = 0

    bbox = diff.getbbox()
    if bbox:
        x1 = max(0, bbox[0] - 10)
        y1 = max(0, bbox[1] - 10)
        x2 = min(w, bbox[2] + 10)
        y2 = min(h, bbox[3] + 10)
        cropped = img.crop((x1, y1, x2, y2))
        
        # Converte branco em transparente mantendo o vermelho #da251c
        c_pixels = cropped.load()
        cw, ch = cropped.size
        for x in range(cw):
            for y in range(ch):
                r, g, b, a = c_pixels[x, y]
                # Se for próximo de branco, torna transparente
                if r > 240 and g > 240 and b > 240:
                    c_pixels[x, y] = (0, 0, 0, 0)
                else:
                    # Garantir que a cor vermelha seja exatamente #da251c (218, 37, 28)
                    dist_to_white = 255 - int((r + g + b) / 3)
                    alpha = min(255, int(dist_to_white * 1.5))
                    c_pixels[x, y] = (218, 37, 28, alpha)
                    
        out_red = os.path.join(DST_DIR, "logo_nexa_red.png")
        cropped.save(out_red, "PNG")
        print("Logo vermelho processado:", out_red, cropped.size)
