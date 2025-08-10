
from datetime import date
from flask import current_app
from models import Document, Employee, Company
from notifications import send_email, send_whatsapp

def _company_contacts(comp: Company):
    return (comp.alert_email or '').strip(), (comp.alert_whatsapp or '').strip()

def build_summary():
    hoje = date.today()
    days_list = current_app.config.get('ALERT_DAYS', [0,7,30])
    result = {}  # comp.id -> days -> {'docs':[], 'asos':[]}
    for comp in Company.query.all():
        result[comp.id] = {d:{'docs':[], 'asos':[]} for d in days_list}
    for d in Document.query.all():
        if not d.data_vencimento or not d.company: continue
        dd = (d.data_vencimento - hoje).days
        if dd in result.get(d.company.id, {}):
            result[d.company.id][dd]['docs'].append(d)
    for e in Employee.query.all():
        if not e.company or not e.aso_validade: continue
        dd = (e.aso_validade - hoje).days
        if dd in result.get(e.company.id, {}):
            result[e.company.id][dd]['asos'].append(e)
    return result

def send_alerts():
    data = build_summary()
    hoje = date.today().strftime('%d/%m/%Y')
    for comp_id, byday in data.items():
        comp = Company.query.get(comp_id)
        emails, whats = _company_contacts(comp)
        for day, bucket in byday.items():
            if not bucket['docs'] and not bucket['asos']: continue
            label = 'hoje' if day==0 else f'em {day} dia(s)'
            lines = [f'Empresa: {comp.razao_social}', f'Relatório gerado em {hoje}', f'Itens com vencimento {label}:', '']
            if bucket['docs']:
                lines.append('Documentos:')
                for d in bucket['docs']:
                    lines.append(f' - {d.tipo.nome} | {d.descricao or ""} | Venc: {d.data_vencimento.isoformat()} (#{d.id})')
            if bucket['asos']:
                lines.append('')
                lines.append('ASO de colaboradores:')
                for e in bucket['asos']:
                    lines.append(f' - {e.nome} | Validade: {e.aso_validade.isoformat()} (#{e.id})')
            body = '\n'.join(lines)
            subject = f'[Transer] Alertas {label} - {comp.razao_social}'
            if emails: send_email(emails, subject, body)
            if whats: send_whatsapp(whats, subject + '\n' + body)
