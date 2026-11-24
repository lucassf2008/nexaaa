# Nexa SENAI — Plataforma de Conexão Profissional & Networking

O **Nexa SENAI** é um sistema web completo de networking profissional inspirado no LinkedIn, desenvolvido exclusivamente para conectar **alunos, ex-alunos e empresas parceiras/patrocinadoras do SENAI**, facilitando a inserção dos estudantes no mercado de trabalho industrial e tecnológico, a divulgação de oportunidades, candidaturas reais e comunicação direta.

---

## 📸 Design e Identidade Visual

O layout segue rigorosamente o design das 5 telas de referência:
1. **Desktop - 1 (Vagas e Busca de Oportunidades):** Barra de filtros à esquerda (tipo de vaga, área de atuação, modalidade, empresa, localização e experiência), barra de pesquisa e cards de vagas com botões de ação e visualização detalhada.
2. **Desktop - 2 (Login e Cadastro Centralizado):** Tela de login com logo Nexa SENAI, campos arredondados com borda suave, abas para Aluno (CPF/Senha), Empresa (CNPJ/Código de acesso) e Administrador.
3. **Desktop - 3 (Feed de Empresas e Networking):** Feed com badge *"Novas Publicações"*, publicações institucionais, área de publicação para estudantes e coluna lateral com *"Sugestões para você"* e CTA de publicação.
4. **Desktop - 1 Inferior (Perfil do Aluno):** Perfil profissional com foto, nome em destaque, badges de conexões, seções *"Sobre Mim"* com ícone, *"Experiências"* em linha do tempo, competências técnicas e coluna lateral com *"Novas Mensagens"*.
5. **Desktop - 4 (Perfil da Empresa e Vagas):** Coluna esquerda com banner da fábrica/instalações, logo corporativo, dados cadastrais, número de funcionários e redes sociais; coluna direita com *"Vagas Publicadas"*, botão *"Ver Candidatos"* e botão *"Criar nova vaga"*.
6. **Elementos Visuais Característicos:**
   - **Barras Verticais Vermelhas Laterais:** Pilares vermelhos arredondados ladeando o conteúdo em todas as telas, reproduzindo a assinatura do mockup.
   - **Navbar e Rodapé Escuros:** `#1E2125` com contrastes em branco e vermelho SENAI (`#E30613`).
   - **Cards Brancos com Cantos Arredondados e Sombras Suaves.**

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11 com Flask
- **Banco de Dados & ORM:** SQLite com SQLAlchemy (estruturado para migração imediata para PostgreSQL via variável de ambiente `DATABASE_URL`)
- **Autenticação & Segurança:** Sessões seguras HTTP-only, hash PBKDF2/SHA256 via Werkzeug, controle de acesso baseado em papéis (`aluno`, `empresa`, `admin`)
- **Algoritmos Matemáticos Oficiais:** Validação real de CPF (algoritmo Módulo 11) e CNPJ (pesos de 2 a 9 e dois dígitos verificadores da Receita Federal)
- **Frontend:** HTML5 semântico, CSS3 com variáveis customizadas, JavaScript moderno (AJAX, polling de chat, máscaras de inputs)
- **Ícones:** Font Awesome 6

---

## 📁 Estrutura do Projeto

```text
nexa_senai/
├── app.py                      # Ponto de entrada da aplicação e inicialização
├── config.py                   # Configurações de banco, uploads e sessões
├── models.py                   # Modelos relacionais SQLAlchemy (18 entidades)
├── forms.py                    # Validações matemáticas de CPF e CNPJ
├── auth.py                     # Controle de autenticação e permissões
├── seed.py                     # Semeador com dados realistas do ecossistema SENAI
├── test_app.py                 # Suíte de testes unitários automatizados
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação completa
├── routes/
│   ├── main.py                 # Feed, curtidas, comentários, conexões e busca global
│   ├── jobs.py                 # Vagas, filtros, candidaturas e favoritos
│   ├── profile.py              # Perfil do aluno, experiências, competências e projetos
│   ├── company.py              # Perfil da empresa, publicação de vagas e gestão de candidatos
│   ├── messages.py             # Sistema de chat e mensagens em tempo real
│   └── admin.py                # Painel de governança administrativa
├── static/
│   ├── css/
│   │   ├── style.css           # Estilos oficiais e tokens visuais SENAI
│   │   └── responsive.css      # Responsividade para celular, tablet e desktop
│   ├── js/
│   │   ├── main.js             # Interações globais, modais e AJAX
│   │   ├── chat.js             # Chat em tempo real com auto-scroll e polling
│   │   └── validators.js       # Máscaras client-side de CPF, CNPJ e telefone
│   ├── images/                 # Vetores SVG e logos (Nexa SENAI, WEG, TechCorp, avatares)
│   └── uploads/                # Diretório de uploads seguros de usuários
└── templates/
    ├── base.html               # Layout base com navbar, barras laterais e rodapé
    ├── jobs.html               # Desktop 1: Vagas e busca com filtros
    ├── job_detail.html         # Visualização detalhada e candidatura
    ├── login.html              # Desktop 2: Login centralizado em abas
    ├── register_aluno.html     # Cadastro de aluno com validação de CPF
    ├── feed.html               # Desktop 3: Feed e sugestões de networking
    ├── profile_student.html    # Desktop 1 (inf): Perfil do aluno e chat lateral
    ├── edit_student_profile.html
    ├── profile_company.html    # Desktop 4: Perfil empresarial e vagas publicadas
    ├── edit_company_profile.html
    ├── company_new_job.html    # Publicação de novas vagas corporativas
    ├── company_candidates.html # Gestão de candidatos e alteração de status
    ├── my_applications.html    # Painel de acompanhamento do aluno
    ├── messages.html           # Tela cheia de comunicação e mensagens
    ├── search_results.html     # Resultados da busca global
    ├── 404.html, 403.html, 500.html
    └── admin/
        ├── dashboard.html      # Métricas e indicadores do sistema
        ├── companies.html      # Autorização de empresas e códigos de acesso
        ├── users.html          # Moderação de usuários
        └── jobs.html           # Moderação de vagas
```

---

## 🚀 Como Executar no Windows

### 1. Clonar ou Acessar a Pasta do Projeto

```powershell
cd C:\Users\lucas\.gemini\antigravity\scratch\nexa_senai
```

### 2. Instalar as Dependências

```powershell
pip install -r requirements.txt
```

> **Nota:** Caso utilize o ambiente Python configurado no ambiente portátil:
> ```powershell
> C:\Users\lucas\.gemini\antigravity\scratch\python311\python.exe -m pip install -r requirements.txt
> ```

### 3. Iniciar o Servidor

```powershell
python app.py
```

Ou:

```powershell
C:\Users\lucas\.gemini\antigravity\scratch\python311\python.exe app.py
```

O banco de dados SQLite (`nexa_senai.db`) será criado e populado **automaticamente** na primeira inicialização com contas, empresas, vagas, feed e mensagens demonstrativas.

Acesse no navegador:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Executar a Suíte de Testes

Para rodar todos os testes automatizados (algoritmos matemáticos, login, vagas, mensagens e segurança):

```powershell
python test_app.py
```

---

## 🔑 Credenciais Pré-Cadastradas para Demonstração

### 1. Acesso do Administrador
- **URL de Login:** `/login?tab=admin`
- **E-mail:** `admin@senai.br`
- **Senha:** `admin123`
- **Acessos:** Cadastro de empresas parceiras, validação de CNPJ, geração e redefinição de códigos de acesso, bloqueio/desbloqueio de contas e moderação de vagas.

### 2. Acesso de Aluno (Exemplo: Clarisse Lima Moura - Desktop 1)
- **URL de Login:** `/login?tab=aluno`
- **CPF:** `234.567.890-92` *(ou e-mail: `clarisse.moura@aluno.senai.br`)*
- **Senha:** `senai123`
- **Acessos:** Busca e filtro de vagas, candidatura com carta de apresentação, acompanhamento de status, salvamento de favoritos, publicação no feed, edição de competências e mensagens.

### 3. Acesso de Empresa Parceira (Exemplo: TechCorp Inovações - Desktop 4)
- **URL de Login:** `/login?tab=empresa`
- **CNPJ:** `11.222.333/0001-81`
- **Código de Acesso:** `TECH-2024`
- **Acessos:** Publicação de vagas, visualização de candidatos inscritos, alteração do status da candidatura (`Recebida` ➔ `Em análise` ➔ `Entrevista` ➔ `Aprovada`), envio de feedback ao aluno e chat.

### 4. Acesso de Segunda Empresa (Exemplo: WEG Equipamentos Elétricos)
- **CNPJ:** `55.666.777/0001-81`
- **Código de Acesso:** `WEG-SENAI`

---

## 🏢 Como Cadastrar Novas Empresas Parceiras e Gerar Códigos

Por questões de segurança e integridade da rede SENAI, **empresas não podem se auto-cadastrar livremente** na internet. O processo é gerenciado pelo Administrador:

1. Acesse o sistema como Administrador (`admin@senai.br` / `admin123`).
2. No menu superior ou no painel, acesse **Painel Administrativo** ➔ **Cadastrar / Autorizar Empresa**.
3. Preencha a Razão Social, o CNPJ Oficial e o E-mail Institucional da empresa.
4. O sistema valida automaticamente o algoritmo do CNPJ.
5. Um **Código de Acesso Empresarial Único** (ex: `NEXA-94B8-BR`) é gerado instantaneamente e exibido na listagem.
6. A administração envia o código para o responsável da empresa, permitindo seu primeiro login em `/login?tab=empresa`.
7. O administrador pode a qualquer momento **redefinir o código** ou **bloquear o acesso** da empresa com 1 clique.

---

## 🔒 Recursos de Segurança Implementados

- Validação matemática estrita de CPF e CNPJ nos formulários e no backend.
- Criptografia de senhas e códigos utilizando hash seguro `pbkdf2:sha256`.
- Proteção contra injeção SQL nativa via ORM SQLAlchemy.
- Sanitização de uploads de arquivos com checagem de extensões permitidas e nomes de arquivo seguros (`secure_filename`).
- Proteção de rotas através dos decoradores `@login_required` e `@role_required`.
- Bloqueio de candidaturas duplicadas por meio de restrição única no banco de dados (`UniqueConstraint('job_id', 'student_id')`).
