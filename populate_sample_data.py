#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
Inclui materiais básicos e composições SINAPI simplificadas
"""

from app import app, db
from models import Material, CostComposition

def populate_materials():
    """Adiciona materiais básicos ao banco"""
    materials_data = [
        # Cimentos e aglomerantes
        {'name': 'Cimento Portland CP II-Z-32', 'category': 'cimento', 'unit': 'kg', 'unit_cost': 0.85, 'supplier': 'Votorantim'},
        {'name': 'Cal hidratada CH-I', 'category': 'cimento', 'unit': 'kg', 'unit_cost': 0.45, 'supplier': 'Itaú'},
        
        # Agregados
        {'name': 'Areia média lavada', 'category': 'areia', 'unit': 'm³', 'unit_cost': 65.00, 'supplier': 'Pedreira São José'},
        {'name': 'Areia fina lavada', 'category': 'areia', 'unit': 'm³', 'unit_cost': 68.00, 'supplier': 'Pedreira São José'},
        {'name': 'Brita 0 (4,8 a 9,5mm)', 'category': 'brita', 'unit': 'm³', 'unit_cost': 75.00, 'supplier': 'Pedreira São José'},
        {'name': 'Brita 1 (9,5 a 19mm)', 'category': 'brita', 'unit': 'm³', 'unit_cost': 80.00, 'supplier': 'Pedreira São José'},
        {'name': 'Pedrisco', 'category': 'brita', 'unit': 'm³', 'unit_cost': 82.00, 'supplier': 'Pedreira São José'},
        
        # Aços
        {'name': 'Aço CA-50 Ø 6,3mm', 'category': 'aco', 'unit': 'kg', 'unit_cost': 6.80, 'supplier': 'Gerdau'},
        {'name': 'Aço CA-50 Ø 8,0mm', 'category': 'aco', 'unit': 'kg', 'unit_cost': 6.75, 'supplier': 'Gerdau'},
        {'name': 'Aço CA-50 Ø 10,0mm', 'category': 'aco', 'unit': 'kg', 'unit_cost': 6.70, 'supplier': 'Gerdau'},
        {'name': 'Aço CA-50 Ø 12,5mm', 'category': 'aco', 'unit': 'kg', 'unit_cost': 6.65, 'supplier': 'Gerdau'},
        {'name': 'Tela soldada Q138', 'category': 'aco', 'unit': 'm²', 'unit_cost': 12.50, 'supplier': 'Gerdau'},
        
        # Blocos e tijolos
        {'name': 'Bloco cerâmico 9x19x19cm', 'category': 'blocos', 'unit': 'un', 'unit_cost': 1.15, 'supplier': 'Cerâmica Paulista'},
        {'name': 'Bloco cerâmico 14x19x39cm', 'category': 'blocos', 'unit': 'un', 'unit_cost': 1.25, 'supplier': 'Cerâmica Paulista'},
        {'name': 'Bloco concreto 14x19x39cm', 'category': 'blocos', 'unit': 'un', 'unit_cost': 3.20, 'supplier': 'Tatu Pré-moldados'},
        
        # Cerâmica e acabamentos
        {'name': 'Piso cerâmico 45x45cm', 'category': 'ceramica', 'unit': 'm²', 'unit_cost': 45.00, 'supplier': 'Portobello'},
        {'name': 'Azulejo 20x30cm branco', 'category': 'ceramica', 'unit': 'm²', 'unit_cost': 35.00, 'supplier': 'Eliane'},
        {'name': 'Rejunte flexível', 'category': 'ceramica', 'unit': 'kg', 'unit_cost': 8.50, 'supplier': 'Quartzolit'},
        {'name': 'Argamassa colante AC-I', 'category': 'ceramica', 'unit': 'kg', 'unit_cost': 0.60, 'supplier': 'Quartzolit'},
        
        # Tubulações
        {'name': 'Tubo PVC soldável Ø 25mm', 'category': 'tubulacao', 'unit': 'm', 'unit_cost': 8.50, 'supplier': 'Tigre'},
        {'name': 'Tubo PVC soldável Ø 32mm', 'category': 'tubulacao', 'unit': 'm', 'unit_cost': 12.80, 'supplier': 'Tigre'},
        {'name': 'Tubo PVC esgoto Ø 100mm', 'category': 'tubulacao', 'unit': 'm', 'unit_cost': 22.50, 'supplier': 'Tigre'},
        
        # Tintas
        {'name': 'Tinta acrílica branca', 'category': 'tinta', 'unit': 'L', 'unit_cost': 35.00, 'supplier': 'Suvinil'},
        {'name': 'Tinta PVA branca', 'category': 'tinta', 'unit': 'L', 'unit_cost': 28.00, 'supplier': 'Coral'},
        {'name': 'Primer para parede', 'category': 'tinta', 'unit': 'L', 'unit_cost': 32.00, 'supplier': 'Suvinil'},
        
        # Outros
        {'name': 'Água', 'category': 'outros', 'unit': 'L', 'unit_cost': 0.005, 'supplier': 'SABESP'},
        {'name': 'Aditivo plastificante', 'category': 'outros', 'unit': 'L', 'unit_cost': 12.00, 'supplier': 'Vedacit'}
    ]
    
    for material_data in materials_data:
        existing = Material.query.filter_by(name=material_data['name']).first()
        if not existing:
            material = Material(**material_data)
            db.session.add(material)
    
    print(f"Adicionados {len(materials_data)} materiais básicos")

def populate_compositions():
    """Adiciona composições básicas baseadas no SINAPI"""
    compositions_data = [
        {
            'sinapi_code': '92885',
            'description': 'Concreto FCK 25 MPa, com brita 1 e 2, slump 8±1cm',
            'unit': 'm³',
            'unit_cost': 480.50,
            'productivity': 4.5,
            'category': 'estrutura',
            'materials_cost': 320.00,
            'labor_cost': 120.50,
            'equipment_cost': 40.00
        },
        {
            'sinapi_code': '92869',
            'description': 'Concreto FCK 20 MPa, com brita 1, slump 8±1cm',
            'unit': 'm³',
            'unit_cost': 445.20,
            'productivity': 4.2,
            'category': 'estrutura',
            'materials_cost': 295.00,
            'labor_cost': 115.20,
            'equipment_cost': 35.00
        },
        {
            'sinapi_code': '87487',
            'description': 'Alvenaria de vedação com bloco cerâmico 14x19x39cm',
            'unit': 'm²',
            'unit_cost': 85.60,
            'productivity': 0.8,
            'category': 'estrutura',
            'materials_cost': 62.40,
            'labor_cost': 18.20,
            'equipment_cost': 5.00
        },
        {
            'sinapi_code': '87269',
            'description': 'Piso cerâmico 45x45cm, assentado com argamassa colante',
            'unit': 'm²',
            'unit_cost': 75.80,
            'productivity': 0.6,
            'category': 'acabamento',
            'materials_cost': 58.30,
            'labor_cost': 15.50,
            'equipment_cost': 2.00
        },
        {
            'sinapi_code': '87755',
            'description': 'Contrapiso em concreto, espessura 5cm',
            'unit': 'm²',
            'unit_cost': 35.90,
            'productivity': 0.4,
            'category': 'estrutura',
            'materials_cost': 25.40,
            'labor_cost': 8.50,
            'equipment_cost': 2.00
        },
        {
            'sinapi_code': '88309',
            'description': 'Chapisco em parede, argamassa 1:3',
            'unit': 'm²',
            'unit_cost': 8.20,
            'productivity': 0.15,
            'category': 'acabamento',
            'materials_cost': 4.50,
            'labor_cost': 3.20,
            'equipment_cost': 0.50
        },
        {
            'sinapi_code': '88340',
            'description': 'Emboço em parede, argamassa 1:2:8',
            'unit': 'm²',
            'unit_cost': 18.50,
            'productivity': 0.35,
            'category': 'acabamento',
            'materials_cost': 12.20,
            'labor_cost': 5.80,
            'equipment_cost': 0.50
        },
        {
            'sinapi_code': '88348',
            'description': 'Reboco em parede, argamassa 1:4,5',
            'unit': 'm²',
            'unit_cost': 12.80,
            'productivity': 0.25,
            'category': 'acabamento',
            'materials_cost': 8.20,
            'labor_cost': 4.10,
            'equipment_cost': 0.50
        },
        {
            'sinapi_code': '74209',
            'description': 'Escavação manual em solo de 1ª categoria',
            'unit': 'm³',
            'unit_cost': 42.50,
            'productivity': 2.1,
            'category': 'movimento_terra',
            'materials_cost': 0.00,
            'labor_cost': 40.50,
            'equipment_cost': 2.00
        },
        {
            'tcpo_code': '02.010.001',
            'description': 'Forma de madeira para concreto, uso 5 vezes',
            'unit': 'm²',
            'unit_cost': 55.20,
            'productivity': 1.2,
            'category': 'estrutura',
            'materials_cost': 32.80,
            'labor_cost': 20.40,
            'equipment_cost': 2.00
        },
        {
            'tcpo_code': '04.001.001',
            'description': 'Armadura aço CA-50, diâmetro 10mm',
            'unit': 'kg',
            'unit_cost': 8.90,
            'productivity': 0.12,
            'category': 'estrutura',
            'materials_cost': 6.70,
            'labor_cost': 2.20,
            'equipment_cost': 0.00
        },
        {
            'description': 'Fundação sapata corrida, concreto FCK 15',
            'unit': 'm³',
            'unit_cost': 380.00,
            'productivity': 5.5,
            'category': 'fundacao',
            'materials_cost': 250.00,
            'labor_cost': 105.00,
            'equipment_cost': 25.00
        }
    ]
    
    for comp_data in compositions_data:
        existing = None
        if comp_data.get('sinapi_code'):
            existing = CostComposition.query.filter_by(sinapi_code=comp_data['sinapi_code']).first()
        elif comp_data.get('tcpo_code'):
            existing = CostComposition.query.filter_by(tcpo_code=comp_data['tcpo_code']).first()
        else:
            existing = CostComposition.query.filter_by(description=comp_data['description']).first()
        
        if not existing:
            composition = CostComposition(**comp_data)
            db.session.add(composition)
    
    print(f"Adicionadas {len(compositions_data)} composições de custo")

def main():
    """Função principal para popular dados de exemplo"""
    with app.app_context():
        print("Populando banco de dados com dados de exemplo...")
        
        try:
            populate_materials()
            populate_compositions()
            
            db.session.commit()
            print("✅ Dados de exemplo adicionados com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao adicionar dados: {e}")
            raise

if __name__ == '__main__':
    main()