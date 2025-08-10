
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from utils import admin_required
from alerts import send_alerts
from models import AuditLog

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')

@admin_bp.route('/alertas/disparar')
@login_required
@admin_required
def trigger_alerts():
    send_alerts()
    flash('Alertas disparados.', 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/auditoria')
@login_required
@admin_required
def audit():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template('admin/audit.html', logs=logs)
