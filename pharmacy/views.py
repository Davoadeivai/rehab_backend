from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Drug, Supplier, DrugPurchase, DrugInventory, DrugSale, InventoryLog
from django.utils import timezone
from django.db.models import Sum
from patients.medication_models import Prescription, MedicationDistribution
from patients.patient_model import Patient
from django.contrib import messages
from django import forms
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
import openpyxl
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.template.loader import render_to_string
from django.views.generic.edit import FormView
from django.forms import ModelForm

# Create your views here.

class PharmacyManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='pharmacy_manager').exists() or user.is_staff

class DrugAdvancedSearchForm(forms.Form):
    name = forms.CharField(label='نام دارو', required=False)
    category = forms.CharField(label='دسته', required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), label='تامین‌کننده', required=False)
    expiration_before = forms.DateField(label='انقضا قبل از تاریخ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    low_stock = forms.BooleanField(label='فقط داروهای کم‌موجودی', required=False)
    expired = forms.BooleanField(label='فقط داروهای تاریخ مصرف گذشته', required=False)

class DrugListView(ListView):
    model = Drug
    template_name = 'pharmacy/drug_list.html'
    context_object_name = 'drugs'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplier')
        form = DrugAdvancedSearchForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('name'):
                queryset = queryset.filter(name__icontains=form.cleaned_data['name'])
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category__icontains=form.cleaned_data['category'])
            if form.cleaned_data.get('supplier'):
                queryset = queryset.filter(supplier=form.cleaned_data['supplier'])
            if form.cleaned_data.get('expiration_before'):
                queryset = queryset.filter(expiration_date__lte=form.cleaned_data['expiration_before'])
            if form.cleaned_data.get('low_stock'):
                low_stock_ids = DrugInventory.objects.filter(quantity__lt=10).values_list('drug_id', flat=True)
                queryset = queryset.filter(id__in=low_stock_ids)
            if form.cleaned_data.get('expired'):
                queryset = queryset.filter(expiration_date__lt=timezone.now().date())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DrugAdvancedSearchForm(self.request.GET)
        return context

class DrugCreateView(CreateView):
    model = Drug
    fields = ['name', 'category', 'description', 'supplier', 'price', 'expiration_date']
    template_name = 'pharmacy/drug_form.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class DrugUpdateView(UpdateView):
    model = Drug
    fields = ['name', 'category', 'description', 'supplier', 'price', 'expiration_date']
    template_name = 'pharmacy/drug_form.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class DrugDeleteView(DeleteView):
    model = Drug
    template_name = 'pharmacy/drug_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class SupplierListView(ListView):
    model = Supplier
    template_name = 'pharmacy/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    fields = ['name', 'contact_info', 'address']
    template_name = 'pharmacy/supplier_form.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class SupplierUpdateView(UpdateView):
    model = Supplier
    fields = ['name', 'contact_info', 'address']
    template_name = 'pharmacy/supplier_form.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'pharmacy/supplier_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class DrugPurchaseListView(ListView):
    model = DrugPurchase
    template_name = 'pharmacy/purchase_list.html'
    context_object_name = 'purchases'

class DrugPurchaseCreateView(CreateView):
    model = DrugPurchase
    fields = ['drug', 'supplier', 'quantity', 'purchase_price']
    template_name = 'pharmacy/purchase_form.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        purchase = form.instance
        inventory, created = DrugInventory.objects.get_or_create(drug=purchase.drug)
        inventory.quantity += purchase.quantity
        inventory.save()
        # ثبت لاگ خرید
        InventoryLog.objects.create(
            drug=purchase.drug,
            action='purchase',
            quantity=purchase.quantity,
            user=self.request.user if self.request.user.is_authenticated else None,
            note=f'خرید از تامین‌کننده: {purchase.supplier}'
        )
        return response

class DrugPurchaseUpdateView(UpdateView):
    model = DrugPurchase
    fields = ['drug', 'supplier', 'quantity', 'purchase_price']
    template_name = 'pharmacy/purchase_form.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

class DrugPurchaseDeleteView(DeleteView):
    model = DrugPurchase
    template_name = 'pharmacy/purchase_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

class DrugSaleListView(ListView):
    model = DrugSale
    template_name = 'pharmacy/sale_list.html'
    context_object_name = 'sales'

class DrugSaleByPrescriptionForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), label='بیمار')
    prescription = forms.ModelChoiceField(queryset=Prescription.objects.none(), label='نسخه فعال')
    quantity = forms.DecimalField(label='مقدار فروش', max_digits=10, decimal_places=2)
    sale_price = forms.DecimalField(label='قیمت فروش', max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        patient_id = kwargs.pop('patient_id', None)
        super().__init__(*args, **kwargs)
        if patient_id:
            self.fields['prescription'].queryset = Prescription.objects.filter(patient_id=patient_id)
        else:
            self.fields['prescription'].queryset = Prescription.objects.none()

class DrugSaleByPrescriptionView(FormView):
    form_class = DrugSaleByPrescriptionForm
    template_name = 'pharmacy/sale_by_prescription_form.html'
    success_url = reverse_lazy('pharmacy:sale_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            patient_id = self.request.POST.get('patient')
        else:
            patient_id = self.request.GET.get('patient')
        kwargs['patient_id'] = patient_id
        return kwargs

    def form_valid(self, form):
        prescription = form.cleaned_data['prescription']
        quantity = form.cleaned_data['quantity']
        sale_price = form.cleaned_data['sale_price']
        patient = form.cleaned_data['patient']
        # بررسی موجودی دارو
        try:
            inventory = prescription.medication_type.inventory
            if quantity > inventory.current_stock:
                form.add_error('quantity', 'موجودی کافی نیست.')
                return self.form_invalid(form)
        except Exception:
            form.add_error('quantity', 'موجودی دارو تعریف نشده است.')
            return self.form_invalid(form)
        # ثبت فروش دارو
        sale = DrugSale.objects.create(
            drug=None,  # اگر مدل داروخانه داروی جدا دارد، باید نگاشت شود
            quantity=quantity,
            sale_price=sale_price,
            patient_name=str(patient),
            prescription=prescription
        )
        # ثبت لاگ فروش
        InventoryLog.objects.create(
            drug=sale.drug,
            action='sale',
            quantity=quantity,
            user=self.request.user if self.request.user.is_authenticated else None,
            note=f'فروش به بیمار: {patient}'
        )
        # ثبت توزیع دارو
        MedicationDistribution.objects.create(
            prescription=prescription,
            distribution_date=timezone.now().date(),
            amount=quantity,
            remaining=prescription.total_prescribed - quantity
        )
        # کاهش موجودی
        inventory.current_stock -= quantity
        inventory.save()
        messages.success(self.request, 'فروش و توزیع دارو با موفقیت ثبت شد.')
        return redirect(self.success_url)

class DrugSaleUpdateView(UpdateView):
    model = DrugSale
    fields = ['drug', 'quantity', 'sale_price', 'patient_name', 'prescription']
    template_name = 'pharmacy/sale_form.html'
    success_url = reverse_lazy('pharmacy:sale_list')

    def form_valid(self, form):
        old_sale = self.get_object()
        old_quantity = old_sale.quantity
        old_drug = old_sale.drug
        response = super().form_valid(form)
        new_sale = form.instance
        if old_drug == new_sale.drug:
            diff = new_sale.quantity - old_quantity
            inventory, _ = DrugInventory.objects.get_or_create(drug=new_sale.drug)
            inventory.quantity -= diff
            inventory.save()
            InventoryLog.objects.create(
                drug=new_sale.drug,
                action='manual',
                quantity=abs(diff),
                user=self.request.user if self.request.user.is_authenticated else None,
                note=f'اصلاح موجودی به علت ویرایش فروش (کد فروش: {new_sale.pk})'
            )
            if inventory.quantity < 5:
                messages.warning(self.request, f'هشدار: موجودی داروی {new_sale.drug.name} کمتر از ۵ عدد است!')
        else:
            old_inventory, _ = DrugInventory.objects.get_or_create(drug=old_drug)
            old_inventory.quantity += old_quantity
            old_inventory.save()
            InventoryLog.objects.create(
                drug=old_drug,
                action='manual',
                quantity=old_quantity,
                user=self.request.user if self.request.user.is_authenticated else None,
                note=f'بازگرداندن موجودی داروی قبلی به علت تغییر دارو در ویرایش فروش (کد فروش: {old_sale.pk})'
            )
            new_inventory, _ = DrugInventory.objects.get_or_create(drug=new_sale.drug)
            new_inventory.quantity -= new_sale.quantity
            new_inventory.save()
            InventoryLog.objects.create(
                drug=new_sale.drug,
                action='manual',
                quantity=new_sale.quantity,
                user=self.request.user if self.request.user.is_authenticated else None,
                note=f'کاهش موجودی داروی جدید به علت تغییر دارو در ویرایش فروش (کد فروش: {new_sale.pk})'
            )
            if new_inventory.quantity < 5:
                messages.warning(self.request, f'هشدار: موجودی داروی {new_sale.drug.name} کمتر از ۵ عدد است!')
        messages.success(self.request, 'ویرایش فروش دارو با موفقیت انجام شد.')
        return response

class DrugSaleDeleteView(DeleteView):
    model = DrugSale
    template_name = 'pharmacy/sale_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:sale_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            inventory = DrugInventory.objects.get(drug=self.object.drug)
            inventory.quantity += self.object.quantity
            inventory.save()
            InventoryLog.objects.create(
                drug=self.object.drug,
                action='manual',
                quantity=self.object.quantity,
                user=request.user if request.user.is_authenticated else None,
                note=f'بازگرداندن موجودی به علت حذف فروش (کد فروش: {self.object.pk})'
            )
        except DrugInventory.DoesNotExist:
            pass
        messages.success(request, 'فروش دارو با موفقیت حذف شد و موجودی اصلاح گردید.')
        return super().delete(request, *args, **kwargs)

class DrugInventoryReportView(ListView):
    model = DrugInventory
    template_name = 'pharmacy/inventory_report.html'
    context_object_name = 'inventories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # داروهای کم‌موجودی
        context['low_stock'] = DrugInventory.objects.filter(quantity__lt=10)
        # داروهای تاریخ مصرف گذشته
        context['expired'] = Drug.objects.filter(expiration_date__lt=timezone.now().date())
        # مجموع فروش و خرید هر دارو
        sales = DrugSale.objects.values('drug__name').annotate(total_sold=Sum('quantity'))
        purchases = DrugPurchase.objects.values('drug__name').annotate(total_bought=Sum('quantity'))
        context['sales'] = {item['drug__name']: item['total_sold'] for item in sales}
        context['purchases'] = {item['drug__name']: item['total_bought'] for item in purchases}
        return context

class PharmacyDashboardView(ListView):
    model = DrugInventory
    template_name = 'pharmacy/dashboard.html'
    context_object_name = 'inventories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['low_stock'] = DrugInventory.objects.filter(quantity__lt=10)
        context['expired'] = Drug.objects.filter(expiration_date__lt=timezone.now().date())
        return context

class DrugInventoryExcelExportView(ListView):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'گزارش موجودی داروها'
        ws.append(['نام دارو', 'دسته', 'تامین‌کننده', 'موجودی', 'مجموع خرید', 'مجموع فروش'])
        for inv in DrugInventory.objects.select_related('drug'):
            drug = inv.drug
            total_bought = DrugPurchase.objects.filter(drug=drug).aggregate(total=Sum('quantity'))['total'] or 0
            total_sold = DrugSale.objects.filter(drug=drug).aggregate(total=Sum('quantity'))['total'] or 0
            ws.append([
                smart_str(drug.name),
                smart_str(drug.category),
                smart_str(drug.supplier) if drug.supplier else '-',
                inv.quantity,
                total_bought,
                total_sold
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=drug_inventory_report.xlsx'
        wb.save(response)
        return response

class DrugSaleCreateView(CreateView):
    model = DrugSale
    fields = ['drug', 'quantity', 'sale_price', 'patient_name', 'prescription']
    template_name = 'pharmacy/sale_form.html'
    success_url = reverse_lazy('pharmacy:sale_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        sale = form.instance
        inventory, created = DrugInventory.objects.get_or_create(drug=sale.drug)
        if sale.quantity > inventory.quantity:
            form.add_error('quantity', 'موجودی کافی نیست.')
            messages.error(self.request, 'موجودی کافی نیست.')
            return self.form_invalid(form)
        inventory.quantity -= sale.quantity
        inventory.save()
        InventoryLog.objects.create(
            drug=sale.drug,
            action='sale',
            quantity=sale.quantity,
            user=self.request.user if self.request.user.is_authenticated else None,
            note=f'فروش به بیمار: {sale.patient_name}'
        )
        if inventory.quantity < 5:
            messages.warning(self.request, f'هشدار: موجودی داروی {sale.drug.name} کمتر از ۵ عدد است!')
        messages.success(self.request, 'فروش دارو با موفقیت ثبت شد.')
        return response

class DrugSaleReportView(TemplateView):
    template_name = 'pharmacy/sale_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import datetime, timedelta
        from django.db.models import Sum
        # پارامترهای بازه زمانی
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        today = timezone.now().date()
        if not start:
            start = today.replace(day=1)  # ابتدای ماه جاری
        else:
            start = datetime.strptime(start, '%Y-%m-%d').date()
        if not end:
            end = today
        else:
            end = datetime.strptime(end, '%Y-%m-%d').date()
        sales = DrugSale.objects.filter(sale_date__date__gte=start, sale_date__date__lte=end)
        sales_by_drug = sales.values('drug__name').annotate(total_quantity=Sum('quantity'), total_amount=Sum('sale_price'))
        context['sales_by_drug'] = sales_by_drug
        context['start'] = start
        context['end'] = end
        context['total_sales'] = sales.aggregate(total=Sum('sale_price'))['total'] or 0
        context['total_count'] = sales.aggregate(total=Sum('quantity'))['total'] or 0
        return context
