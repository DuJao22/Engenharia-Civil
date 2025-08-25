from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    plan = db.Column(db.String(20), default='trial')
    plan_expires = db.Column(db.DateTime)
    trial_expires = db.Column(db.DateTime)
    trial_used = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='engineer')  # admin, engineer, client
    company = db.Column(db.String(200))
    crea_number = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)  # type: ignore
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    calculations = db.relationship('Calculation', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_access_to_module(self, module):
        """Check if user has access to a specific module based on their plan"""
        free_modules = ['structural_basic', 'hydraulics_basic']
        
        # Durante o período de trial, usuário tem acesso completo
        if self.is_in_trial():
            return True
        
        # Se o plano é free, só módulos básicos
        if self.plan == 'free':
            return module in free_modules
        
        # Se o plano é pro e não expirou, acesso completo
        elif self.plan == 'pro':
            if self.plan_expires and self.plan_expires > datetime.utcnow():
                return True
        
        # Caso contrário, só módulos básicos
        return module in free_modules
    
    def is_admin(self):
        """Check if user is an administrator"""
        return self.role == 'admin'
    
    def is_engineer(self):
        """Check if user is an engineer"""
        return self.role in ['admin', 'engineer']
    
    def is_client(self):
        """Check if user is a client"""
        return self.role == 'client'
    
    def can_access_admin_area(self):
        """Check if user can access admin area"""
        return self.is_admin()
    
    def can_create_projects(self):
        """Check if user can create projects"""
        return self.role in ['admin', 'engineer']
    
    def can_perform_calculations(self):
        """Check if user can perform engineering calculations"""
        return self.role in ['admin', 'engineer']
    
    def can_access_reports(self):
        """Check if user can access detailed reports"""
        return self.role in ['admin', 'engineer']
    
    def is_in_trial(self):
        """Check if user is currently in trial period"""
        if self.plan == 'trial' and self.trial_expires:
            return datetime.utcnow() < self.trial_expires
        return False
    
    def get_trial_days_remaining(self):
        """Get number of trial days remaining"""
        if self.is_in_trial() and self.trial_expires:
            remaining = self.trial_expires - datetime.utcnow()
            return max(0, remaining.days)
        return 0
    
    def start_trial(self):
        """Start 7-day trial period"""
        if not self.trial_used:
            self.plan = 'trial'
            self.trial_expires = datetime.utcnow() + timedelta(days=7)
            self.trial_used = True
    
    def upgrade_to_pro(self, duration_months=1):
        """Upgrade user to pro plan"""
        self.plan = 'pro'
        self.plan_expires = datetime.utcnow() + timedelta(days=30 * duration_months)
    
    def downgrade_to_free(self):
        """Downgrade user to free plan"""
        self.plan = 'free'
        self.plan_expires = None
    
    def get_plan_status(self):
        """Get current plan status for display"""
        if self.is_in_trial():
            days_remaining = self.get_trial_days_remaining()
            return {
                'type': 'trial',
                'name': 'Teste Grátis',
                'days_remaining': days_remaining,
                'expires': self.trial_expires,
                'has_full_access': True
            }
        elif self.plan == 'pro' and self.plan_expires and self.plan_expires > datetime.utcnow():
            remaining = self.plan_expires - datetime.utcnow()
            return {
                'type': 'pro',
                'name': 'Profissional',
                'days_remaining': remaining.days,
                'expires': self.plan_expires,
                'has_full_access': True
            }
        else:
            return {
                'type': 'free',
                'name': 'Gratuito',
                'days_remaining': None,
                'expires': None,
                'has_full_access': False
            }
    
    def can_view_project(self, project):
        """Check if user can view a specific project"""
        if self.is_admin():
            return True
        if self.is_engineer():
            return project.user_id == self.id
        if self.is_client():
            # Client can view projects where they are the client
            return project.client_email == self.email
        return False

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mp_payment_id = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='BRL')
    method = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    module = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    inputs = db.Column(db.Text, nullable=False)  # JSON string
    results = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(120))
    client_phone = db.Column(db.String(20))
    address = db.Column(db.Text, nullable=False)
    technical_responsible = db.Column(db.String(200), nullable=False)
    crea_number = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_budget = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='planejamento')  # planejamento, execucao, concluido, cancelado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calculations = db.relationship('Calculation', backref='project', lazy=True)
    budgets = db.relationship('Budget', backref='project', lazy=True)
    schedules = db.relationship('ProjectSchedule', backref='project', lazy=True)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(10), default='1.0')
    description = db.Column(db.Text)
    total_cost = db.Column(db.Float, default=0.0)
    total_materials = db.Column(db.Float, default=0.0)
    total_labor = db.Column(db.Float, default=0.0)
    total_equipment = db.Column(db.Float, default=0.0)
    profit_margin = db.Column(db.Float, default=10.0)  # %
    status = db.Column(db.String(20), default='rascunho')  # rascunho, revisao, aprovado
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(200))
    
    # Relationships
    items = db.relationship('BudgetItem', backref='budget', lazy=True, cascade='all, delete-orphan')

class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    composition_id = db.Column(db.Integer, db.ForeignKey('cost_composition.id'), nullable=True)
    description = db.Column(db.String(500), nullable=False)
    unit = db.Column(db.String(10), nullable=False)  # m², m³, kg, un, etc.
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # estrutura, acabamento, instalacoes, etc.
    notes = db.Column(db.Text)

class CostComposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sinapi_code = db.Column(db.String(20), unique=True)
    tcpo_code = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(500), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    productivity = db.Column(db.Float)  # horas/unidade
    category = db.Column(db.String(100))
    materials_cost = db.Column(db.Float, default=0.0)
    labor_cost = db.Column(db.Float, default=0.0)
    equipment_cost = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    materials = db.relationship('CompositionMaterial', backref='composition', lazy=True)
    budget_items = db.relationship('BudgetItem', backref='composition', lazy=True)

class CompositionMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('cost_composition.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    waste_factor = db.Column(db.Float, default=1.05)  # 5% desperdício padrão

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # cimento, areia, brita, aco, etc.
    unit = db.Column(db.String(10), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    compositions = db.relationship('CompositionMaterial', backref='material', lazy=True)

class ProjectSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(10), default='1.0')
    total_duration = db.Column(db.Integer)  # dias
    critical_path = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('ScheduleActivity', backref='schedule', lazy=True, cascade='all, delete-orphan')

class ScheduleActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('project_schedule.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # dias
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    predecessors = db.Column(db.Text)  # JSON array de IDs
    progress = db.Column(db.Float, default=0.0)  # 0-100%
    responsible = db.Column(db.String(200))
    cost = db.Column(db.Float, default=0.0)
    is_critical = db.Column(db.Boolean, default=False)
