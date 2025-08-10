
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from extensions import db
from models import Employee, Function, Company
from forms import EmployeeForm, FunctionForm, company_choices, function_choices
from utils import save_file, admin_required
from audit import log_create, log_update, log_delete
from datetime import date, datetime as _dt
import io

hr_bp = Blueprint("rh", __name__, template_folder='../../templates/hr')

@hr_bp.route("/funcoes", methods=["GET","POST"])
@login_required
def functions():
    form = FunctionForm()
    if form.validate_on_submit():
        if not Function.query.filter_by(nome=form.nome.data.strip()).first():
            f = Function(nome=form.nome.data.strip(), descricao=form.descricao.data, cbo=form.cbo.data)
            db.session.add(f); db.session.commit()
            flash("Função cadastrada.", "success")
        else:
            flash("Função já existe.", "warning")
    funcoes = Function.query.order_by(Function.nome).all()
    return render_template("hr/functions.html", form=form, funcoes=funcoes)

@hr_bp.route("/funcoes/<int:func_id>/editar", methods=["GET","POST"])
@login_required
def functions_edit(func_id):
    f = Function.query.get_or_404(func_id)
    form = FunctionForm(obj=f)
    if form.validate_on_submit():
        form.populate_obj(f); db.session.commit()
        flash("Função atualizada.", "success")
        return redirect(url_for("rh.functions"))
    return render_template("hr/functions.html", form=form, funcoes=Function.query.order_by(Function.nome).all(), edit_id=func_id)

@hr_bp.route("/colaboradores")
@login_required
def employees_list():
    q = request.args.get("q","").strip()
    company_id = request.args.get("company_id")
    funcao_id = request.args.get("funcao_id")
    status = request.args.get("aso","")
    cnh = request.args.get("cnh","")
    de = request.args.get("aso_de"); ate = request.args.get("aso_ate")

    query = Employee.query
    if company_id: query = query.filter(Employee.company_id == int(company_id))
    if funcao_id: query = query.filter(Employee.funcao_id == int(funcao_id))
    if q:
        like = f"%{q}%"
        query = query.filter((Employee.nome.ilike(like)) | (Employee.cpf.ilike(like)))

    employees = query.order_by(Employee.nome).all()
    hoje = date.today()
    if status:
        if status == "vencido":
            employees = [e for e in employees if e.aso_validade and e.aso_validade < hoje]
        elif status == "a_vencer_30":
            employees = [e for e in employees if e.aso_validade and 0 <= (e.aso_validade - hoje).days <= 30]
        elif status == "a_vencer_60":
            employees = [e for e in employees if e.aso_validade and 31 <= (e.aso_validade - hoje).days <= 60]
        elif status == "vigente":
            employees = [e for e in employees if e.aso_validade and (e.aso_validade - hoje).days > 60]
        elif status == "sem":
            employees = [e for e in employees if not e.aso_validade]

    def parse_date(s):
        try: return _dt.strptime(s, "%Y-%m-%d").date()
        except: return None
    d1, d2 = parse_date(de), parse_date(ate)
    if d1: employees = [e for e in employees if e.aso_validade and e.aso_validade >= d1]
    if d2: employees = [e for e in employees if e.aso_validade and e.aso_validade <= d2]

    if cnh:
        def cnh_status(e):
            if not e.cnh_validade: return "sem"
            if e.cnh_validade < hoje: return "vencida"
            if (e.cnh_validade - hoje).days <= 30: return "a_vencer"
            return "vigente"
        if cnh == "sem": employees = [e for e in employees if not e.cnh_validade]
        else: employees = [e for e in employees if cnh_status(e) == cnh]

    companies = Company.query.order_by(Company.razao_social).all()
    funcoes = Function.query.order_by(Function.nome).all()
    return render_template("hr/employees_list.html", employees=employees, companies=companies, funcoes=funcoes,
                           company_id=company_id, funcao_id=funcao_id, status=status, cnh=cnh, q=q, aso_de=de, aso_ate=ate)

@hr_bp.route("/colaboradores/novo", methods=["GET","POST"])
@login_required
def employees_new():
    form = EmployeeForm()
    form.company_id.choices = company_choices()
    form.funcao_id.choices = [("", "")] + function_choices()
    if form.validate_on_submit():
        def _parse_brl(s):
            s = (s or '').strip().replace('.', '').replace(',', '.')
            try: return float(s)
            except: return None
        e = Employee(
            company_id=int(form.company_id.data), funcao_id=int(form.funcao_id.data) if form.funcao_id.data else None,
            ativo=form.ativo.data, nome=form.nome.data, data_nascimento=form.data_nascimento.data, genero=form.genero.data,
            estado_civil=form.estado_civil.data, nome_pai=form.nome_pai.data, nome_mae=form.nome_mae.data,
            data_admissao=form.data_admissao.data, salario=_parse_brl(form.salario.data), jornada=form.jornada.data,
            cpf=form.cpf.data, rg=form.rg.data, cnh=form.cnh.data, titulo_eleitor=form.titulo_eleitor.data, reservista=form.reservista.data,
            pis_pasep=form.pis_pasep.data, ctps=form.ctps.data,
            cep=form.cep.data, logradouro=form.logradouro.data, numero=form.numero.data, complemento=form.complemento.data,
            bairro=form.bairro.data, cidade=form.cidade.data, uf=form.uf.data,
            fone=form.fone.data, celular=form.celular.data, email=form.email.data,
            banco=form.banco.data, agencia=form.agencia.data, conta=form.conta.data, tipo_conta=form.tipo_conta.data,
            pix_tipo=form.pix_tipo.data, pix_chave=form.pix_chave.data,
            aso_data=form.aso_data.data, aso_tipo=form.aso_tipo.data, aso_validade=form.aso_validade.data,
            cnh_validade=form.cnh_validade.data, exame_toxico_validade=form.exame_toxico_validade.data,
        )
        from utils import save_file
        foto = save_file(form.foto.data, "employees");  e.foto_path = foto or e.foto_path
        ass = save_file(form.assinatura.data, "employees"); e.assinatura_path = ass or e.assinatura_path
        aso = save_file(form.aso_arquivo.data, "employees"); e.aso_arquivo_path = aso or e.aso_arquivo_path
        db.session.add(e); db.session.commit()
        log_create('Employee', e.id, {'nome': e.nome, 'empresa': e.company_id}); db.session.commit()
        flash("Colaborador cadastrado.", "success")
        return redirect(url_for("rh.employees_list"))
    return render_template("hr/employee_form.html", form=form)

@hr_bp.route("/colaboradores/<int:emp_id>/editar", methods=["GET","POST"])
@login_required
def employees_edit(emp_id):
    e = Employee.query.get_or_404(emp_id)
    form = EmployeeForm(obj=e)
    form.company_id.choices = company_choices()
    form.funcao_id.choices = [("", "")] + function_choices()
    if form.validate_on_submit():
        before={'nome': e.nome, 'empresa': e.company_id, 'ativo': e.ativo}
        def _parse_brl(s):
            s = (s or '').strip().replace('.', '').replace(',', '.')
            try: return float(s)
            except: return None
        e.salario = _parse_brl(form.salario.data)
        form.populate_obj(e)
        from utils import save_file
        foto = save_file(form.foto.data, "employees");  e.foto_path = foto or e.foto_path
        ass = save_file(form.assinatura.data, "employees"); e.assinatura_path = ass or e.assinatura_path
        aso = save_file(form.aso_arquivo.data, "employees"); e.aso_arquivo_path = aso or e.aso_arquivo_path
        db.session.commit()
        after={'nome': e.nome, 'empresa': e.company_id, 'ativo': e.ativo}
        log_update('Employee', e.id, before, after); db.session.commit()
        flash("Colaborador atualizado.", "success")
        return redirect(url_for("rh.employees_list"))
    return render_template("hr/employee_form.html", form=form, employee=e)

@hr_bp.route("/colaboradores/<int:emp_id>/excluir", methods=["POST"])
@login_required
@admin_required
def employees_delete(emp_id):
    e = Employee.query.get_or_404(emp_id)
    snap={'id': e.id, 'nome': e.nome, 'empresa': e.company_id}
    db.session.delete(e); log_delete('Employee', e.id, snap); db.session.commit()
    flash("Colaborador excluído.", "info")
    return redirect(url_for("rh.employees_list"))

@hr_bp.route("/colaboradores/exportar.xlsx")
@login_required
def employees_export():
    emps = Employee.query.all()
    rows = []
    for e in emps:
        rows.append({
            "ID": e.id, "Empresa": e.company.razao_social if e.company else "", "Ativo": "Sim" if e.ativo else "Não",
            "Nome": e.nome, "Função": e.funcao.nome if e.funcao else "", "Nascimento": e.data_nascimento.isoformat() if e.data_nascimento else "",
            "Gênero": e.genero or "", "Estado civil": e.estado_civil or "", "Admissão": e.data_admissao.isoformat() if e.data_admissao else "",
            "Salário": e.salario if e.salario is not None else "", "Jornada": e.jornada or "", "CPF": e.cpf or "", "RG": e.rg or "",
            "CNH": e.cnh or "", "CNH Validade": e.cnh_validade.isoformat() if e.cnh_validade else "", "Título eleitor": e.titulo_eleitor or "",
            "Reservista": e.reservista or "", "PIS/PASEP": e.pis_pasep or "", "CTPS": e.ctps or "", "CEP": e.cep or "",
            "Logradouro": e.logradouro or "", "Número": e.numero or "", "Complemento": e.complemento or "", "Bairro": e.bairro or "",
            "Cidade": e.cidade or "", "UF": e.uf or "", "Telefone": e.fone or "", "Celular": e.celular or "", "E-mail": e.email or "",
            "Banco": e.banco or "", "Agência": e.agencia or "", "Conta": e.conta or "", "Tipo de conta": e.tipo_conta or "",
            "PIX tipo": e.pix_tipo or "", "PIX chave": e.pix_chave or "", "ASO tipo": e.aso_tipo or "", "ASO data": e.aso_data.isoformat() if e.aso_data else "",
            "ASO validade": e.aso_validade.isoformat() if e.aso_validade else "", "ASO status": e.aso_status, "Toxicológico validade": e.exame_toxico_validade.isoformat() if e.exame_toxico_validade else "",
        })
    import pandas as pd, io
    bio = io.BytesIO(); df = pd.DataFrame(rows)
    with pd.ExcelWriter(bio, engine="openpyxl") as writer: df.to_excel(writer, index=False, sheet_name="Colaboradores")
    bio.seek(0)
    return send_file(bio, as_attachment=True, download_name="colaboradores.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
