
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db
from models import Company
from forms import CompanyForm
from audit import log_create, log_update, log_delete

companies_bp = Blueprint("companies", __name__, template_folder='../../templates/companies')

@companies_bp.route("/")
@login_required
def list():
    q = request.args.get("q","")
    query = Company.query
    if q:
        like = f"%{q}%"
        query = query.filter((Company.razao_social.ilike(like)) | (Company.nome_fantasia.ilike(like)) | (Company.cnpj.ilike(like)))
    companies = query.order_by(Company.razao_social).all()
    return render_template("companies/list.html", companies=companies, q=q)

@companies_bp.route("/novo", methods=["GET","POST"])
@login_required
def new():
    form = CompanyForm()
    if form.validate_on_submit():
        c = Company(
            razao_social=form.razao_social.data,
            nome_fantasia=form.nome_fantasia.data,
            cnpj=form.cnpj.data,
            inscricao_estadual=form.inscricao_estadual.data,
            cep=form.cep.data, logradouro=form.logradouro.data, numero=form.numero.data,
            complemento=form.complemento.data, bairro=form.bairro.data, cidade=form.cidade.data, uf=form.uf.data,
            ativa=form.ativa.data, alert_email=form.alert_email.data, alert_whatsapp=form.alert_whatsapp.data,
        )
        db.session.add(c); db.session.commit()
        log_create('Company', c.id, {'cnpj': c.cnpj, 'razao_social': c.razao_social}); db.session.commit()
        flash("Empresa cadastrada.", "success")
        return redirect(url_for("companies.list"))
    return render_template("companies/form.html", form=form)

@companies_bp.route("/<int:company_id>/editar", methods=["GET","POST"])
@login_required
def edit(company_id):
    c = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=c)
    if form.validate_on_submit():
        before={'razao_social': c.razao_social, 'nome_fantasia': c.nome_fantasia, 'cnpj': c.cnpj, 'ativa': c.ativa}
        form.populate_obj(c); db.session.commit()
        after={'razao_social': c.razao_social, 'nome_fantasia': c.nome_fantasia, 'cnpj': c.cnpj, 'ativa': c.ativa}
        log_update('Company', c.id, before, after); db.session.commit()
        flash("Empresa atualizada.", "success")
        return redirect(url_for("companies.list"))
    return render_template("companies/form.html", form=form, company=c)

@companies_bp.route("/<int:company_id>/excluir", methods=["POST"])
@login_required
def delete(company_id):
    c = Company.query.get_or_404(company_id)
    snap={'id': c.id, 'cnpj': c.cnpj, 'razao_social': c.razao_social}
    db.session.delete(c); log_delete('Company', c.id, snap); db.session.commit()
    flash("Empresa excluída.", "info")
    return redirect(url_for("companies.list"))
