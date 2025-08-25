from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def engineer_required(f):
    """Decorator to require engineer role (admin or engineer)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_engineer():
            flash('Acesso negado. Apenas engenheiros podem acessar esta funcionalidade.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def can_create_projects_required(f):
    """Decorator to check if user can create projects"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_create_projects():
            flash('Acesso negado. Você não tem permissão para criar projetos.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def can_perform_calculations_required(f):
    """Decorator to check if user can perform calculations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_perform_calculations():
            flash('Acesso negado. Apenas engenheiros podem realizar cálculos.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """Decorator to check if user account is active"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            flash('Conta desativada. Entre em contato com o suporte.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function