from django.contrib.auth.models import User
from django.shortcuts import render, redirect,get_object_or_404
from .models import ProductDetail, ProductUserDetail
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from openpyxl import Workbook
from django.http import HttpResponse

@login_required
def create_product_user_detail(request):
    products = ProductDetail.objects.all()

    if request.method == "POST":
        for product in products:
            qty_key = f"quantity_{product.id}"
            quantity = request.POST.get(qty_key)
            if quantity:
                quantity = int(quantity)
                if quantity > 0:
                    # Update if already exists, else create
                    obj, created = ProductUserDetail.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        obj.quantity += quantity  # You can change this logic as needed
                        obj.save()
        return redirect("order_summary_view")  # Or wherever you want to go after saving
    return render(request, "product_user_detail_form.html", {'products': products})

@login_required
def order_summary_view(request):
    products = ProductUserDetail.objects.filter(user=request.user)
    total_price = products.aggregate(Sum('total_price'))['total_price__sum'] or 0
    return render(request, 'order_summary.html', {
        'products': products,
        'total_price': total_price,
    })

@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(ProductUserDetail, id=product_id)
    if request.method == 'POST':
        product.delete()
    return redirect('order_summary_view')

@login_required
def edit_product_user_detail(request, pk):
    detail = get_object_or_404(ProductUserDetail, pk=pk, user=request.user)
    products = ProductDetail.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')

        try:
            product = ProductDetail.objects.get(id=product_id)
            quantity = int(quantity)

            detail.product = product
            detail.quantity = quantity
            detail.total_price = product.price * quantity
            detail.save()
            return redirect('order_summary_view')  # or wherever you list the user details

        except (ProductDetail.DoesNotExist, ValueError):
            pass  # handle invalid input if needed

    return render(request, 'edit_product_user_detail.html', {
        'detail': detail,
        'products': products,
        'quantity_range': range(1, 11),
    })


@login_required
def export_user_product_details_xls(request):
    if request.user.is_superuser:
        wb = Workbook()
        ws = wb.active
        ws.title = "Product Summary"

        user_lst = User.objects.all()
        product_list = ProductDetail.objects.all()

        # Header row
        ws.append(["Product Name", "Product Price", "Total Quantity"] + list(user_lst.values_list('username',flat=True)))

        for product in product_list:
            prod_lst=[]
            for usr in user_lst:
                try:
                    product_detail = ProductUserDetail.objects.get(user=usr, product=product)
                    prod_lst.append(f'{product_detail.product.price} * {product_detail.quantity} = {product_detail.total_price}')
                except Exception:
                    prod_lst.append(0)
            total_quantity = ProductUserDetail.objects.filter(product__name=product.name).aggregate(total_sum=Sum('quantity'))
            ws.append([product.name,product.price,total_quantity.get('total_sum')] + prod_lst)

        net_count = []
        for usr in user_lst:
            gross_price = ProductUserDetail.objects.filter(user=usr).aggregate(total_sum=Sum('total_price'))
            net_count.append(gross_price.get('total_sum') if gross_price.get('total_sum') else 0)
        ws.append(['Gross Total','--'] + net_count)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=product_summary.xlsx'
        wb.save(response)
        return response
    return HttpResponse('Permission denied!!')

@login_required
def add_product(request):
    if request.user.is_superuser:
        products = [
            {"BALAJI NAMKEEN Chana Dal": 1.60},
            {"BALAJI Mung Dal": 1.60},
            {"BALAJI Tikha Mitha Mix 190gm": 1.60},
            {"BALAJI Ratlami Sev 190gm": 1.60},
            {"BALAJI Aloo Sev 190gm": 1.60},
            {"BALAJI Classic Sev 400gm": 2.95},
            {"BALAJI Aloo Sev 400gm": 2.95},
            {"BALAJI Ratlami Sev 400gm": 2.95},
            {"BALAJI Gathiya": 2.30},
            {"BALAJI Masala Sev Mamra": 2.00},
            {"BALAJI Sev Mamra": 2.00},
            {"BALAJI Bhel Mix Mamra": 2.00},
            {"BALAJI Chat Chaska Wafer": 1.75},
            {"BALAJI Tomato Twist Wafer": 1.75},
            {"BALAJI Simply Salted Wafer": 1.75},
            {"BALAJI Rumble Wafer": 1.75},
            {"BALAJI Masala Masti Wafer": 1.75},
            {"BALAJI Banana Wafers Karibana": 2.00},
            {"BALAJI Banana Wafers Mast Mari": 2.00},
            {"BALAJI Banana Wafers Mast Masala": 2.00},
            {"BALAJI Chataka Pataka Masala Masti": 0.80},
            {"BALAJI Chataka Pataka Flaming Hot": 0.80},
            {"BALAJI Chataka Pataka Tomato": 0.80},
            {"Good Day Biscuit": 2.30},
            {"BALAJI Tikha Mitha Mix 400gm": 2.95},
            {"BALAJI Khatta Mitha Mix": 2.95},
            {"BALAJI Farali Chevdo": 3.20},
            {"BALAJI Pop Ring": 0.90},
            {"BALAJI Wheels": 0.90},
            {"BALAJI Khakhra Methi": 1.40},
            {"BALAJI Khakhra Plain": 1.40},
            {"BALAJI Khakhra Masala": 1.40},
            {"BALAJI Khakhra Jeera": 1.40},
            {"Ol' Tymes Basmati Murmura": 3.99}
        ]
        for data in products:
            for prod,price in data.items():
                try:
                    ProductDetail.objects.get(name=prod)
                except Exception as e:
                    ProductDetail.objects.create(name=prod,price=price)
    return HttpResponse('Data Added Successfully!!')
