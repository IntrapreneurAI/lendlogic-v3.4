#!/usr/bin/env python3.11
"""
LendLogic v3.5 - Enhanced Lender Matching Algorithm
Uses real lender matrix data to match deals to appropriate funders
"""

import pandas as pd
import json
from pathlib import Path

class LenderMatcher:
    """Matches deals to lenders based on real matrix criteria"""
    
    def __init__(self, matrix_path):
        """Load and prepare the lender matrix"""
        self.df = pd.read_csv(matrix_path)
        self.df = self.df[self.df['Funder'].notna()]  # Remove empty rows
        
    def match_deal(self, deal_data):
        """
        Match a deal to appropriate lenders
        
        Args:
            deal_data: Dict containing:
                - fico_score: int
                - time_in_business_months: int
                - amount: float
                - industry: str ('Transportation', 'Non-Trucking', 'Medical', etc.)
                - equipment_type: str
                
        Returns:
            List of matched lenders with scores
        """
        # Convert TIB to years
        tib_years = deal_data['time_in_business_months'] / 12
        
        # Map industry
        industry_map = {
            'Transportation': ['OTR', 'Vocational'],
            'Non-Trucking': ['Non-Trucking'],
            'Medical': ['Medical'],
            'Construction': ['Vocational', 'Non-Trucking']
        }
        
        target_industries = industry_map.get(deal_data.get('industry'), ['Non-Trucking'])
        
        # Filter lenders
        matches = []
        
        for idx, row in self.df.iterrows():
            score = 0
            reasons = []
            decline_risks = []
            
            # Check industry match
            if row['Industry'] not in target_industries:
                continue
                
            # Check FICO
            min_fico = row['Min FICO'] if pd.notna(row['Min FICO']) else 0
            if deal_data['fico_score'] >= min_fico:
                score += 30
                reasons.append(f"FICO {deal_data['fico_score']} meets minimum {int(min_fico)}")
            else:
                decline_risks.append(f"FICO below minimum ({int(min_fico)} required)")
                continue  # Hard stop
                
            # Check TIB
            min_tib = row['TIB (yrs)'] if pd.notna(row['TIB (yrs)']) else 0
            if tib_years >= min_tib:
                score += 25
                reasons.append(f"TIB {tib_years:.1f} yrs meets minimum {min_tib} yrs")
            else:
                decline_risks.append(f"TIB below minimum ({min_tib} yrs required)")
                continue  # Hard stop
                
            # Check amount
            app_only_max = row['App Only Max'] if pd.notna(row['App Only Max']) else float('inf')
            min_financed = row['Min Financed'] if pd.notna(row['Min Financed']) else 0
            
            if min_financed <= deal_data['amount'] <= app_only_max:
                score += 20
                reasons.append(f"Amount ${deal_data['amount']:,.0f} within range")
            else:
                if deal_data['amount'] < min_financed:
                    decline_risks.append(f"Amount below minimum (${min_financed:,.0f} required)")
                else:
                    decline_risks.append(f"Amount exceeds app-only max (${app_only_max:,.0f})")
                continue
                
            # Industry preference bonus
            if row['Industry'] in target_industries[:1]:  # Primary industry
                score += 15
                reasons.append("Primary industry match")
            else:
                score += 5
                reasons.append("Secondary industry match")
                
            # Rate card quality (lower rate = better)
            try:
                rate_range = float(row['Rate Range']) if pd.notna(row['Rate Range']) else 0.5
            except (ValueError, TypeError):
                rate_range = 0.5
                
            if rate_range < 0.15:
                score += 10
                reasons.append("Excellent rate card")
            elif rate_range < 0.25:
                score += 5
                reasons.append("Good rate card")
                
            matches.append({
                'funder': row['Funder'],
                'program': row['Rate Card'],
                'industry': row['Industry'],
                'score': score,
                'min_fico': int(min_fico) if pd.notna(min_fico) else None,
                'min_tib_years': min_tib if pd.notna(min_tib) else None,
                'amount_range': f"${int(min_financed):,} - ${int(app_only_max):,}",
                'rate_range': rate_range,
                'down_payment': row['Down Pmt'] if pd.notna(row['Down Pmt']) else None,
                'reasons': reasons,
                'decline_risks': decline_risks
            })
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 5
        return matches[:5]
    
    def get_lender_stats(self):
        """Get statistics about the lender matrix"""
        return {
            'total_programs': len(self.df),
            'unique_funders': self.df['Funder'].nunique(),
            'industries': self.df['Industry'].unique().tolist(),
            'fico_range': {
                'min': self.df['Min FICO'].min(),
                'max': self.df['Min FICO'].max()
            },
            'amount_range': {
                'min': self.df['Min Financed'].min(),
                'max': self.df['App Only Max'].max()
            }
        }

# Demo usage
if __name__ == "__main__":
    # Initialize matcher
    matcher = LenderMatcher('/home/ubuntu/lendlogic-v3.4/test_inputs/cleaned_lender_matrix.csv')
    
    # Sample deal
    sample_deal = {
        'fico_score': 720,
        'time_in_business_months': 68,
        'amount': 125000,
        'industry': 'Transportation',
        'equipment_type': 'Semi-Truck'
    }
    
    print("=== LENDER MATCHER DEMO ===\n")
    print(f"Deal: {sample_deal}\n")
    
    # Get matches
    matches = matcher.match_deal(sample_deal)
    
    print(f"Found {len(matches)} matching lenders:\n")
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. **{match['funder']}** - {match['program']}")
        print(f"   Score: {match['score']}/100")
        print(f"   Industry: {match['industry']}")
        print(f"   Amount Range: {match['amount_range']}")
        print(f"   Min FICO: {match['min_fico']}")
        print(f"   Min TIB: {match['min_tib_years']} years")
        print(f"   Rate: {match['rate_range']:.2%}")
        print(f"   Reasons: {', '.join(match['reasons'])}")
        print()
    
    # Save results
    output_path = '/home/ubuntu/lendlogic-v3.4/lender_match_demo_output.json'
    
    # Convert numpy types to native Python types for JSON serialization
    stats = matcher.get_lender_stats()
    stats['fico_range']['min'] = float(stats['fico_range']['min'])
    stats['fico_range']['max'] = float(stats['fico_range']['max'])
    stats['amount_range']['min'] = float(stats['amount_range']['min'])
    stats['amount_range']['max'] = float(stats['amount_range']['max'])
    stats['total_programs'] = int(stats['total_programs'])
    stats['unique_funders'] = int(stats['unique_funders'])
    
    with open(output_path, 'w') as f:
        json.dump({
            'deal': sample_deal,
            'matches': matches,
            'stats': stats
        }, f, indent=2)
    
    print(f"✅ Results saved to: {output_path}")

