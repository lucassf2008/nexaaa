import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from app import create_app
from models import db, User, StudentProfile, CompanyProfile, Job, Application, Post, Message
from forms import validate_cpf, validate_cnpj, clean_digits

class NexaSenaiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_algorithms_cpf_cnpj(self):
        """Testa os algoritmos matemáticos de CPF e CNPJ"""
        # CPFs matematicamente válidos
        self.assertTrue(validate_cpf("234.567.890-92"))
        self.assertTrue(validate_cpf("34567890175"))
        # CPFs inválidos
        self.assertFalse(validate_cpf("111.111.111-11"))
        self.assertFalse(validate_cpf("123.456.789-00"))
        self.assertFalse(validate_cpf("123"))

        # CNPJs matematicamente válidos
        self.assertTrue(validate_cnpj("11.222.333/0001-81"))
        self.assertTrue(validate_cnpj("55666777000181"))
        # CNPJs inválidos
        self.assertFalse(validate_cnpj("00.000.000/0000-00"))
        self.assertFalse(validate_cnpj("11.222.333/0001-00"))

    def test_routes_public(self):
        """Testa se rotas públicas e de login respondem com 200"""
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Login', res.data)
        self.assertIn(b'Nexa', res.data)

        res = self.client.get('/cadastro')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Criar Conta de Aluno', res.data)

        res = self.client.get('/vagas')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Encontre sua pr', res.data)
        self.assertIn(b'Filtros', res.data)

    def test_login_aluno(self):
        """Testa o login com credenciais de aluno"""
        res = self.client.post('/login', data={
            'login_type': 'aluno',
            'identifier': '234.567.890-92',
            'password': 'senai123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'CLARISSE LIMA MOURA', res.data)

    def test_login_empresa(self):
        """Testa o login corporativo com CNPJ e código autorizado"""
        res = self.client.post('/login', data={
            'login_type': 'empresa',
            'cnpj': '11.222.333/0001-81',
            'access_code': 'TECH-2024'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'TechCorp', res.data)

    def test_login_admin(self):
        """Testa o login no painel administrativo"""
        res = self.client.post('/login', data={
            'login_type': 'admin',
            'email': 'admin@senai.br',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Painel de Administra', res.data)

    def test_vagas_filters(self):
        """Testa filtros reais de vagas"""
        res = self.client.get('/vagas?area=Desenvolvimento+de+software')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Estagi', res.data)

    def test_student_profile(self):
        """Testa a visualização da tela de perfil de aluno"""
        # Login primeiro
        self.client.post('/login', data={
            'login_type': 'aluno',
            'identifier': 'clarisse.moura@aluno.senai.br',
            'password': 'senai123'
        })
        res = self.client.get('/perfil/aluno')
        self.assertEqual(res.status_code, 302)  # redireciona para o id do aluno
        res = self.client.get('/perfil/aluno', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'CLARISSE LIMA MOURA', res.data)
        self.assertIn(b'Sobre Mim', res.data)
        self.assertIn(b'Experi', res.data)
        self.assertIn(b'Novas Mensagens', res.data)

    def test_messaging_flow(self):
        """Testa envio de mensagem entre usuários"""
        # Login como aluno
        self.client.post('/login', data={
            'login_type': 'aluno',
            'identifier': 'clarisse.moura@aluno.senai.br',
            'password': 'senai123'
        })
        # Envia mensagem para o TechCorp (user_id 7 ou similar)
        with self.app.app_context():
            techcorp = CompanyProfile.query.filter_by(name='TechCorp Inovações S.A.').first()
            target_id = techcorp.user_id

        res = self.client.post('/mensagens/enviar', data={
            'receiver_id': target_id,
            'content': 'Olá, gostaria de tirar uma dúvida sobre a vaga de engenheiro de software!'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_navbar_links_by_role(self):
        """Testa se o cabeçalho exibe apenas o link de perfil correspondente ao tipo de usuário"""
        # Sem login: não exibe nem Perfil do Aluno nem Perfil da Empresa
        res = self.client.get('/vagas')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn(b'Perfil do Aluno', res.data)
        self.assertNotIn(b'Perfil da Empresa', res.data)

        # Login como aluno: exibe Perfil do Aluno, oculta Perfil da Empresa
        self.client.post('/login', data={
            'login_type': 'aluno',
            'identifier': '234.567.890-92',
            'password': 'senai123'
        })
        res = self.client.get('/vagas')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Perfil do Aluno', res.data)
        self.assertNotIn(b'Perfil da Empresa', res.data)
        self.client.get('/logout')

        # Login como empresa: exibe Perfil da Empresa, oculta Perfil do Aluno
        self.client.post('/login', data={
            'login_type': 'empresa',
            'cnpj': '11.222.333/0001-81',
            'access_code': 'TECH-2024'
        })
        res = self.client.get('/vagas')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Perfil da Empresa', res.data)
        self.assertNotIn(b'Perfil do Aluno', res.data)
        self.client.get('/logout')

        # Login como admin: oculta ambos e exibe Painel Admin
        self.client.post('/login', data={
            'login_type': 'admin',
            'email': 'admin@senai.br',
            'password': 'admin123'
        })
        res = self.client.get('/vagas')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Painel Admin', res.data)
        self.assertNotIn(b'Perfil do Aluno', res.data)
        self.assertNotIn(b'Perfil da Empresa', res.data)

if __name__ == '__main__':
    unittest.main()
