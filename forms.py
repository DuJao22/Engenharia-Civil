from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, TextAreaField, SubmitField, DateField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', 
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cadastrar')

class BeamCalculationForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    length = FloatField('Comprimento da Viga (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    load_type = SelectField('Tipo de Carregamento', 
                           choices=[('uniform', 'Uniformemente Distribuída'), 
                                   ('point', 'Carga Pontual no Centro')])
    load_value = FloatField('Valor da Carga', validators=[DataRequired(), NumberRange(min=0)])
    load_unit = SelectField('Unidade', choices=[('kN/m', 'kN/m'), ('kN', 'kN')])
    submit = SubmitField('Calcular')

class ConcreteBeamForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    width = FloatField('Largura da Seção (cm)', validators=[DataRequired(), NumberRange(min=1)])
    height = FloatField('Altura da Seção (cm)', validators=[DataRequired(), NumberRange(min=1)])
    moment = FloatField('Momento de Projeto (kN.m)', validators=[DataRequired(), NumberRange(min=0)])
    fck = FloatField('fck (MPa)', validators=[DataRequired(), NumberRange(min=10, max=50)])
    fyk = FloatField('fyk (MPa)', validators=[DataRequired(), NumberRange(min=250, max=600)])
    submit = SubmitField('Calcular')

class HydraulicsForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    pipe_diameter = FloatField('Diâmetro da Tubulação (mm)', validators=[DataRequired(), NumberRange(min=10)])
    pipe_length = FloatField('Comprimento (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    flow_rate = FloatField('Vazão (L/s)', validators=[DataRequired(), NumberRange(min=0.1)])
    roughness = FloatField('Rugosidade (mm)', validators=[DataRequired(), NumberRange(min=0.001)])
    submit = SubmitField('Calcular')

class FoundationForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    width = FloatField('Largura da Sapata (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    cohesion = FloatField('Coesão do Solo (kPa)', validators=[DataRequired(), NumberRange(min=0)])
    friction_angle = FloatField('Ângulo de Atrito (graus)', validators=[DataRequired(), NumberRange(min=0, max=45)])
    unit_weight = FloatField('Peso Específico do Solo (kN/m³)', validators=[DataRequired(), NumberRange(min=10, max=25)])
    depth = FloatField('Profundidade da Fundação (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    submit = SubmitField('Calcular')

class TopographyForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    coordinates = TextAreaField('Coordenadas (x,y por linha)', 
                               validators=[DataRequired()],
                               render_kw={"placeholder": "Digite as coordenadas separadas por vírgula, uma por linha:\nx1,y1\nx2,y2\nx3,y3"})
    submit = SubmitField('Calcular')

# Project Management Forms
class ProjectForm(FlaskForm):
    name = StringField('Nome do Projeto', validators=[DataRequired(), Length(min=2, max=200)])
    client_name = StringField('Nome do Cliente', validators=[DataRequired(), Length(min=2, max=200)])
    client_email = StringField('Email do Cliente', validators=[Optional(), Email()])
    client_phone = StringField('Telefone do Cliente', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Endereço da Obra', validators=[DataRequired()])
    technical_responsible = StringField('Responsável Técnico', validators=[DataRequired(), Length(min=2, max=200)])
    crea_number = StringField('Número do CREA', validators=[Optional(), Length(max=50)])
    start_date = DateField('Data de Início', validators=[DataRequired()])
    end_date = DateField('Data de Término', validators=[DataRequired()])
    description = TextAreaField('Descrição do Projeto')
    status = SelectField('Status', choices=[
        ('planejamento', 'Planejamento'),
        ('execucao', 'Execução'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado')
    ])
    submit = SubmitField('Salvar Projeto')

class BudgetForm(FlaskForm):
    name = StringField('Nome do Orçamento', validators=[DataRequired(), Length(min=2, max=200)])
    version = StringField('Versão', validators=[DataRequired(), Length(max=10)])
    description = TextAreaField('Descrição')
    profit_margin = FloatField('Margem de Lucro (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    status = SelectField('Status', choices=[
        ('rascunho', 'Rascunho'),
        ('revisao', 'Em Revisão'),
        ('aprovado', 'Aprovado')
    ])
    submit = SubmitField('Salvar Orçamento')

class BudgetItemForm(FlaskForm):
    description = StringField('Descrição', validators=[DataRequired(), Length(min=2, max=500)])
    unit = SelectField('Unidade', choices=[
        ('m²', 'm²'), ('m³', 'm³'), ('m', 'm'), ('un', 'un'), 
        ('kg', 'kg'), ('t', 't'), ('h', 'h'), ('vb', 'vb')
    ])
    quantity = FloatField('Quantidade', validators=[DataRequired(), NumberRange(min=0.001)])
    unit_cost = FloatField('Custo Unitário (R$)', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Categoria', choices=[
        ('estrutura', 'Estrutura'),
        ('fundacao', 'Fundação'),
        ('acabamento', 'Acabamento'),
        ('instalacoes', 'Instalações'),
        ('movimento_terra', 'Movimento de Terra'),
        ('outros', 'Outros')
    ])
    notes = TextAreaField('Observações')
    submit = SubmitField('Adicionar Item')

class MaterialForm(FlaskForm):
    name = StringField('Nome do Material', validators=[DataRequired(), Length(min=2, max=200)])
    category = SelectField('Categoria', choices=[
        ('cimento', 'Cimento'),
        ('areia', 'Areia'),
        ('brita', 'Brita'),
        ('aco', 'Aço'),
        ('blocos', 'Blocos'),
        ('tubulacao', 'Tubulação'),
        ('madeira', 'Madeira'),
        ('ceramica', 'Cerâmica'),
        ('tinta', 'Tinta'),
        ('outros', 'Outros')
    ])
    unit = SelectField('Unidade', choices=[
        ('kg', 'kg'), ('t', 't'), ('m³', 'm³'), ('m²', 'm²'), 
        ('m', 'm'), ('un', 'un'), ('L', 'L'), ('saca', 'saca')
    ])
    unit_cost = FloatField('Custo Unitário (R$)', validators=[DataRequired(), NumberRange(min=0)])
    supplier = StringField('Fornecedor', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Salvar Material')

class CostCompositionForm(FlaskForm):
    sinapi_code = StringField('Código SINAPI', validators=[Optional(), Length(max=20)])
    tcpo_code = StringField('Código TCPO', validators=[Optional(), Length(max=20)])
    description = StringField('Descrição', validators=[DataRequired(), Length(min=2, max=500)])
    unit = SelectField('Unidade', choices=[
        ('m²', 'm²'), ('m³', 'm³'), ('m', 'm'), ('un', 'un'), 
        ('kg', 'kg'), ('t', 't'), ('h', 'h'), ('vb', 'vb')
    ])
    unit_cost = FloatField('Custo Unitário (R$)', validators=[DataRequired(), NumberRange(min=0)])
    productivity = FloatField('Produtividade (h/un)', validators=[Optional(), NumberRange(min=0)])
    category = SelectField('Categoria', choices=[
        ('estrutura', 'Estrutura'),
        ('fundacao', 'Fundação'),
        ('acabamento', 'Acabamento'),
        ('instalacoes', 'Instalações'),
        ('movimento_terra', 'Movimento de Terra'),
        ('outros', 'Outros')
    ])
    submit = SubmitField('Salvar Composição')

class ScheduleActivityForm(FlaskForm):
    name = StringField('Nome da Atividade', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Descrição')
    duration = IntegerField('Duração (dias)', validators=[DataRequired(), NumberRange(min=1)])
    responsible = StringField('Responsável', validators=[Optional(), Length(max=200)])
    cost = FloatField('Custo (R$)', validators=[Optional(), NumberRange(min=0)])
    predecessors = StringField('Atividades Predecessoras (IDs separados por vírgula)', validators=[Optional()])
    submit = SubmitField('Adicionar Atividade')

# Geotechnical Forms
class EarthPressureForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    pressure_type = SelectField('Tipo de Empuxo', choices=[
        ('active', 'Empuxo Ativo'),
        ('passive', 'Empuxo Passivo')
    ])
    unit_weight = FloatField('Peso Específico do Solo (kN/m³)', validators=[DataRequired(), NumberRange(min=10, max=25)])
    height = FloatField('Altura do Muro (m)', validators=[DataRequired(), NumberRange(min=0.5, max=20)])
    friction_angle = FloatField('Ângulo de Atrito (graus)', validators=[DataRequired(), NumberRange(min=0, max=45)])
    cohesion = FloatField('Coesão do Solo (kPa)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Calcular')

class SettlementForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    consolidation_coeff = FloatField('Coeficiente de Adensamento (m²/ano)', validators=[DataRequired(), NumberRange(min=0.001, max=100)])
    time_days = FloatField('Tempo (dias)', validators=[DataRequired(), NumberRange(min=1, max=36500)])
    layer_height = FloatField('Altura da Camada (m)', validators=[DataRequired(), NumberRange(min=0.1, max=50)])
    submit = SubmitField('Calcular')

# Pavement Forms
class PavementCBRForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    traffic_load = FloatField('Carga de Tráfego Equivalente', validators=[DataRequired(), NumberRange(min=1000)])
    cbr_value = FloatField('Valor CBR (%)', validators=[DataRequired(), NumberRange(min=2, max=100)])
    k_constant = FloatField('Constante K', validators=[Optional(), NumberRange(min=0.1, max=5)], default=1.0)
    submit = SubmitField('Calcular')

class EarthworkForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    length = FloatField('Comprimento (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    area1 = FloatField('Área da Seção 1 (m²)', validators=[DataRequired(), NumberRange(min=0)])
    area2 = FloatField('Área da Seção 2 (m²)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calcular')

class TrafficESALForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    axle_loads = TextAreaField('Cargas por Eixo (tons, uma por linha)', validators=[DataRequired()],
                              render_kw={"placeholder": "Digite as cargas em toneladas, uma por linha:\n8.2\n12.0\n16.0"})
    repetitions = TextAreaField('Repetições por Eixo (uma por linha)', validators=[DataRequired()],
                               render_kw={"placeholder": "Digite as repetições, uma por linha:\n1000000\n500000\n200000"})
    submit = SubmitField('Calcular')

# Quantity Calculation Forms
class ConcreteVolumeForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    length = FloatField('Comprimento (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    width = FloatField('Largura (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    height = FloatField('Altura (m)', validators=[DataRequired(), NumberRange(min=0.05)])
    submit = SubmitField('Calcular')

class SteelConsumptionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    steel_bars = TextAreaField('Barras de Aço (diâmetro,comprimento,quantidade por linha)', 
                              validators=[DataRequired()],
                              render_kw={"placeholder": "Digite: diâmetro(mm),comprimento(m),quantidade\n10,3.0,20\n12,6.0,10\n16,4.5,8"})
    submit = SubmitField('Calcular')

class MortarForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    volume_m3 = FloatField('Volume de Argamassa (m³)', validators=[DataRequired(), NumberRange(min=0.001)])
    mix_ratio = SelectField('Traço', choices=[
        ('1:3', '1:3 (Cimento:Areia)'),
        ('1:4', '1:4 (Cimento:Areia)'),
        ('1:4:1', '1:4:1 (Cimento:Areia:Cal)'),
        ('1:5:1', '1:5:1 (Cimento:Areia:Cal)'),
        ('1:6:1', '1:6:1 (Cimento:Areia:Cal)')
    ])
    submit = SubmitField('Calcular')

# Masonry Forms
class BrickConsumptionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    wall_area = FloatField('Área da Parede (m²)', validators=[DataRequired(), NumberRange(min=0.1)])
    brick_length = FloatField('Comprimento do Tijolo (cm)', validators=[Optional(), NumberRange(min=5, max=50)], default=19)
    brick_height = FloatField('Altura do Tijolo (cm)', validators=[Optional(), NumberRange(min=5, max=20)], default=9)
    mortar_joint = FloatField('Espessura da Junta (cm)', validators=[Optional(), NumberRange(min=0.5, max=3)], default=1)
    submit = SubmitField('Calcular')

class WallLoadForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    applied_load = FloatField('Carga Aplicada (kN)', validators=[DataRequired(), NumberRange(min=0.1)])
    wall_area = FloatField('Área da Parede (m²)', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Calcular')

# Sanitation Forms
class RationalMethodForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    runoff_coeff = FloatField('Coeficiente de Escoamento (C)', validators=[DataRequired(), NumberRange(min=0.1, max=1.0)])
    intensity = FloatField('Intensidade da Chuva (mm/h)', validators=[DataRequired(), NumberRange(min=1, max=300)])
    area = FloatField('Área da Bacia (ha)', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Calcular')

class ManningForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    hydraulic_radius = FloatField('Raio Hidráulico (m)', validators=[DataRequired(), NumberRange(min=0.01, max=10)])
    slope = FloatField('Declividade (m/m)', validators=[DataRequired(), NumberRange(min=0.0001, max=1)])
    manning_n = FloatField('Coeficiente de Manning (n)', validators=[DataRequired(), NumberRange(min=0.01, max=0.2)])
    submit = SubmitField('Calcular')

class DarcyWeisbachForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    friction_factor = FloatField('Fator de Atrito (f)', validators=[DataRequired(), NumberRange(min=0.01, max=0.1)])
    length = FloatField('Comprimento da Tubulação (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    diameter = FloatField('Diâmetro (m)', validators=[DataRequired(), NumberRange(min=0.01, max=5)])
    velocity = FloatField('Velocidade (m/s)', validators=[DataRequired(), NumberRange(min=0.1, max=10)])
    submit = SubmitField('Calcular')

# Advanced Structural Forms
class TorsionShearForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    torque = FloatField('Torque (kN.m)', validators=[DataRequired(), NumberRange(min=0.1)])
    c_distance = FloatField('Distância ao Centroide (mm)', validators=[DataRequired(), NumberRange(min=1)])
    polar_moment = FloatField('Momento Polar de Inércia (mm⁴)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Calcular')

# EulerBucklingForm moved to Advanced section below

class ContinuousBeamForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    distributed_load = FloatField('Carga Distribuída (kN/m)', validators=[DataRequired(), NumberRange(min=0.1)])
    length = FloatField('Vão (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    submit = SubmitField('Calcular')

# Hydrology Forms
class ConcentrationTimeForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    length_km = FloatField('Comprimento do Fluxo (km)', validators=[DataRequired(), NumberRange(min=0.01)])
    slope_percent = FloatField('Declividade (%)', validators=[DataRequired(), NumberRange(min=0.1, max=50)])
    method = SelectField('Método', choices=[
        ('kirpich', 'Kirpich'),
        ('nrcs', 'NRCS'),
        ('california', 'California Culverts')
    ])
    submit = SubmitField('Calcular')

class DetentionOutflowForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    inflow_rate = FloatField('Vazão de Entrada (m³/s)', validators=[DataRequired(), NumberRange(min=0.01)])
    volume_change_rate = FloatField('Taxa de Variação do Volume (m³/s)', validators=[DataRequired()])
    submit = SubmitField('Calcular')

# Steel Structures Forms
class SteelTensionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    force_kn = FloatField('Força (kN)', validators=[DataRequired()])
    cross_area_cm2 = FloatField('Área da Seção (cm²)', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Calcular')

class SteelBeamDeflectionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    load_kn = FloatField('Carga Central (kN)', validators=[DataRequired(), NumberRange(min=0.1)])
    length_m = FloatField('Vão (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    elastic_modulus = FloatField('Módulo de Elasticidade (MPa)', validators=[DataRequired(), NumberRange(min=100000)], default=200000)
    moment_inertia_cm4 = FloatField('Momento de Inércia (cm⁴)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Calcular')

# Industrial Construction Forms
class PrecastElementForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    span_m = FloatField('Vão (m)', validators=[DataRequired(), NumberRange(min=1)])
    distributed_load = FloatField('Carga Distribuída (kN/m)', validators=[DataRequired(), NumberRange(min=1)])
    element_height_cm = FloatField('Altura do Elemento (cm)', validators=[DataRequired(), NumberRange(min=10)])
    concrete_fck = FloatField('fck do Concreto (MPa)', validators=[DataRequired(), NumberRange(min=20, max=50)])
    submit = SubmitField('Calcular')

class RibbedSlabForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    rib_width_cm = FloatField('Largura da Nervura (cm)', validators=[DataRequired(), NumberRange(min=8, max=20)])
    rib_height_cm = FloatField('Altura da Nervura (cm)', validators=[DataRequired(), NumberRange(min=15, max=50)])
    flange_thickness_cm = FloatField('Espessura da Mesa (cm)', validators=[DataRequired(), NumberRange(min=4, max=10)])
    rib_spacing_cm = FloatField('Espaçamento entre Nervuras (cm)', validators=[DataRequired(), NumberRange(min=40, max=100)])
    submit = SubmitField('Calcular')

# Building Installations Forms
class VoltageDropForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    current_a = FloatField('Corrente (A)', validators=[DataRequired(), NumberRange(min=0.1)])
    resistance_ohm_km = FloatField('Resistência (Ω/km)', validators=[DataRequired(), NumberRange(min=0.001)])
    length_km = FloatField('Comprimento (km)', validators=[DataRequired(), NumberRange(min=0.001)])
    submit = SubmitField('Calcular')

class GasPipeLossForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    flow_rate_m3h = FloatField('Vazão (m³/h)', validators=[DataRequired(), NumberRange(min=0.1)])
    pipe_diameter_mm = FloatField('Diâmetro da Tubulação (mm)', validators=[DataRequired(), NumberRange(min=10)])
    length_m = FloatField('Comprimento (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    gas_density = FloatField('Densidade do Gás', validators=[Optional(), NumberRange(min=0.1, max=2)], default=0.8)
    submit = SubmitField('Calcular')

# Construction Control Forms
class ProductivityForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    quantity_executed = FloatField('Quantidade Executada', validators=[DataRequired(), NumberRange(min=0.1)])
    time_spent_hours = FloatField('Tempo Gasto (horas)', validators=[DataRequired(), NumberRange(min=0.1)])
    unit = StringField('Unidade', validators=[DataRequired()], default='m²')
    submit = SubmitField('Calcular')

class SCurveForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    total_budget = FloatField('Orçamento Total (R$)', validators=[DataRequired(), NumberRange(min=1)])
    current_time_percent = FloatField('Tempo Decorrido (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    curve_type = SelectField('Tipo de Curva', choices=[
        ('normal', 'Normal (S padrão)'),
        ('fast_start', 'Início rápido'),
        ('slow_start', 'Início lento'),
        ('linear', 'Linear')
    ])
    submit = SubmitField('Calcular')

# Sustainability Forms
class CarbonFootprintForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    material_mass_kg = FloatField('Massa do Material (kg)', validators=[DataRequired(), NumberRange(min=0.1)])
    emission_factor_kg_co2_kg = FloatField('Fator de Emissão (kg CO₂/kg)', validators=[DataRequired(), NumberRange(min=0)])
    material_type = SelectField('Tipo de Material', choices=[
        ('cement', 'Cimento'),
        ('steel', 'Aço'),
        ('aluminum', 'Alumínio'),
        ('concrete', 'Concreto'),
        ('wood', 'Madeira'),
        ('brick', 'Tijolo')
    ])
    submit = SubmitField('Calcular')

class ThermalLossForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    u_value = FloatField('Coeficiente U (W/m²·K)', validators=[DataRequired(), NumberRange(min=0.1, max=10)])
    area_m2 = FloatField('Área (m²)', validators=[DataRequired(), NumberRange(min=0.1)])
    temp_difference = FloatField('Diferença de Temperatura (K)', validators=[DataRequired(), NumberRange(min=1, max=50)])
    element_type = SelectField('Tipo de Elemento', choices=[
        ('wall_uninsulated', 'Parede sem isolamento'),
        ('wall_insulated', 'Parede com isolamento'),
        ('roof_uninsulated', 'Cobertura sem isolamento'),
        ('roof_insulated', 'Cobertura com isolamento'),
        ('window_single', 'Janela simples'),
        ('window_double', 'Janela dupla'),
        ('window_triple', 'Janela tripla')
    ])
    submit = SubmitField('Calcular')


# Advanced Structural Forms
class LoadCombinationForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    dead_load = FloatField('Carga Permanente - D (kN)', validators=[DataRequired(), NumberRange(min=0)])
    live_load = FloatField('Carga Variável - L (kN)', validators=[DataRequired(), NumberRange(min=0)])
    wind_load = FloatField('Carga de Vento - W (kN)', validators=[DataRequired(), NumberRange(min=0)])
    snow_load = FloatField('Sobrecarga - S (kN)', validators=[DataRequired(), NumberRange(min=0)])
    alpha_d = FloatField('Fator αD', validators=[Optional(), NumberRange(min=0.5, max=3.0)], default=1.2)
    alpha_l = FloatField('Fator αL', validators=[Optional(), NumberRange(min=0.5, max=3.0)], default=1.6)
    alpha_w = FloatField('Fator αW', validators=[Optional(), NumberRange(min=0.5, max=3.0)], default=1.6)
    alpha_s = FloatField('Fator αS', validators=[Optional(), NumberRange(min=0.5, max=3.0)], default=1.2)
    submit = SubmitField('Calcular')

class ConcreteShearForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    asv = FloatField('Área da Armadura Transversal - Asv (mm²)', validators=[DataRequired(), NumberRange(min=1)])
    fy = FloatField('Resistência do Aço - fy (MPa)', validators=[DataRequired(), NumberRange(min=250, max=600)])
    d = FloatField('Altura Útil - d (mm)', validators=[DataRequired(), NumberRange(min=50)])
    s = FloatField('Espaçamento - s (mm)', validators=[DataRequired(), NumberRange(min=50, max=400)])
    submit = SubmitField('Calcular')

class PunchingShearForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    tau_rd = FloatField('Tensão Resistente - τRd,c (MPa)', validators=[DataRequired(), NumberRange(min=0.1, max=5.0)])
    u1 = FloatField('Perímetro Crítico - u1 (mm)', validators=[DataRequired(), NumberRange(min=100)])
    d = FloatField('Altura Útil - d (mm)', validators=[DataRequired(), NumberRange(min=50)])
    submit = SubmitField('Calcular')

class EulerBucklingForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    e_modulus = FloatField('Módulo de Elasticidade - E (MPa)', validators=[DataRequired(), NumberRange(min=100000)])
    moment_inertia = FloatField('Momento de Inércia - I (mm⁴)', validators=[DataRequired(), NumberRange(min=1000)])
    k_factor = FloatField('Fator K (Comprimento Efetivo)', validators=[DataRequired(), NumberRange(min=0.5, max=2.0)])
    length = FloatField('Comprimento - L (mm)', validators=[DataRequired(), NumberRange(min=100)])
    submit = SubmitField('Calcular')

class LateralTorsionalBucklingForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    c1 = FloatField('Fator de Modificação C1', validators=[DataRequired(), NumberRange(min=0.5, max=2.5)])
    e_modulus = FloatField('Módulo de Elasticidade - E (MPa)', validators=[DataRequired(), NumberRange(min=100000)])
    iz = FloatField('Momento de Inércia - Iz (mm⁴)', validators=[DataRequired(), NumberRange(min=1000)])
    lb = FloatField('Comprimento Não Contraventado - Lb (mm)', validators=[DataRequired(), NumberRange(min=100)])
    g_modulus = FloatField('Módulo de Cisalhamento - G (MPa)', validators=[DataRequired(), NumberRange(min=50000)])
    j_constant = FloatField('Constante de Torção - J (mm⁴)', validators=[DataRequired(), NumberRange(min=100)])
    iw = FloatField('Constante de Empenamento - Iw (mm⁶)', validators=[DataRequired(), NumberRange(min=1000000)])
    submit = SubmitField('Calcular')

class WoodConnectionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    embedment_strength = FloatField('Resistência ao Embutimento (kN)', validators=[DataRequired(), NumberRange(min=0.1)])
    flexural_strength = FloatField('Resistência à Flexão do Conector (kN)', validators=[DataRequired(), NumberRange(min=0.1)])
    withdrawal_strength = FloatField('Resistência ao Arrancamento (kN)', validators=[DataRequired(), NumberRange(min=0.1)])
    connection_type = SelectField('Tipo de Conexão', choices=[
        ('nail', 'Prego'),
        ('bolt', 'Parafuso'),
        ('screw', 'Tirante/Parafuso Roscado')
    ])
    submit = SubmitField('Calcular')

# Advanced Geotechnical Forms
class EccentricFootingForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    normal_force = FloatField('Força Normal - N (kN)', validators=[DataRequired(), NumberRange(min=1)])
    base_width = FloatField('Largura da Base - B (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    base_length = FloatField('Comprimento da Base - L (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    eccentricity = FloatField('Excentricidade - e (m)', validators=[DataRequired()])
    submit = SubmitField('Calcular')

class InfiniteSlopeForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    cohesion = FloatField('Coesão - c\' (kPa)', validators=[DataRequired(), NumberRange(min=0)])
    unit_weight = FloatField('Peso Específico - γ (kN/m³)', validators=[DataRequired(), NumberRange(min=15, max=25)])
    depth = FloatField('Profundidade - z (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    slope_angle = FloatField('Ângulo do Talude - θ (graus)', validators=[DataRequired(), NumberRange(min=5, max=60)])
    friction_angle = FloatField('Ângulo de Atrito - φ\' (graus)', validators=[DataRequired(), NumberRange(min=0, max=45)])
    pore_pressure = FloatField('Poropressão - u (kPa)', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Calcular')

class ElasticSettlementForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    q_load = FloatField('Pressão de Contato - q (kPa)', validators=[DataRequired(), NumberRange(min=10)])
    width = FloatField('Largura da Fundação - B (m)', validators=[DataRequired(), NumberRange(min=0.5)])
    elastic_modulus = FloatField('Módulo de Elasticidade - E (kPa)', validators=[DataRequired(), NumberRange(min=1000)])
    poisson_ratio = FloatField('Coeficiente de Poisson - ν', validators=[DataRequired(), NumberRange(min=0.1, max=0.49)])
    influence_factor = FloatField('Fator de Influência - Is', validators=[Optional(), NumberRange(min=0.1, max=2.0)], default=1.0)
    submit = SubmitField('Calcular')

class PileCapacityForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    qp = FloatField('Resistência de Ponta - qp (kPa)', validators=[DataRequired(), NumberRange(min=100)])
    ap = FloatField('Área da Ponta - Ap (m²)', validators=[DataRequired(), NumberRange(min=0.01)])
    fs_values = StringField('Atritos Laterais - fs (kPa, separado por vírgula)', validators=[DataRequired()])
    as_values = StringField('Áreas Laterais - As (m², separado por vírgula)', validators=[DataRequired()])
    safety_factor = FloatField('Fator de Segurança', validators=[Optional(), NumberRange(min=1.5, max=5.0)], default=2.5)
    submit = SubmitField('Calcular')

# Advanced Hydrology Forms
class SCSRunoffForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    precipitation = FloatField('Precipitação - P (mm)', validators=[DataRequired(), NumberRange(min=0.1)])
    curve_number = IntegerField('Curve Number - CN', validators=[DataRequired(), NumberRange(min=30, max=100)])
    submit = SubmitField('Calcular')

class KirpichTimeForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    length_km = FloatField('Comprimento do Talvegue - L (km)', validators=[DataRequired(), NumberRange(min=0.1)])
    slope_percent = FloatField('Declividade - S (%)', validators=[DataRequired(), NumberRange(min=0.1, max=50)])
    submit = SubmitField('Calcular')

class ChannelEnergyForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    depth = FloatField('Profundidade - y (m)', validators=[DataRequired(), NumberRange(min=0.01)])
    velocity = FloatField('Velocidade - v (m/s)', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Calcular')

class WaterHammerForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    density = FloatField('Densidade da Água - ρ (kg/m³)', validators=[Optional(), NumberRange(min=900, max=1100)], default=1000)
    wave_velocity = FloatField('Velocidade da Onda - a (m/s)', validators=[DataRequired(), NumberRange(min=800, max=1500)])
    velocity_change = FloatField('Variação de Velocidade - ΔV (m/s)', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Calcular')

class PumpSimilarityForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    n1 = FloatField('Rotação Inicial - N1 (rpm)', validators=[DataRequired(), NumberRange(min=100)])
    q1 = FloatField('Vazão Inicial - Q1 (L/s)', validators=[DataRequired(), NumberRange(min=1)])
    h1 = FloatField('Altura Manométrica Inicial - H1 (m)', validators=[DataRequired(), NumberRange(min=1)])
    p1 = FloatField('Potência Inicial - P1 (kW)', validators=[DataRequired(), NumberRange(min=0.1)])
    n2 = FloatField('Nova Rotação - N2 (rpm)', validators=[DataRequired(), NumberRange(min=100)])
    submit = SubmitField('Calcular')

# Advanced Pavement Forms
class ESALForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    axle_loads = StringField('Número de Eixos por Tipo (separado por vírgula)', validators=[DataRequired()])
    equivalence_factors = StringField('Fatores de Equivalência (separado por vírgula)', validators=[DataRequired()])
    submit = SubmitField('Calcular')

class TrafficGrowthForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    adt0 = FloatField('Tráfego Inicial - ADT0 (veículos/dia)', validators=[DataRequired(), NumberRange(min=10)])
    growth_rate_pct = FloatField('Taxa de Crescimento - r (%/ano)', validators=[DataRequired(), NumberRange(min=0, max=20)])
    period_years = IntegerField('Período - n (anos)', validators=[DataRequired(), NumberRange(min=1, max=30)])
    lane_factor = FloatField('Fator de Faixa - LF', validators=[Optional(), NumberRange(min=0.3, max=1.0)], default=1.0)
    directional_factor = FloatField('Fator Direcional - DL', validators=[Optional(), NumberRange(min=0.3, max=0.7)], default=0.5)
    submit = SubmitField('Calcular')

class StoppingDistanceForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    speed_kmh = FloatField('Velocidade - v (km/h)', validators=[DataRequired(), NumberRange(min=20, max=150)])
    reaction_time_s = FloatField('Tempo de Reação - tr (s)', validators=[Optional(), NumberRange(min=0.5, max=3.0)], default=2.5)
    friction_coeff = FloatField('Coeficiente de Atrito - f', validators=[DataRequired(), NumberRange(min=0.1, max=0.8)])
    grade_pct = FloatField('Rampa - G (% - positivo subida)', validators=[Optional(), NumberRange(min=-15, max=15)], default=0)
    submit = SubmitField('Calcular')

# Building Systems Forms
class LightingDesignForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    illuminance_target = FloatField('Iluminância Requerida - E (lux)', validators=[DataRequired(), NumberRange(min=50, max=2000)])
    area_m2 = FloatField('Área - A (m²)', validators=[DataRequired(), NumberRange(min=1)])
    lamp_lumens = FloatField('Lúmens por Lâmpada - Φlamp (lm)', validators=[DataRequired(), NumberRange(min=500)])
    utilization_factor = FloatField('Fator de Utilização - UF', validators=[Optional(), NumberRange(min=0.3, max=0.8)], default=0.6)
    maintenance_factor = FloatField('Fator de Manutenção - MF', validators=[Optional(), NumberRange(min=0.6, max=1.0)], default=0.8)
    submit = SubmitField('Calcular')

class ThermalTransmissionForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    u_value = FloatField('Coeficiente U (W/m²·K)', validators=[DataRequired(), NumberRange(min=0.1, max=10)])
    area_m2 = FloatField('Área - A (m²)', validators=[DataRequired(), NumberRange(min=0.1)])
    temp_difference_k = FloatField('Diferença de Temperatura - ΔT (K)', validators=[DataRequired(), NumberRange(min=1, max=50)])
    submit = SubmitField('Calcular')

class ReverberationForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    volume_m3 = FloatField('Volume - V (m³)', validators=[DataRequired(), NumberRange(min=10)])
    absorption_coefficients = StringField('Coeficientes de Absorção α (separado por vírgula)', validators=[DataRequired()])
    surface_areas = StringField('Áreas das Superfícies S (m², separado por vírgula)', validators=[DataRequired()])
    submit = SubmitField('Calcular')

class GutterSizingForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    rainfall_intensity = FloatField('Intensidade de Chuva - i (L/s·m²)', validators=[DataRequired(), NumberRange(min=0.001, max=0.01)])
    catchment_area = FloatField('Área de Captação - A (m²)', validators=[DataRequired(), NumberRange(min=10)])
    velocity_factor = FloatField('Fator de Velocidade', validators=[Optional(), NumberRange(min=0.5, max=1.5)], default=1.0)
    submit = SubmitField('Calcular')

class StairBlondelForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    riser_height_cm = FloatField('Altura do Degrau - h (cm)', validators=[DataRequired(), NumberRange(min=15, max=20)])
    tread_depth_cm = FloatField('Profundidade do Degrau - b (cm)', validators=[DataRequired(), NumberRange(min=25, max=35)])
    submit = SubmitField('Calcular')

class PrismoidalVolumeForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    area1 = FloatField('Área Inicial - A1 (m²)', validators=[DataRequired(), NumberRange(min=0)])
    area_middle = FloatField('Área do Meio - Am (m²)', validators=[DataRequired(), NumberRange(min=0)])
    area2 = FloatField('Área Final - A2 (m²)', validators=[DataRequired(), NumberRange(min=0)])
    length = FloatField('Comprimento - L (m)', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Calcular')

# Economic Forms
class NPVForm(FlaskForm):
    name = StringField('Nome do Cálculo', validators=[DataRequired()])
    cash_flows = StringField('Fluxos de Caixa (separado por vírgula)', validators=[DataRequired()], 
                            render_kw={"placeholder": "Ex: 1000,1200,1500,800"})
    discount_rate_pct = FloatField('Taxa de Desconto - i (%)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    initial_investment = FloatField('Investimento Inicial (R$)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calcular')
