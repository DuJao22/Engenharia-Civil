import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

class BudgetCalculator:
    """Calculadora para orçamentos de obra com composições SINAPI/TCPO"""
    
    # Composições básicas pré-definidas (SINAPI simplificado)
    DEFAULT_COMPOSITIONS = {
        'concreto_fck25': {
            'description': 'Concreto FCK 25 MPa',
            'unit': 'm³',
            'materials': {
                'cimento': {'quantity': 350, 'unit': 'kg'},
                'areia': {'quantity': 0.55, 'unit': 'm³'},
                'brita': {'quantity': 0.9, 'unit': 'm³'},
                'agua': {'quantity': 180, 'unit': 'L'}
            },
            'labor_hours': 4.5,  # horas/m³
            'equipment_hours': 1.2  # horas/m³
        },
        'alvenaria_bloco': {
            'description': 'Alvenaria com bloco cerâmico 14x19x39cm',
            'unit': 'm²',
            'materials': {
                'bloco_ceramico': {'quantity': 13, 'unit': 'un'},
                'argamassa': {'quantity': 0.012, 'unit': 'm³'},
                'aco_ca50': {'quantity': 1.5, 'unit': 'kg'}
            },
            'labor_hours': 0.8,  # horas/m²
            'equipment_hours': 0
        },
        'piso_ceramico': {
            'description': 'Piso cerâmico 45x45cm',
            'unit': 'm²',
            'materials': {
                'ceramica': {'quantity': 1.05, 'unit': 'm²'},
                'argamassa_cola': {'quantity': 5, 'unit': 'kg'},
                'rejunte': {'quantity': 0.5, 'unit': 'kg'}
            },
            'labor_hours': 0.6,  # horas/m²
            'equipment_hours': 0
        }
    }
    
    # Preços base dos materiais (R$) - atualização simulada SINAPI
    MATERIAL_PRICES = {
        'cimento': 0.85,  # R$/kg
        'areia': 65.0,    # R$/m³
        'brita': 80.0,    # R$/m³
        'agua': 0.005,    # R$/L
        'bloco_ceramico': 1.25,  # R$/un
        'argamassa': 180.0,  # R$/m³
        'aco_ca50': 6.80,    # R$/kg
        'ceramica': 45.0,    # R$/m²
        'argamassa_cola': 12.0,  # R$/kg
        'rejunte': 8.50      # R$/kg
    }
    
    LABOR_COST = 25.0  # R$/hora
    EQUIPMENT_COST = 15.0  # R$/hora
    
    def calculate_composition_cost(self, composition_key: str) -> Dict[str, Any]:
        """Calcula o custo de uma composição SINAPI"""
        if composition_key not in self.DEFAULT_COMPOSITIONS:
            raise ValueError(f"Composição '{composition_key}' não encontrada")
        
        comp = self.DEFAULT_COMPOSITIONS[composition_key]
        materials_cost = 0.0
        
        # Calcula custo dos materiais
        for material, data in comp['materials'].items():
            unit_price = self.MATERIAL_PRICES.get(material, 0)
            materials_cost += data['quantity'] * unit_price
        
        # Calcula custo de mão de obra
        labor_cost = comp['labor_hours'] * self.LABOR_COST
        
        # Calcula custo de equipamentos
        equipment_cost = comp['equipment_hours'] * self.EQUIPMENT_COST
        
        # Custo total unitário
        total_unit_cost = materials_cost + labor_cost + equipment_cost
        
        return {
            'description': comp['description'],
            'unit': comp['unit'],
            'materials_cost': round(materials_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'equipment_cost': round(equipment_cost, 2),
            'total_unit_cost': round(total_unit_cost, 2),
            'breakdown': comp['materials']
        }
    
    def calculate_budget_totals(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula os totais do orçamento"""
        total_materials = sum(item.get('materials_cost', 0) * item.get('quantity', 0) for item in items)
        total_labor = sum(item.get('labor_cost', 0) * item.get('quantity', 0) for item in items)
        total_equipment = sum(item.get('equipment_cost', 0) * item.get('quantity', 0) for item in items)
        subtotal = sum(item.get('total_cost', 0) for item in items)
        
        return {
            'total_materials': round(total_materials, 2),
            'total_labor': round(total_labor, 2),
            'total_equipment': round(total_equipment, 2),
            'subtotal': round(subtotal, 2)
        }
    
    def apply_profit_margin(self, subtotal: float, margin_percent: float) -> Dict[str, float]:
        """Aplica margem de lucro ao orçamento"""
        profit = subtotal * (margin_percent / 100)
        total_with_profit = subtotal + profit
        
        return {
            'subtotal': round(subtotal, 2),
            'profit_margin': round(margin_percent, 2),
            'profit_value': round(profit, 2),
            'total': round(total_with_profit, 2)
        }

class ScheduleCalculator:
    """Calculadora de cronogramas usando CPM (Critical Path Method)"""
    
    def __init__(self):
        self.activities = []
    
    def add_activity(self, activity_id: int, name: str, duration: int, predecessors: Optional[List[int]] = None):
        """Adiciona uma atividade ao cronograma"""
        self.activities.append({
            'id': activity_id,
            'name': name,
            'duration': duration,
            'predecessors': predecessors if predecessors is not None else [],
            'early_start': 0,
            'early_finish': 0,
            'late_start': 0,
            'late_finish': 0,
            'slack': 0,
            'is_critical': False
        })
    
    def calculate_cpm(self) -> Dict[str, Any]:
        """Calcula o caminho crítico usando CPM"""
        # Forward pass - cálculo dos tempos mais cedo
        for activity in self.activities:
            if not activity['predecessors']:
                activity['early_start'] = 0
            else:
                max_finish = 0
                for pred_id in activity['predecessors']:
                    pred = next((a for a in self.activities if a['id'] == pred_id), None)
                    if pred:
                        max_finish = max(max_finish, pred['early_finish'])
                activity['early_start'] = max_finish
            
            activity['early_finish'] = activity['early_start'] + activity['duration']
        
        # Determina a duração total do projeto
        project_duration = max(a['early_finish'] for a in self.activities)
        
        # Backward pass - cálculo dos tempos mais tarde
        for activity in reversed(self.activities):
            # Encontra sucessores
            successors = [a for a in self.activities if activity['id'] in a['predecessors']]
            
            if not successors:
                activity['late_finish'] = project_duration
            else:
                min_start = min(succ['late_start'] for succ in successors)
                activity['late_finish'] = min_start
            
            activity['late_start'] = activity['late_finish'] - activity['duration']
            activity['slack'] = activity['late_start'] - activity['early_start']
            activity['is_critical'] = activity['slack'] == 0
        
        # Identifica o caminho crítico
        critical_path = [a['id'] for a in self.activities if a['is_critical']]
        
        return {
            'activities': self.activities,
            'project_duration': project_duration,
            'critical_path': critical_path,
            'critical_activities': [a for a in self.activities if a['is_critical']]
        }
    
    def generate_gantt_data(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Gera dados para o gráfico de Gantt"""
        gantt_data = []
        
        for activity in self.activities:
            activity_start = start_date + timedelta(days=activity['early_start'])
            activity_end = start_date + timedelta(days=activity['early_finish'])
            
            gantt_data.append({
                'id': activity['id'],
                'name': activity['name'],
                'start_date': activity_start.strftime('%Y-%m-%d'),
                'end_date': activity_end.strftime('%Y-%m-%d'),
                'duration': activity['duration'],
                'is_critical': activity['is_critical'],
                'slack': activity['slack'],
                'predecessors': activity['predecessors']
            })
        
        return gantt_data

class ProductivityCalculator:
    """Calculadora de produtividade e acompanhamento de obra"""
    
    @staticmethod
    def calculate_s_curve(activities: List[Dict[str, Any]], start_date: datetime) -> List[Dict[str, Any]]:
        """Calcula a curva S do projeto (custo acumulado ao longo do tempo)"""
        daily_costs = {}
        total_cost = sum(a.get('cost', 0) for a in activities)
        
        for activity in activities:
            cost_per_day = activity.get('cost', 0) / activity.get('duration', 1)
            activity_start = start_date + timedelta(days=activity.get('early_start', 0))
            
            for day in range(activity.get('duration', 0)):
                current_date = activity_start + timedelta(days=day)
                date_str = current_date.strftime('%Y-%m-%d')
                
                if date_str not in daily_costs:
                    daily_costs[date_str] = 0
                daily_costs[date_str] += cost_per_day
        
        # Calcula custo acumulado
        cumulative_cost = 0
        s_curve_data = []
        
        for date_str in sorted(daily_costs.keys()):
            cumulative_cost += daily_costs[date_str]
            percentage = (cumulative_cost / total_cost) * 100 if total_cost > 0 else 0
            
            s_curve_data.append({
                'date': date_str,
                'daily_cost': round(daily_costs[date_str], 2),
                'cumulative_cost': round(cumulative_cost, 2),
                'percentage': round(percentage, 2)
            })
        
        return s_curve_data
    
    @staticmethod
    def calculate_progress_metrics(planned_cost: float, actual_cost: float, 
                                 earned_value: float) -> Dict[str, float]:
        """Calcula métricas de desempenho do projeto (EVM - Earned Value Management)"""
        # Variações
        cost_variance = earned_value - actual_cost  # CV
        schedule_variance = earned_value - planned_cost  # SV
        
        # Índices de desempenho
        cost_performance_index = earned_value / actual_cost if actual_cost > 0 else 0  # CPI
        schedule_performance_index = earned_value / planned_cost if planned_cost > 0 else 0  # SPI
        
        return {
            'cost_variance': round(cost_variance, 2),
            'schedule_variance': round(schedule_variance, 2),
            'cost_performance_index': round(cost_performance_index, 3),
            'schedule_performance_index': round(schedule_performance_index, 3),
            'budget_efficiency': round((cost_performance_index * 100) - 100, 1),
            'schedule_efficiency': round((schedule_performance_index * 100) - 100, 1)
        }

class ReportGenerator:
    """Gerador de relatórios em PDF"""
    
    @staticmethod
    def generate_budget_report(project_data: Dict[str, Any], budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de orçamento (retorna estrutura de dados)"""
        return {
            'report_type': 'budget',
            'project_name': project_data.get('name', ''),
            'client': project_data.get('client_name', ''),
            'total_cost': budget_data.get('total', 0),
            'items_count': len(budget_data.get('items', [])),
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'status': 'ready_for_pdf_generation'
        }
    
    @staticmethod
    def generate_budget_pdf(project_data: Dict[str, Any], budget_data: Dict[str, Any], items: List[Any]) -> BytesIO:
        """Gera PDF do relatório de orçamento"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=20*mm, bottomMargin=20*mm)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        
        # Conteúdo do PDF
        story = []
        
        # Título
        story.append(Paragraph("RELATÓRIO DE ORÇAMENTO", title_style))
        story.append(Spacer(1, 20))
        
        # Informações do Projeto
        story.append(Paragraph("INFORMAÇÕES DO PROJETO", header_style))
        
        project_info = [
            ['Projeto:', project_data.get('name', 'N/A')],
            ['Cliente:', project_data.get('client_name', 'N/A')],
            ['Responsável Técnico:', project_data.get('technical_responsible', 'N/A')],
            ['CREA:', project_data.get('crea_number', 'N/A')],
            ['Orçamento:', budget_data.get('name', 'N/A')],
            ['Versão:', budget_data.get('version', 'N/A')],
            ['Data de Geração:', datetime.now().strftime('%d/%m/%Y %H:%M')]
        ]
        
        project_table = Table(project_info, colWidths=[4*mm*10, 10*mm*10])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        story.append(project_table)
        story.append(Spacer(1, 20))
        
        # Resumo Financeiro
        story.append(Paragraph("RESUMO FINANCEIRO", header_style))
        
        financial_info = [
            ['Total do Orçamento:', f"R$ {budget_data.get('total_cost', 0):.2f}"],
            ['Margem de Lucro:', f"{budget_data.get('profit_margin', 0):.1f}%"],
            ['Total de Itens:', str(len(items))],
            ['Status:', budget_data.get('status', 'N/A').title()]
        ]
        
        financial_table = Table(financial_info, colWidths=[4*mm*10, 10*mm*10])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        story.append(financial_table)
        story.append(Spacer(1, 20))
        
        # Itens do Orçamento
        if items:
            story.append(Paragraph("ITENS DO ORÇAMENTO", header_style))
            
            # Cabeçalho da tabela
            table_data = [['Item', 'Descrição', 'Qtd', 'Unidade', 'Valor Unit.', 'Total']]
            
            # Dados dos itens
            for i, item in enumerate(items, 1):
                table_data.append([
                    str(i),
                    item.description[:40] + '...' if len(item.description) > 40 else item.description,
                    f"{item.quantity:.2f}",
                    item.unit,
                    f"R$ {item.unit_cost:.2f}",
                    f"R$ {item.total_cost:.2f}"
                ])
            
            # Total
            table_data.append([
                '', '', '', '', 'TOTAL GERAL:',
                f"R$ {budget_data.get('total_cost', 0):.2f}"
            ])
            
            items_table = Table(table_data, colWidths=[1*mm*6, 7*mm*6, 1.5*mm*6, 1.5*mm*6, 2.5*mm*6, 2.5*mm*6])
            items_table.setStyle(TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Dados
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # Item
                ('ALIGN', (2, 1), (2, -2), 'RIGHT'),   # Quantidade
                ('ALIGN', (3, 1), (3, -2), 'CENTER'),  # Unidade
                ('ALIGN', (4, 1), (-1, -2), 'RIGHT'),  # Valores
                
                # Total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('ALIGN', (4, -1), (-1, -1), 'RIGHT'),
                
                # Bordas
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4)
            ]))
            
            story.append(items_table)
        
        # Observações
        if budget_data.get('description'):
            story.append(Spacer(1, 20))
            story.append(Paragraph("OBSERVAÇÕES", header_style))
            story.append(Paragraph(budget_data.get('description', ''), normal_style))
        
        # Rodapé
        story.append(Spacer(1, 30))
        footer_text = f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - Sistema de Engenharia Civil"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=1
        )
        story.append(Paragraph(footer_text, footer_style))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_schedule_report(project_data: Dict[str, Any], schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de cronograma (retorna estrutura de dados)"""
        return {
            'report_type': 'schedule',
            'project_name': project_data.get('name', ''),
            'duration': schedule_data.get('project_duration', 0),
            'critical_activities': len(schedule_data.get('critical_path', [])),
            'total_activities': len(schedule_data.get('activities', [])),
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'status': 'ready_for_pdf_generation'
        }