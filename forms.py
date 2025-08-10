
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, FileField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from models import Company, Function, DocumentType

class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

class UserForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Perfil", choices=[("admin","Administrador"),("user","Usuário comum")])
    submit = SubmitField("Salvar")

class CompanyForm(FlaskForm):
    razao_social = StringField("Razão Social", validators=[DataRequired()])
    nome_fantasia = StringField("Nome Fantasia")
    cnpj = StringField("CNPJ", validators=[DataRequired()])
    inscricao_estadual = StringField("Inscrição Estadual")
    cep = StringField("CEP")
    logradouro = StringField("Logradouro")
    numero = StringField("Número")
    complemento = StringField("Complemento")
    bairro = StringField("Bairro")
    cidade = StringField("Cidade")
    uf = StringField("UF")
    ativa = BooleanField("Ativa", default=True)
    alert_email = StringField("E-mails para alertas (separados por ;)")
    alert_whatsapp = StringField("WhatsApp(s) para alertas (separados por ;)")
    submit = SubmitField("Salvar")

class FunctionForm(FlaskForm):
    nome = StringField("Nome da Função", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    cbo = StringField("CBO", validators=[Optional()])
    submit = SubmitField("Salvar")

class DocumentTypeForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    submit = SubmitField("Salvar")

def company_choices():
    return [(str(c.id), c.razao_social) for c in Company.query.order_by(Company.razao_social).all()]
def function_choices():
    return [(str(f.id), f.nome) for f in Function.query.order_by(Function.nome).all()]
def doctype_choices():
    return [(str(dt.id), dt.nome) for dt in DocumentType.query.order_by(DocumentType.nome).all()]

class DocumentForm(FlaskForm):
    tipo_id = SelectField("Tipo", choices=[], validators=[DataRequired()])
    company_id = SelectField("Empresa", choices=[], validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[Optional()])
    numero = StringField("Número", validators=[Optional()])
    data_expedicao = DateField("Data de Expedição", validators=[Optional()])
    data_vencimento = DateField("Data de Vencimento", validators=[Optional()])
    orgao_emissor = StringField("Órgão Emissor", validators=[Optional()])
    responsavel = StringField("Responsável", validators=[Optional()])
    arquivo = FileField("Arquivo (PDF/Imagem)", validators=[Optional()])
    submit = SubmitField("Salvar")

class EmployeeForm(FlaskForm):
    company_id = SelectField("Empresa", choices=[], validators=[DataRequired()])
    funcao_id = SelectField("Função", choices=[], validators=[Optional()])
    ativo = BooleanField("Ativo", default=True)
    nome = StringField("Nome completo", validators=[DataRequired()])
    data_nascimento = DateField("Data de nascimento", validators=[Optional()])
    genero = SelectField("Gênero", choices=[("",""),("M","Masculino"),("F","Feminino"),("O","Outro")], validators=[Optional()])
    estado_civil = SelectField("Estado civil", choices=[("",""),("Solteiro(a)","Solteiro(a)"),("Casado(a)","Casado(a)"),("Divorciado(a)","Divorciado(a)"),("Viúvo(a)","Viúvo(a)"),("União Estável","União Estável")], validators=[Optional()])
    nome_pai = StringField("Nome do pai", validators=[Optional()])
    nome_mae = StringField("Nome da mãe", validators=[Optional()])
    data_admissao = DateField("Data de admissão", validators=[Optional()])
    salario = StringField("Salário", validators=[Optional()])
    jornada = StringField("Jornada", validators=[Optional()])
    cpf = StringField("CPF", validators=[Optional()])
    rg = StringField("RG", validators=[Optional()])
    cnh = StringField("CNH", validators=[Optional()])
    titulo_eleitor = StringField("Título de eleitor", validators=[Optional()])
    reservista = StringField("Reservista", validators=[Optional()])
    pis_pasep = StringField("PIS/PASEP", validators=[Optional()])
    ctps = StringField("CTPS", validators=[Optional()])
    cep = StringField("CEP", validators=[Optional()])
    logradouro = StringField("Logradouro", validators=[Optional()])
    numero = StringField("Número", validators=[Optional()])
    complemento = StringField("Complemento", validators=[Optional()])
    bairro = StringField("Bairro", validators=[Optional()])
    cidade = StringField("Cidade", validators=[Optional()])
    uf = StringField("UF", validators=[Optional()])
    fone = StringField("Telefone", validators=[Optional()])
    celular = StringField("Celular", validators=[Optional()])
    email = StringField("E-mail", validators=[Optional()])
    banco = StringField("Banco", validators=[Optional()])
    agencia = StringField("Agência", validators=[Optional()])
    conta = StringField("Conta", validators=[Optional()])
    tipo_conta = SelectField("Tipo de conta", choices=[("",""),("C/C","C/C"),("Salário","Salário"),("Poupança","Poupança")], validators=[Optional()])
    pix_tipo = SelectField("Tipo de PIX", choices=[("",""),("CPF","CPF"),("CNPJ","CNPJ"),("Celular","Celular"),("E-mail","E-mail"),("Chave Aleatória","Chave Aleatória")], validators=[Optional()])
    pix_chave = StringField("Chave PIX", validators=[Optional()])
    foto = FileField("Foto 3x4", validators=[Optional()])
    assinatura = FileField("Assinatura digital", validators=[Optional()])
    aso_data = DateField("Data do ASO", validators=[Optional()])
    aso_tipo = SelectField("Tipo de ASO", choices=[("",""),("admissional","Admissional"),("periodico","Periódico"),("demissional","Demissional")], validators=[Optional()])
    aso_arquivo = FileField("Arquivo do ASO", validators=[Optional()])
    aso_validade = DateField("Validade do ASO", validators=[Optional()])
    cnh_validade = DateField("Validade da CNH", validators=[Optional()])
    exame_toxico_validade = DateField("Validade do exame toxicológico", validators=[Optional()])
    submit = SubmitField("Salvar")
