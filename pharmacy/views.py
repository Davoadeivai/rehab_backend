from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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
from django.db import models
from patients.models import Notification
from django.db.models.functions import TruncMonth

# Create your views here.

class PharmacyManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Allow superusers and staff members to access pharmacy views
        if user.is_authenticated and (user.is_superuser or user.is_staff):
            return True
        # Also allow users in pharmacy_manager group
        return user.groups.filter(name='pharmacy_manager').exists()

class DrugAdvancedSearchForm(forms.Form):
    name = forms.CharField(label='نام دارو', required=False)
    category = forms.CharField(label='دسته', required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), label='تامین‌کننده', required=False)
    expiration_before = forms.DateField(label='انقضا قبل از تاریخ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    low_stock = forms.BooleanField(label='فقط داروهای کم‌موجودی', required=False)
    expired = forms.BooleanField(label='فقط داروهای تاریخ مصرف گذشته', required=False)

class DrugListView(LoginRequiredMixin, ListView):
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

class DrugCreateView(LoginRequiredMixin, CreateView):
    model = Drug
    fields = ['name', 'category', 'description', 'supplier', 'price', 'expiration_date']
    template_name = 'pharmacy/drug_form.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class DrugUpdateView(LoginRequiredMixin, UpdateView):
    model = Drug
    fields = ['name', 'category', 'description', 'supplier', 'price', 'expiration_date']
    template_name = 'pharmacy/drug_form.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class DrugDeleteView(LoginRequiredMixin, DeleteView):
    model = Drug
    template_name = 'pharmacy/drug_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:drug_list')

class SupplierListView(PharmacyManagerRequiredMixin, ListView):
    model = Supplier
    template_name = 'pharmacy/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(PharmacyManagerRequiredMixin, CreateView):
    model = Supplier
    fields = ['name', 'contact_info', 'address']
    template_name = 'pharmacy/supplier_form.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class SupplierUpdateView(PharmacyManagerRequiredMixin, UpdateView):
    model = Supplier
    fields = ['name', 'contact_info', 'address']
    template_name = 'pharmacy/supplier_form.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class SupplierDeleteView(PharmacyManagerRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'pharmacy/supplier_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:supplier_list')

class DrugPurchaseForm(forms.ModelForm):
    class Meta:
        model = DrugPurchase
        fields = ['drug', 'supplier', 'quantity', 'purchase_price', 'interval_days', 'total_cost']
        widgets = {
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'interval_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        purchase_price = cleaned_data.get('purchase_price')
        if quantity and purchase_price:
            cleaned_data['total_cost'] = quantity * purchase_price
        return cleaned_data

class DrugPurchaseCreateView(LoginRequiredMixin, CreateView):
    model = DrugPurchase
    form_class = DrugPurchaseForm
    template_name = 'pharmacy/purchase_form.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

    def form_valid(self, form):
        # ثبت زمان دقیق خرید
        form.instance.purchase_datetime = timezone.now()
        # محاسبه مبلغ کل خرید
        if not form.instance.total_cost:
            form.instance.total_cost = form.instance.quantity * form.instance.purchase_price
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

class DrugPurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = DrugPurchase
    form_class = DrugPurchaseForm
    template_name = 'pharmacy/purchase_form.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

class DrugPurchaseDeleteView(LoginRequiredMixin, DeleteView):
    model = DrugPurchase
    template_name = 'pharmacy/purchase_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:purchase_list')

class DrugPurchaseSearchForm(forms.Form):
    drug = forms.ModelChoiceField(queryset=Drug.objects.all(), label='دارو', required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), label='تامین‌کننده', required=False)
    date_from = forms.DateField(label='از تاریخ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(label='تا تاریخ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class DrugPurchaseListView(LoginRequiredMixin, ListView):
    model = DrugPurchase
    template_name = 'pharmacy/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('drug', 'supplier')
        form = DrugPurchaseSearchForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('drug'):
                queryset = queryset.filter(drug=form.cleaned_data['drug'])
            if form.cleaned_data.get('supplier'):
                queryset = queryset.filter(supplier=form.cleaned_data['supplier'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(purchase_date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(purchase_date__lte=form.cleaned_data['date_to'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchases = context['purchases']
        total_cost_sum = purchases.aggregate(total=models.Sum('total_cost'))['total'] or 0
        context['total_cost_sum'] = total_cost_sum
        context['search_form'] = DrugPurchaseSearchForm(self.request.GET)
        # موجودی فعلی هر دارو
        drug_ids = purchases.values_list('drug_id', flat=True)
        inventory_map = {inv.drug_id: inv.quantity for inv in DrugInventory.objects.filter(drug_id__in=drug_ids)}
        context['inventory_map'] = inventory_map
        context['low_stock_threshold'] = 10
        return context

class DrugSaleListView(LoginRequiredMixin, ListView):
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

class DrugSaleByPrescriptionView(LoginRequiredMixin, CreateView):
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
        # نگاشت نوع دارو در نسخه به مدل داروی داروخانه
        medication_type = prescription.medication_type
        drug, _ = Drug.objects.get_or_create(
            medication_type=medication_type,
            defaults={
                'name': medication_type.name,
                'category': '',
                'description': getattr(medication_type, 'description', '') or '',
                'price': 0,
            },
        )
        # ثبت فروش دارو
        sale = DrugSale.objects.create(
            drug=drug,
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

class DrugSaleUpdateView(LoginRequiredMixin, UpdateView):
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

class DrugSaleDeleteView(LoginRequiredMixin, DeleteView):
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

class DrugInventoryReportView(PharmacyManagerRequiredMixin, ListView):
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

from django.contrib.auth.mixins import LoginRequiredMixin

class PharmacyDashboardView(LoginRequiredMixin, ListView):
    model = DrugInventory
    template_name = 'pharmacy/dashboard.html'
    context_object_name = 'inventories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اعلان کم‌موجودی
        low_stock = DrugInventory.objects.filter(quantity__lt=10)
        for inv in low_stock:
            Notification.objects.get_or_create(
                title=f"هشدار کم‌موجودی: {inv.drug.name}",
                message=f"موجودی داروی {inv.drug.name} کمتر از ۱۰ عدد است (فعلی: {inv.quantity}).",
                patient=None
            )
        # اعلان تاریخ مصرف گذشته
        expired = Drug.objects.filter(expiration_date__lt=timezone.now().date())
        for drug in expired:
            Notification.objects.get_or_create(
                title=f"هشدار تاریخ مصرف گذشته: {drug.name}",
                message=f"داروی {drug.name} تاریخ مصرفش گذشته است (انقضا: {drug.expiration_date}).",
                patient=None
            )
        # دیگر contextها را فقط برای نمایش اصلی ارسال کن
        return context

class DrugInventoryExcelExportView(PharmacyManagerRequiredMixin, ListView):
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

class DrugSaleCreateView(LoginRequiredMixin, CreateView):
    model = DrugSale
    fields = ['drug', 'quantity', 'sale_price', 'patient_name', 'prescription']
    template_name = 'pharmacy/sale_form.html'
    success_url = reverse_lazy('pharmacy:sale_list')

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Form is valid, processing...")
        
        try:
            # Get the cleaned data
            drug = form.cleaned_data.get('drug')
            quantity = form.cleaned_data.get('quantity')
            logger.info(f"Processing sale for drug: {drug}, quantity: {quantity}")
            
            if not drug or quantity is None:
                messages.error(self.request, 'لطفا تمام فیلدهای ضروری را پر کنید.')
                return self.form_invalid(form)

            # Check inventory
            inventory, created = DrugInventory.objects.get_or_create(drug=drug)
            if quantity > inventory.quantity:
                form.add_error('quantity', f'موجودی کافی نیست. موجودی فعلی: {inventory.quantity}')
                messages.error(self.request, f'موجودی کافی نیست. موجودی فعلی: {inventory.quantity}')
                return self.form_invalid(form)

            # Save the form
            logger.info("Saving the form...")
            response = super().form_valid(form)
            sale = form.instance
            logger.info(f"Sale saved with ID: {sale.id}")
            
            # Update inventory
            inventory.quantity -= quantity
            inventory.save()
            
            # Log the sale
            InventoryLog.objects.create(
                drug=sale.drug,
                action='sale',
                quantity=sale.quantity,
                user=self.request.user,
                note=f'فروش به بیمار: {sale.patient_name}'
            )

            # Show success message
            messages.success(
                self.request,
                f'فروش {sale.quantity} عدد از داروی {sale.drug.name} با موفقیت ثبت شد.'
            )

            # Show warning if inventory is low
            if inventory.quantity < 5:
                messages.warning(
                    self.request,
                    f'هشدار: موجودی داروی {sale.drug.name} به {inventory.quantity} عدد کاهش یافت!'
                )

            logger.info(f"Sale processed successfully. New inventory: {inventory.quantity}")
            return response

        except Exception as e:
            logger.error(f"Error in form processing: {str(e)}", exc_info=True)
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in DrugSaleCreateView: {str(e)}")
            
            # Show error message to user
            messages.error(
                self.request,
                'خطایی در ثبت فروش رخ داد. لطفاً دوباره تلاش کنید.'
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Log form errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)

class DrugSaleReportView(LoginRequiredMixin, TemplateView):
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

class DrugPurchaseExcelExportView(LoginRequiredMixin, View):
    model = DrugPurchase

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'خریدهای دارو'
        # Header
        ws.append([
            'نام دارو', 'تامین‌کننده', 'تعداد', 'قیمت خرید', 'مبلغ کل', 'تاریخ خرید', 'زمان دقیق خرید', 'بازه زمانی (روز)'
        ])
        for purchase in queryset:
            ws.append([
                str(purchase.drug),
                str(purchase.supplier) if purchase.supplier else '-',
                purchase.quantity,
                float(purchase.purchase_price),
                float(purchase.total_cost) if purchase.total_cost else '',
                purchase.purchase_date.strftime('%Y-%m-%d') if purchase.purchase_date else '',
                purchase.purchase_datetime.strftime('%Y-%m-%d %H:%M') if purchase.purchase_datetime else '',
                purchase.interval_days if purchase.interval_days else '',
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=purchase_list.xlsx'
        wb.save(response)
        return response

class DrugPurchaseDetailView(LoginRequiredMixin, DetailView):
    model = DrugPurchase
    template_name = 'pharmacy/purchase_detail.html'
    context_object_name = 'purchase'

class DrugDetailView(LoginRequiredMixin, DetailView):
    model = Drug
    template_name = 'pharmacy/drug_detail.html'
    context_object_name = 'drug'
    login_url = '/login/'

class PharmacyAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'pharmacy/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # فروش ماهانه
        sales_by_month = (
            DrugSale.objects.annotate(month=TruncMonth('sale_date'))
            .values('month')
            .annotate(total=Sum('quantity'))
            .order_by('month')
        )
        context['sales_by_month'] = list(sales_by_month)
        # خرید ماهانه
        purchases_by_month = (
            DrugPurchase.objects.annotate(month=TruncMonth('purchase_date'))
            .values('month')
            .annotate(total=Sum('quantity'))
            .order_by('month')
        )
        context['purchases_by_month'] = list(purchases_by_month)
        # پرفروش‌ترین داروها
        top_drugs = (
            DrugSale.objects.values('drug__name')
            .annotate(total=Sum('quantity'))
            .order_by('-total')[:10]
        )
        context['top_drugs'] = list(top_drugs)
        return context
