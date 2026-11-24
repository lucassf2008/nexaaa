import os

BASE_IMG = os.path.join(os.path.dirname(__file__), 'static', 'images')

def write_file(rel_path, content):
    full_path = os.path.join(BASE_IMG, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# 1. LOGO PRINCIPAL NEXA SENAI
logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 60" width="320" height="60">
  <defs>
    <linearGradient id="senaiRed" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E30613"/>
      <stop offset="100%" stop-color="#B7000B"/>
    </linearGradient>
  </defs>
  <!-- Símbolo Estilizado Nexa / Conexão -->
  <g transform="translate(10, 10)">
    <circle cx="20" cy="20" r="18" fill="url(#senaiRed)"/>
    <path d="M12 20 L28 20 M20 12 L20 28 M14 14 L26 26 M14 26 L26 14" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="20" cy="20" r="5" fill="#FFFFFF"/>
  </g>
  <!-- Texto Nexa -->
  <text x="58" y="38" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="28" font-weight="900" fill="#FFFFFF" letter-spacing="0.5">Nexa</text>
  <!-- Badge SENAI -->
  <rect x="135" y="16" width="75" height="28" rx="6" fill="#E30613"/>
  <text x="141" y="36" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="18" font-weight="900" fill="#FFFFFF" letter-spacing="1.5">SENAI</text>
</svg>'''

# 1.2 LOGO NEXA SENAI PARA O CARD DE LOGIN (fundo claro)
logo_login_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 60" width="320" height="60">
  <defs>
    <linearGradient id="senaiRed2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E30613"/>
      <stop offset="100%" stop-color="#B7000B"/>
    </linearGradient>
  </defs>
  <g transform="translate(10, 10)">
    <circle cx="20" cy="20" r="18" fill="url(#senaiRed2)"/>
    <path d="M12 20 L28 20 M20 12 L20 28 M14 14 L26 26 M14 26 L26 14" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="20" cy="20" r="5" fill="#FFFFFF"/>
  </g>
  <text x="58" y="38" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="28" font-weight="900" fill="#E30613" letter-spacing="0.5">Nexa</text>
  <rect x="135" y="16" width="75" height="28" rx="6" fill="#E30613"/>
  <text x="141" y="36" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="18" font-weight="900" fill="#FFFFFF" letter-spacing="1.5">SENAI</text>
</svg>'''

write_file('logo.svg', logo_svg)
write_file('logo_login.svg', logo_login_svg)

# 2. LOGOS DE EMPRESAS
def make_company_logo(name, initials, color1, color2, icon_type='tech'):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <defs>
    <linearGradient id="grad_{initials}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="20" fill="url(#grad_{initials})"/>
  <circle cx="50" cy="50" r="38" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.3"/>
  <text x="50" y="58" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="26" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{initials}</text>
</svg>'''

write_file('companies/techcorp.png', make_company_logo('TechCorp', 'TC', '#1A73E8', '#0D47A1'))
write_file('companies/dutech.png', make_company_logo('DuTech', 'DT', '#00C853', '#1B5E20'))
write_file('companies/lumina.png', make_company_logo('Lumina Data', 'LD', '#FF6D00', '#D50000'))
write_file('companies/orion.png', make_company_logo('Orion Systems', 'OS', '#6200EA', '#304FFE'))
write_file('companies/weg.png', make_company_logo('WEG', 'WEG', '#0072BC', '#003366'))
write_file('companies/totvs.png', make_company_logo('TOTVS', 'TVS', '#E91E63', '#880E4F'))
write_file('default_company.png', make_company_logo('Empresa', 'SENAI', '#E30613', '#900008'))

# 3. AVATARES DE ALUNOS
def make_avatar(name, initials, bg1, bg2, gender='F'):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
  <defs>
    <linearGradient id="av_{initials}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg1}"/>
      <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
  </defs>
  <circle cx="60" cy="60" r="60" fill="url(#av_{initials})"/>
  <circle cx="60" cy="46" r="22" fill="#FFFFFF" opacity="0.95"/>
  <path d="M22 104 C25 76 95 76 98 104 Z" fill="#FFFFFF" opacity="0.95"/>
  <circle cx="60" cy="60" r="58" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <text x="60" y="52" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="16" font-weight="900" fill="{bg2}" text-anchor="middle">{initials}</text>
</svg>'''

write_file('avatars/clarisse.jpg', make_avatar('Clarisse', 'CL', '#E91E63', '#AD1457', 'F'))
write_file('avatars/joao.jpg', make_avatar('João Paulo', 'JT', '#29B6F6', '#0277BD', 'M'))
write_file('avatars/natalia.jpg', make_avatar('Natália', 'NC', '#AB47BC', '#6A1B9A', 'F'))
write_file('avatars/gabriel.jpg', make_avatar('Gabriel', 'GC', '#26A69A', '#00695C', 'M'))
write_file('avatars/aline.jpg', make_avatar('Aline', 'AS', '#FFA726', '#E65100', 'F'))
write_file('avatars/marina.jpg', make_avatar('Marina', 'MS', '#EC407A', '#C2185B', 'F'))
write_file('default_student.png', make_avatar('Aluno', 'SN', '#E30613', '#7F0008', 'M'))
write_file('default_avatar.png', make_avatar('Usuário', 'NX', '#546E7A', '#263238', 'M'))

# 4. BANNERS
def make_banner(title, subtitle, color1, color2):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 350" width="1200" height="350">
  <defs>
    <linearGradient id="ban_{color1[:3]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="350" fill="url(#ban_{color1[:3]})"/>
  <g opacity="0.12">
    <path d="M0 0 L1200 350 M0 100 L1200 450 M0 200 L1200 550" stroke="#FFFFFF" stroke-width="4"/>
    <circle cx="200" cy="150" r="100" stroke="#FFFFFF" stroke-width="6" fill="none"/>
    <circle cx="1000" cy="200" r="140" stroke="#FFFFFF" stroke-width="8" fill="none"/>
  </g>
  <text x="60" y="160" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="44" font-weight="900" fill="#FFFFFF">{title}</text>
  <text x="60" y="210" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="22" font-weight="500" fill="#EEEEEE">{subtitle}</text>
</svg>'''

write_file('companies/techcorp_banner.jpg', make_banner('TechCorp Inovações', 'Indústria 4.0 & Inovação Tecnológica SENAI', '#0D47A1', '#1565C0'))
write_file('companies/dutech_banner.jpg', make_banner('DuTech Solutions', 'Soluções Digitais & Inteligência Artificial', '#1B5E20', '#2E7D32'))
write_file('companies/lumina_banner.jpg', make_banner('Lumina Data Labs', 'Ciência de Dados e Análise Preditiva', '#BF360C', '#E64A19'))
write_file('companies/orion_banner.jpg', make_banner('Orion Systems', 'Segurança da Informação & SOC Corporativo', '#311B92', '#4527A0'))
write_file('companies/weg_banner.jpg', make_banner('WEG Motores & Automação', 'Parceria Histórica de Capacitação Técnica com o SENAI', '#003366', '#004c99'))
write_file('companies/totvs_banner.jpg', make_banner('TOTVS Tecnologia', 'Impulsionando o Futuro do Software Corporativo', '#880E4F', '#AD1457'))
write_file('default_company_banner.jpg', make_banner('Nexa SENAI', 'Conectando o Futuro da Indústria Brasileira', '#212529', '#343A40'))
write_file('default_banner.jpg', make_banner('Nexa SENAI', 'Perfil Profissional do Aluno SENAI', '#B7000B', '#E30613'))

# 5. IMAGENS DE VAGAS (Thumbnails)
def make_job_thumbnail(label, subtitle, c1, c2, icon='cpu'):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150" width="200" height="150">
  <defs>
    <linearGradient id="job_{c1[:3]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="200" height="150" rx="14" fill="url(#job_{c1[:3]})"/>
  <circle cx="100" cy="65" r="32" fill="#FFFFFF" opacity="0.2"/>
  <rect x="78" y="45" width="44" height="40" rx="8" fill="#FFFFFF"/>
  <rect x="85" y="53" width="30" height="6" rx="3" fill="{c1}"/>
  <rect x="85" y="63" width="20" height="4" rx="2" fill="#888888"/>
  <rect x="85" y="71" width="26" height="4" rx="2" fill="#888888"/>
  <text x="100" y="125" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{label}</text>
</svg>'''

write_file('jobs/automacao.jpg', make_job_thumbnail('Automação', 'CLP & Robótica', '#0288D1', '#01579B'))
write_file('jobs/software.jpg', make_job_thumbnail('Software', 'Desenvolvimento', '#5E35B1', '#311B92'))
write_file('jobs/eletrotecnica.jpg', make_job_thumbnail('Eletrotécnica', 'Quadros & Ensaios', '#F57C00', '#E65100'))
write_file('jobs/dados.jpg', make_job_thumbnail('Dados & IA', 'Analytics & SQL', '#388E3C', '#1B5E20'))
write_file('job_default.jpg', make_job_thumbnail('Oportunidade', 'SENAI Carreira', '#E30613', '#B7000B'))

# 6. IMAGENS DE POSTS
def make_post_img(title, tag, col1, col2):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" width="600" height="300">
  <defs>
    <linearGradient id="p_{col1[:3]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{col1}"/>
      <stop offset="100%" stop-color="{col2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="300" rx="14" fill="url(#p_{col1[:3]})"/>
  <rect x="40" y="40" width="120" height="30" rx="15" fill="#FFFFFF"/>
  <text x="100" y="60" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="13" font-weight="900" fill="{col1}" text-anchor="middle">{tag}</text>
  <text x="40" y="140" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="28" font-weight="bold" fill="#FFFFFF">{title}</text>
  <text x="40" y="180" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="18" font-weight="400" fill="#E0E0E0">Programa de Capacitação e Contratação Nexa SENAI</text>
  <circle cx="520" cy="220" r="50" fill="#FFFFFF" opacity="0.15"/>
</svg>'''

write_file('posts/post_dutech.jpg', make_post_img('Transformação Digital', 'PARCERIA OFICIAL', '#1B5E20', '#2E7D32'))
write_file('posts/post_lumina.jpg', make_post_img('Hackathon de IA Industrial', 'EVENTO SENAI', '#BF360C', '#E64A19'))
write_file('posts/post_techcorp.jpg', make_post_img('10 Vagas para Estágio', 'OPORTUNIDADE', '#0D47A1', '#1976D2'))

print("Todos os assets vetoriais gerados com sucesso!")
