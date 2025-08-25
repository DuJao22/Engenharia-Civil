import math
import json

class StructuralCalculations:
    @staticmethod
    def calculate_beam_moment(length, load_value, load_type):
        """Calculate maximum moment for simply supported beam"""
        if load_type == 'uniform':
            # For uniformly distributed load: M_max = wL²/8
            moment_max = (load_value * length**2) / 8
            shear_max = (load_value * length) / 2
        elif load_type == 'point':
            # For point load at center: M_max = PL/4
            moment_max = (load_value * length) / 4
            shear_max = load_value / 2
        else:
            raise ValueError("Invalid load type")
        
        return {
            'moment_max': round(moment_max, 2),
            'shear_max': round(shear_max, 2),
            'length': length,
            'load_value': load_value,
            'load_type': load_type
        }

class ConcreteCalculations:
    @staticmethod
    def calculate_concrete_beam(width, height, moment, fck, fyk):
        """Basic reinforced concrete beam design"""
        # Convert units
        width_m = width / 100  # cm to m
        height_m = height / 100  # cm to m
        d = height_m - 0.05  # effective depth (assuming 5cm cover)
        
        # Material properties
        fcd = fck / 1.4  # Design compressive strength
        fyd = fyk / 1.15  # Design yield strength
        
        # Calculate required steel area (simplified method)
        # Assuming z = 0.9*d for simplification
        z = 0.9 * d
        # Steel area calculation: As = M/(fyd*z) with unit conversion
        # moment(kN.m)*1000 → N.m; fyd(MPa) → N/mm²; z(m) → result in mm²
        As_required = (moment * 1000) / (fyd * z)  # mm²
        
        # Minimum steel area (0.15% of concrete area)
        As_min = 0.0015 * width_m * height_m * 1000000  # mm²
        
        # Final steel area
        As_final = max(As_required, As_min)
        
        # Steel ratio
        steel_ratio = (As_final / 1000000) / (width_m * d) * 100  # %
        
        return {
            'As_required': round(As_required, 2),
            'As_min': round(As_min, 2),
            'As_final': round(As_final, 2),
            'steel_ratio': round(steel_ratio, 3),
            'effective_depth': round(d * 100, 1),  # cm
            'fcd': round(fcd, 2),
            'fyd': round(fyd, 2)
        }

class HydraulicsCalculations:
    @staticmethod
    def calculate_pipe_flow(diameter_mm, length_m, flow_rate_ls, roughness_mm):
        """Calculate head loss using Darcy-Weisbach equation"""
        # Convert units
        diameter = diameter_mm / 1000  # mm to m
        flow_rate = flow_rate_ls / 1000  # L/s to m³/s
        roughness = roughness_mm / 1000  # mm to m
        
        # Calculate velocity
        area = math.pi * (diameter/2)**2
        velocity = flow_rate / area
        
        # Reynolds number (assuming water at 20°C, ν ≈ 1.0e-6 m²/s)
        kinematic_viscosity = 1.0e-6
        reynolds = velocity * diameter / kinematic_viscosity
        
        # Friction factor using Swamee-Jain equation
        relative_roughness = roughness / diameter
        friction_factor = 0.25 / (math.log10(relative_roughness/3.7 + 5.74/(reynolds**0.9)))**2
        
        # Head loss
        g = 9.81  # gravity
        head_loss = friction_factor * (length_m / diameter) * (velocity**2) / (2 * g)
        
        return {
            'velocity': round(velocity, 3),
            'reynolds': round(reynolds, 0),
            'friction_factor': round(friction_factor, 4),
            'head_loss': round(head_loss, 3),
            'flow_rate_ms': round(flow_rate, 6),
            'area': round(area * 10000, 2)  # cm²
        }

class FoundationCalculations:
    @staticmethod
    def calculate_bearing_capacity(width, cohesion, friction_angle, unit_weight, depth):
        """Calculate ultimate bearing capacity using Terzaghi equation"""
        phi_rad = math.radians(friction_angle)
        
        # Terzaghi bearing capacity factors
        Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.pi/4 + phi_rad/2))**2
        Nc = (Nq - 1) / math.tan(phi_rad) if friction_angle > 0 else 5.14
        Ngamma = 2 * (Nq + 1) * math.tan(phi_rad)
        
        # Ultimate bearing capacity
        q_ult = cohesion * Nc + unit_weight * depth * Nq + 0.5 * unit_weight * width * Ngamma
        
        # Allowable bearing capacity (FS = 3)
        safety_factor = 3
        q_allow = q_ult / safety_factor
        
        return {
            'q_ultimate': round(q_ult, 2),
            'q_allowable': round(q_allow, 2),
            'safety_factor': safety_factor,
            'Nc': round(Nc, 2),
            'Nq': round(Nq, 2),
            'Ngamma': round(Ngamma, 2)
        }

class TopographyCalculations:
    @staticmethod
    def calculate_area_shoelace(coordinates):
        """Calculate area of polygon using shoelace formula"""
        if len(coordinates) < 3:
            raise ValueError("Pelo menos 3 pontos são necessários")
        
        n = len(coordinates)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += coordinates[i][0] * coordinates[j][1]
            area -= coordinates[j][0] * coordinates[i][1]
        
        area = abs(area) / 2.0
        
        # Calculate perimeter
        perimeter = 0.0
        for i in range(n):
            j = (i + 1) % n
            dx = coordinates[j][0] - coordinates[i][0]
            dy = coordinates[j][1] - coordinates[i][1]
            perimeter += math.sqrt(dx**2 + dy**2)
        
        return {
            'area': round(area, 2),
            'perimeter': round(perimeter, 2),
            'num_vertices': n,
            'coordinates': coordinates
        }

class GeotechnicalCalculations:
    @staticmethod
    def calculate_earth_pressure_active(unit_weight, height, friction_angle, cohesion=0):
        """Calculate active earth pressure using Rankine theory"""
        phi_rad = math.radians(friction_angle)
        
        # Active earth pressure coefficient
        Ka = math.tan(math.pi/4 - phi_rad/2)**2
        
        # Active earth pressure at depth H
        sigma_v = unit_weight * height  # Vertical stress
        sigma_a = sigma_v * Ka - 2 * cohesion * math.sqrt(Ka)  # Active pressure
        
        # Total active force (triangular distribution)
        Ea = 0.5 * sigma_a * height
        
        return {
            'Ka': round(Ka, 3),
            'sigma_active': round(sigma_a, 2),
            'total_force': round(Ea, 2),
            'force_location': round(height/3, 2)  # From bottom
        }
    
    @staticmethod
    def calculate_earth_pressure_passive(unit_weight, height, friction_angle, cohesion=0):
        """Calculate passive earth pressure using Rankine theory"""
        phi_rad = math.radians(friction_angle)
        
        # Passive earth pressure coefficient
        Kp = math.tan(math.pi/4 + phi_rad/2)**2
        
        # Passive earth pressure at depth H
        sigma_v = unit_weight * height  # Vertical stress
        sigma_p = sigma_v * Kp + 2 * cohesion * math.sqrt(Kp)  # Passive pressure
        
        # Total passive force (triangular distribution)
        Ep = 0.5 * sigma_p * height
        
        return {
            'Kp': round(Kp, 3),
            'sigma_passive': round(sigma_p, 2),
            'total_force': round(Ep, 2),
            'force_location': round(height/3, 2)  # From bottom
        }
    
    @staticmethod
    def calculate_settlement_terzaghi(consolidation_coeff, time_days, layer_height):
        """Calculate settlement using Terzaghi consolidation theory"""
        # Convert time to seconds
        time_sec = time_days * 24 * 3600
        
        # Convert consolidation coefficient from m²/year to m²/s
        cv_m2_per_sec = consolidation_coeff / (365 * 24 * 3600)
        
        # Time factor
        Tv = (cv_m2_per_sec * time_sec) / (layer_height**2)
        
        # Degree of consolidation (approximation for Tv < 0.6)
        if Tv <= 0.196:
            U = math.sqrt(4 * Tv / math.pi) * 100
        else:
            U = (1 - 8/(math.pi**2) * math.exp(-math.pi**2 * Tv / 4)) * 100
        
        # Settlement ratio
        settlement_ratio = U / 100
        
        return {
            'time_factor': round(Tv, 4),
            'degree_consolidation': round(U, 2),
            'settlement_ratio': round(settlement_ratio, 4),
            'time_days': time_days
        }

class PavementCalculations:
    @staticmethod
    def calculate_flexible_pavement_cbr(traffic_load, cbr_value, k_constant=1.0):
        """Calculate flexible pavement thickness using CBR method"""
        # H = K * (W)^0.25 * CBR^(-0.25)
        thickness = k_constant * (traffic_load**0.25) * (cbr_value**(-0.25))
        
        # Minimum thickness recommendations
        min_thickness = 15.0  # cm minimum
        final_thickness = max(thickness, min_thickness)
        
        return {
            'calculated_thickness': round(thickness, 2),
            'minimum_thickness': min_thickness,
            'final_thickness': round(final_thickness, 2),
            'cbr_value': cbr_value,
            'traffic_load': traffic_load
        }
    
    @staticmethod
    def calculate_earthwork_volume(length, area1, area2):
        """Calculate earthwork volume using average end area method"""
        # V = L/2 * (A1 + A2)
        volume = (length / 2) * (area1 + area2)
        
        return {
            'volume': round(volume, 2),
            'length': length,
            'area1': area1,
            'area2': area2,
            'average_area': round((area1 + area2) / 2, 2)
        }
    
    @staticmethod
    def calculate_traffic_esal(axle_loads_tons, repetitions):
        """Calculate Equivalent Single Axle Load (ESAL)"""
        # Standard axle load = 8.2 tons (18 kips)
        standard_axle = 8.2
        
        total_esal = 0
        for i, load in enumerate(axle_loads_tons):
            if i < len(repetitions):
                # Load equivalency factor (simplified: (P/8.2)^4)
                equivalency_factor = (load / standard_axle)**4
                esal_contribution = repetitions[i] * equivalency_factor
                total_esal += esal_contribution
        
        return {
            'total_esal': round(total_esal, 0),
            'axle_loads': axle_loads_tons,
            'repetitions': repetitions,
            'standard_axle': standard_axle
        }

class QuantityCalculations:
    @staticmethod
    def calculate_concrete_volume(length, width, height):
        """Calculate concrete volume"""
        volume = length * width * height
        
        # Add 10% waste factor
        volume_with_waste = volume * 1.1
        
        return {
            'volume_theoretical': round(volume, 3),
            'volume_with_waste': round(volume_with_waste, 3),
            'waste_factor': 0.1,
            'dimensions': {'length': length, 'width': width, 'height': height}
        }
    
    @staticmethod
    def calculate_steel_consumption(bar_data):
        """Calculate steel consumption for reinforced concrete
        bar_data: list of dicts with 'diameter', 'length', 'quantity'
        """
        total_weight = 0
        steel_density = 7.85  # kg/dm³
        details = []
        
        for bar in bar_data:
            diameter_mm = bar['diameter']
            length_m = bar['length']
            quantity = bar['quantity']
            
            # Calculate weight per meter: π * d² / 4 * ρ (kg/m)
            # d in mm -> convert to m for area calculation
            area_mm2 = math.pi * (diameter_mm/2)**2  # Area in mm²
            area_m2 = area_mm2 / 1000000  # Convert mm² to m²
            weight_per_meter = area_m2 * steel_density * 1000  # kg/m (density in kg/dm³)
            total_weight_bar = weight_per_meter * length_m * quantity
            
            details.append({
                'diameter': diameter_mm,
                'length': length_m,
                'quantity': quantity,
                'weight_per_meter': round(weight_per_meter, 3),
                'total_weight': round(total_weight_bar, 2)
            })
            
            total_weight += total_weight_bar
        
        return {
            'total_weight': round(total_weight, 2),
            'details': details,
            'steel_density': steel_density
        }
    
    @staticmethod
    def calculate_mortar_composition(volume_m3, mix_ratio='1:4:1'):
        """Calculate mortar composition (cement:sand:lime)"""
        # Parse mix ratio
        parts = [int(x) for x in mix_ratio.split(':')]
        cement_parts, sand_parts, lime_parts = parts
        total_parts = sum(parts)
        
        # Volume calculations (considering 30% voids for sand)
        cement_volume = (cement_parts / total_parts) * volume_m3
        sand_volume = (sand_parts / total_parts) * volume_m3 * 1.3  # Add 30% for voids
        lime_volume = (lime_parts / total_parts) * volume_m3
        
        # Material quantities
        cement_kg = cement_volume * 1400  # Cement density ~1400 kg/m³
        sand_m3 = sand_volume
        lime_kg = lime_volume * 900  # Lime density ~900 kg/m³
        
        return {
            'volume_mortar': volume_m3,
            'mix_ratio': mix_ratio,
            'cement_kg': round(cement_kg, 1),
            'sand_m3': round(sand_m3, 3),
            'lime_kg': round(lime_kg, 1),
            'total_parts': total_parts
        }

class MasonryCalculations:
    @staticmethod
    def calculate_brick_consumption(wall_area, brick_length=19, brick_height=9, mortar_joint=1):
        """Calculate brick consumption for masonry walls
        Dimensions in cm, area in m²
        """
        # Convert to consistent units (cm)
        wall_area_cm2 = wall_area * 10000  # m² to cm²
        
        # Brick area including mortar joint
        brick_area_with_joint = (brick_length + mortar_joint) * (brick_height + mortar_joint)
        
        # Number of bricks
        num_bricks = wall_area_cm2 / brick_area_with_joint
        
        # Add 10% waste
        num_bricks_with_waste = num_bricks * 1.1
        
        # Mortar volume calculation
        mortar_volume_m3 = wall_area * mortar_joint / 1000  # Simplified
        
        return {
            'num_bricks': round(num_bricks, 0),
            'num_bricks_with_waste': round(num_bricks_with_waste, 0),
            'mortar_volume': round(mortar_volume_m3, 3),
            'brick_dimensions': f'{brick_length}x{brick_height} cm',
            'wall_area': wall_area
        }
    
    @staticmethod
    def calculate_wall_load(applied_load, wall_area):
        """Calculate distributed stress on wall"""
        stress = applied_load / wall_area
        
        # Typical allowable stresses for different masonry types (kN/m²)
        allowable_stresses = {
            'ceramic_block': 1200,
            'concrete_block': 1800,
            'clay_brick': 800
        }
        
        safety_factors = {}
        for masonry_type, allowable in allowable_stresses.items():
            safety_factors[masonry_type] = round(allowable / stress, 2)
        
        return {
            'applied_stress': round(stress, 2),
            'applied_load': applied_load,
            'wall_area': wall_area,
            'safety_factors': safety_factors
        }

class SanitationCalculations:
    @staticmethod
    def calculate_rational_method(runoff_coeff, intensity, area):
        """Calculate peak flow using Rational Method: Q = C * i * A"""
        flow_rate = runoff_coeff * intensity * area
        
        return {
            'flow_rate': round(flow_rate, 3),
            'runoff_coefficient': runoff_coeff,
            'intensity': intensity,
            'area': area,
            'method': 'Rational Method'
        }
    
    @staticmethod
    def calculate_manning_velocity(hydraulic_radius, slope, manning_n):
        """Calculate velocity in open channel using Manning equation"""
        # V = (1/n) * R^(2/3) * S^(1/2)
        velocity = (1/manning_n) * (hydraulic_radius**(2/3)) * (slope**(1/2))
        
        return {
            'velocity': round(velocity, 3),
            'hydraulic_radius': hydraulic_radius,
            'slope': slope,
            'manning_n': manning_n
        }
    
    @staticmethod
    def calculate_darcy_weisbach_loss(friction_factor, length, diameter, velocity):
        """Calculate head loss using Darcy-Weisbach equation"""
        g = 9.81  # gravity acceleration
        
        # hf = f * (L/D) * (V²/2g)
        head_loss = friction_factor * (length/diameter) * (velocity**2) / (2*g)
        
        return {
            'head_loss': round(head_loss, 3),
            'friction_factor': friction_factor,
            'length': length,
            'diameter': diameter,
            'velocity': velocity
        }


class AdvancedCalculations:
    @staticmethod
    def calculate_torsion_shear(torque, c_distance, polar_moment):
        """Calculate maximum shear stress in rectangular beam under torsion"""
        # τ_max = T * c / J
        shear_stress = (torque * c_distance) / polar_moment
        
        return {
            'shear_stress': round(shear_stress, 3),
            'torque': torque,
            'c_distance': c_distance,
            'polar_moment': polar_moment,
            'formula': 'τ_max = T·c/J'
        }
    
    @staticmethod
    def calculate_euler_buckling(elastic_modulus, moment_inertia, k_factor, length):
        """Calculate critical buckling load using Euler formula"""
        # P_cr = π²EI/(KL)²
        critical_load = (math.pi**2 * elastic_modulus * moment_inertia) / (k_factor * length)**2
        
        # Typical K factors
        k_factors = {
            'both_pinned': 1.0,
            'one_fixed_one_pinned': 0.7,
            'both_fixed': 0.5,
            'one_fixed_one_free': 2.0
        }
        
        return {
            'critical_load': round(critical_load, 2),
            'k_factor': k_factor,
            'effective_length': k_factor * length,
            'k_factors_reference': k_factors,
            'formula': 'P_cr = π²EI/(KL)²'
        }
    
    @staticmethod
    def calculate_continuous_beam_moment(distributed_load, length):
        """Calculate negative moment at support for continuous beam"""
        # M_neg = wL²/12 (approximation for uniformly distributed load)
        negative_moment = (distributed_load * length**2) / 12
        positive_moment = (distributed_load * length**2) / 24  # Mid-span moment
        
        return {
            'negative_moment': round(negative_moment, 2),
            'positive_moment': round(positive_moment, 2),
            'distributed_load': distributed_load,
            'span_length': length,
            'formula': 'M_neg = wL²/12'
        }


class HydrologyCalculations:
    @staticmethod
    def calculate_concentration_time(length_km, slope_percent, method='kirpich'):
        """Calculate time of concentration using different methods"""
        # Convert slope to decimal
        slope = slope_percent / 100
        
        if method == 'kirpich':
            # tc = 0.0195 * (L^0.77) / (S^0.385) for L in km, tc in minutes
            k = 0.0195
            tc = k * (length_km**0.77) / (slope**0.385)
            
        elif method == 'nrcs':
            # tc = K * L^0.8 / S^0.5
            k = 0.057
            tc = k * (length_km**0.8) / (slope**0.5)
            
        else:
            # Default to NRCS method
            k = 0.057
            tc = k * (length_km**0.8) / (slope**0.5)
        
        return {
            'time_concentration': round(tc, 2),
            'length_km': length_km,
            'slope_percent': slope_percent,
            'method': method,
            'formula': f'tc = {k} * L^0.8 / S^0.5'
        }
    
    @staticmethod
    def calculate_detention_outflow(inflow_rate, volume_change_rate):
        """Calculate detention reservoir outflow"""
        # Q_out = Q_in - dV/dt
        outflow_rate = inflow_rate - volume_change_rate
        
        return {
            'outflow_rate': round(outflow_rate, 3),
            'inflow_rate': inflow_rate,
            'volume_change_rate': volume_change_rate,
            'formula': 'Q_out = Q_in - dV/dt'
        }


class SteelStructuresCalculations:
    @staticmethod
    def calculate_steel_tension_stress(force_kn, cross_area_cm2):
        """Calculate stress in steel bar under tension/compression"""
        # σ = F/A
        stress = (force_kn * 1000) / (cross_area_cm2 / 100)  # Convert to N/mm²
        
        # Check against typical steel strengths
        typical_strengths = {
            'S235': 235,  # MPa
            'S275': 275,  # MPa
            'S355': 355   # MPa
        }
        
        safety_factors = {}
        for steel_type, strength in typical_strengths.items():
            safety_factors[steel_type] = round(strength / abs(stress), 2)
        
        return {
            'stress': round(stress, 2),
            'force_kn': force_kn,
            'cross_area_cm2': cross_area_cm2,
            'safety_factors': safety_factors,
            'formula': 'σ = F/A'
        }
    
    @staticmethod
    def calculate_steel_beam_deflection(load_kn, length_m, elastic_modulus, moment_inertia_cm4):
        """Calculate maximum deflection of steel beam with central load"""
        # δ_max = PL³/48EI
        load_n = load_kn * 1000
        moment_inertia_mm4 = moment_inertia_cm4 * 10000  # cm4 to mm4
        
        deflection = (load_n * (length_m * 1000)**3) / (48 * elastic_modulus * moment_inertia_mm4)
        
        # Check against typical limits
        allowable_deflection = (length_m * 1000) / 250  # L/250
        safety_ratio = allowable_deflection / abs(deflection)
        
        return {
            'deflection_mm': round(deflection, 2),
            'allowable_deflection_mm': round(allowable_deflection, 2),
            'safety_ratio': round(safety_ratio, 2),
            'length_m': length_m,
            'formula': 'δ_max = PL³/48EI'
        }


class IndustrialConstructionCalculations:
    @staticmethod
    def calculate_precast_element(span_m, distributed_load, element_height_cm, concrete_fck):
        """Calculate moment and deflection for precast elements"""
        # Maximum moment for simply supported beam
        max_moment = (distributed_load * span_m**2) / 8
        
        # Estimate moment of inertia (rectangular section)
        width_cm = element_height_cm * 0.4  # Typical ratio
        moment_inertia = (width_cm * element_height_cm**3) / 12
        
        # Elastic modulus from concrete strength
        elastic_modulus = 5600 * math.sqrt(concrete_fck)  # MPa
        
        # Maximum deflection
        max_deflection = (5 * distributed_load * (span_m * 1000)**4) / (384 * elastic_modulus * moment_inertia * 10**8)
        
        return {
            'max_moment_knm': round(max_moment, 2),
            'max_deflection_mm': round(max_deflection, 2),
            'moment_inertia_cm4': round(moment_inertia, 2),
            'elastic_modulus_mpa': round(elastic_modulus, 0),
            'estimated_width_cm': round(width_cm, 1)
        }
    
    @staticmethod
    def calculate_ribbed_slab_inertia(rib_width_cm, rib_height_cm, flange_thickness_cm, rib_spacing_cm):
        """Calculate effective moment of inertia for ribbed slab"""
        # Simplified calculation for T-section
        effective_width = min(rib_spacing_cm, rib_width_cm + 8 * flange_thickness_cm)
        
        # Calculate composite section properties
        total_height = rib_height_cm + flange_thickness_cm
        
        # Area and centroid calculations for T-section
        flange_area = effective_width * flange_thickness_cm
        rib_area = rib_width_cm * rib_height_cm
        total_area = flange_area + rib_area
        
        # Centroid from bottom
        y_centroid = (rib_area * (rib_height_cm/2) + flange_area * (rib_height_cm + flange_thickness_cm/2)) / total_area
        
        # Moment of inertia about centroidal axis
        I_flange = (effective_width * flange_thickness_cm**3) / 12 + flange_area * (rib_height_cm + flange_thickness_cm/2 - y_centroid)**2
        I_rib = (rib_width_cm * rib_height_cm**3) / 12 + rib_area * (rib_height_cm/2 - y_centroid)**2
        I_effective = I_flange + I_rib
        
        return {
            'effective_inertia_cm4': round(I_effective, 2),
            'effective_width_cm': round(effective_width, 2),
            'centroid_height_cm': round(y_centroid, 2),
            'total_area_cm2': round(total_area, 2),
            'total_height_cm': total_height
        }


class BuildingInstallationsCalculations:
    @staticmethod
    def calculate_voltage_drop(current_a, resistance_ohm_km, length_km):
        """Calculate voltage drop in electrical installation"""
        # ΔV = I × R × L
        voltage_drop = current_a * resistance_ohm_km * length_km
        
        # Typical maximum voltage drops
        max_drops = {
            'lighting': 3,  # 3% for lighting
            'motors': 5,    # 5% for motors
            'general': 4    # 4% for general circuits
        }
        
        return {
            'voltage_drop_v': round(voltage_drop, 2),
            'current_a': current_a,
            'resistance_ohm_km': resistance_ohm_km,
            'length_km': length_km,
            'max_drops_reference': max_drops,
            'formula': 'ΔV = I × R × L'
        }
    
    @staticmethod
    def calculate_gas_pipe_loss(flow_rate_m3h, pipe_diameter_mm, length_m, gas_density=0.8):
        """Calculate pressure loss in gas piping using simplified method"""
        # Simplified formula for natural gas
        diameter_m = pipe_diameter_mm / 1000
        
        # Pressure drop approximation (kPa/m)
        pressure_drop_per_meter = 0.1 * (flow_rate_m3h**2) / (diameter_m**5)
        total_pressure_drop = pressure_drop_per_meter * length_m
        
        return {
            'pressure_drop_kpa': round(total_pressure_drop, 2),
            'pressure_drop_per_meter': round(pressure_drop_per_meter, 4),
            'flow_rate_m3h': flow_rate_m3h,
            'pipe_diameter_mm': pipe_diameter_mm,
            'length_m': length_m
        }


class ConstructionControlCalculations:
    @staticmethod
    def calculate_productivity(quantity_executed, time_spent_hours):
        """Calculate team productivity"""
        # Prod = Quantity executed / Time spent
        if time_spent_hours <= 0:
            raise ValueError("Time spent must be greater than zero")
            
        productivity = quantity_executed / time_spent_hours
        
        # Estimate completion time for remaining work
        def estimate_completion(remaining_quantity):
            return remaining_quantity / productivity if productivity > 0 else 0
        
        return {
            'productivity_per_hour': round(productivity, 3),
            'quantity_executed': quantity_executed,
            'time_spent_hours': time_spent_hours,
            'estimate_function': estimate_completion,
            'formula': 'Prod = Qty executed / Time spent'
        }
    
    @staticmethod
    def calculate_s_curve(total_budget, current_time_percent, curve_type='normal'):
        """Calculate S-curve value for construction project"""
        # Different S-curve models
        t = current_time_percent / 100  # Convert to decimal
        
        if curve_type == 'normal':
            # Standard S-curve: slower start and end
            if t <= 0.5:
                cumulative_percent = 2 * t**2
            else:
                cumulative_percent = 1 - 2 * (1 - t)**2
                
        elif curve_type == 'fast_start':
            # Fast start, slow finish
            cumulative_percent = t**0.7
            
        elif curve_type == 'slow_start':
            # Slow start, fast finish
            cumulative_percent = t**1.5
            
        else:  # linear
            cumulative_percent = t
        
        cumulative_cost = total_budget * cumulative_percent
        
        return {
            'cumulative_cost': round(cumulative_cost, 2),
            'cumulative_percent': round(cumulative_percent * 100, 1),
            'current_time_percent': current_time_percent,
            'total_budget': total_budget,
            'curve_type': curve_type
        }


class SustainabilityCalculations:
    @staticmethod
    def calculate_carbon_footprint(material_mass_kg, emission_factor_kg_co2_kg):
        """Calculate carbon footprint of construction materials"""
        # CO2 = mass × emission factor
        co2_emissions = material_mass_kg * emission_factor_kg_co2_kg
        
        # Typical emission factors (kg CO2/kg material)
        emission_factors = {
            'cement': 0.87,
            'steel': 2.29,
            'aluminum': 11.46,
            'concrete': 0.11,
            'wood': -0.9,  # Carbon sequestration
            'brick': 0.24
        }
        
        return {
            'co2_emissions_kg': round(co2_emissions, 2),
            'co2_emissions_tons': round(co2_emissions / 1000, 3),
            'material_mass_kg': material_mass_kg,
            'emission_factor': emission_factor_kg_co2_kg,
            'typical_factors': emission_factors,
            'formula': 'CO2 = mass × emission factor'
        }
    
    @staticmethod
    def calculate_thermal_loss(u_value, area_m2, temp_difference):
        """Calculate heat loss through building envelope"""
        # Q = U × A × ΔT
        heat_loss_w = u_value * area_m2 * temp_difference
        
        # Convert to daily energy loss
        daily_energy_kwh = (heat_loss_w * 24) / 1000
        
        # Typical U-values (W/m²·K)
        typical_u_values = {
            'wall_uninsulated': 2.5,
            'wall_insulated': 0.3,
            'roof_uninsulated': 2.0,
            'roof_insulated': 0.2,
            'window_single': 5.8,
            'window_double': 2.8,
            'window_triple': 1.6
        }
        
        return {
            'heat_loss_w': round(heat_loss_w, 2),
            'daily_energy_kwh': round(daily_energy_kwh, 2),
            'u_value': u_value,
            'area_m2': area_m2,
            'temp_difference': temp_difference,
            'typical_u_values': typical_u_values,
            'formula': 'Q = U × A × ΔT'
        }


class AdvancedStructuralCalculations:
    @staticmethod
    def calculate_load_combination(dead_load, live_load, wind_load, snow_load, alpha_d=1.2, alpha_l=1.6, alpha_w=1.6, alpha_s=1.2):
        """Calculate load combination: U = αD·D + αL·L + αW·W + αS·S"""
        ultimate_load = alpha_d * dead_load + alpha_l * live_load + alpha_w * wind_load + alpha_s * snow_load
        
        # Calculate individual contributions
        dead_contribution = (alpha_d * dead_load / ultimate_load) * 100 if ultimate_load > 0 else 0
        live_contribution = (alpha_l * live_load / ultimate_load) * 100 if ultimate_load > 0 else 0
        wind_contribution = (alpha_w * wind_load / ultimate_load) * 100 if ultimate_load > 0 else 0
        snow_contribution = (alpha_s * snow_load / ultimate_load) * 100 if ultimate_load > 0 else 0
        
        return {
            'ultimate_load': round(ultimate_load, 2),
            'dead_contribution_pct': round(dead_contribution, 1),
            'live_contribution_pct': round(live_contribution, 1),
            'wind_contribution_pct': round(wind_contribution, 1),
            'snow_contribution_pct': round(snow_contribution, 1),
            'formula': 'U = αD·D + αL·L + αW·W + αS·S'
        }

    @staticmethod
    def calculate_concrete_shear(asv, fy, d, s):
        """Calculate concrete shear resistance: Vs = (Asv·fy·d)/s"""
        vs = (asv * fy * d) / s if s > 0 else 0
        
        # Typical concrete contribution (Vc) estimation
        vc_typical = 0.17 * d * 10  # Simplified estimation
        
        # Total shear resistance
        vrd = vc_typical + vs
        
        return {
            'vs_shear': round(vs, 2),
            'vc_concrete': round(vc_typical, 2),
            'vrd_total': round(vrd, 2),
            'reinforcement_ratio': round(asv / (1000 * s) * 100, 3) if s > 0 else 0,
            'formula': 'Vs = (Asv·fy·d)/s; VRd = Vc + Vs'
        }

    @staticmethod
    def calculate_punching_shear(tau_rd, u1, d):
        """Calculate punching shear resistance: VRd,c = τRd,c·u1·d"""
        vrd_c = tau_rd * u1 * d
        
        # Critical perimeter calculation (typical square column)
        column_size_estimated = u1 / 4 - 2 * d if u1 > 8 * d else u1 / 4
        
        return {
            'vrd_punching': round(vrd_c, 2),
            'critical_perimeter': round(u1, 2),
            'effective_depth': d,
            'tau_design': tau_rd,
            'estimated_column_size': round(max(column_size_estimated, 0.2), 2),
            'formula': 'VRd,c = τRd,c·u1·d'
        }

    @staticmethod
    def calculate_euler_buckling(e_modulus, moment_inertia, k_factor, length):
        """Calculate Euler critical load: Pcr = π²EI/(KL)²"""
        kl_effective = k_factor * length
        pcr = (math.pi**2 * e_modulus * moment_inertia) / (kl_effective**2)
        
        # Critical stress (assuming area from typical steel section)
        area_estimated = moment_inertia / (length**2 / 12)  # Rough estimation
        sigma_cr = pcr / area_estimated if area_estimated > 0 else 0
        
        return {
            'critical_load_kn': round(pcr / 1000, 2),
            'critical_stress_mpa': round(sigma_cr / 1000000, 2),
            'effective_length': round(kl_effective, 2),
            'slenderness_ratio': round(kl_effective / math.sqrt(moment_inertia / area_estimated), 1) if area_estimated > 0 else 0,
            'formula': 'Pcr = π²EI/(KL)²'
        }

    @staticmethod
    def calculate_lateral_torsional_buckling(c1, e_modulus, iz, lb, g_modulus, j_constant, iw):
        """Calculate critical moment for lateral-torsional buckling (simplified)"""
        # First term under square root
        term1 = (g_modulus * j_constant) / (e_modulus * iz)
        
        # Second term under square root  
        term2 = (math.pi**2 * iw) / (lb**2 * iz)
        
        # Critical moment calculation
        mcr = c1 * ((math.pi**2 * e_modulus * iz) / lb**2) * math.sqrt(term1 + term2)
        
        return {
            'critical_moment_knm': round(mcr / 1000000, 2),
            'unbraced_length': lb,
            'modification_factor': c1,
            'torsional_parameter': round(math.sqrt(term1), 3),
            'warping_parameter': round(math.sqrt(term2), 3),
            'formula': 'Mcr ≈ C1·(π²EIz/Lb²)·√(GJ/EIz + π²Iw/Lb²Iz)'
        }

    @staticmethod
    def calculate_wood_connection_capacity(embedment_strength, flexural_strength, withdrawal_strength, connection_type='nail'):
        """Calculate wood connection capacity: Rn = min{Remb, Rflex, Rarranc}"""
        capacities = {
            'embedment': embedment_strength,
            'flexural': flexural_strength,
            'withdrawal': withdrawal_strength
        }
        
        # Find governing mode
        governing_capacity = min(capacities.values())
        governing_mode = min(capacities.keys(), key=lambda k: capacities[k])
        
        # Safety factors by connection type
        safety_factors = {
            'nail': 2.5,
            'bolt': 3.0,
            'screw': 2.8
        }
        
        allowable_capacity = governing_capacity / safety_factors.get(connection_type, 2.5)
        
        return {
            'nominal_capacity_kn': round(governing_capacity, 2),
            'allowable_capacity_kn': round(allowable_capacity, 2),
            'governing_mode': governing_mode,
            'safety_factor': safety_factors.get(connection_type, 2.5),
            'capacity_breakdown': {k: round(v, 2) for k, v in capacities.items()},
            'formula': 'Rn = min{Remb, Rflex, Rarranc}'
        }


class AdvancedGeotechnicalCalculations:
    @staticmethod
    def calculate_eccentric_footing_stress(normal_force, base_width, base_length, eccentricity):
        """Calculate stress under footing with eccentricity: σ = N/BL(1 ± 6e/B)"""
        area = base_width * base_length
        average_stress = normal_force / area
        
        # Check if eccentricity is within kern limit
        kern_limit = base_width / 6
        within_kern = abs(eccentricity) <= kern_limit
        
        if within_kern:
            stress_max = average_stress * (1 + 6 * eccentricity / base_width)
            stress_min = average_stress * (1 - 6 * eccentricity / base_width)
            contact_length = base_length
        else:
            # Partial contact case
            contact_length = 3 * (base_width/2 - abs(eccentricity))
            stress_max = (2 * normal_force) / (base_width * contact_length)
            stress_min = 0
        
        return {
            'stress_max_kpa': round(stress_max, 2),
            'stress_min_kpa': round(stress_min, 2),
            'average_stress_kpa': round(average_stress, 2),
            'kern_limit_m': round(kern_limit, 3),
            'within_kern': within_kern,
            'contact_length_m': round(contact_length, 2),
            'formula': 'σmax,min = N/BL(1 ± 6e/B)'
        }

    @staticmethod
    def calculate_infinite_slope_stability(cohesion, unit_weight, depth, slope_angle, friction_angle, pore_pressure=0):
        """Calculate factor of safety for infinite slope: FS = [c' + (γz cos²θ - u)tan φ'] / (γz sin θ cos θ)"""
        theta_rad = math.radians(slope_angle)
        phi_rad = math.radians(friction_angle)
        
        # Vertical stress
        sigma_v = unit_weight * depth
        
        # Normal stress on failure plane
        sigma_n = sigma_v * (math.cos(theta_rad))**2
        
        # Shear stress on failure plane
        tau = sigma_v * math.sin(theta_rad) * math.cos(theta_rad)
        
        # Shear strength
        tau_f = cohesion + (sigma_n - pore_pressure) * math.tan(phi_rad)
        
        # Factor of safety
        fs = tau_f / tau if tau > 0 else float('inf')
        
        return {
            'factor_of_safety': round(fs, 3),
            'shear_stress_kpa': round(tau, 2),
            'shear_strength_kpa': round(tau_f, 2),
            'normal_stress_kpa': round(sigma_n, 2),
            'slope_angle_deg': slope_angle,
            'stability_status': 'Stable' if fs >= 1.5 else 'Critical' if fs >= 1.0 else 'Unstable',
            'formula': "FS = [c' + (γz cos²θ - u)tan φ'] / (γz sin θ cos θ)"
        }

    @staticmethod
    def calculate_elastic_settlement(q_load, width, elastic_modulus, poisson_ratio, influence_factor=1.0):
        """Calculate elastic settlement: s = qB(1-ν²)Is/E"""
        settlement = (q_load * width * (1 - poisson_ratio**2) * influence_factor) / elastic_modulus
        
        # Typical influence factors
        typical_factors = {
            'center_flexible': 1.12,
            'center_rigid': 0.93,
            'corner_flexible': 0.56,
            'average_flexible': 0.95
        }
        
        return {
            'settlement_mm': round(settlement * 1000, 2),
            'settlement_m': round(settlement, 4),
            'influence_factor': influence_factor,
            'typical_factors': typical_factors,
            'load_intensity_kpa': q_load,
            'foundation_width_m': width,
            'formula': 's = qB(1-ν²)Is/E'
        }

    @staticmethod
    def calculate_pile_capacity(qp, ap, fs_values, as_values, safety_factor=2.5):
        """Calculate pile capacity: Qu = qp·Ap + Σ(fs,i·As,i)"""
        # Point resistance
        point_resistance = qp * ap
        
        # Shaft resistance (sum of all layers)
        shaft_resistance = sum(fs * a_s for fs, a_s in zip(fs_values, as_values))
        
        # Ultimate capacity
        qu = point_resistance + shaft_resistance
        
        # Allowable capacity
        qadm = qu / safety_factor
        
        # Resistance distribution
        point_percentage = (point_resistance / qu) * 100 if qu > 0 else 0
        shaft_percentage = (shaft_resistance / qu) * 100 if qu > 0 else 0
        
        return {
            'ultimate_capacity_kn': round(qu, 2),
            'allowable_capacity_kn': round(qadm, 2),
            'point_resistance_kn': round(point_resistance, 2),
            'shaft_resistance_kn': round(shaft_resistance, 2),
            'point_percentage': round(point_percentage, 1),
            'shaft_percentage': round(shaft_percentage, 1),
            'safety_factor': safety_factor,
            'formula': 'Qu = qp·Ap + Σ(fs,i·As,i)'
        }


class AdvancedHydrologyCalculations:
    @staticmethod
    def calculate_scs_runoff(precipitation, curve_number):
        """Calculate SCS runoff: Q = (P-Ia)²/(P-Ia+S) where S = 25400/CN - 254"""
        # Storage parameter (mm)
        s_storage = (25400 / curve_number) - 254
        
        # Initial abstraction (mm)
        ia = 0.2 * s_storage
        
        # Direct runoff (only if P > Ia)
        if precipitation > ia:
            runoff = ((precipitation - ia)**2) / (precipitation - ia + s_storage)
        else:
            runoff = 0
            
        # Runoff coefficient
        runoff_coefficient = runoff / precipitation if precipitation > 0 else 0
        
        return {
            'runoff_mm': round(runoff, 2),
            'storage_parameter_mm': round(s_storage, 2),
            'initial_abstraction_mm': round(ia, 2),
            'runoff_coefficient': round(runoff_coefficient, 3),
            'precipitation_mm': precipitation,
            'curve_number': curve_number,
            'formula': 'Q = (P-Ia)²/(P-Ia+S); S = 25400/CN - 254; Ia = 0.2S'
        }

    @staticmethod
    def calculate_kirpich_time(length_km, slope_percent):
        """Calculate time of concentration (Kirpich): tc(min) = 0.0195 L^0.77 S^-0.385"""
        if slope_percent <= 0:
            raise ValueError("Slope must be greater than zero")
            
        tc_minutes = 0.0195 * (length_km * 1000)**0.77 * (slope_percent/100)**(-0.385)
        tc_hours = tc_minutes / 60
        
        # Typical range check
        typical_range = {
            'urban_min': 5,    # minutes
            'urban_max': 30,   # minutes  
            'rural_min': 30,   # minutes
            'rural_max': 180   # minutes
        }
        
        return {
            'tc_minutes': round(tc_minutes, 1),
            'tc_hours': round(tc_hours, 2),
            'length_m': length_km * 1000,
            'slope_percent': slope_percent,
            'typical_ranges_min': typical_range,
            'formula': 'tc(min) = 0.0195 L^0.77 S^-0.385'
        }

    @staticmethod
    def calculate_channel_energy(depth, velocity):
        """Calculate specific energy and Froude number: E = y + v²/2g"""
        g = 9.81  # gravity constant
        
        # Specific energy
        kinetic_head = velocity**2 / (2 * g)
        specific_energy = depth + kinetic_head
        
        # Froude number
        froude = velocity / math.sqrt(g * depth) if depth > 0 else 0
        
        # Flow regime
        if froude < 1:
            flow_regime = 'Subcritical'
        elif froude > 1:
            flow_regime = 'Supercritical'
        else:
            flow_regime = 'Critical'
            
        # Critical depth for rectangular channel (q = Q/b)
        q_unit = velocity * depth  # unit discharge
        critical_depth = (q_unit**2 / g)**(1/3)
        
        return {
            'specific_energy_m': round(specific_energy, 3),
            'froude_number': round(froude, 3),
            'flow_regime': flow_regime,
            'kinetic_head_m': round(kinetic_head, 3),
            'critical_depth_m': round(critical_depth, 3),
            'unit_discharge_m2s': round(q_unit, 3),
            'formula': 'E = y + v²/2g; Fr = v/√(gy)'
        }

    @staticmethod
    def calculate_water_hammer(density, wave_velocity, velocity_change):
        """Calculate water hammer pressure: Δp = ρaΔV"""
        pressure_increase = density * wave_velocity * abs(velocity_change)
        
        # Convert to more common units
        pressure_kpa = pressure_increase / 1000  # Pa to kPa
        pressure_mca = pressure_kpa / 9.81  # kPa to m.c.a.
        
        # Critical time (approximate)
        # tc ≈ 2L/a (depends on pipe length, not provided here)
        
        return {
            'pressure_increase_pa': round(pressure_increase, 0),
            'pressure_increase_kpa': round(pressure_kpa, 2),
            'pressure_increase_mca': round(pressure_mca, 2),
            'wave_velocity_ms': wave_velocity,
            'velocity_change_ms': abs(velocity_change),
            'density_kg_m3': density,
            'formula': 'Δp = ρaΔV'
        }

    @staticmethod
    def calculate_pump_similarity_laws(n1, q1, h1, p1, n2):
        """Calculate pump performance at different speeds using similarity laws"""
        # Flow rate ratio
        q2 = q1 * (n2 / n1)
        
        # Head ratio
        h2 = h1 * (n2 / n1)**2
        
        # Power ratio
        p2 = p1 * (n2 / n1)**3
        
        # Efficiency typically remains constant (ideal case)
        eff1 = (q1 * h1 * 9.81 * 1000) / (p1 * 1000) if p1 > 0 else 0  # Rough estimation
        
        return {
            'flow_rate_2_lps': round(q2, 2),
            'head_2_m': round(h2, 2),
            'power_2_kw': round(p2, 2),
            'speed_ratio': round(n2/n1, 3),
            'estimated_efficiency_pct': round(eff1 * 100, 1),
            'original_conditions': {'Q': q1, 'H': h1, 'P': p1, 'N': n1},
            'formula': 'Q2/Q1 = N2/N1; H2/H1 = (N2/N1)²; P2/P1 = (N2/N1)³'
        }


class AdvancedPavementCalculations:
    @staticmethod
    def calculate_esal_equivalence(axle_loads, equivalence_factors):
        """Calculate ESAL: ESAL = Σ(Ni × Ei)"""
        if len(axle_loads) != len(equivalence_factors):
            raise ValueError("Axle loads and equivalence factors must have same length")
            
        total_esal = sum(ni * ei for ni, ei in zip(axle_loads, equivalence_factors))
        
        # Calculate individual contributions
        contributions = []
        for i, (ni, ei) in enumerate(zip(axle_loads, equivalence_factors)):
            contribution = ni * ei
            percentage = (contribution / total_esal * 100) if total_esal > 0 else 0
            contributions.append({
                'axle_type': f'Type_{i+1}',
                'count': ni,
                'equivalence_factor': ei,
                'esal_contribution': round(contribution, 2),
                'percentage': round(percentage, 1)
            })
            
        return {
            'total_esal': round(total_esal, 2),
            'contributions': contributions,
            'formula': 'ESAL = Σ(Ni × Ei)'
        }

    @staticmethod
    def calculate_traffic_growth(adt0, growth_rate_pct, period_years, lane_factor=1.0, directional_factor=0.5):
        """Calculate accumulated traffic: Nacum = ADT0 × 365 × [(1+r)^n - 1]/r × LF × DL"""
        r = growth_rate_pct / 100
        
        if r == 0:
            # Linear growth case
            growth_factor = period_years
        else:
            # Compound growth case
            growth_factor = ((1 + r)**period_years - 1) / r
            
        accumulated_traffic = adt0 * 365 * growth_factor * lane_factor * directional_factor
        
        # Calculate year-by-year breakdown
        yearly_breakdown = []
        for year in range(1, min(period_years + 1, 11)):  # Limit to 10 years for display
            yearly_adt = adt0 * (1 + r)**year
            yearly_breakdown.append({
                'year': year,
                'adt': round(yearly_adt, 0),
                'annual_total': round(yearly_adt * 365 * lane_factor * directional_factor, 0)
            })
        
        return {
            'accumulated_traffic': round(accumulated_traffic, 0),
            'growth_factor': round(growth_factor, 2),
            'initial_adt': adt0,
            'growth_rate_pct': growth_rate_pct,
            'period_years': period_years,
            'yearly_breakdown': yearly_breakdown[:10],  # Limit display
            'formula': 'Nacum = ADT0 × 365 × [(1+r)^n - 1]/r × LF × DL'
        }

    @staticmethod
    def calculate_stopping_distance(speed_kmh, reaction_time_s, friction_coeff, grade_pct=0):
        """Calculate stopping sight distance: SSD = v·tr + v²/[2g(f±G)]"""
        v_ms = speed_kmh / 3.6  # Convert to m/s
        g = 9.81  # gravity
        grade_decimal = grade_pct / 100
        
        # Reaction distance
        reaction_distance = v_ms * reaction_time_s
        
        # Braking distance
        if grade_pct >= 0:  # Uphill grade helps braking
            braking_distance = v_ms**2 / (2 * g * (friction_coeff + grade_decimal))
        else:  # Downhill grade hinders braking
            braking_distance = v_ms**2 / (2 * g * (friction_coeff - abs(grade_decimal)))
        
        # Total stopping distance
        total_distance = reaction_distance + braking_distance
        
        # Design recommendations
        design_speeds = {
            30: 35,   # km/h: stopping distance (m)
            40: 50,
            50: 65,
            60: 85,
            70: 105,
            80: 130,
            90: 160,
            100: 190
        }
        
        return {
            'total_stopping_distance_m': round(total_distance, 1),
            'reaction_distance_m': round(reaction_distance, 1),
            'braking_distance_m': round(braking_distance, 1),
            'speed_ms': round(v_ms, 2),
            'grade_effect': 'Favorable' if grade_pct > 0 else 'Adverse' if grade_pct < 0 else 'Flat',
            'design_reference_m': design_speeds,
            'formula': 'SSD = v·tr + v²/[2g(f±G)]'
        }


class BuildingSystemsCalculations:
    @staticmethod
    def calculate_lighting_design(illuminance_target, area_m2, lamp_lumens, utilization_factor=0.6, maintenance_factor=0.8):
        """Calculate lighting using lumen method: E = Φ·UF·MF/A; Nlum = E·A/(Φlamp·UF·MF)"""
        # Required total lumens
        total_lumens_required = illuminance_target * area_m2
        
        # Number of luminaires needed
        effective_lumens_per_lamp = lamp_lumens * utilization_factor * maintenance_factor
        number_luminaires = total_lumens_required / effective_lumens_per_lamp if effective_lumens_per_lamp > 0 else 0
        
        # Actual illuminance with rounded number of luminaires
        number_luminaires_rounded = math.ceil(number_luminaires)
        actual_illuminance = (number_luminaires_rounded * effective_lumens_per_lamp) / area_m2
        
        # Typical illuminance levels (lux)
        typical_levels = {
            'residence_general': 150,
            'office_general': 500,
            'office_tasks': 750,
            'classroom': 300,
            'workshop': 300,
            'parking': 75
        }
        
        return {
            'luminaires_needed': number_luminaires_rounded,
            'actual_illuminance_lux': round(actual_illuminance, 1),
            'target_illuminance_lux': illuminance_target,
            'luminaires_exact': round(number_luminaires, 2),
            'effective_lumens_per_lamp': round(effective_lumens_per_lamp, 0),
            'typical_levels_lux': typical_levels,
            'formula': 'E = Φ·UF·MF/A; Nlum = E·A/(Φlamp·UF·MF)'
        }

    @staticmethod
    def calculate_thermal_transmission(u_value, area_m2, temp_difference_k):
        """Calculate heat transmission load: Q = U·A·ΔT"""
        heat_loss_w = u_value * area_m2 * temp_difference_k
        heat_loss_kwh_day = (heat_loss_w * 24) / 1000
        
        # Cost estimation (assuming R$ 0.50/kWh)
        cost_per_kwh = 0.50
        daily_cost = heat_loss_kwh_day * cost_per_kwh
        monthly_cost = daily_cost * 30
        
        # Typical U-values for comparison (W/m²·K)
        typical_u_values = {
            'wall_concrete_uninsulated': 2.5,
            'wall_brick_uninsulated': 2.0,
            'wall_insulated': 0.4,
            'roof_concrete_uninsulated': 3.0,
            'roof_insulated': 0.3,
            'window_single_glass': 5.8,
            'window_double_glass': 2.8
        }
        
        return {
            'heat_loss_w': round(heat_loss_w, 1),
            'daily_energy_kwh': round(heat_loss_kwh_day, 2),
            'monthly_cost_brl': round(monthly_cost, 2),
            'u_value_w_m2k': u_value,
            'area_m2': area_m2,
            'temp_difference_k': temp_difference_k,
            'typical_u_values': typical_u_values,
            'formula': 'Q = U·A·ΔT'
        }

    @staticmethod
    def calculate_reverberation_time(volume_m3, absorption_coefficients, surface_areas):
        """Calculate reverberation time (Sabine): T60 = 0.161·V/Aeq"""
        if len(absorption_coefficients) != len(surface_areas):
            raise ValueError("Absorption coefficients and surface areas must have same length")
            
        # Calculate equivalent absorption area
        aeq = sum(alpha * area for alpha, area in zip(absorption_coefficients, surface_areas))
        
        # Reverberation time
        t60 = (0.161 * volume_m3) / aeq if aeq > 0 else 0
        
        # Recommended reverberation times (seconds)
        recommended_times = {
            'speech_small_room': 0.6,
            'speech_large_room': 1.0,
            'music_chamber': 1.4,
            'music_concert_hall': 2.0,
            'church': 2.5,
            'classroom': 0.7,
            'office': 0.5
        }
        
        # Surface breakdown
        surface_breakdown = []
        for i, (alpha, area) in enumerate(zip(absorption_coefficients, surface_areas)):
            absorption = alpha * area
            percentage = (absorption / aeq * 100) if aeq > 0 else 0
            surface_breakdown.append({
                'surface': f'Surface_{i+1}',
                'alpha': alpha,
                'area_m2': area,
                'absorption': round(absorption, 2),
                'percentage': round(percentage, 1)
            })
        
        return {
            'reverberation_time_s': round(t60, 2),
            'equivalent_absorption_m2': round(aeq, 2),
            'volume_m3': volume_m3,
            'surface_breakdown': surface_breakdown,
            'recommended_times_s': recommended_times,
            'formula': 'T60 = 0.161·V/Aeq'
        }

    @staticmethod
    def calculate_gutter_sizing(rainfall_intensity, catchment_area, velocity_factor=1.0):
        """Calculate gutter flow: Q = i·A; check Q ≤ v·Acond"""
        flow_rate = rainfall_intensity * catchment_area
        
        # Typical gutter dimensions and capacities
        gutter_capacities = {
            100: {'diameter_mm': 100, 'capacity_ls': 2.8},
            125: {'diameter_mm': 125, 'capacity_ls': 4.5},
            150: {'diameter_mm': 150, 'capacity_ls': 6.8},
            200: {'diameter_mm': 200, 'capacity_ls': 12.0}
        }
        
        # Find minimum gutter size
        suitable_gutters = []
        for size, data in gutter_capacities.items():
            adjusted_capacity = data['capacity_ls'] * velocity_factor
            if adjusted_capacity >= flow_rate:
                suitable_gutters.append({
                    'diameter_mm': size,
                    'capacity_ls': round(adjusted_capacity, 2),
                    'safety_factor': round(adjusted_capacity / flow_rate, 2)
                })
        
        recommended_size = min(suitable_gutters, key=lambda x: x['diameter_mm']) if suitable_gutters else None
        
        return {
            'flow_rate_ls': round(flow_rate, 3),
            'recommended_diameter_mm': recommended_size['diameter_mm'] if recommended_size else 'Oversized',
            'all_suitable_options': suitable_gutters,
            'rainfall_intensity': rainfall_intensity,
            'catchment_area_m2': catchment_area,
            'velocity_factor': velocity_factor,
            'formula': 'Q = i·A'
        }

    @staticmethod
    def calculate_stair_blondel(riser_height_cm, tread_depth_cm):
        """Calculate stair proportions using Blondel rule: 2h + b ≈ 63-65 cm"""
        blondel_value = 2 * riser_height_cm + tread_depth_cm
        
        # Comfort evaluation
        ideal_range = (63, 65)
        acceptable_range = (60, 68)
        
        if ideal_range[0] <= blondel_value <= ideal_range[1]:
            comfort_rating = 'Ideal'
        elif acceptable_range[0] <= blondel_value <= acceptable_range[1]:
            comfort_rating = 'Acceptable'
        else:
            comfort_rating = 'Poor'
        
        # Additional checks
        max_riser = 18.5  # cm (typical building code)
        min_tread = 25    # cm (typical building code)
        
        code_compliance = {
            'riser_ok': riser_height_cm <= max_riser,
            'tread_ok': tread_depth_cm >= min_tread,
            'overall_ok': riser_height_cm <= max_riser and tread_depth_cm >= min_tread
        }
        
        # Slope calculation
        slope_degrees = math.degrees(math.atan(riser_height_cm / tread_depth_cm))
        
        return {
            'blondel_value_cm': round(blondel_value, 1),
            'comfort_rating': comfort_rating,
            'code_compliance': code_compliance,
            'slope_degrees': round(slope_degrees, 1),
            'riser_cm': riser_height_cm,
            'tread_cm': tread_depth_cm,
            'ideal_range_cm': ideal_range,
            'formula': '2h + b ≈ 63-65 cm'
        }

    @staticmethod
    def calculate_prismoidal_volume(area1, area_middle, area2, length):
        """Calculate prismoidal volume: V = L/6(A1 + 4Am + A2)"""
        volume = (length / 6) * (area1 + 4 * area_middle + area2)
        
        # Compare with other methods
        trapezoidal_volume = (length / 2) * (area1 + area2)  # Less accurate
        average_area = (area1 + area_middle + area2) / 3
        
        # Volume distribution
        end_contribution = (area1 + area2) / 6 * length
        middle_contribution = (4 * area_middle) / 6 * length
        
        return {
            'prismoidal_volume_m3': round(volume, 3),
            'trapezoidal_volume_m3': round(trapezoidal_volume, 3),
            'volume_difference_m3': round(volume - trapezoidal_volume, 3),
            'average_area_m2': round(average_area, 2),
            'end_sections_contribution_pct': round(end_contribution / volume * 100, 1) if volume > 0 else 0,
            'middle_section_contribution_pct': round(middle_contribution / volume * 100, 1) if volume > 0 else 0,
            'length_m': length,
            'formula': 'V = L/6(A1 + 4Am + A2)'
        }


class EconomicCalculations:
    @staticmethod
    def calculate_npv(cash_flows, discount_rate_pct, initial_investment=0):
        """Calculate Net Present Value: NPV = Σ[FCt/(1+i)^t]"""
        discount_rate = discount_rate_pct / 100
        npv = -initial_investment  # Initial investment is negative cash flow
        
        # Calculate present value of each cash flow
        pv_breakdown = []
        for t, cf in enumerate(cash_flows):
            present_value = cf / ((1 + discount_rate) ** (t + 1))
            npv += present_value
            pv_breakdown.append({
                'period': t + 1,
                'cash_flow': cf,
                'present_value': round(present_value, 2),
                'discount_factor': round(1 / ((1 + discount_rate) ** (t + 1)), 4)
            })
        
        # Calculate other metrics
        total_cash_flows = sum(cash_flows)
        payback_period = 0
        cumulative_cf = -initial_investment
        
        for t, cf in enumerate(cash_flows):
            cumulative_cf += cf
            if cumulative_cf >= 0 and payback_period == 0:
                payback_period = t + 1
                break
        
        # IRR approximation (simplified)
        irr_estimate = ((total_cash_flows / initial_investment) ** (1 / len(cash_flows)) - 1) * 100 if initial_investment > 0 else 0
        
        return {
            'npv': round(npv, 2),
            'npv_status': 'Viable' if npv >= 0 else 'Not Viable',
            'total_cash_inflows': round(total_cash_flows, 2),
            'initial_investment': initial_investment,
            'payback_period_years': payback_period if payback_period > 0 else 'Not achieved',
            'irr_estimate_pct': round(irr_estimate, 2),
            'discount_rate_pct': discount_rate_pct,
            'pv_breakdown': pv_breakdown,
            'formula': 'NPV = Σ[FCt/(1+i)^t] - Investment'
        }
