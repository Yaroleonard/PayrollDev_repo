"""
Ghana PAYE Tax & SSNIT Calculator
Based on Ghana Revenue Authority (GRA) tax bands
"""
from decimal import Decimal


# Ghana PAYE tax bands (annual) - 2024
GHANA_TAX_BANDS = [
    (Decimal('0'), Decimal('4380'), Decimal('0')),          # First GHS 365/month → 0%
    (Decimal('4380'), Decimal('5940'), Decimal('5')),        # Next GHS 130/month → 5%
    (Decimal('5940'), Decimal('18000'), Decimal('10')),      # Next GHS 1005/month → 10%
    (Decimal('18000'), Decimal('42000'), Decimal('17.5')),   # Next GHS 2000/month → 17.5%
    (Decimal('42000'), Decimal('144000'), Decimal('25')),    # Next → 25%
    (Decimal('144000'), None, Decimal('30')),                # Above → 30%
]

SSNIT_EMPLOYEE_RATE = Decimal('5.5')   # 5.5% of basic salary
SSNIT_EMPLOYER_RATE = Decimal('13')    # 13% of basic salary


def calculate_paye(annual_taxable_income: Decimal) -> Decimal:
    """Calculate PAYE tax from annual taxable income."""
    total_tax = Decimal('0')
    for lower, upper, rate in GHANA_TAX_BANDS:
        if annual_taxable_income <= lower:
            break
        taxable = (upper if upper else annual_taxable_income) - lower
        taxable = min(taxable, annual_taxable_income - lower)
        total_tax += taxable * rate / Decimal('100')
    return total_tax / Decimal('12')  # Return monthly tax


def calculate_ssnit(basic_salary: Decimal):
    """Return (employee_contribution, employer_contribution)."""
    employee = basic_salary * SSNIT_EMPLOYEE_RATE / Decimal('100')
    employer = basic_salary * SSNIT_EMPLOYER_RATE / Decimal('100')
    return employee.quantize(Decimal('0.01')), employer.quantize(Decimal('0.01'))


def compute_payslip(salary_grade, extra_deductions=None, bonus=Decimal('0'), overtime=Decimal('0')):
    """
    Compute full payslip breakdown.
    Returns a dict with all earnings, deductions, and net pay.
    """
    basic = salary_grade.basic_salary
    housing = salary_grade.housing_allowance
    transport = salary_grade.transport_allowance
    medical = salary_grade.medical_allowance
    other_allow = salary_grade.other_allowances

    gross = basic + housing + transport + medical + other_allow + bonus + overtime

    # SSNIT on basic salary only
    ssnit_emp, ssnit_er = calculate_ssnit(basic)

    # PAYE: taxable income = gross - SSNIT employee share
    taxable_monthly = gross - ssnit_emp
    annual_taxable = taxable_monthly * Decimal('12')
    paye = calculate_paye(annual_taxable).quantize(Decimal('0.01'))

    # Other deductions
    other_deduct_total = Decimal('0')
    deductions_breakdown = []
    if extra_deductions:
        for ed in extra_deductions:
            val = ed.custom_value or ed.deduction.value
            if ed.deduction.deduction_type == 'percentage':
                amount = basic * val / Decimal('100')
            else:
                amount = val
            other_deduct_total += amount
            deductions_breakdown.append({
                'name': ed.deduction.name,
                'amount': str(amount.quantize(Decimal('0.01')))
            })

    total_deductions = paye + ssnit_emp + other_deduct_total
    net_salary = gross - total_deductions

    return {
        'basic_salary': basic,
        'housing_allowance': housing,
        'transport_allowance': transport,
        'medical_allowance': medical,
        'other_allowances': other_allow,
        'overtime_pay': overtime,
        'bonus': bonus,
        'gross_salary': gross.quantize(Decimal('0.01')),
        'paye_tax': paye,
        'ssnit_employee': ssnit_emp,
        'ssnit_employer': ssnit_er,
        'other_deductions': other_deduct_total.quantize(Decimal('0.01')),
        'total_deductions': total_deductions.quantize(Decimal('0.01')),
        'net_salary': net_salary.quantize(Decimal('0.01')),
        'deductions_breakdown': deductions_breakdown,
    }
