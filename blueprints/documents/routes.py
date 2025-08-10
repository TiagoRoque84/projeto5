
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app, abort
from flask_login import login_required
from extensions import db
from models import Document, DocumentType, Company
from forms import DocumentForm, doctype_choices, company_choices, DocumentTypeForm
from utils import save_file, admin_required
from audit import log_create, log_update, log_delete
from datetime import date, datetime as _dt
import io, os

documents_bp = Blueprint("documents", __name__, template_folder='../../templates/documents')

@documents_bp.route("/")
@login_required
def list():
    company_id = request.args.get("company_id")
    tipo_id = request.args.get("tipo_id")
    status = request.args.get("status", "")
    q = request.args.get("q","").strip()
    de = request.args.get("venc_de")
    ate = request.args.get("venc_ate")

    query = Document.query
    if company_id: query = query.filter(Document.company_id == int(company_id))
    if tipo_id: query = query.filter(Document.tipo_id == int(tipo_id))
    if q:
        like = f"%{q}%"
        query = query.filter((Document.descricao.ilike(like)) | (Document.numero.ilike(like)) | (Document.orgao_emissor.ilike(like)) | (Document.responsavel.ilike(like)))

    docs = query.order_by(Document.data_vencimento.asc()).all()
    hoje = date.today()
    if status:
        tmp = []
        for d in docs:
            st = d.status
            if status == "vencido" and st == "Vencido": tmp.append(d)
            elif status == "a_vencer" and st == "A vencer": tmp.append(d)
            elif status == "vigente" and st == "Vigente": tmp.append(d)
        docs = tmp

    def parse_date(s):
        try: return _dt.strptime(s, "%Y-%m-%d").date()
        except: return None
    d1, d2 = parse_date(de), parse_date(ate)
    if d1: docs = [d for d in docs if d.data_vencimento and d.data_vencimento >= d1]
    if d2: docs = [d for d in docs if d.data_vencimento and d.data_vencimento <= d2]

    companies = Company.query.order_by(Company.razao_social).all()
    tipos = DocumentType.query.order_by(DocumentType.nome).all()
    return render_template("documents/list.html", docs=docs, companies=companies, tipos=tipos,
                           company_id=company_id, tipo_id=tipo_id, status=status, q=q, venc_de=de, venc_ate=ate)

@documents_bp.route("/novo", methods=["GET","POST"])
@login_required
def new():
    form = DocumentForm()
    form.tipo_id.choices = doctype_choices()
    form.company_id.choices = company_choices()
    if form.validate_on_submit():
        if form.data_expedicao.data and form.data_vencimento.data and form.data_vencimento.data < form.data_expedicao.data:
            flash('Data de vencimento não pode ser anterior à data de expedição.', 'warning')
            return render_template('documents/form.html', form=form)
        d = Document(
            tipo_id=int(form.tipo_id.data),
            company_id=int(form.company_id.data),
            descricao=form.descricao.data,
            numero=form.numero.data,
            data_expedicao=form.data_expedicao.data,
            data_vencimento=form.data_vencimento.data,
            orgao_emissor=form.orgao_emissor.data,
            responsavel=form.responsavel.data,
        )
        path = save_file(form.arquivo.data, "documents")
        if path: d.arquivo_path = path
        db.session.add(d); db.session.commit()
        log_create('Document', d.id, {'numero': d.numero, 'empresa': d.company_id, 'tipo': d.tipo_id}); db.session.commit()
        flash("Documento cadastrado.", "success")
        return redirect(url_for("documents.list"))
    return render_template("documents/form.html", form=form)

@documents_bp.route("/<int:doc_id>/editar", methods=["GET","POST"])
@login_required
def edit(doc_id):
    d = Document.query.get_or_404(doc_id)
    form = DocumentForm(obj=d)
    form.tipo_id.choices = doctype_choices()
    form.company_id.choices = company_choices()
    if form.validate_on_submit():
        before={'numero': d.numero, 'empresa': d.company_id, 'tipo': d.tipo_id, 'venc': d.data_vencimento.isoformat() if d.data_vencimento else None}
        if form.data_expedicao.data and form.data_vencimento.data and form.data_vencimento.data < form.data_expedicao.data:
            flash('Data de vencimento não pode ser anterior à data de expedição.', 'warning')
            return render_template('documents/form.html', form=form, doc=d)
        d.tipo_id = int(form.tipo_id.data); d.company_id = int(form.company_id.data)
        d.descricao = form.descricao.data; d.numero = form.numero.data
        d.data_expedicao = form.data_expedicao.data; d.data_vencimento = form.data_vencimento.data
        d.orgao_emissor = form.orgao_emissor.data; d.responsavel = form.responsavel.data
        path = save_file(form.arquivo.data, "documents")
        if path: d.arquivo_path = path
        db.session.commit()
        after={'numero': d.numero, 'empresa': d.company_id, 'tipo': d.tipo_id, 'venc': d.data_vencimento.isoformat() if d.data_vencimento else None}
        log_update('Document', d.id, before, after); db.session.commit()
        flash("Documento atualizado.", "success")
        return redirect(url_for("documents.list"))
    return render_template("documents/form.html", form=form, doc=d)

@documents_bp.route("/<int:doc_id>/excluir", methods=["POST"])
@login_required
@admin_required
def delete(doc_id):
    d = Document.query.get_or_404(doc_id)
    snap={'id': d.id, 'numero': d.numero, 'empresa': d.company_id}
    db.session.delete(d); log_delete('Document', d.id, snap); db.session.commit()
    flash("Documento excluído.", "info")
    return redirect(url_for("documents.list"))

@documents_bp.route("/tipos", methods=["GET","POST"])
@login_required
def types():
    form = DocumentTypeForm()
    if form.validate_on_submit():
        if not DocumentType.query.filter_by(nome=form.nome.data.strip()).first():
            dt = DocumentType(nome=form.nome.data.strip(), descricao=form.descricao.data)
            db.session.add(dt); db.session.commit()
            flash("Tipo de documento adicionado.", "success")
        else:
            flash("Tipo já existe.", "warning")
    tipos = DocumentType.query.order_by(DocumentType.nome).all()
    return render_template("documents/types.html", tipos=tipos, form=form)

@documents_bp.route("/tipos/<int:type_id>/editar", methods=["GET","POST"])
@login_required
def types_edit(type_id):
    t = DocumentType.query.get_or_404(type_id)
    form = DocumentTypeForm(obj=t)
    if form.validate_on_submit():
        form.populate_obj(t); db.session.commit()
        flash("Tipo de documento atualizado.", "success")
        return redirect(url_for("documents.types"))
    tipos = DocumentType.query.order_by(DocumentType.nome).all()
    return render_template("documents/types.html", tipos=tipos, form=form, edit_id=type_id)

@documents_bp.route("/arquivo/<int:doc_id>")
@login_required
def arquivo(doc_id):
    d = Document.query.get_or_404(doc_id)
    if not d.arquivo_path: abort(404)
    abs_path = os.path.join(current_app.root_path, d.arquivo_path.replace('..','').lstrip('/'))
    if not os.path.exists(abs_path): abort(404)
    return send_file(abs_path, as_attachment=False)

@documents_bp.route("/exportar.xlsx")
@login_required
def export_xlsx():
    docs = Document.query.all()
    rows = []
    for d in docs:
        rows.append({
            "ID": d.id,
            "Empresa": d.company.razao_social if d.company else "",
            "Tipo": d.tipo.nome if d.tipo else "",
            "Descrição": d.descricao or "",
            "Número": d.numero or "",
            "Expedição": d.data_expedicao.isoformat() if d.data_expedicao else "",
            "Vencimento": d.data_vencimento.isoformat() if d.data_vencimento else "",
            "Dias": d.days_to_due() if d.data_vencimento else "",
            "Status": d.status
        })
    import pandas as pd, io
    bio = io.BytesIO()
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Documentos")
    bio.seek(0)
    return send_file(bio, as_attachment=True, download_name="documentos.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
