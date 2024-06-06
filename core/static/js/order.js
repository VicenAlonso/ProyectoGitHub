document.addEventListener('DOMContentLoaded', function() {
    const addProductButton = document.getElementById('addProduct');
    const productTableBody = document.querySelector('#productTable tbody');
    const amountPaidInput = document.querySelector('input[name="amount_paid"]');
    const shippingCostInput = document.querySelector('input[name="shipping_cost"]');
    const currencySelector = document.getElementById('currency');

    const submitOrderButton = document.getElementById('submitOrder');
    const confirmYesButton = document.getElementById('confirmYes');
    const confirmNoButton = document.getElementById('confirmNo');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));

    let generatePDF = false;

    const exchangeRates = {
        USD: 1,
        CLP: 800 // 1 USD = 800 CLP (ejemplo de tasa de cambio)
    };

    addProductButton.addEventListener('click', function() {
        const newRow = document.createElement('tr');

        newRow.innerHTML = `
            <td><input type="text" name="product_description[]" class="form-control" placeholder="Descripción del producto" required></td>
            <td><input type="number" step="0.01" name="product_net_price[]" class="form-control" placeholder="Precio Neto" data-usd="" required></td>
            <td><input type="number" name="product_quantity[]" class="form-control" placeholder="Cantidad" required></td>
            <td><input type="text" name="product_tax[]" class="form-control" value="19%" readonly></td>
            <td><input type="number" step="0.01" name="product_discount[]" class="form-control" placeholder="Descuento" required></td>
            <td><input type="number" step="0.01" name="product_total_net[]" class="form-control" placeholder="Total Neto" readonly></td>
            <td><button type="button" class="btn btn-danger btn-sm remove-product">Eliminar</button></td>
        `;

        productTableBody.appendChild(newRow);
        addEventListenersToRow(newRow);
    });

    function addEventListenersToRow(row) {
        const netPriceInput = row.querySelector('input[name="product_net_price[]"]');
        const quantityInput = row.querySelector('input[name="product_quantity[]"]');
        const discountInput = row.querySelector('input[name="product_discount[]"]');
        const totalNetInput = row.querySelector('input[name="product_total_net[]"]');
        const removeButton = row.querySelector('.remove-product');

        function calculateTotalNet() {
            const netPrice = parseFloat(netPriceInput.value) || 0;
            const quantity = parseInt(quantityInput.value) || 0;
            const discount = parseFloat(discountInput.value) || 0;

            const totalNet = (netPrice * quantity) * (1 - (discount / 100));
            totalNetInput.value = totalNet.toFixed(2);

            calculateSummary();
        }

        netPriceInput.addEventListener('input', calculateTotalNet);
        quantityInput.addEventListener('input', calculateTotalNet);
        discountInput.addEventListener('input', calculateTotalNet);
        removeButton.addEventListener('click', function() {
            row.remove();
            calculateSummary();
        });
    }

    function calculateSummary() {
        const totalNetInputs = document.querySelectorAll('input[name="product_total_net[]"]');
        const discountInputs = document.querySelectorAll('input[name="product_discount[]"]');
        let subtotal = 0;
        let discountTotal = 0;
        let taxTotal = 0;

        totalNetInputs.forEach((input, index) => {
            const totalNet = parseFloat(input.value) || 0;
            const discount = parseFloat(discountInputs[index].value) || 0;
            subtotal += totalNet;
            discountTotal += (totalNet * discount) / (100 - discount); // Ajuste del cálculo del descuento
        });

        taxTotal = subtotal * 0.19;
        const total = subtotal + taxTotal;
        const amountPaid = parseFloat(amountPaidInput.value) || 0;
        const shippingCost = parseFloat(shippingCostInput.value) || 0;
        const balanceDue = total - amountPaid + shippingCost;

        document.querySelector('input[name="subtotal"]').value = subtotal.toFixed(2);
        document.querySelector('input[name="discount_total"]').value = discountTotal.toFixed(2);
        document.querySelector('input[name="tax_total"]').value = taxTotal.toFixed(2);
        document.querySelector('input[name="total"]').value = total.toFixed(2);
        document.querySelector('input[name="balance_due"]').value = balanceDue.toFixed(2);
    }

    function convertCurrency() {
        const currency = currencySelector.value;
        const rate = exchangeRates[currency];

        document.querySelectorAll('input[name="product_net_price[]"]').forEach(input => {
            const valueInUSD = parseFloat(input.dataset.usd) || 0;
            input.value = (valueInUSD * rate).toFixed(2);
        });

        calculateSummary();
    }

    submitOrderButton.addEventListener('click', function() {
        confirmModal.show();
    });

    confirmYesButton.addEventListener('click', function() {
        generatePDF = true;
        confirmModal.hide();
        submitOrder();
    });

    confirmNoButton.addEventListener('click', function() {
        generatePDF = false;
        confirmModal.hide();
        submitOrder();
    });

    function submitOrder() {
        const form = document.getElementById('orderForm');
        const formData = new FormData(form);

        if (generatePDF) {
            formData.append('generate_pdf', 'true');
        }

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/submit_order/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Orden guardada');
                if (generatePDF) {
                    window.location.href = `/download_order_pdf/${data.order_id}/`;
                } else {
                    window.location.href = '/order/';
                }
            } else {
                alert('Error al guardar la orden');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    amountPaidInput.addEventListener('input', calculateSummary);
    shippingCostInput.addEventListener('input', calculateSummary);
    currencySelector.addEventListener('change', convertCurrency);

    // Add event listeners to the initial row
    document.querySelectorAll('#productTable tbody tr').forEach(row => {
        addEventListenersToRow(row);
    });

    // Initial calculations
    calculateSummary();
});
