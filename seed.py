from datetime import datetime, timedelta
from models import (
    db, User, StudentProfile, CompanyProfile, Job, Application,
    Post, Comment, Like, Follow, Connection, Message, Skill, Experience, Education, Project, Certificate
)
from forms import clean_digits, format_cpf, format_cnpj

def make_valid_cpf(base9="111444777"):
    soma1 = sum(int(base9[i]) * (10 - i) for i in range(9))
    r1 = (soma1 * 10) % 11
    d1 = 0 if r1 in (10, 11) else r1
    base10 = base9 + str(d1)
    soma2 = sum(int(base10[i]) * (11 - i) for i in range(10))
    r2 = (soma2 * 10) % 11
    d2 = 0 if r2 in (10, 11) else r2
    return f"{base9[:3]}.{base9[3:6]}.{base9[6:9]}-{d1}{d2}"

def make_valid_cnpj(base12="123456780001"):
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(base12[i]) * pesos1[i] for i in range(12))
    r1 = soma1 % 11
    d1 = 0 if r1 < 2 else 11 - r1
    base13 = base12 + str(d1)
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma2 = sum(int(base13[i]) * pesos2[i] for i in range(13))
    r2 = soma2 % 11
    d2 = 0 if r2 < 2 else 11 - r2
    return f"{base12[:2]}.{base12[2:5]}.{base12[5:8]}/{base12[8:12]}-{d1}{d2}"

def seed_database():
    # Se já houver usuários cadastrados, não duplica
    if User.query.first():
        return

    print("Inicializando banco de dados com dados reais e humanizados do ecossistema Nexa SENAI...")

    # -------------------------------------------------------------
    # 1. ADMINISTRADOR
    # -------------------------------------------------------------
    admin_user = User(
        email='admin@senai.br',
        role='admin',
        is_active=True
    )
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    # -------------------------------------------------------------
    # 2. ALUNOS E EGRESSOS DO SENAI
    # -------------------------------------------------------------
    # Clarisse Lima Moura (Referência do mockup Desktop 1)
    cpf_clarisse = make_valid_cpf("234567890")
    user_clarisse = User(
        email='clarisse.moura@aluno.senai.br',
        role='aluno',
        is_active=True
    )
    user_clarisse.set_password('senai123')
    db.session.add(user_clarisse)
    db.session.flush()

    student_clarisse = StudentProfile(
        user_id=user_clarisse.id,
        full_name='CLARISSE LIMA MOURA',
        cpf=cpf_clarisse,
        birth_date='2002-04-15',
        phone='(11) 98765-4321',
        city='São Paulo',
        state='SP',
        senai_course='Técnico em Redes de Computadores',
        course_status='Concluído',
        professional_area='Desenvolvimento de software',
        headline='Estagiária de Infraestrutura & Redes | Formada pelo SENAI Suíço-Brasileira',
        about_me='Técnica em Redes e Cibersegurança formada pela Escola SENAI Suíço-Brasileira Paulo Ernesto Tolle. Atualmente estagio no suporte de infraestrutura e estudo automação de redes com Python. Tenho facilidade para trabalhar em equipe, aprender novas ferramentas de forma rápida e colocar a mão na massa em projetos práticos.',
        avatar_url='/static/images/avatars/clarisse.jpg',
        connections_count=524
    )
    db.session.add(student_clarisse)
    db.session.flush()

    # Experiências da Clarisse (exatamente como na imagem)
    exp1 = Experience(
        student_id=student_clarisse.id,
        company='Faculdade SENAI de Tecnologia',
        role='Assistente de Suporte Técnico',
        period='Jan 2023 - Atual',
        description='Atuação direta no suporte aos laboratórios de informática, configuração de switches e roteadores Cisco, gerenciamento de permissões de rede e apoio técnico aos alunos e professores.',
        is_current=True
    )
    exp2 = Experience(
        student_id=student_clarisse.id,
        company='SENAI Informática',
        role='Pós-Graduação / Aperfeiçoamento Técnico',
        period='Ago 2022 - Dez 2022',
        description='Curso de extensão focado em segurança de redes, firewall defensivo, monitoramento com Zabbix e automação de rotinas em servidores Linux.'
    )
    db.session.add_all([exp1, exp2])

    # Competências da Clarisse
    skills_clarisse = [
        Skill(student_id=student_clarisse.id, name='Redes de Computadores', level='Avançado'),
        Skill(student_id=student_clarisse.id, name='Python', level='Intermediário'),
        Skill(student_id=student_clarisse.id, name='Linux & Servidores', level='Avançado'),
        Skill(student_id=student_clarisse.id, name='Segurança da Informação', level='Intermediário'),
        Skill(student_id=student_clarisse.id, name='Roteamento Cisco', level='Intermediário'),
        Skill(student_id=student_clarisse.id, name='SQL Básico', level='Básico')
    ]
    db.session.add_all(skills_clarisse)

    # Formação da Clarisse
    edu_clarisse = Education(
        student_id=student_clarisse.id,
        institution='Escola SENAI Suíço-Brasileira',
        course='Curso Técnico em Redes de Computadores',
        start_year='2021',
        end_year='2023',
        status='Concluído'
    )
    db.session.add(edu_clarisse)

    # Projeto prático
    proj_clarisse = Project(
        student_id=student_clarisse.id,
        title='Sistema Automatizado de Bloqueio de Portas com Python',
        description='Projeto desenvolvido no laboratório do SENAI que identifica varreduras suspeitas de portas em servidores locais e aplica regras dinâmicas de firewall.',
        technologies='Python, Linux, iptables, Socket API',
        link_url='https://github.com/clarisse-moura/senai-firewall-lab'
    )
    db.session.add(proj_clarisse)

    # Outros alunos reais da comunidade SENAI (Sugestões do mockup Desktop 3 e 1)
    other_students_data = [
        {
            'name': 'João Paulo Torres',
            'email': 'joao.torres@aluno.senai.br',
            'base9': '345678901',
            'area': 'Automação industrial',
            'course': 'Técnico em Mecatrônica',
            'headline': 'Estudante de Automação Industrial e Robótica | SENAI Santos',
            'about': 'Estudante do 3º termo de Mecatrônica no SENAI Santos. Fascinado por CLPs, esteiras automatizadas e inversores de frequência. Buscando estágio em chão de fábrica.',
            'avatar': '/static/images/avatars/joao.jpg',
            'city': 'Santos - SP'
        },
        {
            'name': 'Natália Castier',
            'email': 'natalia.castier@aluno.senai.br',
            'base9': '456789012',
            'area': 'Desenvolvimento de software',
            'course': 'Desenvolvimento de Sistemas',
            'headline': 'Desenvolvedora Full Stack Jr | React, Node.js e SQL | Ex-Aluna SENAI',
            'about': 'Formada em Desenvolvimento de Sistemas pelo SENAI. Apaixonada por interfaces limpas, código organizado e desenvolvimento web moderno.',
            'avatar': '/static/images/avatars/natalia.jpg',
            'city': 'São Paulo - SP'
        },
        {
            'name': 'Gabriel Castro Silva',
            'email': 'gabriel.castro@aluno.senai.br',
            'base9': '567890123',
            'area': 'Dados',
            'course': 'Ciência de Dados e IA',
            'headline': 'Estagiário em Análise de Dados e Python | SENAI Campinas',
            'about': 'Gosto de transformar números brutos de produção industrial em gráficos e insights claros para tomadas de decisão rápidas.',
            'avatar': '/static/images/avatars/gabriel.jpg',
            'city': 'Campinas - SP'
        },
        {
            'name': 'Aline Schirmer Santos',
            'email': 'aline.schirmer@aluno.senai.br',
            'base9': '678901234',
            'area': 'Design',
            'course': 'Design Gráfico e UI/UX',
            'headline': 'Designer UI/UX & Comunicação Visual | Aluna SENAI Curitiba',
            'about': 'Focada em design centrado no usuário, prototipação ágil no Figma e acessibilidade digital para plataformas corporativas.',
            'avatar': '/static/images/avatars/aline.jpg',
            'city': 'Curitiba - PR'
        },
        {
            'name': 'Marina Schirmer',
            'email': 'marina.schirmer@aluno.senai.br',
            'base9': '789012345',
            'area': 'Eletrônica',
            'course': 'Técnico em Eletroeletrônica',
            'headline': 'Técnica em Eletroeletrônica | Foco em Hardware e IoT Industrial',
            'about': 'Experiência em bancadas de montagem de circuitos, sensores analógicos e digitais e integração de microcontroladores com microcomputadores.',
            'avatar': '/static/images/avatars/marina.jpg',
            'city': 'Joinville - SC'
        }
    ]

    created_students = [student_clarisse]
    for sdata in other_students_data:
        u = User(email=sdata['email'], role='aluno', is_active=True)
        u.set_password('senai123')
        db.session.add(u)
        db.session.flush()

        sp = StudentProfile(
            user_id=u.id,
            full_name=sdata['name'],
            cpf=make_valid_cpf(sdata['base9']),
            birth_date='2001-08-20',
            phone='(11) 91234-5678',
            city=sdata['city'].split('-')[0].strip(),
            state=sdata['city'].split('-')[1].strip() if '-' in sdata['city'] else 'SP',
            senai_course=sdata['course'],
            course_status='Em andamento',
            professional_area=sdata['area'],
            headline=sdata['headline'],
            about_me=sdata['about'],
            avatar_url=sdata['avatar'],
            connections_count=180
        )
        db.session.add(sp)
        created_students.append(sp)

    db.session.commit()

    # -------------------------------------------------------------
    # 3. EMPRESAS PARCEIRAS E PATROCINADORAS
    # -------------------------------------------------------------
    # TechCorp Inovações (Desktop 4)
    cnpj_techcorp = make_valid_cnpj("112223330001")
    code_techcorp = "TECH-2024"
    u_tech = User(email='contato@techcorpinovacoes.com.br', role='empresa', is_active=True)
    u_tech.set_password(code_techcorp)
    db.session.add(u_tech)
    db.session.flush()

    comp_techcorp = CompanyProfile(
        user_id=u_tech.id,
        name='TechCorp Inovações S.A.',
        cnpj=cnpj_techcorp,
        access_code=code_techcorp,
        is_authorized=True,
        is_blocked=False,
        sector='Tecnologia e Indústria 4.0',
        headline='Sistemas de automação industrial, telemetria em nuvem e IoT fabril',
        description='A TechCorp atua na modernização de plantas fabris por meio de telemetria, sensores inteligentes e softwares sob medida. Mais de 40% do nosso time técnico veio diretamente de cursos e programas de estágio do SENAI. Nosso ambiente é colaborativo, prático e aberto a quem quer crescer com a gente.',
        location='São Paulo - SP (Próximo ao Polo Tecnológico de Santo Amaro)',
        website='https://techcorpinovacoes.com.br',
        contact_email='recrutamento@techcorpinovacoes.com.br',
        contact_phone='(11) 3200-4000',
        employee_count='150+ colaboradores (40% formados no SENAI)',
        logo_url='/static/images/companies/techcorp.png',
        banner_url='/static/images/companies/techcorp_banner.jpg',
        facebook='https://facebook.com/techcorp',
        instagram='https://instagram.com/techcorp',
        twitter='https://x.com/techcorp'
    )
    db.session.add(comp_techcorp)

    # DuTech Solutions (Desktop 3)
    cnpj_dutech = make_valid_cnpj("223334440001")
    code_dutech = "DUTECH-88"
    u_dutech = User(email='contato@dutechsolutions.com.br', role='empresa', is_active=True)
    u_dutech.set_password(code_dutech)
    db.session.add(u_dutech)
    db.session.flush()

    comp_dutech = CompanyProfile(
        user_id=u_dutech.id,
        name='DuTech Solutions',
        cnpj=cnpj_dutech,
        access_code=code_dutech,
        is_authorized=True,
        is_blocked=False,
        sector='Desenvolvimento de Software',
        headline='Desenvolvimento de Software e Inovação Digital',
        description='Somos uma empresa ágil focada em construir plataformas web, aplicativos móveis e integrações corporativas. Buscamos pessoas curiosas, com vontade de codar projetos reais e aprender no dia a dia.',
        location='São Paulo - SP',
        website='https://dutechsolutions.com.br',
        contact_email='rh@dutechsolutions.com.br',
        contact_phone='(11) 4004-1010',
        employee_count='60 colaboradores',
        logo_url='/static/images/companies/dutech.png',
        banner_url='/static/images/companies/dutech_banner.jpg'
    )
    db.session.add(comp_dutech)

    # Lumina Data Labs (Desktop 3)
    cnpj_lumina = make_valid_cnpj("334445550001")
    code_lumina = "LUMINA-42"
    u_lumina = User(email='carreiras@luminadata.com.br', role='empresa', is_active=True)
    u_lumina.set_password(code_lumina)
    db.session.add(u_lumina)
    db.session.flush()

    comp_lumina = CompanyProfile(
        user_id=u_lumina.id,
        name='Lumina Data Labs',
        cnpj=cnpj_lumina,
        access_code=code_lumina,
        is_authorized=True,
        is_blocked=False,
        sector='Dados e Inteligência Artificial',
        headline='Ciência de Dados e Analytics Industrial',
        description='Ajudamos empresas de logística e indústrias a prever falhas e otimizar rotas com análise de dados e machine learning. Incentivamos projetos acadêmicos e parcerias com turmas de TI do SENAI.',
        location='Campinas - SP',
        website='https://luminadata.com.br',
        contact_email='carreiras@luminadata.com.br',
        contact_phone='(19) 3500-8800',
        employee_count='85 colaboradores',
        logo_url='/static/images/companies/lumina.png',
        banner_url='/static/images/companies/lumina_banner.jpg'
    )
    db.session.add(comp_lumina)

    # Orion Systems (Desktop 3)
    cnpj_orion = make_valid_cnpj("445556660001")
    code_orion = "ORION-99"
    u_orion = User(email='rh@orionsystems.com.br', role='empresa', is_active=True)
    u_orion.set_password(code_orion)
    db.session.add(u_orion)
    db.session.flush()

    comp_orion = CompanyProfile(
        user_id=u_orion.id,
        name='Orion Systems',
        cnpj=cnpj_orion,
        access_code=code_orion,
        is_authorized=True,
        is_blocked=False,
        sector='Segurança da Informação e Infraestrutura',
        headline='Segurança da Informação e Infraestrutura de Redes',
        description='Atuamos na proteção e suporte a sistemas de missão crítica, com monitoramento SOC, regras de firewall e arquitetura de redes para bancos e grandes indústrias.',
        location='São Paulo - SP',
        website='https://orionsystems.com.br',
        contact_email='vagas@orionsystems.com.br',
        contact_phone='(11) 5555-0199',
        employee_count='210 colaboradores',
        logo_url='/static/images/companies/orion.png',
        banner_url='/static/images/companies/orion_banner.jpg'
    )
    db.session.add(comp_orion)

    # WEG (Desktop 1)
    cnpj_weg = make_valid_cnpj("556667770001")
    code_weg = "WEG-SENAI"
    u_weg = User(email='estagios@weg.net', role='empresa', is_active=True)
    u_weg.set_password(code_weg)
    db.session.add(u_weg)
    db.session.flush()

    comp_weg = CompanyProfile(
        user_id=u_weg.id,
        name='WEG Equipamentos Elétricos',
        cnpj=cnpj_weg,
        access_code=code_weg,
        is_authorized=True,
        is_blocked=False,
        sector='Automação Industrial e Energia',
        headline='Motores elétricos, automação, geração de energia e acionamentos',
        description='Com mais de 60 anos de história, a WEG é parceira de longa data do SENAI na formação e contratação de jovens técnicos. Oferecemos trilhas de capacitação contínua em nossas fábricas.',
        location='Jaraguá do Sul - SC / Joinville - SC',
        website='https://weg.net',
        contact_email='estagios@weg.net',
        contact_phone='(47) 3276-4000',
        employee_count='Mais de 30.000 colaboradores',
        logo_url='/static/images/companies/weg.png',
        banner_url='/static/images/companies/weg_banner.jpg'
    )
    db.session.add(comp_weg)

    # TOTVS (Desktop 1)
    cnpj_totvs = make_valid_cnpj("667778880001")
    code_totvs = "TOTVS-DEV"
    u_totvs = User(email='talentos@totvs.com.br', role='empresa', is_active=True)
    u_totvs.set_password(code_totvs)
    db.session.add(u_totvs)
    db.session.flush()

    comp_totvs = CompanyProfile(
        user_id=u_totvs.id,
        name='TOTVS Brasil',
        cnpj=cnpj_totvs,
        access_code=code_totvs,
        is_authorized=True,
        is_blocked=False,
        sector='Software Corporativo',
        headline='Maior empresa de tecnologia do Brasil, presente no dia a dia da indústria',
        description='A TOTVS desenvolve softwares de gestão e produtividade que movem o Brasil. Nossos programas para estudantes do SENAI combinam mentoria com desafios reais em equipes multidisciplinares.',
        location='São Paulo - SP',
        website='https://totvs.com',
        contact_email='talentos@totvs.com.br',
        contact_phone='(11) 2099-7000',
        employee_count='Mais de 10.000 colaboradores',
        logo_url='/static/images/companies/totvs.png',
        banner_url='/static/images/companies/totvs_banner.jpg'
    )
    db.session.add(comp_totvs)

    db.session.commit()

    # -------------------------------------------------------------
    # 4. VAGAS REAIS E HUMANIZADAS (Desktop 1 e 4)
    # -------------------------------------------------------------
    job1 = Job(
        company_id=comp_weg.id,
        title='Estagiário para Técnico em Automação Industrial',
        description='Procuramos estudantes do SENAI para atuar junto aos nossos técnicos e engenheiros na montagem de bancadas de teste, parametrização de inversores de frequência e comissionamento de painéis elétricos com CLP Siemens. Ambiente prático com muito aprendizado de chão de fábrica.',
        requirements='Estar cursando o Técnico em Automação Industrial ou Mecatrônica no SENAI;\nNoções de comandos elétricos e lógica de programação (Ladder);\nVontade de aprender e perfil focado em segurança do trabalho.',
        area='Automação industrial',
        job_type='Estágio',
        modality='Presencial',
        location='Joinville - SC',
        salary='R$ 1.850,00',
        benefits='Bolsa-auxílio, Vale-Transporte ou fretado, restaurante no local, plano de saúde e participação nos lucros da empresa.',
        experience_level='Estágio',
        vacancies=3,
        image_url='/static/images/jobs/automacao.jpg',
        created_at=datetime.utcnow() - timedelta(days=1)
    )

    job2 = Job(
        company_id=comp_techcorp.id,
        title='Estagiário para Engenheiro de Software',
        description='Você curte programar e quer ver seu código rodando na prática em chão de fábrica? Nosso time de IoT está procurando um estagiário de desenvolvimento para ajudar a construir APIs REST em Python e integrar sensores industriais em nossos dashboards de monitoramento.',
        requirements='Cursando Desenvolvimento de Sistemas ou Engenharia de Software no SENAI;\nConhecimento básico de Python ou JavaScript;\nNoções de Git para versionamento de código e banco de dados relacional.',
        area='Desenvolvimento de software',
        job_type='Estágio',
        modality='Híbrida',
        location='São Paulo - SP',
        salary='R$ 2.400,00',
        benefits='Bolsa-estágio, Vale-Refeição de R$ 42/dia, Vale-Transporte, Auxílio Home Office e convênio médico.',
        experience_level='Estágio',
        vacancies=2,
        image_url='/static/images/jobs/software.jpg',
        created_at=datetime.utcnow() - timedelta(days=2)
    )

    job3 = Job(
        company_id=comp_weg.id,
        title='Estagiário em Eletrotécnica Industrial',
        description='Oportunidade para apoiar o setor de ensaios elétricos de motores de alta tensão, leitura de diagramas unifilares e montagem de quadros de comando elétrico.',
        requirements='Cursando Técnico em Eletrotécnica ou Eletroeletrônica no SENAI;\nLeitura básica de esquemas elétricos industriais;\nNR-10 será considerada um diferencial bacana.',
        area='Eletrônica',
        job_type='Estágio',
        modality='Presencial',
        location='Jaraguá do Sul - SC',
        salary='R$ 1.750,00',
        benefits='Bolsa-auxílio, transporte fretado, alimentação no refeitório e convênio farmácia.',
        experience_level='Estágio',
        vacancies=2,
        image_url='/static/images/jobs/eletrotecnica.jpg',
        created_at=datetime.utcnow() - timedelta(days=3)
    )

    job4 = Job(
        company_id=comp_techcorp.id,
        title='Analista de Dados Júnior',
        description='Vaga efetiva voltada para recém-formados do SENAI na área de dados e computação. Você trabalhará na criação de relatórios automatizados, dashboards em Power BI e scripts de extração de dados com Python.',
        requirements='Formado no curso técnico ou tecnólogo do SENAI em Dados ou Informática;\nDomínio de SQL e bibliotecas Pandas/NumPy em Python;\nBoa capacidade de comunicação para explicar números aos gestores.',
        area='Dados',
        job_type='Emprego efetivo',
        modality='Híbrida',
        location='São Paulo - SP',
        salary='R$ 4.200,00',
        benefits='Regime CLT, Plano de Saúde Bradesco, Vale-Alimentação (R$ 800/mês), PLR semestral e Gympass.',
        experience_level='Júnior',
        vacancies=1,
        image_url='/static/images/jobs/dados.jpg',
        created_at=datetime.utcnow() - timedelta(days=4)
    )

    job5 = Job(
        company_id=comp_totvs.id,
        title='Desenvolvedor Front-end React (Jovem Aprendiz)',
        description='Se você é jovem e quer iniciar sua carreira na maior empresa de software do país, essa vaga é para você! Você participará de aulas práticas e do desenvolvimento de telas utilizando o design system corporativo da TOTVS.',
        requirements='Estar matriculado no programa de Aprendizagem Industrial do SENAI em Informática ou Programação;\nConhecimento básico de HTML5, CSS3 e JavaScript;\nVontade de aprender e crescer com a equipe.',
        area='Desenvolvimento de software',
        job_type='Jovem aprendiz',
        modality='Remota',
        location='Remoto',
        salary='R$ 1.350,00',
        benefits='Bolsa aprendiz, Vale-Alimentação, capacitação continuada na TOTVS University e apoio de tutoria.',
        experience_level='Sem experiência',
        vacancies=4,
        image_url='/static/images/jobs/software.jpg',
        created_at=datetime.utcnow() - timedelta(days=5)
    )

    db.session.add_all([job1, job2, job3, job4, job5])
    db.session.commit()

    # -------------------------------------------------------------
    # 5. CANDIDATURAS REAIS
    # -------------------------------------------------------------
    app1 = Application(
        job_id=job2.id,
        student_id=student_clarisse.id,
        status='em_analise',
        notes='Currículo recebido e em triagem com o time de engenharia de software da TechCorp.'
    )
    app2 = Application(
        job_id=job1.id,
        student_id=created_students[1].id,  # João Paulo Torres
        status='entrevista',
        notes='Parabéns, João! Sua entrevista técnica foi agendada para sexta-feira às 14h com o supervisor de automação.'
    )
    db.session.add_all([app1, app2])

    # -------------------------------------------------------------
    # 6. PUBLICAÇÕES HUMANIZADAS NO FEED (Desktop 3)
    # -------------------------------------------------------------
    post1 = Post(
        user_id=u_dutech.id,
        title='Processo seletivo aberto para estagiários em desenvolvimento!',
        content='Fala pessoal do SENAI! Estamos abrindo nosso processo seletivo para estagiários em desenvolvimento back-end (Python e Node.js). Quem curte programar e quer trabalhar em projetos reais com microsserviços, confira os detalhes na aba de Vagas ou mande seu currículo por aqui!',
        category='oportunidade',
        image_url='/static/images/posts/post_dutech.jpg',
        created_at=datetime.utcnow() - timedelta(hours=3)
    )

    post2 = Post(
        user_id=u_lumina.id,
        title='Inscrições abertas para o Hackathon de IA Industrial SENAI + Lumina!',
        content='Estão abertas as inscrições para o nosso Hackathon anual de IA Industrial! Se você e seus colegas têm um projeto bacana de análise de dados ou automação com Python, montem uma equipe de 3 a 5 alunos. Teremos premiações em dinheiro e conversas diretas com nossos líderes técnicos.',
        category='evento',
        image_url='/static/images/posts/post_lumina.jpg',
        created_at=datetime.utcnow() - timedelta(hours=7)
    )

    post3 = Post(
        user_id=u_tech.id,
        title='TechCorp abre 10 novas vagas de estágio técnico para 2024',
        content='Se você é estudante do SENAI nas áreas de Mecatrônica, Automação ou Desenvolvimento de Sistemas, venha construir projetos de fábrica inteligente conosco. O escritório fica perto da estação Santo Amaro, temos horário flexível e plano de desenvolvimento individual!',
        category='novidades',
        image_url='/static/images/posts/post_techcorp.jpg',
        created_at=datetime.utcnow() - timedelta(days=1)
    )

    post4 = Post(
        user_id=user_clarisse.id,
        title='Concluí minha certificação em Defesa de Redes no SENAI!',
        content='Muito feliz em compartilhar que finalizei o módulo avançado de Defesa de Redes e Infraestruturas Críticas pelo SENAI. Foram semanas intensas configurando roteadores Cisco, firewalls e scripts de monitoramento em Python. Um agradecimento especial aos professores e colegas pela parceria!',
        category='conquista',
        image_url=None,
        created_at=datetime.utcnow() - timedelta(days=2)
    )

    db.session.add_all([post1, post2, post3, post4])
    db.session.commit()

    # Comentários humanos e naturais
    c1 = Comment(
        post_id=post1.id,
        user_id=user_clarisse.id,
        content='Excelente oportunidade da DuTech! O curso do SENAI dá uma base prática muito forte em lógica e banco de dados.'
    )
    c2 = Comment(
        post_id=post4.id,
        user_id=u_orion.id,
        content='Parabéns pela dedicação, Clarisse! Profissionais que entendem de redes e segurança na prática são muito requisitados.'
    )
    db.session.add_all([c1, c2])

    # Curtidas
    l1 = Like(post_id=post1.id, user_id=user_clarisse.id)
    l2 = Like(post_id=post1.id, user_id=u_tech.id)
    l3 = Like(post_id=post4.id, user_id=u_orion.id)
    l4 = Like(post_id=post3.id, user_id=user_clarisse.id)
    db.session.add_all([l1, l2, l3, l4])

    # Seguir empresas
    f1 = Follow(follower_id=user_clarisse.id, company_id=comp_techcorp.id)
    f2 = Follow(follower_id=user_clarisse.id, company_id=comp_dutech.id)
    f3 = Follow(follower_id=user_clarisse.id, company_id=comp_weg.id)
    db.session.add_all([f1, f2, f3])

    # Conexões
    conn1 = Connection(requester_id=user_clarisse.id, addressee_id=created_students[1].user_id, status='aceita')
    conn2 = Connection(requester_id=user_clarisse.id, addressee_id=created_students[2].user_id, status='aceita')
    db.session.add_all([conn1, conn2])

    # -------------------------------------------------------------
    # 7. MENSAGENS REAIS E NATURAIS (Desktop 1 - Novas Mensagens)
    # -------------------------------------------------------------
    m1 = Message(
        sender_id=created_students[5].user_id,  # Marina Schirmer
        receiver_id=user_clarisse.id,
        content='Oi Clarisse! Vi seu projeto de firewall no perfil, achei sensacional! Você usou as máquinas virtuais do laboratório do SENAI pra testar o tráfego?',
        is_read=True,
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )
    m2 = Message(
        sender_id=user_clarisse.id,
        receiver_id=created_students[5].user_id,
        content='Oi Marina! Usei sim, configurei duas VMs Linux lá na bancada pra simular os pacotes e testar os bloqueios. Se quiser te mostro a estrutura!',
        is_read=True,
        created_at=datetime.utcnow() - timedelta(minutes=30)
    )
    m3 = Message(
        sender_id=created_students[3].user_id,  # Gabriel Castro Silva
        receiver_id=user_clarisse.id,
        content='E aí Clarisse! Você vai participar do Hackathon da Lumina que publicaram no feed? Estava pensando em montar um time com a galera de redes.',
        is_read=True,
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    m4 = Message(
        sender_id=u_tech.id,
        receiver_id=user_clarisse.id,
        content='Olá Clarisse, tudo bem? Vimos sua candidatura para a vaga de estágio em desenvolvimento e gostamos muito do seu perfil técnico. Você teria disponibilidade para um bate-papo online rápido nesta quinta-feira?',
        is_read=False,
        created_at=datetime.utcnow() - timedelta(minutes=15)
    )
    m5 = Message(
        sender_id=created_students[2].user_id,  # Natália Castier
        receiver_id=user_clarisse.id,
        content='Oi Clarisse! Vamos nos conectar no LinkedIn também? Te mandei convite lá.',
        is_read=True,
        created_at=datetime.utcnow() - timedelta(days=1)
    )

    db.session.add_all([m1, m2, m3, m4, m5])
    db.session.commit()
    print("Seed humanizado concluído com sucesso!")
