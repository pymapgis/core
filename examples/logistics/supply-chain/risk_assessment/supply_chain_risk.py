#!/usr/bin/env python3
"""
Supply Chain Risk Assessment Example

This example demonstrates how to use PyMapGIS for comprehensive supply chain
risk assessment and mitigation planning. The analysis evaluates geographic,
operational, and strategic risks across a global supplier network.

Backstory:
---------
GlobalTech Manufacturing is a multinational technology company that sources
components and materials from suppliers across 12 countries. Recent global
events (natural disasters, geopolitical tensions, cyber attacks) have highlighted
the vulnerability of their supply chain. The company needs to:

1. Assess risk exposure across their supplier network
2. Identify high-risk suppliers and geographic concentrations
3. Evaluate backup supplier capabilities
4. Develop risk mitigation strategies
5. Create contingency plans for supply disruptions

The analysis considers multiple risk factors:
- Natural disasters (earthquakes, typhoons, floods)
- Geopolitical instability
- Cyber security threats
- Financial stability of suppliers
- Geographic concentration risks

Usage:
------
python supply_chain_risk.py

Requirements:
------------
- pymapgis
- geopandas
- pandas
- matplotlib
- seaborn
"""

import pymapgis as pmg
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

def load_supply_chain_data():
    """Load supplier and risk zone data."""
    print("🌍 Loading global supply chain data...")
    
    # Load supplier locations and details
    suppliers = pmg.read("file://data/suppliers.geojson")
    print(f"   ✓ Loaded {len(suppliers)} suppliers across {suppliers['country'].nunique()} countries")
    
    # Load risk zones (natural disasters, political instability, etc.)
    risk_zones = pmg.read("file://data/risk_zones.geojson")
    print(f"   ✓ Loaded {len(risk_zones)} risk zones")
    
    return suppliers, risk_zones

def assess_geographic_risks(suppliers, risk_zones):
    """Assess which suppliers are located in high-risk geographic areas."""
    print("🗺️  Assessing geographic risk exposure...")
    
    risk_assessment = []
    
    for _, supplier in suppliers.iterrows():
        supplier_risks = []
        
        # Check if supplier location intersects with any risk zones
        for _, risk_zone in risk_zones.iterrows():
            if risk_zone.geometry.contains(supplier.geometry):
                risk_info = {
                    'risk_type': risk_zone['risk_type'],
                    'severity': risk_zone['severity'],
                    'probability': risk_zone['probability'],
                    'description': risk_zone['description']
                }
                supplier_risks.append(risk_info)
        
        # Calculate composite risk score
        if supplier_risks:
            # Weight risks by severity and probability
            severity_weights = {'low': 1, 'medium': 2, 'high': 3}
            total_risk_score = sum(
                severity_weights.get(risk['severity'], 1) * risk['probability'] 
                for risk in supplier_risks
            )
        else:
            total_risk_score = 0
        
        risk_assessment.append({
            'supplier_id': supplier['supplier_id'],
            'name': supplier['name'],
            'country': supplier['country'],
            'annual_volume': supplier['annual_volume'],
            'geographic_risk_score': total_risk_score,
            'risk_count': len(supplier_risks),
            'risks': supplier_risks
        })
    
    return pd.DataFrame(risk_assessment)

def calculate_operational_risks(suppliers):
    """Calculate operational risk scores based on supplier characteristics."""
    print("⚙️  Calculating operational risk factors...")
    
    operational_risks = []
    
    for _, supplier in suppliers.iterrows():
        # Financial stability risk (inverse scoring)
        financial_risk = {
            'excellent': 0.1,
            'good': 0.3,
            'fair': 0.6,
            'poor': 0.9
        }.get(supplier['financial_stability'], 0.5)
        
        # Lead time risk (longer lead times = higher risk)
        lead_time_risk = min(supplier['lead_time_days'] / 60, 1.0)  # Normalize to 0-1
        
        # Backup supplier risk (fewer backups = higher risk)
        backup_risk = max(0, 1 - (supplier['backup_suppliers'] / 5))  # Normalize to 0-1
        
        # Quality risk (lower quality = higher risk)
        quality_risk = max(0, (5 - supplier['quality_rating']) / 5)
        
        # Volume concentration risk (higher volume = higher impact if disrupted)
        volume_risk = min(supplier['annual_volume'] / 30000000, 1.0)  # Normalize
        
        # Composite operational risk score
        operational_risk_score = (
            financial_risk * 0.25 +
            lead_time_risk * 0.20 +
            backup_risk * 0.25 +
            quality_risk * 0.15 +
            volume_risk * 0.15
        )
        
        operational_risks.append({
            'supplier_id': supplier['supplier_id'],
            'financial_risk': financial_risk,
            'lead_time_risk': lead_time_risk,
            'backup_risk': backup_risk,
            'quality_risk': quality_risk,
            'volume_risk': volume_risk,
            'operational_risk_score': operational_risk_score
        })
    
    return pd.DataFrame(operational_risks)

def analyze_concentration_risks(suppliers):
    """Analyze geographic and supplier type concentration risks."""
    print("📊 Analyzing concentration risks...")
    
    # Country concentration
    country_volumes = suppliers.groupby('country')['annual_volume'].sum().sort_values(ascending=False)
    total_volume = suppliers['annual_volume'].sum()
    country_concentration = (country_volumes / total_volume).head(5)
    
    # Supplier type concentration
    type_volumes = suppliers.groupby('supplier_type')['annual_volume'].sum().sort_values(ascending=False)
    type_concentration = (type_volumes / total_volume)
    
    # Single supplier dependency (suppliers representing >15% of total volume)
    supplier_volumes = suppliers.set_index('supplier_id')['annual_volume'] / total_volume
    critical_suppliers = supplier_volumes[supplier_volumes > 0.15]
    
    concentration_analysis = {
        'country_concentration': country_concentration,
        'type_concentration': type_concentration,
        'critical_suppliers': critical_suppliers,
        'total_volume': total_volume
    }
    
    return concentration_analysis

def create_comprehensive_risk_matrix(suppliers, geographic_risks, operational_risks):
    """Create comprehensive risk assessment matrix."""
    print("🎯 Creating comprehensive risk matrix...")
    
    # Merge all risk assessments
    risk_matrix = suppliers[['supplier_id', 'name', 'country', 'supplier_type', 
                           'annual_volume', 'quality_rating', 'backup_suppliers']].copy()
    
    # Add geographic risks
    geo_risk_df = geographic_risks[['supplier_id', 'geographic_risk_score', 'risk_count']]
    risk_matrix = risk_matrix.merge(geo_risk_df, on='supplier_id', how='left')
    
    # Add operational risks
    op_risk_df = operational_risks[['supplier_id', 'operational_risk_score']]
    risk_matrix = risk_matrix.merge(op_risk_df, on='supplier_id', how='left')
    
    # Calculate composite risk score
    risk_matrix['composite_risk_score'] = (
        risk_matrix['geographic_risk_score'] * 0.4 +
        risk_matrix['operational_risk_score'] * 0.6
    )
    
    # Risk categorization
    risk_matrix['risk_category'] = pd.cut(
        risk_matrix['composite_risk_score'],
        bins=[0, 0.3, 0.6, 1.0, float('inf')],
        labels=['Low', 'Medium', 'High', 'Critical']
    )
    
    return risk_matrix

def visualize_risk_assessment(suppliers, risk_zones, risk_matrix, concentration_analysis):
    """Create comprehensive risk assessment visualizations."""
    print("📈 Creating risk assessment visualizations...")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Global supplier and risk zone map
    ax1 = plt.subplot(2, 3, 1)
    
    # Plot risk zones
    risk_zones.plot(ax=ax1, alpha=0.3, color='red', edgecolor='darkred', linewidth=0.5)
    
    # Plot suppliers with risk-based coloring
    risk_colors = {'Low': 'green', 'Medium': 'yellow', 'High': 'orange', 'Critical': 'red'}
    for category in risk_colors:
        category_suppliers = suppliers[suppliers['supplier_id'].isin(
            risk_matrix[risk_matrix['risk_category'] == category]['supplier_id']
        )]
        if not category_suppliers.empty:
            category_suppliers.plot(ax=ax1, color=risk_colors[category], 
                                  markersize=50, alpha=0.8, label=f'{category} Risk')
    
    ax1.set_title('Global Supplier Risk Assessment Map', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    
    # 2. Risk score distribution
    ax2 = plt.subplot(2, 3, 2)
    
    risk_matrix['composite_risk_score'].hist(bins=20, ax=ax2, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.axvline(risk_matrix['composite_risk_score'].mean(), color='red', linestyle='--', 
                label=f'Mean: {risk_matrix["composite_risk_score"].mean():.2f}')
    ax2.set_title('Risk Score Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Composite Risk Score')
    ax2.set_ylabel('Number of Suppliers')
    ax2.legend()
    
    # 3. Country concentration
    ax3 = plt.subplot(2, 3, 3)
    
    country_conc = concentration_analysis['country_concentration']
    bars = ax3.bar(range(len(country_conc)), country_conc.values, color='lightcoral', alpha=0.7)
    ax3.set_title('Country Concentration Risk', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Countries')
    ax3.set_ylabel('Volume Percentage')
    ax3.set_xticks(range(len(country_conc)))
    ax3.set_xticklabels(country_conc.index, rotation=45)
    
    # Add percentage labels on bars
    for bar, pct in zip(bars, country_conc.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{pct:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Risk vs Volume scatter plot
    ax4 = plt.subplot(2, 3, 4)
    
    scatter = ax4.scatter(risk_matrix['composite_risk_score'], 
                         risk_matrix['annual_volume']/1000000,
                         c=risk_matrix['quality_rating'], 
                         s=risk_matrix['backup_suppliers']*20,
                         alpha=0.7, cmap='RdYlGn')
    
    ax4.set_title('Risk vs Volume Analysis', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Composite Risk Score')
    ax4.set_ylabel('Annual Volume (Millions $)')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Quality Rating')
    
    # 5. Supplier type risk breakdown
    ax5 = plt.subplot(2, 3, 5)
    
    type_risk = risk_matrix.groupby('supplier_type')['composite_risk_score'].mean().sort_values(ascending=True)
    bars = ax5.barh(range(len(type_risk)), type_risk.values, color='lightblue', alpha=0.7)
    ax5.set_title('Risk by Supplier Type', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Average Risk Score')
    ax5.set_yticks(range(len(type_risk)))
    ax5.set_yticklabels(type_risk.index)
    
    # 6. Risk category summary
    ax6 = plt.subplot(2, 3, 6)
    
    risk_summary = risk_matrix['risk_category'].value_counts()
    colors = [risk_colors[cat] for cat in risk_summary.index]
    wedges, texts, autotexts = ax6.pie(risk_summary.values, labels=risk_summary.index,
                                      autopct='%1.1f%%', colors=colors)
    ax6.set_title('Risk Category Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('supply_chain_risk_assessment.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_risk_recommendations(risk_matrix, concentration_analysis, geographic_risks):
    """Generate actionable risk mitigation recommendations."""
    print("\n" + "="*70)
    print("🚨 SUPPLY CHAIN RISK ASSESSMENT REPORT")
    print("="*70)
    
    # High-risk suppliers
    high_risk_suppliers = risk_matrix[risk_matrix['risk_category'].isin(['High', 'Critical'])]
    
    print(f"\n⚠️  HIGH-RISK SUPPLIERS ({len(high_risk_suppliers)} suppliers):")
    print("-" * 50)
    for _, supplier in high_risk_suppliers.iterrows():
        print(f"• {supplier['name']} ({supplier['country']})")
        print(f"  Risk Score: {supplier['composite_risk_score']:.2f} | Category: {supplier['risk_category']}")
        print(f"  Annual Volume: ${supplier['annual_volume']:,} | Backups: {supplier['backup_suppliers']}")
        print()
    
    # Concentration risks
    print(f"🌍 CONCENTRATION RISK ANALYSIS:")
    print("-" * 50)
    
    country_conc = concentration_analysis['country_concentration']
    print(f"Top country dependencies:")
    for country, percentage in country_conc.head(3).items():
        print(f"• {country}: {percentage:.1%} of total volume")
    
    critical_suppliers = concentration_analysis['critical_suppliers']
    if not critical_suppliers.empty:
        print(f"\nCritical single-supplier dependencies:")
        for supplier_id, percentage in critical_suppliers.items():
            supplier_name = risk_matrix[risk_matrix['supplier_id'] == supplier_id]['name'].iloc[0]
            print(f"• {supplier_name}: {percentage:.1%} of total volume")
    
    # Geographic risk hotspots
    geo_risks = geographic_risks[geographic_risks['geographic_risk_score'] > 0]
    if not geo_risks.empty:
        print(f"\n🗺️  GEOGRAPHIC RISK HOTSPOTS:")
        print("-" * 50)
        high_geo_risk = geo_risks.nlargest(5, 'geographic_risk_score')
        for _, supplier in high_geo_risk.iterrows():
            print(f"• {supplier['name']} ({supplier['country']})")
            print(f"  Geographic Risk Score: {supplier['geographic_risk_score']:.2f}")
            print(f"  Risk Types: {len(supplier['risks'])} identified")
            print()
    
    # Recommendations
    print(f"💡 RISK MITIGATION RECOMMENDATIONS:")
    print("-" * 50)
    
    recommendations = [
        "1. IMMEDIATE ACTIONS:",
        f"   • Develop contingency plans for {len(high_risk_suppliers)} high-risk suppliers",
        f"   • Increase backup suppliers for critical dependencies",
        f"   • Negotiate flexible contracts with alternative suppliers",
        "",
        "2. DIVERSIFICATION STRATEGY:",
        f"   • Reduce country concentration (top 3 countries: {country_conc.head(3).sum():.1%})",
        f"   • Identify suppliers in low-risk geographic regions",
        f"   • Balance cost savings vs. risk exposure",
        "",
        "3. MONITORING & EARLY WARNING:",
        f"   • Implement real-time risk monitoring for high-risk regions",
        f"   • Establish supplier financial health tracking",
        f"   • Create automated alert systems for risk events",
        "",
        "4. SUPPLY CHAIN RESILIENCE:",
        f"   • Increase inventory buffers for critical components",
        f"   • Develop multi-modal transportation options",
        f"   • Invest in supplier relationship management"
    ]
    
    for rec in recommendations:
        print(rec)
    
    return {
        'high_risk_count': len(high_risk_suppliers),
        'concentration_risk': country_conc.head(3).sum(),
        'geographic_hotspots': len(geo_risks),
        'recommendations': recommendations
    }

def main():
    """Main execution function."""
    print("🌐 GLOBAL SUPPLY CHAIN RISK ASSESSMENT")
    print("=" * 50)
    print("Analyzing risk exposure for GlobalTech Manufacturing")
    print("Comprehensive evaluation of supplier network vulnerabilities")
    print()
    
    try:
        # Load data
        suppliers, risk_zones = load_supply_chain_data()
        
        # Assess geographic risks
        geographic_risks = assess_geographic_risks(suppliers, risk_zones)
        
        # Calculate operational risks
        operational_risks = calculate_operational_risks(suppliers)
        
        # Analyze concentration risks
        concentration_analysis = analyze_concentration_risks(suppliers)
        
        # Create comprehensive risk matrix
        risk_matrix = create_comprehensive_risk_matrix(suppliers, geographic_risks, operational_risks)
        
        # Visualize results
        visualize_risk_assessment(suppliers, risk_zones, risk_matrix, concentration_analysis)
        
        # Generate recommendations
        recommendations = generate_risk_recommendations(risk_matrix, concentration_analysis, geographic_risks)
        
        print(f"\n✅ Risk assessment complete! Check 'supply_chain_risk_assessment.png' for detailed analysis.")
        
    except Exception as e:
        print(f"❌ Error during risk assessment: {e}")
        raise

if __name__ == "__main__":
    main()
