
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    active = db.Column(db.Boolean, default=True)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Company(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(150), nullable=False)
    nome_fantasia = db.Column(db.String(150))
    cnpj = db.Column(db.String(20), unique=True, nullable=False)
    inscricao_estadual = db.Column(db.String(30))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    ativa = db.Column(db.Boolean, default=True)
    alert_email = db.Column(db.String(200))
    alert_whatsapp = db.Column(db.String(50))
    documents = db.relationship("Document", backref="company", lazy=True)
    employees = db.relationship("Employee", backref="company", lazy=True)

class DocumentType(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    descricao = db.Column(db.String(255))

class Document(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_id = db.Column(db.Integer, db.ForeignKey("document_type.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    descricao = db.Column(db.String(255))
    numero = db.Column(db.String(120))
    data_expedicao = db.Column(db.Date)
    data_vencimento = db.Column(db.Date)
    orgao_emissor = db.Column(db.String(150))
    responsavel = db.Column(db.String(150))
    arquivo_path = db.Column(db.String(255))
    tipo = db.relationship("DocumentType")
    def days_to_due(self):
        if not self.data_vencimento: return None
        return (self.data_vencimento - date.today()).days
    @property
    def status(self):
        if self.data_vencimento:
            if self.data_vencimento < date.today(): return "Vencido"
            elif (self.data_vencimento - date.today()).days <= 30: return "A vencer"
        return "Vigente"

class Function(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    cbo = db.Column(db.String(20))

class Employee(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    funcao_id = db.Column(db.Integer, db.ForeignKey("function.id"))
    ativo = db.Column(db.Boolean, default=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    estado_civil = db.Column(db.String(50))
    nome_pai = db.Column(db.String(150))
    nome_mae = db.Column(db.String(150))
    data_admissao = db.Column(db.Date)
    salario = db.Column(db.Float)
    jornada = db.Column(db.String(100))
    cpf = db.Column(db.String(14))
    rg = db.Column(db.String(20))
    cnh = db.Column(db.String(20))
    titulo_eleitor = db.Column(db.String(20))
    reservista = db.Column(db.String(30))
    pis_pasep = db.Column(db.String(20))
    ctps = db.Column(db.String(30))
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    fone = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120))
    banco = db.Column(db.String(100))
    agencia = db.Column(db.String(20))
    conta = db.Column(db.String(20))
    tipo_conta = db.Column(db.String(20))
    pix_tipo = db.Column(db.String(20))
    pix_chave = db.Column(db.String(200))
    foto_path = db.Column(db.String(255))
    assinatura_path = db.Column(db.String(255))
    aso_data = db.Column(db.Date)
    aso_tipo = db.Column(db.String(30))
    aso_arquivo_path = db.Column(db.String(255))
    aso_validade = db.Column(db.Date)
    cnh_validade = db.Column(db.Date)
    exame_toxico_validade = db.Column(db.Date)
    funcao = db.relationship("Function")
    @property
    def aso_status(self):
        if self.aso_validade:
            if self.aso_validade < date.today(): return "ASO vencido"
            elif (self.aso_validade - date.today()).days <= 30: return "ASO a vencer"
            return "ASO vigente"
        return "Sem ASO"

class AuditLog(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    action = db.Column(db.String(20))
    user = db.Column(db.String(80))
    changes = db.Column(db.Text)
