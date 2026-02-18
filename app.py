from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from calculator import InvestmentCalculator
import os
import subprocess
import time

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def index():
    """Главная страница - отдает index.html"""
    return send_from_directory('static', 'index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    API endpoint для расчета инвестиций.
    
    Принимает JSON:
    {
        "initial_capital": 1600000,
        "monthly_income": 25000,
        "monthly_expenses": 0,
        "interest_rate": 8,  // в процентах
        "inflation_rate": 2,  // в процентах
        "current_age": 35,
        "retirement_age": 45,
        "max_age": 90  // опционально
    }
    
    Возвращает JSON с массивом данных по годам
    """
    try:
        data = request.json
        
        # Валидация входных данных
        required_fields = [
            'initial_capital', 'monthly_income', 'monthly_living_expenses',
            'income_growth_rate', 'interest_rate', 'inflation_rate', 
            'current_age', 'retirement_age'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Отсутствует поле: {field}'}), 400
        
        # Конвертируем проценты в десятичные дроби
        params = {
            'initial_capital': float(data['initial_capital']),
            'monthly_income': float(data['monthly_income']),
            'monthly_living_expenses': float(data['monthly_living_expenses']),
            'income_growth_rate': float(data['income_growth_rate']) / 100,
            'interest_rate': float(data['interest_rate']) / 100,
            'inflation_rate': float(data['inflation_rate']) / 100,
            'current_age': int(data['current_age']),
            'retirement_age': int(data['retirement_age']),
            'retirement_mode': data.get('retirement_mode', 'manual')
        }
        
        # Проверка логических ограничений
        if params['retirement_mode'] == 'manual' and params['retirement_age'] <= params['current_age']:
            return jsonify({'error': 'Возраст пенсии должен быть больше текущего возраста'}), 400
        
        if params['initial_capital'] < 0:
            return jsonify({'error': 'Начальный капитал не может быть отрицательным'}), 400
        
        # Создаем калькулятор и получаем результаты
        calculator = InvestmentCalculator(params)
        max_age = int(data.get('max_age', 90))
        projection_data, actual_ret_age = calculator.get_full_projection(max_age)
        
        # Форматируем результаты для отправки
        formatted_results = []
        for year_data in projection_data:
            formatted_results.append({
                'year': year_data['year'],
                'age': year_data['age'],
                'investment_capital': round(year_data['investment_capital'], 2) if isinstance(year_data['investment_capital'], (int, float)) else year_data['investment_capital'],
                'expenses_inflation': round(year_data['expenses_inflation'], 2) if isinstance(year_data['expenses_inflation'], (int, float)) else year_data['expenses_inflation'],
                'net_capital': round(year_data['net_capital'], 2) if isinstance(year_data['net_capital'], (int, float)) else year_data['net_capital'],
                'annual_expenses': round(year_data['annual_expenses'], 2) if isinstance(year_data['annual_expenses'], (int, float)) else year_data['annual_expenses'],
                'total_capital_start': round(year_data['total_capital_start'], 2) if isinstance(year_data['total_capital_start'], (int, float)) else year_data['total_capital_start'],
                'interest_income': round(year_data['interest_income'], 2) if isinstance(year_data['interest_income'], (int, float)) else year_data['interest_income'],
                'half_year_interest': round(year_data['half_year_interest'], 2) if isinstance(year_data['half_year_interest'], (int, float)) else year_data['half_year_interest'],
                'total_capital_end': round(year_data['total_capital_end'], 2) if isinstance(year_data['total_capital_end'], (int, float)) else year_data['total_capital_end'],
                'expense_percentage': round(year_data['expense_percentage'], 2)
            })
        
        return jsonify({
            'success': True,
            'data': formatted_results,
            'actual_retirement_age': actual_ret_age
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Запуск бота в отдельном процессе (для экономии на Render Free Tier)
    if os.environ.get('TELEGRAM_BOT_TOKEN'):
        print("Starting Bot as a subprocess...")
        subprocess.Popen(["python", "bot.py"])
    
    port = int(os.environ.get('PORT', 5000))
    # Включаем debug=False для продакшена на Render
    app.run(host='0.0.0.0', port=port, debug=False)
