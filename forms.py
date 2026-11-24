import re

def clean_digits(value):
    if not value:
        return ''
    return re.sub(r'\D', '', str(value))

def validate_cpf(cpf_str):
    cpf = clean_digits(cpf_str)
    if len(cpf) != 11:
        return False
    # CPFs com todos dígitos iguais são inválidos
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto in (10, 11) else resto
    if d1 != int(cpf[9]):
        return False

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto in (10, 11) else resto
    if d2 != int(cpf[10]):
        return False

    return True

def validate_cnpj(cnpj_str):
    cnpj = clean_digits(cnpj_str)
    if len(cnpj) != 14:
        return False
    # CNPJs com todos dígitos iguais são inválidos
    if cnpj == cnpj[0] * 14:
        return False

    # Primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto1 = soma1 % 11
    d1 = 0 if resto1 < 2 else 11 - resto1
    if d1 != int(cnpj[12]):
        return False

    # Segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else 11 - resto2
    if d2 != int(cnpj[13]):
        return False

    return True

def format_cpf(cpf_str):
    c = clean_digits(cpf_str)
    if len(c) == 11:
        return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"
    return cpf_str

def format_cnpj(cnpj_str):
    c = clean_digits(cnpj_str)
    if len(c) == 14:
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
    return cnpj_str

def validate_email_format(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))
