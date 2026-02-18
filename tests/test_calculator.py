"""
Unit tests for InvestmentCalculator
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator import InvestmentCalculator

def test_basic_calculation():
    """Test basic calculation with simple parameters"""
    params = {
        'initial_capital': 1000000,
        'monthly_income': 10000,
        'monthly_living_expenses': 5000,
        'interest_rate': 0.08,
        'inflation_rate': 0.02,
        'income_growth_rate': 0.03,
        'current_age': 30,
        'retirement_age': 40
    }
    
    calculator = InvestmentCalculator(params)
    results, actual_ret_age = calculator.get_full_projection(max_age=50)
    
    assert len(results) > 0
    assert results[0]['age'] == 31
    assert results[0]['year'] == 1
    assert actual_ret_age == 40

def test_excel_parameters():
    """Test with parameters from Excel file"""
    params = {
        'initial_capital': 1600000,
        'monthly_income': 25000,
        'monthly_living_expenses': 0,
        'interest_rate': 0.08,
        'inflation_rate': 0.02,
        'income_growth_rate': 0.03,
        'current_age': 35,
        'retirement_age': 45
    }
    
    calculator = InvestmentCalculator(params)
    results, actual_ret_age = calculator.get_full_projection(max_age=90)
    
    # Check first year
    assert results[0]['year'] == 1
    assert results[0]['age'] == 36
    assert results[0]['total_capital_start'] == 1600000
    
    # Find year 36 (row 37 in Excel)
    year_36 = next((r for r in results if r['year'] == 36), None)
    assert year_36 is not None
    assert year_36['age'] == 71
    
    # Values should be close to our model's expectation
    # Our new logic (start-of-period indexation) yields ~34.8M
    expected_capital = 34850000
    actual_capital = year_36['total_capital_start']
    margin = expected_capital * 0.05
    
    assert abs(actual_capital - expected_capital) < margin, \
        f"Expected ~{expected_capital}, got {actual_capital}"

def test_retirement_phase():
    """Test that expenses start after retirement age"""
    params = {
        'initial_capital': 1000000,
        'monthly_income': 10000,
        'monthly_living_expenses': 5000,
        'interest_rate': 0.08,
        'inflation_rate': 0.02,
        'income_growth_rate': 0.03,
        'current_age': 30,
        'retirement_age': 35
    }
    
    calculator = InvestmentCalculator(params)
    results, _ = calculator.get_full_projection(max_age=40)
    
    # Before retirement - no expenses in accumulation phase
    year_before = next(r for r in results if r['age'] == 34)
    assert year_before['expenses_inflation'] == 0
    
    # After retirement - expenses should start
    year_after = next(r for r in results if r['age'] == 36)
    assert year_after['expenses_inflation'] > 0

def test_2percent_floor_rule():
    """Test the 2% Floor Rule for retirement spending"""
    params = {
        'initial_capital': 10000000,
        'monthly_income': 0,
        'monthly_living_expenses': 1000,
        'interest_rate': 0.05,
        'inflation_rate': 0.02,
        'current_age': 50,
        'retirement_age': 51
    }
    
    calculator = InvestmentCalculator(params)
    results, _ = calculator.get_full_projection(max_age=60)
    
    retirement_year = next(r for r in results if r['age'] == 51)
    
    # Withdrawal should be floor-based
    # Start capital is roughly 10.5M
    # 2% of 10.5M is 210k. 
    # monthly_living_expenses indexed is ~1020.
    assert retirement_year['expenses_inflation'] >= (retirement_year['total_capital_start'] * 0.02 / 12)
    assert retirement_year['expenses_inflation'] > 1020

def test_auto_retirement_mode():
    """Test searching for retirement age via 4% rule"""
    params = {
        'initial_capital': 1000000,
        'monthly_income': 10000,
        'monthly_living_expenses': 2000,
        'interest_rate': 0.08,
        'inflation_rate': 0.02,
        'income_growth_rate': 0.03,
        'current_age': 30,
        'retirement_mode': 'auto'
    }
    
    calculator = InvestmentCalculator(params)
    results, actual_ret_age = calculator.get_full_projection(max_age=60)
    
    assert actual_ret_age > 30
    assert actual_ret_age < 60
    
    ret_year_data = next(r for r in results if r['age'] == actual_ret_age)
    withdrawal_rate = (ret_year_data['current_monthly_living_expenses'] * 12 / ret_year_data['total_capital_end']) * 100
    assert withdrawal_rate <= 4.1

if __name__ == '__main__':
    test_basic_calculation()
    test_excel_parameters()
    test_retirement_phase()
    test_2percent_floor_rule()
    test_auto_retirement_mode()
    print("Success: All tests passed!")
