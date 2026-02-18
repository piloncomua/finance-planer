"""
Модуль для расчета инвестиций со сложным процентом.
Воспроизводит логику Excel калькулятора.
"""

class InvestmentCalculator:
    def __init__(self, params):
        """
        Инициализация калькулятора с параметрами.
        """
        self.initial_capital = params['initial_capital']
        self.monthly_income = params['monthly_income']
        self.monthly_living_expenses = params['monthly_living_expenses']
        self.income_growth_rate = params.get('income_growth_rate', 0.0)
        self.interest_rate = params['interest_rate']
        self.inflation_rate = params['inflation_rate']
        self.current_age = params['current_age']
        
        # Режимы пенсии
        self.retirement_mode = params.get('retirement_mode', 'manual') # 'manual' или 'auto'
        self.retirement_age = params.get('retirement_age', 60)
        
    def calculate_year(self, year_num, prev_year_data, actual_retirement_age=None):
        """
        Расчет одного года. Коэффициенты индексации применяются с 1-го года (year_num).
        """
        age = self.current_age + year_num
        
        # Индексация со старта (Year 1 уже проиндексирован)
        current_monthly_income = self.monthly_income * ((1 + self.income_growth_rate) ** year_num)
        current_monthly_living_expenses = self.monthly_living_expenses * ((1 + self.inflation_rate) ** year_num)
        
        total_capital_start = self.initial_capital if year_num == 1 else prev_year_data['total_capital_end']
        
        if total_capital_start == 'Ø':
            return self._empty_year(year_num, age, current_monthly_income, current_monthly_living_expenses)

        # Определяем фазу (накопление или пенсия)
        eff_retirement_age = actual_retirement_age if actual_retirement_age is not None else self.retirement_age
        
        is_accumulation = age < eff_retirement_age
        
        if is_accumulation:
            investment_capital = current_monthly_income - current_monthly_living_expenses
            expenses_inflation = 0
        else:
            # На пенсии доход = 0, расходы = проиндексированные расходы на жизнь (не менее 2% от капитала)
            investment_capital = 0
            # 2% Floor Rule: withdrawal is at least 2% of starting capital annually
            base_expenses = current_monthly_living_expenses
            floor_expenses = (0.02 * total_capital_start) / 12
            expenses_inflation = max(base_expenses, floor_expenses)

        # Чистый приток/отток
        net_capital = investment_capital - expenses_inflation
        annual_net = net_capital * 12
        
        # Доход от процентов
        interest_income = total_capital_start * self.interest_rate
        
        # Процент на новые вложения за полгода (среднее)
        half_year_interest = max(0, net_capital * (self.interest_rate * 12) / 2)
        
        total_sum = half_year_interest + interest_income + total_capital_start + annual_net
        total_capital_end = total_sum if total_sum > 0 else 'Ø'
        
        # Процент расходов относительно КРУПНОГО капитала в конце года
        if total_capital_end != 'Ø' and total_capital_end > 0:
            expense_percentage = (expenses_inflation * 12) / total_capital_end * 100
        else:
            expense_percentage = 0
            
        return {
            'year': year_num,
            'age': age,
            'current_monthly_income': current_monthly_income,
            'current_monthly_living_expenses': current_monthly_living_expenses,
            'investment_capital': investment_capital,
            'expenses_inflation': expenses_inflation,
            'net_capital': net_capital,
            'annual_expenses': annual_net,
            'total_capital_start': total_capital_start,
            'interest_income': interest_income,
            'half_year_interest': half_year_interest,
            'total_capital_end': total_capital_end,
            'expense_percentage': expense_percentage
        }

    def _empty_year(self, year_num, age, income, expenses):
        return {
            'year': year_num, 'age': age,
            'current_monthly_income': income, 'current_monthly_living_expenses': expenses,
            'investment_capital': 0, 'expenses_inflation': expenses,
            'net_capital': -expenses, 'annual_expenses': -expenses * 12,
            'total_capital_start': 'Ø', 'interest_income': 0,
            'half_year_interest': 0, 'total_capital_end': 'Ø',
            'expense_percentage': 0
        }

    def get_full_projection(self, max_age=90):
        """
        Получить полный прогноз. Если режим 'auto', сначала ищем возраст пенсии.
        """
        actual_retirement_age = self.retirement_age
        
        if self.retirement_mode == 'auto':
            actual_retirement_age = self._find_auto_retirement_age(max_age)
            
        results = []
        prev_year_data = None
        max_years = max_age - self.current_age
        
        for year_num in range(1, max_years + 1):
            year_data = self.calculate_year(year_num, prev_year_data, actual_retirement_age)
            results.append(year_data)
            prev_year_data = year_data
            if year_data['total_capital_end'] == 'Ø' and year_num > (actual_retirement_age - self.current_age):
                break
        
        return results, actual_retirement_age

    def _find_auto_retirement_age(self, max_age):
        """
        Ищет минимальный возраст, когда расходы / капитал <= 4%.
        """
        prev_year_data = None
        for year_num in range(1, max_age - self.current_age + 1):
            # В режиме поиска мы всегда в фазе накопления
            year_data = self.calculate_year(year_num, prev_year_data, actual_retirement_age=999)
            
            # Проверяем условие 4%: расходы будущего года / текущий капитал
            # (Для простоты: текущие расходы / текущий капитал в конце года)
            if year_data['total_capital_end'] != 'Ø' and year_data['total_capital_end'] > 0:
                current_expenses_annual = year_data['current_monthly_living_expenses'] * 12
                withdrawal_rate = (current_expenses_annual / year_data['total_capital_end']) * 100
                if withdrawal_rate <= 4:
                    return self.current_age + year_num
            
            prev_year_data = year_data
            if year_data['total_capital_end'] == 'Ø':
                break
        return max_age # Если не нашли, выходим в конце
