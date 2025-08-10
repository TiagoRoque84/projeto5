
from flask import Blueprint, render_template
from flask_login import login_required
from models import Document, Employee
from datetime import date, timedelta

main_bp = Blueprint("main", __name__, template_folder='../../templates')

@main_bp.route("/")
@login_required
def index():
    hoje = date.today()
    em_30 = hoje + timedelta(days=30)
    docs_vencidos = Document.query.filter(Document.data_vencimento < hoje).count()
    docs_a_vencer = Document.query.filter(Document.data_vencimento >= hoje, Document.data_vencimento <= em_30).count()
    aso_vencidos = Employee.query.filter(Employee.aso_validade < hoje).count()
    aso_a_vencer = Employee.query.filter(Employee.aso_validade >= hoje, Employee.aso_validade <= em_30).count()
    num_func = Employee.query.count()
    num_func_ativos = Employee.query.filter_by(ativo=True).count()
    num_func_inativos = Employee.query.filter_by(ativo=False).count()
    return render_template("index.html", docs_vencidos=docs_vencidos, docs_a_vencer=docs_a_vencer, aso_vencidos=aso_vencidos, aso_a_vencer=aso_a_vencer, num_func=num_func, num_func_ativos=num_func_ativos, num_func_inativos=num_func_inativos)
