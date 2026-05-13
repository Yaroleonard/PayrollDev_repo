from rest_framework import serializers
from .models import TaxBracket, Deduction, EmployeeDeduction, PayrollPeriod, Payslip


class TaxBracketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxBracket
        fields = '__all__'


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'


class EmployeeDeductionSerializer(serializers.ModelSerializer):
    deduction_name = serializers.CharField(source='deduction.name', read_only=True)

    class Meta:
        model = EmployeeDeduction
        fields = '__all__'


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department = serializers.CharField(source='employee.department.name', read_only=True)
    period = serializers.CharField(source='payroll_period.__str__', read_only=True)

    class Meta:
        model = Payslip
        fields = '__all__'


class PayrollPeriodSerializer(serializers.ModelSerializer):
    payslip_count = serializers.SerializerMethodField()
    total_gross = serializers.SerializerMethodField()
    total_net = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PayrollPeriod
        fields = '__all__'

    def get_payslip_count(self, obj):
        return obj.payslips.count()

    def get_total_gross(self, obj):
        from django.db.models import Sum
        result = obj.payslips.aggregate(total=Sum('gross_salary'))
        return result['total'] or 0

    def get_total_net(self, obj):
        from django.db.models import Sum
        result = obj.payslips.aggregate(total=Sum('net_salary'))
        return result['total'] or 0


class PayrollPeriodCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = ['month', 'year', 'start_date', 'end_date', 'payment_date', 'notes']
