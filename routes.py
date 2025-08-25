import json
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import (User, Calculation, Project, Budget, BudgetItem, 
                   CostComposition, Material, ProjectSchedule, ScheduleActivity)
from forms import (LoginForm, RegisterForm, BeamCalculationForm, ConcreteBeamForm, 
                   HydraulicsForm, FoundationForm, TopographyForm, ProjectForm,
                   BudgetForm, BudgetItemForm, MaterialForm, CostCompositionForm,
                   ScheduleActivityForm, EarthPressureForm, SettlementForm,
                   PavementCBRForm, EarthworkForm, TrafficESALForm, ConcreteVolumeForm,
                   SteelConsumptionForm, MortarForm, BrickConsumptionForm, WallLoadForm,
                   RationalMethodForm, ManningForm, DarcyWeisbachForm, TorsionShearForm,
                   EulerBucklingForm, ContinuousBeamForm, ConcentrationTimeForm, DetentionOutflowForm,
                   SteelTensionForm, SteelBeamDeflectionForm, PrecastElementForm, RibbedSlabForm,
                   VoltageDropForm, GasPipeLossForm, ProductivityForm, SCurveForm,
                   CarbonFootprintForm, ThermalLossForm,
                   LoadCombinationForm, ConcreteShearForm, PunchingShearForm, LateralTorsionalBucklingForm,
                   WoodConnectionForm, EccentricFootingForm, InfiniteSlopeForm, ElasticSettlementForm,
                   PileCapacityForm, SCSRunoffForm, KirpichTimeForm, ChannelEnergyForm, WaterHammerForm,
                   PumpSimilarityForm, ESALForm, TrafficGrowthForm, StoppingDistanceForm, LightingDesignForm,
                   ThermalTransmissionForm, ReverberationForm, GutterSizingForm, StairBlondelForm,
                   PrismoidalVolumeForm, NPVForm)
from auth_decorators import (admin_required, engineer_required, can_create_projects_required,
                           can_perform_calculations_required, active_user_required)
from calculations import (StructuralCalculations, ConcreteCalculations, 
                         HydraulicsCalculations, FoundationCalculations, 
                         TopographyCalculations, GeotechnicalCalculations,
                         PavementCalculations, QuantityCalculations, 
                         MasonryCalculations, SanitationCalculations,
                         AdvancedCalculations, AdvancedStructuralCalculations, HydrologyCalculations,
                         SteelStructuresCalculations, IndustrialConstructionCalculations,
                         BuildingInstallationsCalculations, ConstructionControlCalculations,
                         SustainabilityCalculations, AdvancedGeotechnicalCalculations,
                         AdvancedHydrologyCalculations, AdvancedPavementCalculations,
                         BuildingSystemsCalculations, EconomicCalculations)
from project_calculations import (BudgetCalculator, ScheduleCalculator,
                                ProductivityCalculator, ReportGenerator)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Este email já está cadastrado.', 'danger')
            return render_template('register.html', form=form)
        
        user = User(name=form.name.data, email=form.email.data)  # type: ignore
        user.set_password(form.password.data)
        user.start_trial()  # Inicia automaticamente o período de teste de 7 dias
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Você ganhou 7 dias de acesso completo grátis!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Migrar usuários existentes para trial se ainda não tiveram trial
    if current_user.plan == 'free' and not current_user.trial_used:
        current_user.start_trial()
        db.session.commit()
        flash('🎉 Parabéns! Você ganhou 7 dias de acesso completo ao sistema!', 'success')
    
    # Verificar se trial expirou e mudar para free
    if current_user.plan == 'trial' and not current_user.is_in_trial():
        current_user.downgrade_to_free()
        db.session.commit()
        flash('Seu período de teste expirou. Faça upgrade para continuar com acesso completo.', 'warning')
    
    # Cálculos recentes
    recent_calculations = Calculation.query.filter_by(user_id=current_user.id)\
                                         .order_by(Calculation.created_at.desc())\
                                         .limit(5).all()
    
    # Estatísticas de projetos
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Status do plano do usuário
    plan_status = current_user.get_plan_status()
    
    # Estatísticas de orçamentos
    total_budgets = 0
    total_budget_value = 0.0
    active_projects = 0
    completed_projects = 0
    
    for project in projects:
        if project.status == 'ativo':
            active_projects += 1
        elif project.status == 'concluido':
            completed_projects += 1
            
        budgets = Budget.query.filter_by(project_id=project.id).all()
        total_budgets += len(budgets)
        
        for budget in budgets:
            if budget.total_cost:
                total_budget_value += budget.total_cost
    
    # Estatísticas de cálculos
    total_calculations = Calculation.query.filter_by(user_id=current_user.id).count()
    
    # Cálculos por módulo para gráfico
    calculations_by_module = {}
    for calc in Calculation.query.filter_by(user_id=current_user.id).all():
        module = calc.module
        if module in calculations_by_module:
            calculations_by_module[module] += 1
        else:
            calculations_by_module[module] = 1
    
    # Projetos por status para gráfico
    projects_by_status = {
        'planejamento': 0,
        'ativo': 0,
        'pausado': 0,
        'concluido': 0
    }
    
    for project in projects:
        if project.status in projects_by_status:
            projects_by_status[project.status] += 1
    
    # Atividade mensal (últimos 6 meses)
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_activity = Calculation.query.filter_by(user_id=current_user.id)\
                                     .filter(Calculation.created_at >= six_months_ago)\
                                     .order_by(Calculation.created_at).all()
    
    # Agrupar por mês
    monthly_activity = {}
    for calc in recent_activity:
        month_key = calc.created_at.strftime('%Y-%m')
        if month_key in monthly_activity:
            monthly_activity[month_key] += 1
        else:
            monthly_activity[month_key] = 1
    
    dashboard_stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_budgets': total_budgets,
        'total_budget_value': total_budget_value,
        'total_calculations': total_calculations,
        'calculations_by_module': calculations_by_module,
        'projects_by_status': projects_by_status,
        'monthly_activity': monthly_activity
    }
    
    return render_template('dashboard.html', 
                         calculations=recent_calculations,
                         stats=dashboard_stats,
                         plan_status=plan_status)

@app.route('/structural', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def structural():
    if not current_user.has_access_to_module('structural_basic'):
        if current_user.get_plan_status()['type'] == 'free':
            flash('Este módulo está disponível apenas no período de teste ou plano Pro. Cadastre-se para ganhar 7 dias grátis!', 'warning')
        else:
            flash('Upgrade para o plano Pro para continuar acessando este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = BeamCalculationForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = StructuralCalculations.calculate_beam_moment(
                form.length.data, 
                form.load_value.data, 
                form.load_type.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'length': form.length.data,
                    'load_value': form.load_value.data,
                    'load_type': form.load_type.data,
                    'load_unit': form.load_unit.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('structural.html', form=form, result=result)

@app.route('/concrete', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def concrete():
    if not current_user.has_access_to_module('concrete'):
        if current_user.get_plan_status()['type'] == 'free':
            flash('Este módulo está disponível apenas no período de teste ou plano Pro. Cadastre-se para ganhar 7 dias grátis!', 'warning')
        else:
            flash('Upgrade para o plano Pro para continuar acessando este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ConcreteBeamForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = ConcreteCalculations.calculate_concrete_beam(
                form.width.data,
                form.height.data,
                form.moment.data,
                form.fck.data,
                form.fyk.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='concrete',
                name=form.name.data,
                inputs=json.dumps({
                    'width': form.width.data,
                    'height': form.height.data,
                    'moment': form.moment.data,
                    'fck': form.fck.data,
                    'fyk': form.fyk.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('concrete.html', form=form, result=result)

@app.route('/hydraulics', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def hydraulics():
    if not current_user.has_access_to_module('hydraulics_basic'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = HydraulicsForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = HydraulicsCalculations.calculate_pipe_flow(
                form.pipe_diameter.data,
                form.pipe_length.data,
                form.flow_rate.data,
                form.roughness.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='hydraulics',
                name=form.name.data,
                inputs=json.dumps({
                    'pipe_diameter': form.pipe_diameter.data,
                    'pipe_length': form.pipe_length.data,
                    'flow_rate': form.flow_rate.data,
                    'roughness': form.roughness.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('hydraulics.html', form=form, result=result)

@app.route('/foundations', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def foundations():
    if not current_user.has_access_to_module('foundations'):
        if current_user.get_plan_status()['type'] == 'free':
            flash('Este módulo está disponível apenas no período de teste ou plano Pro. Cadastre-se para ganhar 7 dias grátis!', 'warning')
        else:
            flash('Upgrade para o plano Pro para continuar acessando este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = FoundationForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = FoundationCalculations.calculate_bearing_capacity(
                form.width.data,
                form.cohesion.data,
                form.friction_angle.data,
                form.unit_weight.data,
                form.depth.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='foundations',
                name=form.name.data,
                inputs=json.dumps({
                    'width': form.width.data,
                    'cohesion': form.cohesion.data,
                    'friction_angle': form.friction_angle.data,
                    'unit_weight': form.unit_weight.data,
                    'depth': form.depth.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('foundations.html', form=form, result=result)

@app.route('/topography', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def topography():
    if not current_user.has_access_to_module('topography'):
        if current_user.get_plan_status()['type'] == 'free':
            flash('Este módulo está disponível apenas no período de teste ou plano Pro. Cadastre-se para ganhar 7 dias grátis!', 'warning')
        else:
            flash('Upgrade para o plano Pro para continuar acessando este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = TopographyForm()
    result = None
    
    if form.validate_on_submit():
        try:
            # Parse coordinates
            lines = (form.coordinates.data or "").strip().split('\n')
            coordinates = []
            for line in lines:
                if line.strip():
                    x, y = map(float, line.strip().split(','))
                    coordinates.append([x, y])
            
            result = TopographyCalculations.calculate_area_shoelace(coordinates)
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='topography',
                name=form.name.data,
                inputs=json.dumps({
                    'coordinates': coordinates
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except ValueError as e:
            flash('Formato de coordenadas inválido. Use: x,y por linha', 'danger')
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('topography.html', form=form, result=result)

@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    calculations = Calculation.query.filter_by(user_id=current_user.id)\
                                  .order_by(Calculation.created_at.desc())\
                                  .paginate(page=page, per_page=10, error_out=False)
    return render_template('history.html', calculations=calculations)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Project Management Routes
@app.route('/projects')
@login_required
def projects():
    """Lista todos os projetos do usuário"""
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('projects/index.html', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
@can_create_projects_required
def new_project():
    """Cria um novo projeto"""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(  # type: ignore
            user_id=current_user.id,
            name=form.name.data,
            client_name=form.client_name.data,
            client_email=form.client_email.data,
            client_phone=form.client_phone.data,
            address=form.address.data,
            technical_responsible=form.technical_responsible.data,
            crea_number=form.crea_number.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            status=form.status.data
        )
        db.session.add(project)
        db.session.commit()
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('project_detail', id=project.id))
    
    return render_template('projects/new.html', form=form)

@app.route('/projects/<int:id>')
@login_required
def project_detail(id):
    """Exibe detalhes de um projeto"""
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    budgets = Budget.query.filter_by(project_id=id).order_by(Budget.created_at.desc()).all()
    schedules = ProjectSchedule.query.filter_by(project_id=id).order_by(ProjectSchedule.created_at.desc()).all()
    return render_template('projects/detail.html', project=project, budgets=budgets, schedules=schedules)

@app.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    """Edita um projeto"""
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        form.populate_obj(project)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('project_detail', id=project.id))
    
    return render_template('projects/edit.html', form=form, project=project)

@app.route('/projects/<int:id>/budgets/new', methods=['GET', 'POST'])
@login_required
def new_budget(id):
    """Cria um novo orçamento para um projeto"""
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm()
    
    if form.validate_on_submit():
        budget = Budget(  # type: ignore
            project_id=id,
            name=form.name.data,
            version=form.version.data,
            description=form.description.data,
            profit_margin=form.profit_margin.data,
            status=form.status.data,
            created_by=current_user.name
        )
        db.session.add(budget)
        db.session.commit()
        flash('Orçamento criado com sucesso!', 'success')
        return redirect(url_for('budget_detail', project_id=id, budget_id=budget.id))
    
    return render_template('projects/budget_new.html', form=form, project=project)

@app.route('/projects/<int:project_id>/budgets/<int:budget_id>')
@login_required
def budget_detail(project_id, budget_id):
    """Exibe detalhes de um orçamento"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    budget = Budget.query.filter_by(id=budget_id, project_id=project_id).first_or_404()
    items = BudgetItem.query.filter_by(budget_id=budget_id).all()
    
    # Calcula totais
    calculator = BudgetCalculator()
    item_data = []
    for item in items:
        item_data.append({
            'quantity': item.quantity,
            'total_cost': item.total_cost,
            'materials_cost': item.total_cost * 0.6,  # Estimativa
            'labor_cost': item.total_cost * 0.3,     # Estimativa
            'equipment_cost': item.total_cost * 0.1   # Estimativa
        })
    
    totals = calculator.calculate_budget_totals(item_data)
    final_totals = calculator.apply_profit_margin(totals['subtotal'], budget.profit_margin)
    
    return render_template('projects/budget_detail.html', 
                         project=project, budget=budget, items=items, 
                         totals=totals, final_totals=final_totals)

@app.route('/projects/<int:project_id>/budgets/<int:budget_id>/items/new', methods=['GET', 'POST'])
@login_required
def new_budget_item(project_id, budget_id):
    """Adiciona um item ao orçamento"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    budget = Budget.query.filter_by(id=budget_id, project_id=project_id).first_or_404()
    form = BudgetItemForm()
    
    # Carrega composições disponíveis
    compositions = CostComposition.query.all()
    composition_choices = [(0, 'Personalizado')] + [(c.id, f"{c.description} - R$ {c.unit_cost:.2f}/{c.unit}") for c in compositions]
    
    if form.validate_on_submit():
        total_cost = (form.quantity.data or 0) * (form.unit_cost.data or 0)
        
        item = BudgetItem(  # type: ignore
            budget_id=budget_id,
            description=form.description.data,
            unit=form.unit.data,
            quantity=form.quantity.data,
            unit_cost=form.unit_cost.data,
            total_cost=total_cost,
            category=form.category.data,
            notes=form.notes.data
        )
        db.session.add(item)
        
        # Atualiza totais do orçamento
        items = BudgetItem.query.filter_by(budget_id=budget_id).all()
        budget.total_cost = sum(i.total_cost for i in items) + total_cost
        
        db.session.commit()
        flash('Item adicionado ao orçamento!', 'success')
        return redirect(url_for('budget_detail', project_id=project_id, budget_id=budget_id))
    
    return render_template('projects/budget_item_new.html', 
                         form=form, project=project, budget=budget, 
                         compositions=composition_choices)

@app.route('/api/compositions/<int:id>')
@login_required
def get_composition(id):
    """API para obter dados de uma composição"""
    composition = CostComposition.query.get_or_404(id)
    return jsonify({
        'description': composition.description,
        'unit': composition.unit,
        'unit_cost': composition.unit_cost,
        'materials_cost': composition.materials_cost,
        'labor_cost': composition.labor_cost,
        'equipment_cost': composition.equipment_cost
    })

@app.route('/projects/<int:project_id>/schedules/new', methods=['GET', 'POST'])
@login_required
def new_schedule(project_id):
    """Cria um novo cronograma para um projeto"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        schedule = ProjectSchedule(  # type: ignore
            project_id=project_id,
            name=request.form.get('name', 'Cronograma Principal'),
            version=request.form.get('version', '1.0')
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Cronograma criado com sucesso!', 'success')
        return redirect(url_for('schedule_detail', project_id=project_id, schedule_id=schedule.id))
    
    return render_template('projects/schedule_new.html', project=project)

@app.route('/projects/<int:project_id>/schedules/<int:schedule_id>')
@login_required
def schedule_detail(project_id, schedule_id):
    """Exibe detalhes de um cronograma"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    schedule = ProjectSchedule.query.filter_by(id=schedule_id, project_id=project_id).first_or_404()
    activities = ScheduleActivity.query.filter_by(schedule_id=schedule_id).all()
    
    # Calcula CPM se há atividades
    cpm_data = None
    if activities:
        calculator = ScheduleCalculator()
        for activity in activities:
            predecessors = json.loads(activity.predecessors) if activity.predecessors else []
            calculator.add_activity(activity.id, activity.name, activity.duration, predecessors)
        
        cpm_data = calculator.calculate_cpm()
        gantt_data = calculator.generate_gantt_data(project.start_date)
    else:
        gantt_data = []
    
    return render_template('projects/schedule_detail.html', 
                         project=project, schedule=schedule, activities=activities,
                         cpm_data=cpm_data, gantt_data=gantt_data)

@app.route('/projects/<int:project_id>/schedules/<int:schedule_id>/activities/new', methods=['GET', 'POST'])
@login_required
def new_activity(project_id, schedule_id):
    """Adiciona uma atividade ao cronograma"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    schedule = ProjectSchedule.query.filter_by(id=schedule_id, project_id=project_id).first_or_404()
    form = ScheduleActivityForm()
    
    if form.validate_on_submit():
        # Processa predecessores
        predecessors = []
        if form.predecessors.data:
            try:
                predecessors = [int(x.strip()) for x in form.predecessors.data.split(',')]
            except ValueError:
                flash('IDs de predecessores devem ser números separados por vírgula', 'danger')
                return render_template('projects/activity_new.html', form=form, project=project, schedule=schedule)
        
        activity = ScheduleActivity(  # type: ignore
            schedule_id=schedule_id,
            name=form.name.data,
            description=form.description.data,
            duration=form.duration.data,
            responsible=form.responsible.data,
            cost=form.cost.data or 0.0,
            predecessors=json.dumps(predecessors)
        )
        db.session.add(activity)
        db.session.commit()
        flash('Atividade adicionada ao cronograma!', 'success')
        return redirect(url_for('schedule_detail', project_id=project_id, schedule_id=schedule_id))
    
    return render_template('projects/activity_new.html', form=form, project=project, schedule=schedule)

@app.route('/materials')
@login_required
def materials():
    """Lista todos os materiais"""
    materials = Material.query.order_by(Material.category, Material.name).all()
    return render_template('materials/index.html', materials=materials)

@app.route('/materials/new', methods=['GET', 'POST'])
@login_required
def new_material():
    """Cria um novo material"""
    form = MaterialForm()
    if form.validate_on_submit():
        material = Material(  # type: ignore
            name=form.name.data,
            category=form.category.data,
            unit=form.unit.data,
            unit_cost=form.unit_cost.data,
            supplier=form.supplier.data
        )
        db.session.add(material)
        db.session.commit()
        flash('Material cadastrado com sucesso!', 'success')
        return redirect(url_for('materials'))
    
    return render_template('materials/new.html', form=form)

@app.route('/compositions')
@login_required
def compositions():
    """Lista todas as composições de custo"""
    compositions = CostComposition.query.order_by(CostComposition.category, CostComposition.description).all()
    return render_template('compositions/index.html', compositions=compositions)

@app.route('/compositions/new', methods=['GET', 'POST'])
@login_required
def new_composition():
    """Cria uma nova composição de custo"""
    form = CostCompositionForm()
    if form.validate_on_submit():
        composition = CostComposition(  # type: ignore
            sinapi_code=form.sinapi_code.data,
            tcpo_code=form.tcpo_code.data,
            description=form.description.data,
            unit=form.unit.data,
            unit_cost=form.unit_cost.data,
            productivity=form.productivity.data,
            category=form.category.data
        )
        db.session.add(composition)
        db.session.commit()
        flash('Composição cadastrada com sucesso!', 'success')
        return redirect(url_for('compositions'))
    
    return render_template('compositions/new.html', form=form)

@app.route('/api/sinapi/<code>')
@login_required
def get_sinapi_composition(code):
    """API simulada para obter composição do SINAPI"""
    calculator = BudgetCalculator()
    
    # Mapeia códigos para composições pré-definidas
    code_map = {
        '92885': 'concreto_fck25',
        '87487': 'alvenaria_bloco',
        '87269': 'piso_ceramico'
    }
    
    if code in code_map:
        composition_data = calculator.calculate_composition_cost(code_map[code])
        return jsonify({
            'found': True,
            'data': composition_data
        })
    
    return jsonify({'found': False, 'message': 'Composição não encontrada'})

@app.route('/reports/budget/<int:project_id>/<int:budget_id>')
@login_required
def budget_report(project_id, budget_id):
    """Gera relatório de orçamento"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    budget = Budget.query.filter_by(id=budget_id, project_id=project_id).first_or_404()
    items = BudgetItem.query.filter_by(budget_id=budget_id).all()
    
    generator = ReportGenerator()
    report_data = generator.generate_budget_report(
        {'name': project.name, 'client_name': project.client_name},
        {'total': budget.total_cost, 'items': items}
    )
    
    return render_template('reports/budget.html', 
                         project=project, budget=budget, items=items, report=report_data)

@app.route('/reports/budget/<int:project_id>/<int:budget_id>/pdf')
@login_required
def budget_report_pdf(project_id, budget_id):
    """Gera PDF do relatório de orçamento"""
    from flask import make_response
    
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    budget = Budget.query.filter_by(id=budget_id, project_id=project_id).first_or_404()
    items = BudgetItem.query.filter_by(budget_id=budget_id).all()
    
    # Preparar dados para o PDF
    project_data = {
        'name': project.name,
        'client_name': project.client_name,
        'technical_responsible': project.technical_responsible,
        'crea_number': project.crea_number
    }
    
    budget_data = {
        'name': budget.name,
        'version': budget.version,
        'total_cost': budget.total_cost,
        'profit_margin': budget.profit_margin,
        'status': budget.status,
        'description': budget.description
    }
    
    # Gerar PDF
    generator = ReportGenerator()
    pdf_buffer = generator.generate_budget_pdf(project_data, budget_data, items)
    
    # Criar resposta
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="orcamento_{project.name}_{budget.name}.pdf"'
    
    return response

# Painel Administrativo
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Painel administrativo"""
    # Estatísticas gerais do sistema
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_projects = Project.query.count()
    total_calculations = Calculation.query.count()
    
    # Usuários por tipo
    users_by_role = {
        'admin': User.query.filter_by(role='admin').count(),
        'engineer': User.query.filter_by(role='engineer').count(),
        'client': User.query.filter_by(role='client').count()
    }
    
    # Usuários por plano
    users_by_plan = {
        'free': User.query.filter_by(plan='free').count(),
        'pro': User.query.filter_by(plan='pro').count()
    }
    
    # Atividade recente
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    
    # Projetos por status
    projects_status = {
        'planejamento': Project.query.filter_by(status='planejamento').count(),
        'ativo': Project.query.filter_by(status='ativo').count(),
        'pausado': Project.query.filter_by(status='pausado').count(),
        'concluido': Project.query.filter_by(status='concluido').count()
    }
    
    admin_stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'total_calculations': total_calculations,
        'users_by_role': users_by_role,
        'users_by_plan': users_by_plan,
        'projects_status': projects_status
    }
    
    return render_template('admin/panel.html', 
                         stats=admin_stats,
                         recent_users=recent_users,
                         recent_projects=recent_projects)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Gerenciar usuários"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required  
def admin_toggle_user_status(user_id):
    """Ativar/desativar usuário"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'ativado' if user.is_active else 'desativado'
        flash(f'Usuário {user.name} foi {status}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/technical-standards')
@login_required
def technical_standards():
    """Biblioteca de normas técnicas"""
    return render_template('technical_standards.html')

# Geotechnical Routes
@app.route('/geotechnical/earth-pressure', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def earth_pressure():
    if not current_user.has_access_to_module('geotechnical'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = EarthPressureForm()
    result = None
    
    if form.validate_on_submit():
        try:
            if form.pressure_type.data == 'active':
                result = GeotechnicalCalculations.calculate_earth_pressure_active(
                    form.unit_weight.data,
                    form.height.data,
                    form.friction_angle.data,
                    int(form.cohesion.data or 0)
                )
            else:
                result = GeotechnicalCalculations.calculate_earth_pressure_passive(
                    form.unit_weight.data,
                    form.height.data,
                    form.friction_angle.data,
                    int(form.cohesion.data or 0)
                )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='geotechnical',
                name=form.name.data,
                inputs=json.dumps({
                    'pressure_type': form.pressure_type.data,
                    'unit_weight': form.unit_weight.data,
                    'height': form.height.data,
                    'friction_angle': form.friction_angle.data,
                    'cohesion': form.cohesion.data or 0
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('geotechnical/earth_pressure.html', form=form, result=result)

@app.route('/geotechnical/settlement', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def settlement():
    if not current_user.has_access_to_module('geotechnical'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = SettlementForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = GeotechnicalCalculations.calculate_settlement_terzaghi(
                form.consolidation_coeff.data,
                form.time_days.data,
                form.layer_height.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='geotechnical',
                name=form.name.data,
                inputs=json.dumps({
                    'consolidation_coeff': form.consolidation_coeff.data,
                    'time_days': form.time_days.data,
                    'layer_height': form.layer_height.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('geotechnical/settlement.html', form=form, result=result)

# Pavement Routes
@app.route('/pavement/cbr', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def pavement_cbr():
    if not current_user.has_access_to_module('pavement'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = PavementCBRForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = PavementCalculations.calculate_flexible_pavement_cbr(
                form.traffic_load.data,
                form.cbr_value.data,
                form.k_constant.data or 1.0
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='pavement',
                name=form.name.data,
                inputs=json.dumps({
                    'traffic_load': form.traffic_load.data,
                    'cbr_value': form.cbr_value.data,
                    'k_constant': form.k_constant.data or 1.0
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('pavement/cbr.html', form=form, result=result)

@app.route('/pavement/earthwork', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def earthwork():
    if not current_user.has_access_to_module('pavement'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = EarthworkForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = PavementCalculations.calculate_earthwork_volume(
                form.length.data,
                form.area1.data,
                form.area2.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='pavement',
                name=form.name.data,
                inputs=json.dumps({
                    'length': form.length.data,
                    'area1': form.area1.data,
                    'area2': form.area2.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('pavement/earthwork.html', form=form, result=result)

@app.route('/pavement/esal', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def traffic_esal():
    if not current_user.has_access_to_module('pavement'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = TrafficESALForm()
    result = None
    
    if form.validate_on_submit():
        try:
            # Parse axle loads and repetitions
            axle_loads = [float(x.strip()) for x in (form.axle_loads.data or '').strip().split('\n') if x.strip()]
            repetitions = [int(x.strip()) for x in (form.repetitions.data or '').strip().split('\n') if x.strip()]
            
            result = PavementCalculations.calculate_traffic_esal(axle_loads, repetitions)
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='pavement',
                name=form.name.data,
                inputs=json.dumps({
                    'axle_loads': axle_loads,
                    'repetitions': repetitions
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('pavement/esal.html', form=form, result=result)

# Quantity Calculation Routes
@app.route('/quantities/concrete', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def concrete_volume():
    if not current_user.has_access_to_module('quantities'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ConcreteVolumeForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = QuantityCalculations.calculate_concrete_volume(
                form.length.data,
                form.width.data,
                form.height.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='quantities',
                name=form.name.data,
                inputs=json.dumps({
                    'length': form.length.data,
                    'width': form.width.data,
                    'height': form.height.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('quantities/concrete.html', form=form, result=result)

@app.route('/quantities/steel', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def steel_consumption():
    if not current_user.has_access_to_module('quantities'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = SteelConsumptionForm()
    result = None
    
    if form.validate_on_submit():
        try:
            # Parse steel bar data
            bar_data = []
            lines = (form.steel_bars.data or '').strip().split('\n')
            for line in lines:
                if line.strip():
                    diameter, length, quantity = map(float, line.strip().split(','))
                    bar_data.append({
                        'diameter': diameter,
                        'length': length,
                        'quantity': int(quantity)
                    })
            
            result = QuantityCalculations.calculate_steel_consumption(bar_data)
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='quantities',
                name=form.name.data,
                inputs=json.dumps({
                    'bar_data': bar_data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('quantities/steel.html', form=form, result=result)

@app.route('/quantities/mortar', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def mortar_composition():
    if not current_user.has_access_to_module('quantities'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = MortarForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = QuantityCalculations.calculate_mortar_composition(
                form.volume_m3.data,
                form.mix_ratio.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='quantities',
                name=form.name.data,
                inputs=json.dumps({
                    'volume_m3': form.volume_m3.data,
                    'mix_ratio': form.mix_ratio.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('quantities/mortar.html', form=form, result=result)

# Masonry Routes
@app.route('/masonry/bricks', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def brick_consumption():
    if not current_user.has_access_to_module('masonry'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = BrickConsumptionForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = MasonryCalculations.calculate_brick_consumption(
                form.wall_area.data,
                int(form.brick_length.data or 19),
                int(form.brick_height.data or 9),
                int(form.mortar_joint.data or 1)
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='masonry',
                name=form.name.data,
                inputs=json.dumps({
                    'wall_area': form.wall_area.data,
                    'brick_length': form.brick_length.data or 19,
                    'brick_height': form.brick_height.data or 9,
                    'mortar_joint': form.mortar_joint.data or 1
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('masonry/bricks.html', form=form, result=result)

@app.route('/masonry/wall-load', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def wall_load():
    if not current_user.has_access_to_module('masonry'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = WallLoadForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = MasonryCalculations.calculate_wall_load(
                form.applied_load.data,
                form.wall_area.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='masonry',
                name=form.name.data,
                inputs=json.dumps({
                    'applied_load': form.applied_load.data,
                    'wall_area': form.wall_area.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('masonry/wall_load.html', form=form, result=result)

# Sanitation Routes
@app.route('/sanitation/rational', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def rational_method():
    if not current_user.has_access_to_module('sanitation'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = RationalMethodForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SanitationCalculations.calculate_rational_method(
                form.runoff_coeff.data,
                form.intensity.data,
                form.area.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='sanitation',
                name=form.name.data,
                inputs=json.dumps({
                    'runoff_coeff': form.runoff_coeff.data,
                    'intensity': form.intensity.data,
                    'area': form.area.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('sanitation/rational.html', form=form, result=result)

@app.route('/sanitation/manning', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def manning_velocity():
    if not current_user.has_access_to_module('sanitation'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ManningForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SanitationCalculations.calculate_manning_velocity(
                form.hydraulic_radius.data,
                form.slope.data,
                form.manning_n.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='sanitation',
                name=form.name.data,
                inputs=json.dumps({
                    'hydraulic_radius': form.hydraulic_radius.data,
                    'slope': form.slope.data,
                    'manning_n': form.manning_n.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('sanitation/manning.html', form=form, result=result)

@app.route('/sanitation/darcy', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def darcy_weisbach():
    if not current_user.has_access_to_module('sanitation'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = DarcyWeisbachForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SanitationCalculations.calculate_darcy_weisbach_loss(
                form.friction_factor.data,
                form.length.data,
                form.diameter.data,
                form.velocity.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='sanitation',
                name=form.name.data,
                inputs=json.dumps({
                    'friction_factor': form.friction_factor.data,
                    'length': form.length.data,
                    'diameter': form.diameter.data,
                    'velocity': form.velocity.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('sanitation/darcy.html', form=form, result=result)

# Advanced Structural Calculations
@app.route('/advanced-structural/torsion', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def torsion_shear():
    if not current_user.has_access_to_module('advanced_structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = TorsionShearForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedCalculations.calculate_torsion_shear(
                form.torque.data,
                form.c_distance.data,
                form.polar_moment.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='advanced_structural',
                name=form.name.data,
                inputs=json.dumps({
                    'torque': form.torque.data,
                    'c_distance': form.c_distance.data,
                    'polar_moment': form.polar_moment.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced_structural/torsion.html', form=form, result=result)

@app.route('/advanced-structural/buckling', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def euler_buckling():
    if not current_user.has_access_to_module('advanced_structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = EulerBucklingForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedCalculations.calculate_euler_buckling(
                form.e_modulus.data,
                form.moment_inertia.data,
                form.k_factor.data,
                form.length.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='advanced_structural',
                name=form.name.data,
                inputs=json.dumps({
                    'e_modulus': form.e_modulus.data,
                    'moment_inertia': form.moment_inertia.data,
                    'k_factor': form.k_factor.data,
                    'length': form.length.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced_structural/buckling.html', form=form, result=result)

@app.route('/advanced-structural/continuous', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def continuous_beam():
    if not current_user.has_access_to_module('advanced_structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ContinuousBeamForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedCalculations.calculate_continuous_beam_moment(
                form.distributed_load.data,
                form.length.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='advanced_structural',
                name=form.name.data,
                inputs=json.dumps({
                    'distributed_load': form.distributed_load.data,
                    'length': form.length.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced_structural/continuous.html', form=form, result=result)

# Hydrology Calculations
@app.route('/hydrology/concentration-time', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def concentration_time():
    if not current_user.has_access_to_module('hydrology'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ConcentrationTimeForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = HydrologyCalculations.calculate_concentration_time(
                form.length_km.data,
                form.slope_percent.data,
                form.method.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='hydrology',
                name=form.name.data,
                inputs=json.dumps({
                    'length_km': form.length_km.data,
                    'slope_percent': form.slope_percent.data,
                    'method': form.method.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('hydrology/concentration.html', form=form, result=result)

@app.route('/hydrology/detention', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def detention_outflow():
    if not current_user.has_access_to_module('hydrology'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = DetentionOutflowForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = HydrologyCalculations.calculate_detention_outflow(
                form.inflow_rate.data,
                form.volume_change_rate.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='hydrology',
                name=form.name.data,
                inputs=json.dumps({
                    'inflow_rate': form.inflow_rate.data,
                    'volume_change_rate': form.volume_change_rate.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('hydrology/detention.html', form=form, result=result)

# Steel Structures Calculations
@app.route('/steel/tension', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def steel_tension():
    if not current_user.has_access_to_module('steel_structures'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = SteelTensionForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SteelStructuresCalculations.calculate_steel_tension_stress(
                form.force_kn.data,
                form.cross_area_cm2.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='steel_structures',
                name=form.name.data,
                inputs=json.dumps({
                    'force_kn': form.force_kn.data,
                    'cross_area_cm2': form.cross_area_cm2.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('steel/tension.html', form=form, result=result)

@app.route('/steel/deflection', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def steel_deflection():
    if not current_user.has_access_to_module('steel_structures'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = SteelBeamDeflectionForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SteelStructuresCalculations.calculate_steel_beam_deflection(
                form.load_kn.data,
                form.length_m.data,
                form.elastic_modulus.data,
                form.moment_inertia_cm4.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='steel_structures',
                name=form.name.data,
                inputs=json.dumps({
                    'load_kn': form.load_kn.data,
                    'length_m': form.length_m.data,
                    'elastic_modulus': form.elastic_modulus.data,
                    'moment_inertia_cm4': form.moment_inertia_cm4.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('steel/deflection.html', form=form, result=result)

# Construction Control Calculations
@app.route('/control/productivity', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def productivity():
    if not current_user.has_access_to_module('construction_control'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ProductivityForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = ConstructionControlCalculations.calculate_productivity(
                form.quantity_executed.data,
                form.time_spent_hours.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='construction_control',
                name=form.name.data,
                inputs=json.dumps({
                    'quantity_executed': form.quantity_executed.data,
                    'time_spent_hours': form.time_spent_hours.data,
                    'unit': form.unit.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('control/productivity.html', form=form, result=result)

@app.route('/control/s-curve', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def s_curve():
    if not current_user.has_access_to_module('construction_control'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = SCurveForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = ConstructionControlCalculations.calculate_s_curve(
                form.total_budget.data,
                form.current_time_percent.data,
                form.curve_type.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='construction_control',
                name=form.name.data,
                inputs=json.dumps({
                    'total_budget': form.total_budget.data,
                    'current_time_percent': form.current_time_percent.data,
                    'curve_type': form.curve_type.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('control/s_curve.html', form=form, result=result)

# Sustainability Calculations
@app.route('/sustainability/carbon-footprint', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def carbon_footprint():
    if not current_user.has_access_to_module('sustainability'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = CarbonFootprintForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SustainabilityCalculations.calculate_carbon_footprint(
                form.material_mass_kg.data,
                form.emission_factor_kg_co2_kg.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='sustainability',
                name=form.name.data,
                inputs=json.dumps({
                    'material_mass_kg': form.material_mass_kg.data,
                    'emission_factor_kg_co2_kg': form.emission_factor_kg_co2_kg.data,
                    'material_type': form.material_type.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('sustainability/carbon.html', form=form, result=result)

@app.route('/sustainability/thermal-loss', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def thermal_loss():
    if not current_user.has_access_to_module('sustainability'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ThermalLossForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = SustainabilityCalculations.calculate_thermal_loss(
                form.u_value.data,
                form.area_m2.data,
                form.temp_difference.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='sustainability',
                name=form.name.data,
                inputs=json.dumps({
                    'u_value': form.u_value.data,
                    'area_m2': form.area_m2.data,
                    'temp_difference': form.temp_difference.data,
                    'element_type': form.element_type.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('sustainability/thermal.html', form=form, result=result)


# Advanced Formula Routes
@app.route('/advanced/load-combination', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def load_combination():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = LoadCombinationForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_load_combination(
                form.dead_load.data,
                form.live_load.data,
                form.wind_load.data,
                form.snow_load.data,
                form.alpha_d.data or 1.2,
                form.alpha_l.data or 1.6,
                form.alpha_w.data or 1.6,
                form.alpha_s.data or 1.6
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'dead_load': form.dead_load.data,
                    'live_load': form.live_load.data,
                    'wind_load': form.wind_load.data,
                    'snow_load': form.snow_load.data,
                    'alpha_d': form.alpha_d.data,
                    'alpha_l': form.alpha_l.data,
                    'alpha_w': form.alpha_w.data,
                    'alpha_s': form.alpha_s.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/load_combination.html', form=form, result=result)

@app.route('/advanced/concrete-shear', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def concrete_shear():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = ConcreteShearForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_concrete_shear(
                form.asv.data,
                form.fy.data,
                form.d.data,
                form.s.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'asv': form.asv.data,
                    'fy': form.fy.data,
                    'd': form.d.data,
                    's': form.s.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/concrete_shear.html', form=form, result=result)

@app.route('/advanced/punching-shear', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def punching_shear():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = PunchingShearForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_punching_shear(
                form.tau_rd.data,
                form.u1.data,
                form.d.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'tau_rd': form.tau_rd.data,
                    'u1': form.u1.data,
                    'd': form.d.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/punching_shear.html', form=form, result=result)

@app.route('/advanced/euler-buckling-advanced', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def euler_buckling_advanced():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = EulerBucklingForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_euler_buckling(
                form.e_modulus.data,
                form.moment_inertia.data,
                form.k_factor.data,
                form.length.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'e_modulus': form.e_modulus.data,
                    'moment_inertia': form.moment_inertia.data,
                    'k_factor': form.k_factor.data,
                    'length': form.length.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/euler_buckling.html', form=form, result=result)

@app.route('/advanced/lateral-torsional-buckling', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def lateral_torsional_buckling():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = LateralTorsionalBucklingForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_lateral_torsional_buckling(
                form.c1.data,
                form.e_modulus.data,
                form.iz.data,
                form.lb.data,
                form.g_modulus.data,
                form.j_constant.data,
                form.iw.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'c1': form.c1.data,
                    'e_modulus': form.e_modulus.data,
                    'iz': form.iz.data,
                    'lb': form.lb.data,
                    'g_modulus': form.g_modulus.data,
                    'j_constant': form.j_constant.data,
                    'iw': form.iw.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/lateral_torsional_buckling.html', form=form, result=result)

@app.route('/advanced/wood-connection', methods=['GET', 'POST'])
@login_required
@can_perform_calculations_required
def wood_connection():
    if not current_user.has_access_to_module('structural'):
        flash('Upgrade para o plano Pro para acessar este módulo.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = WoodConnectionForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = AdvancedStructuralCalculations.calculate_wood_connection_capacity(
                form.embedment_strength.data,
                form.flexural_strength.data,
                form.withdrawal_strength.data,
                form.connection_type.data
            )
            
            # Save calculation
            calculation = Calculation(  # type: ignore
                user_id=current_user.id,
                module='structural',
                name=form.name.data,
                inputs=json.dumps({
                    'embedment_strength': form.embedment_strength.data,
                    'flexural_strength': form.flexural_strength.data,
                    'withdrawal_strength': form.withdrawal_strength.data,
                    'connection_type': form.connection_type.data
                }),
                results=json.dumps(result)
            )
            db.session.add(calculation)
            db.session.commit()
            
            flash('Cálculo realizado e salvo com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro no cálculo: {str(e)}', 'danger')
    
    return render_template('advanced/wood_connection.html', form=form, result=result)
