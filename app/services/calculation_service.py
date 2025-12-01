from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Dict
from dateutil.relativedelta import relativedelta

class CalculationService:
    
    @staticmethod
    def calculate_monthly_payment(
        principal: Decimal, 
        annual_rate: Decimal, 
        months: int,
        insurance_monthly: Decimal = Decimal("0")
    ) -> Decimal:
        base_payment = CalculationService._calculate_base_payment(principal, annual_rate, months)
        total_payment = base_payment + Decimal(str(insurance_monthly))
        return total_payment.quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @staticmethod
    def generate_amortization_schedule(
        principal: Decimal,
        annual_rate: Decimal,
        months: int,
        start_date: date,
        payment_day: int = 1,
        payment_frequency: str = "monthly",
        insurance_monthly: Decimal = Decimal("0"),
        grace_period_months: int = 0,
        interest_calculation_method: str = "30/360"
    ) -> List[Dict]:
        monthly_rate = Decimal(str(annual_rate)) / 100 / 12
        base_payment = CalculationService._calculate_base_payment(principal, annual_rate, months)
        insurance = Decimal(str(insurance_monthly))
        
        balance = Decimal(str(principal))
        schedule = []
        
        current_date = CalculationService._get_first_payment_date(start_date, payment_day, payment_frequency)
        
        for i in range(1, months + 1):
            if i == 1:
                days_in_period = CalculationService._calculate_days_in_period(
                    start_date, 
                    current_date, 
                    interest_calculation_method
                )
            else:
                prev_date = CalculationService._get_previous_payment_date(current_date, payment_frequency, payment_day)
                days_in_period = CalculationService._calculate_days_in_period(
                    prev_date,
                    current_date,
                    interest_calculation_method
                )
            
            if interest_calculation_method == "30/360":
                interest = (balance * monthly_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
            elif interest_calculation_method == "actual/365":
                daily_rate = Decimal(str(annual_rate)) / 100 / 365
                interest = (balance * daily_rate * days_in_period).quantize(Decimal('0.01'), ROUND_HALF_UP)
            else:
                daily_rate = Decimal(str(annual_rate)) / 100 / 360
                interest = (balance * daily_rate * days_in_period).quantize(Decimal('0.01'), ROUND_HALF_UP)
            
            if i <= grace_period_months:
                principal_payment = Decimal("0")
                total_payment = interest + insurance
            else:
                principal_payment = base_payment - interest
                total_payment = base_payment + insurance
            
            if i == months:
                principal_payment = balance
                total_payment = balance + interest + insurance
            
            balance -= principal_payment
            
            schedule.append({
                "payment_number": i,
                "due_date": current_date,
                "scheduled_payment": float(total_payment),
                "scheduled_principal": float(principal_payment),
                "scheduled_interest": float(interest),
                "insurance_amount": float(insurance),
                "remaining_balance": float(max(balance, 0)),
                "is_grace_period": i <= grace_period_months
            })
            
            current_date = CalculationService._get_next_payment_date(current_date, payment_frequency, payment_day)
        
        return schedule
    
    @staticmethod
    def calculate_late_payment_penalty(
        scheduled_payment: Decimal,
        days_overdue: int,
        penalty_rate: Decimal
    ) -> Decimal:
        if days_overdue <= 0 or penalty_rate == 0:
            return Decimal("0")
        
        daily_rate = Decimal(str(penalty_rate)) / 100
        penalty = (scheduled_payment * daily_rate * days_overdue).quantize(Decimal('0.01'), ROUND_HALF_UP)
        return penalty
    
    @staticmethod
    def _calculate_base_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
        P = Decimal(str(principal))
        r = Decimal(str(annual_rate)) / 100 / 12
        n = months
        
        if r == 0:
            return (P / n).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return payment.quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_days_in_period(start: date, end: date, method: str) -> int:
        if method == "30/360":
            return 30
        else:
            return (end - start).days
    
    @staticmethod
    def _get_first_payment_date(start_date: date, payment_day: int, frequency: str) -> date:
        if frequency == "monthly":
            next_month = start_date + relativedelta(months=1)
            try:
                return next_month.replace(day=payment_day)
            except ValueError:
                return next_month.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        elif frequency == "biweekly":
            return start_date + timedelta(days=15)
        elif frequency == "weekly":
            return start_date + timedelta(days=7)
        return start_date + relativedelta(months=1)
    
    @staticmethod
    def _get_next_payment_date(current_date: date, frequency: str, payment_day: int) -> date:
        if frequency == "monthly":
            next_date = current_date + relativedelta(months=1)
            try:
                return next_date.replace(day=payment_day)
            except ValueError:
                return next_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        elif frequency == "biweekly":
            return current_date + timedelta(days=15)
        elif frequency == "weekly":
            return current_date + timedelta(days=7)
        return current_date + relativedelta(months=1)
    
    @staticmethod
    def _get_previous_payment_date(current_date: date, frequency: str, payment_day: int) -> date:
        if frequency == "monthly":
            prev_date = current_date - relativedelta(months=1)
            try:
                return prev_date.replace(day=payment_day)
            except ValueError:
                return prev_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        elif frequency == "biweekly":
            return current_date - timedelta(days=15)
        elif frequency == "weekly":
            return current_date - timedelta(days=7)
        return current_date - relativedelta(months=1)