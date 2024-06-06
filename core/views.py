from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .models import Order
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def index(request):
    form = UserRegisterForm()
    return render(request, 'core/index.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Tu cuenta ha sido creada! Ahora puedes iniciar sesión.')
            return redirect('index')
        else:
            messages.error(request, 'Hubo un error en el registro. Por favor, revisa los campos.')
            return render(request, 'core/index.html', {'form': form})
    return redirect('index')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verificar si el usuario existe
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario no existe.')
            form = UserRegisterForm()  # Asegúrate de que el formulario de registro esté disponible
            return render(request, 'core/index.html', {'form': form})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Contraseña incorrecta.')
            form = UserRegisterForm()  # Asegúrate de que el formulario de registro esté disponible
            return render(request, 'core/index.html', {'form': form})

    form = UserRegisterForm()  # Asegúrate de que el formulario de registro esté disponible
    return render(request, 'core/index.html', {'form': form})

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def order(request):
    next_order_number = Order.objects.count() + 1
    return render(request, 'core/order.html', {'next_order_number': next_order_number})

@login_required
def submit_order(request):
    if request.method == 'POST':
        try:
            # Recoger datos del formulario
            order_data = {
                'user': request.user,
                'order_date': request.POST.get('order_date'),
                'seller_name': request.POST.get('seller_name'),
                'seller_email': request.POST.get('seller_email'),
                'seller_phone': request.POST.get('seller_phone'),
                'seller_website': request.POST.get('seller_website'),
                'seller_address': request.POST.get('seller_address'),
                'buyer_name': request.POST.get('buyer_name'),
                'buyer_email': request.POST.get('buyer_email'),
                'buyer_phone': request.POST.get('buyer_phone'),
                'buyer_address': request.POST.get('buyer_address'),
                'shipping_address': request.POST.get('shipping_address'),
                'payment_email': request.POST.get('payment_email'),
                'cheque_to': request.POST.get('cheque_to'),
                'bank_transfer': request.POST.get('bank_transfer'),
                'notes': request.POST.get('notes', ''),
                'subtotal': request.POST.get('subtotal'),
                'discount_total': request.POST.get('discount_total'),
                'shipping_cost': request.POST.get('shipping_cost'),
                'tax_total': request.POST.get('tax_total'),
                'total': request.POST.get('total'),
                'amount_paid': request.POST.get('amount_paid'),
                'balance_due': request.POST.get('balance_due'),
            }
            order = Order.objects.create(**order_data)

            # Generar PDF si es necesario
            if 'generate_pdf' in request.POST:
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="order_{order.order_number}.pdf"'
                buffer = canvas.Canvas(response, pagesize=letter)

                # Títulos
                buffer.setFont("Helvetica-Bold", 16)
                buffer.drawString(100, 750, "Orden de Compra")
                buffer.setFont("Helvetica", 12)

                # Información del vendedor
                buffer.drawString(100, 730, f"Vendedor: {order.seller_name}")
                buffer.drawString(100, 715, f"Correo: {order.seller_email}")
                buffer.drawString(100, 700, f"Teléfono: {order.seller_phone}")
                buffer.drawString(100, 685, f"Dirección: {order.seller_address}")

                # Información del comprador
                buffer.drawString(100, 665, f"Comprador: {order.buyer_name}")
                buffer.drawString(100, 650, f"Correo: {order.buyer_email}")
                buffer.drawString(100, 635, f"Teléfono: {order.buyer_phone}")
                buffer.drawString(100, 620, f"Dirección: {order.buyer_address}")

                # Detalles del pedido
                y = 600
                buffer.drawString(100, y, "Descripción")
                buffer.drawString(200, y, "Precio Neto")
                buffer.drawString(300, y, "Cantidad")
                buffer.drawString(400, y, "Descuento")
                buffer.drawString(500, y, "Total Neto")

                product_details = zip(
                    request.POST.getlist('product_description[]'),
                    request.POST.getlist('product_net_price[]'),
                    request.POST.getlist('product_quantity[]'),
                    request.POST.getlist('product_tax[]'),
                    request.POST.getlist('product_discount[]'),
                    request.POST.getlist('product_total_net[]'),
                )

                y -= 20
                for description, net_price, quantity, tax, discount, total_net in product_details:
                    buffer.drawString(100, y, description)
                    buffer.drawString(200, y, net_price)
                    buffer.drawString(300, y, quantity)
                    buffer.drawString(400, y, discount)
                    buffer.drawString(500, y, total_net)
                    y -= 20

                # Totales
                y -= 20
                buffer.drawString(100, y, f"Subtotal: {order.subtotal}")
                y -= 20
                buffer.drawString(100, y, f"Descuento Total: {order.discount_total}")
                y -= 20
                buffer.drawString(100, y, f"Costo de Envío: {order.shipping_cost}")
                y -= 20
                buffer.drawString(100, y, f"Impuesto de Venta: {order.tax_total}")
                y -= 20
                buffer.drawString(100, y, f"Total: {order.total}")
                y -= 20
                buffer.drawString(100, y, f"Cantidad Pagada: {order.amount_paid}")
                y -= 20
                buffer.drawString(100, y, f"Saldo Adeudado: {order.balance_due}")

                buffer.showPage()
                buffer.save()
                return response

            messages.success(request, 'Orden guardada con éxito.')
            return JsonResponse({'success': True, 'order_id': order.order_number})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
@login_required
def download_order_pdf(request, order_id):
    order = get_object_or_ock(Order, pk=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'
    buffer = canvas.Canvas(response, pagesize=letter)

    # Títulos
    buffer.setFont("Helvetica-Bold", 16)
    buffer.drawString(100, 750, "Orden de Compra")
    buffer.setFont("Helvetica", 12)

    # Información del vendedor
    buffer.drawString(100, 730, f"Vendedor: {order.seller_name}")
    buffer.drawString(100, 715, f"Correo: {order.seller_email}")
    buffer.drawString(100, 700, f"Teléfono: {order.seller_phone}")
    buffer.drawString(100, 685, f"Dirección: {order.seller_address}")

    # Información del comprador
    buffer.drawString(100, 665, f"Comprador: {order.buyer_name}")
    buffer.drawString(100, 650, f"Correo: {order.buyer_email}")
    buffer.drawString(100, 635, f"Teléfono: {order.buyer_phone}")
    buffer.drawString(100, 620, f"Dirección: {order.buyer_address}")

    # Detalles del pedido
    y = 600
    buffer.drawString(100, y, "Descripción")
    buffer.drawString(200, y, "Precio Neto")
    buffer.drawString(300, y, "Cantidad")
    buffer.drawString(400, y, "Descuento")
    buffer.drawString(500, y, "Total Neto")

    product_details = zip(
        order.product_description.split(','),
        order.product_net_price.split(','),
        order.product_quantity.split(','),
        order.product_tax.split(','),
        order.product_discount.split(','),
        order.product_total_net.split(','),
    )

    y -= 20
    for description, net_price, quantity, tax, discount, total_net in product_details:
        buffer.drawString(100, y, description)
        buffer.drawString(200, y, net_price)
        buffer.drawString(300, y, quantity)
        buffer.drawString(400, y, discount)
        buffer.drawString(500, y, total_net)
        y -= 20

    # Totales
    y -= 20
    buffer.drawString(100, y, f"Subtotal: {order.subtotal}")
    y -= 20
    buffer.drawString(100, y, f"Descuento Total: {order.discount_total}")
    y -= 20
    buffer.drawString(100, y, f"Costo de Envío: {order.shipping_cost}")
    y -= 20
    buffer.drawString(100, y, f"Impuesto de Venta: {order.tax_total}")
    y -= 20
    buffer.drawString(100, y, f"Total: {order.total}")
    y -= 20
    buffer.drawString(100, y, f"Cantidad Pagada: {order.amount_paid}")
    y -= 20
    buffer.drawString(100, y, f"Saldo Adeudado: {order.balance_due}")

    buffer.showPage()
    buffer.save()
    return response