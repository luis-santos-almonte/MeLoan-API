from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Dict
from dateutil.relativedelta import relativedelta

class CalculationService:
    
    @staticmethod
    def calculate_monthly_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
        P = Decimal(str(principal))
        r = Decimal(str(annual_rate)) / 100 / 12
        n = months
        
        if r == 0:
            return (P / n).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return payment.quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @staticmethod
    def generate_amortization_schedule(
        principal: Decimal,
        annual_rate: Decimal,
        months: int,
        start_date: date
    ) -> List[Dict]:
        monthly_payment = CalculationService.calculate_monthly_payment(principal, annual_rate, months)
        monthly_rate = Decimal(str(annual_rate)) / 100 / 12
        
        balance = Decimal(str(principal))
        schedule = []
        current_date = start_date
        
        for i in range(1, months + 1):
            interest = (balance * monthly_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
            
            principal_payment = monthly_payment - interest
            
            if i == months:
                principal_payment = balance
                monthly_payment = balance + interest
            
            balance -= principal_payment
            
            due_date = current_date + relativedelta(months=1)
            
            schedule.append({
                "payment_number": i,
                "due_date": due_date,
                "scheduled_payment": float(monthly_payment),
                "scheduled_principal": float(principal_payment),
                "scheduled_interest": float(interest),
                "remaining_balance": float(max(balance, 0))
            })
            
            current_date = due_date
        
        return schedule