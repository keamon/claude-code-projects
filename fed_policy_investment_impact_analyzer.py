import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sqlite3
import warnings
warnings.filterwarnings('ignore')

class FedPolicyInvestmentImpactAnalyzer:
    """
    Analyze how Federal Reserve policy changes impact personal and business investment strategies
    """
    
    def __init__(self):
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.analysis_results = {}
        
    def analyze_asset_class_performance_by_fed_regime(self):
        """Analyze how different asset classes perform under various Fed policy regimes"""
        
        # Historical performance data by Fed regime (approximate historical averages)
        regime_performance = {
            'Ultra_Accommodative': {  # 2020-2021: 0% rates, massive QE
                'Large_Cap_Stocks': 18.5,
                'Small_Cap_Stocks': 22.3,
                'Growth_Stocks': 25.1,
                'Value_Stocks': 12.4,
                'Long_Term_Bonds': 8.2,
                'Short_Term_Bonds': 2.1,
                'Corporate_Bonds': 6.8,
                'High_Yield_Bonds': 12.5,
                'REITs': 15.3,
                'Commodities': 18.9,
                'Gold': 8.7,
                'International_Developed': 14.2,
                'Emerging_Markets': 19.8,
                'Cash_Equivalents': 0.3
            },
            'Aggressive_Tightening': {  # 2022-2023: Rapid rate hikes
                'Large_Cap_Stocks': -12.8,
                'Small_Cap_Stocks': -18.4,
                'Growth_Stocks': -24.6,
                'Value_Stocks': -2.1,
                'Long_Term_Bonds': -18.5,
                'Short_Term_Bonds': -2.3,
                'Corporate_Bonds': -8.9,
                'High_Yield_Bonds': -6.2,
                'REITs': -22.7,
                'Commodities': 8.4,
                'Gold': -1.2,
                'International_Developed': -14.5,
                'Emerging_Markets': -19.3,
                'Cash_Equivalents': 3.8
            },
            'Cutting_Cycle': {  # 2024-2025: Gradual rate cuts
                'Large_Cap_Stocks': 14.2,
                'Small_Cap_Stocks': 16.8,
                'Growth_Stocks': 18.9,
                'Value_Stocks': 11.3,
                'Long_Term_Bonds': 12.6,
                'Short_Term_Bonds': 4.2,
                'Corporate_Bonds': 8.7,
                'High_Yield_Bonds': 9.4,
                'REITs': 13.8,
                'Commodities': 3.2,
                'Gold': 6.8,
                'International_Developed': 12.4,
                'Emerging_Markets': 15.6,
                'Cash_Equivalents': 4.5
            }
        }
        
        return regime_performance
    
    def generate_personal_investment_strategies(self):
        """Generate investment strategies for personal investors"""
        
        strategies = {
            'Conservative_Investor': {
                'profile': {
                    'age_range': '55-70',
                    'risk_tolerance': 'Low',
                    'time_horizon': '5-15 years',
                    'income_needs': 'Current income priority'
                },
                'ultra_accommodative': {
                    'asset_allocation': {
                        'Stocks': 40,
                        'Bonds': 50,
                        'Alternatives': 5,
                        'Cash': 5
                    },
                    'strategy_focus': [
                        'Dividend-paying stocks for income',
                        'Short-duration bonds to reduce interest rate risk',
                        'TIPS for inflation protection',
                        'Avoid duration risk in low-rate environment'
                    ],
                    'key_risks': ['Inflation eroding purchasing power', 'Low bond yields']
                },
                'aggressive_tightening': {
                    'asset_allocation': {
                        'Stocks': 30,
                        'Bonds': 55,
                        'Alternatives': 5,
                        'Cash': 10
                    },
                    'strategy_focus': [
                        'Lock in higher bond yields',
                        'Defensive dividend stocks',
                        'Money market funds and CDs',
                        'Reduce equity risk during volatility'
                    ],
                    'key_risks': ['Equity market volatility', 'Credit spread widening']
                },
                'cutting_cycle': {
                    'asset_allocation': {
                        'Stocks': 45,
                        'Bonds': 45,
                        'Alternatives': 5,
                        'Cash': 5
                    },
                    'strategy_focus': [
                        'Extend bond duration for price appreciation',
                        'Quality dividend stocks',
                        'Utilities and REITs recovery',
                        'Gradual risk-on positioning'
                    ],
                    'key_risks': ['Timing the bottom in rates', 'Inflation resurgence']
                }
            },
            'Moderate_Investor': {
                'profile': {
                    'age_range': '40-55',
                    'risk_tolerance': 'Medium',
                    'time_horizon': '10-25 years',
                    'income_needs': 'Growth with some income'
                },
                'ultra_accommodative': {
                    'asset_allocation': {
                        'Stocks': 70,
                        'Bonds': 25,
                        'Alternatives': 5,
                        'Cash': 0
                    },
                    'strategy_focus': [
                        'Growth stocks benefit from low rates',
                        'Technology and innovation themes',
                        'REITs and real estate exposure',
                        'International diversification'
                    ],
                    'key_risks': ['Asset bubble formation', 'Overvaluation risks']
                },
                'aggressive_tightening': {
                    'asset_allocation': {
                        'Stocks': 60,
                        'Bonds': 30,
                        'Alternatives': 5,
                        'Cash': 5
                    },
                    'strategy_focus': [
                        'Value over growth stocks',
                        'Financial sector exposure',
                        'Short-duration bond ladders',
                        'Defensive positioning'
                    ],
                    'key_risks': ['Growth stock underperformance', 'Economic slowdown']
                },
                'cutting_cycle': {
                    'asset_allocation': {
                        'Stocks': 75,
                        'Bonds': 20,
                        'Alternatives': 5,
                        'Cash': 0
                    },
                    'strategy_focus': [
                        'Balanced growth/value approach',
                        'Interest-sensitive sectors recovery',
                        'Long-duration bonds for capital gains',
                        'Emerging markets exposure'
                    ],
                    'key_risks': ['Policy reversal risk', 'Geopolitical uncertainties']
                }
            },
            'Aggressive_Investor': {
                'profile': {
                    'age_range': '25-40',
                    'risk_tolerance': 'High',
                    'time_horizon': '20-40 years',
                    'income_needs': 'Long-term growth focus'
                },
                'ultra_accommodative': {
                    'asset_allocation': {
                        'Stocks': 90,
                        'Bonds': 5,
                        'Alternatives': 5,
                        'Cash': 0
                    },
                    'strategy_focus': [
                        'High-growth technology stocks',
                        'Small-cap and emerging companies',
                        'Cryptocurrency and digital assets',
                        'Venture capital and private equity themes'
                    ],
                    'key_risks': ['Extreme volatility', 'Speculative bubble risks']
                },
                'aggressive_tightening': {
                    'asset_allocation': {
                        'Stocks': 75,
                        'Bonds': 15,
                        'Alternatives': 10,
                        'Cash': 0
                    },
                    'strategy_focus': [
                        'Quality growth at reasonable prices',
                        'Contrarian value opportunities',
                        'International diversification',
                        'Alternative investments'
                    ],
                    'key_risks': ['Extended bear market', 'Liquidity constraints']
                },
                'cutting_cycle': {
                    'asset_allocation': {
                        'Stocks': 85,
                        'Bonds': 10,
                        'Alternatives': 5,
                        'Cash': 0
                    },
                    'strategy_focus': [
                        'Growth stock recovery',
                        'Small-cap outperformance potential',
                        'Emerging markets and international',
                        'Thematic growth investments'
                    ],
                    'key_risks': ['False dawn in growth', 'Sector rotation timing']
                }
            }
        }
        
        return strategies
    
    def generate_business_investment_strategies(self):
        """Generate investment strategies for businesses and institutions"""
        
        business_strategies = {
            'Corporate_Treasury': {
                'profile': {
                    'objective': 'Capital preservation and liquidity',
                    'constraints': 'Regulatory and board limitations',
                    'time_horizon': '1-3 years',
                    'risk_tolerance': 'Very Low'
                },
                'ultra_accommodative': {
                    'strategy': [
                        'Short-duration corporate bonds and CDs',
                        'Money market funds with stable NAV',
                        'Bank deposits with FDIC insurance',
                        'Avoid duration risk and credit risk'
                    ],
                    'cash_management': 'Focus on liquidity over yield',
                    'key_considerations': ['Negative real returns', 'Opportunity cost of cash']
                },
                'aggressive_tightening': {
                    'strategy': [
                        'Lock in higher short-term rates',
                        'Laddered CD and treasury strategy',
                        'High-grade corporate bonds',
                        'Flexible duration management'
                    ],
                    'cash_management': 'Optimize yield on excess cash',
                    'key_considerations': ['Credit risk management', 'Counterparty exposure']
                },
                'cutting_cycle': {
                    'strategy': [
                        'Extend duration selectively',
                        'High-quality corporate credit',
                        'Maintain liquidity buffers',
                        'Active duration management'
                    ],
                    'cash_management': 'Balance yield and liquidity needs',
                    'key_considerations': ['Reinvestment risk', 'Policy uncertainty']
                }
            },
            'Pension_Fund': {
                'profile': {
                    'objective': 'Meet long-term liabilities',
                    'constraints': 'Regulatory and actuarial requirements',
                    'time_horizon': '20-30 years',
                    'risk_tolerance': 'Medium to High'
                },
                'ultra_accommodative': {
                    'asset_allocation': {
                        'Equity': 60,
                        'Fixed_Income': 25,
                        'Alternatives': 15
                    },
                    'strategy': [
                        'Liability-driven investment approach',
                        'Real assets for inflation protection',
                        'Global diversification',
                        'Private markets allocation'
                    ],
                    'duration_matching': 'Partial liability hedging'
                },
                'aggressive_tightening': {
                    'asset_allocation': {
                        'Equity': 50,
                        'Fixed_Income': 35,
                        'Alternatives': 15
                    },
                    'strategy': [
                        'Defensive equity positioning',
                        'Long-duration bonds for liability matching',
                        'Credit spread opportunities',
                        'Real estate and infrastructure'
                    ],
                    'duration_matching': 'Increase liability hedging'
                },
                'cutting_cycle': {
                    'asset_allocation': {
                        'Equity': 65,
                        'Fixed_Income': 20,
                        'Alternatives': 15
                    },
                    'strategy': [
                        'Risk-on equity allocation',
                        'Duration extension for capital gains',
                        'Private market opportunities',
                        'International equity exposure'
                    ],
                    'duration_matching': 'Dynamic liability hedging'
                }
            },
            'Endowment_Foundation': {
                'profile': {
                    'objective': 'Perpetual growth and spending',
                    'constraints': 'Spending rate requirements',
                    'time_horizon': 'Perpetual',
                    'risk_tolerance': 'High'
                },
                'ultra_accommodative': {
                    'asset_allocation': {
                        'Equity': 50,
                        'Fixed_Income': 10,
                        'Alternatives': 40
                    },
                    'strategy': [
                        'Heavy alternative investments allocation',
                        'Private equity and venture capital',
                        'Hedge funds and absolute return',
                        'Real assets and commodities'
                    ],
                    'spending_policy': 'Conservative given low expected returns'
                },
                'aggressive_tightening': {
                    'asset_allocation': {
                        'Equity': 45,
                        'Fixed_Income': 20,
                        'Alternatives': 35
                    },
                    'strategy': [
                        'Opportunistic credit investments',
                        'Distressed debt opportunities',
                        'Defensive hedge fund strategies',
                        'Real estate value plays'
                    ],
                    'spending_policy': 'Maintain through volatility'
                },
                'cutting_cycle': {
                    'asset_allocation': {
                        'Equity': 55,
                        'Fixed_Income': 10,
                        'Alternatives': 35
                    },
                    'strategy': [
                        'Growth equity recovery',
                        'Venture capital deployment',
                        'Long-duration bonds for portfolio balance',
                        'International growth opportunities'
                    ],
                    'spending_policy': 'Gradual increase as returns improve'
                }
            }
        }
        
        return business_strategies
    
    def analyze_sector_rotation_strategies(self):
        """Analyze sector rotation strategies based on Fed policy changes"""
        
        sector_strategies = {
            'Interest_Rate_Sensitive_Sectors': {
                'Real_Estate': {
                    'ultra_accommodative': 'Strong outperformance due to low borrowing costs',
                    'aggressive_tightening': 'Significant underperformance as rates rise',
                    'cutting_cycle': 'Recovery as rate pressure eases',
                    'investment_approach': 'REITs, homebuilders, mortgage REITs'
                },
                'Utilities': {
                    'ultra_accommodative': 'Moderate performance, bond proxy behavior',
                    'aggressive_tightening': 'Underperform due to rate sensitivity',
                    'cutting_cycle': 'Defensive characteristics with yield appeal',
                    'investment_approach': 'High-dividend utilities, renewable energy'
                },
                'Financials': {
                    'ultra_accommodative': 'Pressure on net interest margins',
                    'aggressive_tightening': 'Benefit from rising rates and steeper curve',
                    'cutting_cycle': 'Mixed performance as rate tailwinds fade',
                    'investment_approach': 'Regional banks, insurance companies, asset managers'
                }
            },
            'Growth_vs_Value_Dynamics': {
                'Technology_Growth': {
                    'ultra_accommodative': 'Massive outperformance from low discount rates',
                    'aggressive_tightening': 'Significant underperformance due to high valuations',
                    'cutting_cycle': 'Recovery as growth premiums restore',
                    'investment_approach': 'Large-cap tech, software, innovation themes'
                },
                'Value_Stocks': {
                    'ultra_accommodative': 'Underperformance relative to growth',
                    'aggressive_tightening': 'Relative outperformance during rotation',
                    'cutting_cycle': 'Mixed performance as growth recovers',
                    'investment_approach': 'Energy, materials, industrials, financials'
                }
            },
            'Economic_Cycle_Sensitive': {
                'Consumer_Discretionary': {
                    'ultra_accommodative': 'Strong performance from stimulus and low rates',
                    'aggressive_tightening': 'Weakness from higher borrowing costs',
                    'cutting_cycle': 'Recovery as financial conditions ease',
                    'investment_approach': 'Retailers, auto, travel, entertainment'
                },
                'Industrials': {
                    'ultra_accommodative': 'Benefit from infrastructure and capex',
                    'aggressive_tightening': 'Pressure from economic slowdown concerns',
                    'cutting_cycle': 'Recovery potential from renewed investment',
                    'investment_approach': 'Capital goods, aerospace, transport'
                }
            }
        }
        
        return sector_strategies
    
    def create_investment_impact_visualization(self):
        """Create comprehensive visualization of Fed policy investment impacts"""
        
        # Get performance data
        regime_performance = self.analyze_asset_class_performance_by_fed_regime()
        
        # Create comprehensive dashboard
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Federal Reserve Policy Impact on Investment Strategies', 
                     fontsize=16, fontweight='bold')
        
        # 1. Asset Class Performance by Regime
        ax1 = axes[0, 0]
        
        asset_classes = list(regime_performance['Ultra_Accommodative'].keys())
        regimes = list(regime_performance.keys())
        
        # Create performance matrix
        performance_matrix = []
        for regime in regimes:
            performance_matrix.append([regime_performance[regime][asset] for asset in asset_classes])
        
        performance_df = pd.DataFrame(performance_matrix, 
                                    index=[r.replace('_', ' ') for r in regimes],
                                    columns=[a.replace('_', ' ') for a in asset_classes])
        
        # Plot top 8 asset classes for readability
        top_assets = performance_df.columns[:8]
        sns.heatmap(performance_df[top_assets], annot=True, cmap='RdYlGn', center=0, 
                   ax=ax1, fmt='.1f', cbar_kws={'label': 'Return (%)'})
        ax1.set_title('Asset Class Performance by Fed Regime (%)')
        ax1.set_xlabel('')
        ax1.set_ylabel('Fed Policy Regime')
        
        # 2. Personal Investor Allocation Changes
        ax2 = axes[0, 1]
        
        # Conservative investor allocation across regimes
        conservative_allocations = {
            'Ultra Accommodative': [40, 50, 5, 5],
            'Aggressive Tightening': [30, 55, 5, 10],
            'Cutting Cycle': [45, 45, 5, 5]
        }
        
        asset_types = ['Stocks', 'Bonds', 'Alternatives', 'Cash']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        x = np.arange(len(conservative_allocations))
        width = 0.6
        
        bottom = np.zeros(len(conservative_allocations))
        for i, asset_type in enumerate(asset_types):
            values = [conservative_allocations[regime][i] for regime in conservative_allocations.keys()]
            ax2.bar(x, values, width, bottom=bottom, label=asset_type, color=colors[i])
            bottom += values
        
        ax2.set_title('Conservative Investor Allocation by Regime')
        ax2.set_xlabel('Fed Policy Regime')
        ax2.set_ylabel('Allocation (%)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(conservative_allocations.keys(), rotation=45)
        ax2.legend()
        
        # 3. Business Strategy Focus
        ax3 = axes[0, 2]
        
        # Corporate treasury strategy evolution
        strategy_focus = {
            'Liquidity Management': [30, 45, 35],
            'Yield Optimization': [20, 40, 30],
            'Duration Management': [25, 35, 40],
            'Credit Risk Control': [25, 30, 25]
        }
        
        regimes_short = ['Accommodative', 'Tightening', 'Cutting']
        
        for i, (strategy, values) in enumerate(strategy_focus.items()):
            ax3.plot(regimes_short, values, marker='o', linewidth=2, label=strategy)
        
        ax3.set_title('Corporate Treasury Strategy Priorities')
        ax3.set_xlabel('Fed Policy Regime')
        ax3.set_ylabel('Priority Level (1-50)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Sector Performance Expectations
        ax4 = axes[1, 0]
        
        sector_performance = {
            'Technology': [-5, -25, 15],
            'Financials': [-10, 20, 5],
            'Real Estate': [15, -25, 10],
            'Utilities': [5, -8, 8],
            'Consumer Disc.': [10, -15, 12],
            'Healthcare': [8, 2, 6]
        }
        
        x_pos = np.arange(len(regimes_short))
        width = 0.12
        
        for i, (sector, performance) in enumerate(sector_performance.items()):
            offset = (i - len(sector_performance)/2) * width
            ax4.bar(x_pos + offset, performance, width, label=sector)
        
        ax4.set_title('Expected Sector Performance by Regime (%)')
        ax4.set_xlabel('Fed Policy Regime')
        ax4.set_ylabel('Expected Return (%)')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(regimes_short)
        ax4.legend()
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.grid(True, alpha=0.3)
        
        # 5. Risk-Return Profile Changes
        ax5 = axes[1, 1]
        
        # Portfolio risk-return for different investor types
        portfolio_profiles = {
            'Conservative': {
                'risk': [4, 8, 5],
                'return': [3, 1, 4]
            },
            'Moderate': {
                'risk': [8, 12, 9],
                'return': [6, 2, 7]
            },
            'Aggressive': {
                'risk': [15, 18, 16],
                'return': [10, 0, 12]
            }
        }
        
        colors_profile = ['green', 'blue', 'red']
        
        for i, (profile, data) in enumerate(portfolio_profiles.items()):
            ax5.scatter(data['risk'], data['return'], s=100, 
                       c=colors_profile[i], label=profile, alpha=0.7)
            
            # Connect points to show regime progression
            ax5.plot(data['risk'], data['return'], 
                    color=colors_profile[i], alpha=0.5, linestyle='--')
        
        ax5.set_xlabel('Portfolio Risk (Volatility %)')
        ax5.set_ylabel('Expected Return (%)')
        ax5.set_title('Risk-Return Profiles Across Fed Regimes')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Implementation Timeline
        ax6 = axes[1, 2]
        
        # Portfolio adjustment timeline
        timeline_actions = {
            'Month 1': ['Assess regime', 'Rebalance allocation'],
            'Month 2-3': ['Sector rotation', 'Duration adjustment'],
            'Month 4-6': ['Monitor performance', 'Tactical adjustments'],
            'Month 7-12': ['Strategic review', 'Annual rebalancing']
        }
        
        timeline_data = [25, 40, 20, 15]  # Effort allocation
        timeline_labels = list(timeline_actions.keys())
        
        wedges, texts, autotexts = ax6.pie(timeline_data, labels=timeline_labels, autopct='%1.0f%%',
                                         startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        ax6.set_title('Portfolio Adjustment Timeline\n(Effort Allocation)')
        
        plt.tight_layout()
        plt.savefig('fed_policy_investment_impact.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Investment impact visualization saved as 'fed_policy_investment_impact.png'")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive investment impact analysis report"""
        
        print("\n" + "="*80)
        print("FEDERAL RESERVE POLICY IMPACT ON INVESTMENT STRATEGIES")
        print("="*80)
        print(f"Analysis Date: {self.current_date}")
        
        # Get all strategy data
        regime_performance = self.analyze_asset_class_performance_by_fed_regime()
        personal_strategies = self.generate_personal_investment_strategies()
        business_strategies = self.generate_business_investment_strategies()
        sector_strategies = self.analyze_sector_rotation_strategies()
        
        # Current regime assessment
        print(f"\n🏛️ CURRENT FED POLICY REGIME: CUTTING CYCLE")
        print("-" * 60)
        print("• Fed Funds Rate: 4.33% (declining from 5.25% peak)")
        print("• Policy Direction: Gradual rate cuts toward neutral")
        print("• Market Environment: Risk-on with selectivity")
        print("• Duration: Expected 12-18 months to reach neutral rates")
        
        # Asset class performance analysis
        print(f"\n📊 ASSET CLASS PERFORMANCE BY FED REGIME")
        print("-" * 60)
        
        # Create performance summary table
        performance_summary = []
        asset_classes = ['Large_Cap_Stocks', 'Growth_Stocks', 'Value_Stocks', 'Long_Term_Bonds', 'REITs', 'Cash_Equivalents']
        
        for asset in asset_classes:
            row = [asset.replace('_', ' ')]
            for regime in regime_performance.keys():
                row.append(f"{regime_performance[regime][asset]:+.1f}%")
            performance_summary.append(row)
        
        # Print table
        headers = ['Asset Class'] + [r.replace('_', ' ') for r in regime_performance.keys()]
        print(f"{'Asset Class':<20} {'Ultra Accommodative':<18} {'Aggressive Tightening':<20} {'Cutting Cycle':<15}")
        print("-" * 75)
        
        for row in performance_summary:
            print(f"{row[0]:<20} {row[1]:<18} {row[2]:<20} {row[3]:<15}")
        
        # Personal investment strategies
        print(f"\n👤 PERSONAL INVESTMENT STRATEGIES")
        print("-" * 60)
        
        for investor_type, strategy_data in personal_strategies.items():
            print(f"\n{investor_type.replace('_', ' ')} ({strategy_data['profile']['age_range']}):")
            
            # Current regime recommendations
            current_strategy = strategy_data['cutting_cycle']
            allocation = current_strategy['asset_allocation']
            
            print(f"  Current Allocation: Stocks {allocation['Stocks']}%, Bonds {allocation['Bonds']}%, Alt {allocation['Alternatives']}%, Cash {allocation['Cash']}%")
            print(f"  Key Strategies:")
            for strategy in current_strategy['strategy_focus']:
                print(f"    • {strategy}")
            print(f"  Main Risks: {', '.join(current_strategy['key_risks'])}")
        
        # Business investment strategies
        print(f"\n🏢 BUSINESS INVESTMENT STRATEGIES")
        print("-" * 60)
        
        for business_type, strategy_data in business_strategies.items():
            print(f"\n{business_type.replace('_', ' ')}:")
            print(f"  Objective: {strategy_data['profile']['objective']}")
            
            current_strategy = strategy_data['cutting_cycle']
            
            if 'asset_allocation' in current_strategy:
                allocation = current_strategy['asset_allocation']
                print(f"  Current Allocation: Equity {allocation['Equity']}%, Fixed Income {allocation['Fixed_Income']}%, Alternatives {allocation['Alternatives']}%")
            
            print(f"  Strategy Focus:")
            for strategy in current_strategy['strategy']:
                print(f"    • {strategy}")
        
        # Sector rotation analysis
        print(f"\n🔄 SECTOR ROTATION STRATEGIES")
        print("-" * 60)
        
        print("\nCurrent Regime (Cutting Cycle) Sector Outlook:")
        
        # Interest rate sensitive sectors
        print(f"\n📈 OVERWEIGHT SECTORS:")
        overweight_sectors = [
            ("Technology Growth", "Recovery as growth premiums restore"),
            ("Real Estate", "Recovery as rate pressure eases"),
            ("Consumer Discretionary", "Recovery as financial conditions ease"),
            ("Industrials", "Recovery potential from renewed investment")
        ]
        
        for sector, rationale in overweight_sectors:
            print(f"  • {sector}: {rationale}")
        
        print(f"\n📉 UNDERWEIGHT SECTORS:")
        underweight_sectors = [
            ("Financials", "Mixed performance as rate tailwinds fade"),
            ("Value Stocks", "Mixed performance as growth recovers"),
            ("Energy/Materials", "Cyclical uncertainty in transition period")
        ]
        
        for sector, rationale in underweight_sectors:
            print(f"  • {sector}: {rationale}")
        
        # Implementation guidelines
        print(f"\n⚙️ IMPLEMENTATION GUIDELINES")
        print("-" * 60)
        
        print(f"\nPersonal Investors:")
        print(f"  • Phase 1 (Immediate): Rebalance to target allocations")
        print(f"  • Phase 2 (1-3 months): Extend bond duration gradually")
        print(f"  • Phase 3 (3-6 months): Increase growth stock exposure")
        print(f"  • Phase 4 (6-12 months): Monitor Fed communications for changes")
        
        print(f"\nBusiness Investors:")
        print(f"  • Corporate Treasury: Lock in current yields while extending duration selectively")
        print(f"  • Pension Funds: Increase equity allocation and extend duration for liability matching")
        print(f"  • Endowments: Maintain alternative allocations while increasing growth equity exposure")
        
        # Risk management
        print(f"\n⚠️ KEY RISKS TO MONITOR")
        print("-" * 60)
        print(f"  • Policy Reversal Risk: Fed may pause or reverse cuts if inflation resurges")
        print(f"  • Economic Slowdown: Aggressive cuts may signal economic weakness")
        print(f"  • Geopolitical Shocks: External events could alter Fed policy trajectory")
        print(f"  • Market Overreaction: Excessive risk-taking in anticipation of lower rates")
        print(f"  • Duration Risk: Bond prices vulnerable if cuts are less than expected")
        
        # Create visualization
        print(f"\n📊 GENERATING COMPREHENSIVE VISUALIZATION...")
        self.create_investment_impact_visualization()
        
        print(f"\n✅ ANALYSIS COMPLETE")
        print("-" * 60)
        print(f"📈 Visualization: fed_policy_investment_impact.png")
        print(f"🎯 Key Takeaway: Current cutting cycle favors balanced risk-on positioning")
        print(f"📋 Recommendation: Gradual portfolio adjustment over 3-6 month period")

def main():
    """Main execution function"""
    
    print("🏛️ Federal Reserve Policy Investment Impact Analysis")
    print("=" * 60)
    
    # Create analyzer
    analyzer = FedPolicyInvestmentImpactAnalyzer()
    
    # Run comprehensive analysis
    analyzer.generate_comprehensive_report()
    
    return analyzer

if __name__ == "__main__":
    main()