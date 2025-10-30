"""
Invoice generation utilities using ReportLab for PDF creation.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


def generate_invoice_pdf(order, customer, order_items, config, output_path=None):
    """
    Generate a professional PDF invoice for an order.

    Args:
        order: Order dictionary with order details
        customer: Customer dictionary with customer details
        order_items: List of order items
        config: Flask app config
        output_path: Optional custom path for the PDF

    Returns:
        Tuple (success: bool, file_path: str or error_message: str)
    """
    try:
        # Create invoices directory if it doesn't exist
        invoices_dir = os.path.join('static', 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)

        # Generate invoice number if not exists
        if not order.get('invoice_number'):
            invoice_number = f"INV-{order['order_number']}"
        else:
            invoice_number = order['invoice_number']

        # Set output path
        if not output_path:
            output_path = os.path.join(invoices_dir, f"{invoice_number}.pdf")

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=6,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=12
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151')
        )

        # Company Header with Logo
        logo_path = os.path.join('static', 'images', 'logo', 'SSG-Logo.png')

        if os.path.exists(logo_path):
            # Create header with logo
            logo = Image(logo_path, width=25*mm, height=25*mm)

            header_data = [
                [logo, Paragraph(f"<b>{config['SITE_NAME']}</b>", title_style)],
                ['', Paragraph("Snow Spoiled Gifts", normal_style)],
                ['', Paragraph("Email: info@snowspoiledgifts.co.za", normal_style)],
            ]

            header_table = Table(header_data, colWidths=[30*mm, 140*mm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('SPAN', (0, 0), (0, 2)),  # Span logo across rows
            ]))
        else:
            # Fallback without logo
            header_data = [
                [Paragraph(f"<b>{config['SITE_NAME']}</b>", title_style)],
                [Paragraph("Snow Spoiled Gifts", normal_style)],
                [Paragraph("Email: info@snowspoiledgifts.co.za", normal_style)],
            ]

            header_table = Table(header_data, colWidths=[170*mm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

        elements.append(header_table)
        elements.append(Spacer(1, 10*mm))

        # Invoice title and number
        invoice_title_data = [
            [Paragraph("<b>INVOICE</b>", title_style)],
            [Paragraph(f"Invoice #: {invoice_number}", heading_style)],
            [Paragraph(f"Order #: {order['order_number']}", normal_style)],
            [Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", normal_style)],
        ]

        invoice_title_table = Table(invoice_title_data, colWidths=[170*mm])
        invoice_title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2563eb')),
        ]))

        elements.append(invoice_title_table)
        elements.append(Spacer(1, 10*mm))

        # Customer information
        bill_to_data = [
            [Paragraph("<b>Bill To:</b>", heading_style), ""],
            [Paragraph(f"<b>{customer['name']}</b>", normal_style), ""],
            [Paragraph(customer['email'], normal_style), ""],
        ]

        if customer.get('phone'):
            bill_to_data.append([Paragraph(customer['phone'], normal_style), ""])

        # Add shipping address if not pickup
        if order.get('shipping_method') != 'pickup' and order.get('shipping_address'):
            bill_to_data.append([Paragraph("<b>Ship To:</b>", heading_style), ""])
            bill_to_data.append([Paragraph(order['shipping_address'], normal_style), ""])
            if order.get('shipping_city'):
                address_line = f"{order['shipping_city']}, {order.get('shipping_state', '')}"
                bill_to_data.append([Paragraph(address_line, normal_style), ""])
            if order.get('shipping_postal_code'):
                bill_to_data.append([Paragraph(order['shipping_postal_code'], normal_style), ""])

        bill_to_table = Table(bill_to_data, colWidths=[85*mm, 85*mm])
        bill_to_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(bill_to_table)
        elements.append(Spacer(1, 10*mm))

        # Order items table
        items_data = [
            [
                Paragraph("<b>Item</b>", heading_style),
                Paragraph("<b>Qty</b>", heading_style),
                Paragraph("<b>Price</b>", heading_style),
                Paragraph("<b>Total</b>", heading_style)
            ]
        ]

        for item in order_items:
            items_data.append([
                Paragraph(item['name'], normal_style),
                Paragraph(str(item['quantity']), normal_style),
                Paragraph(f"R{item['price']:.2f}", normal_style),
                Paragraph(f"R{(item['price'] * item['quantity']):.2f}", normal_style)
            ])

        items_table = Table(items_data, colWidths=[90*mm, 25*mm, 30*mm, 25*mm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 5*mm))

        # Totals section
        totals_data = [
            ["", "", Paragraph("<b>Subtotal:</b>", normal_style), Paragraph(f"R{order['subtotal']:.2f}", normal_style)],
        ]

        if order.get('shipping_cost', 0) > 0:
            shipping_label = "Shipping"
            if order.get('shipping_method') == 'pudo':
                pudo_map = {
                    'locker_to_locker': 'PUDO L2L',
                    'locker_to_kiosk': 'PUDO L2K',
                    'locker_to_door': 'PUDO L2D',
                    'kiosk_to_door': 'PUDO K2D'
                }
                shipping_label = pudo_map.get(order.get('pudo_option'), 'Shipping')

            totals_data.append([
                "", "",
                Paragraph(f"<b>{shipping_label}:</b>", normal_style),
                Paragraph(f"R{order['shipping_cost']:.2f}", normal_style)
            ])

        totals_data.append([
            "", "",
            Paragraph("<b>TOTAL:</b>", heading_style),
            Paragraph(f"<b>R{order['total_amount']:.2f}</b>", heading_style)
        ])

        totals_table = Table(totals_data, colWidths=[90*mm, 25*mm, 30*mm, 25*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (2, -1), (-1, -1), 1.5, colors.HexColor('#2563eb')),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 10*mm))

        # Payment information
        payment_method = order.get('payment_method', 'EFT / Bank Transfer')
        payment_status = order.get('status', 'pending')

        # Map order status to payment status display
        payment_status_display = {
            'pending': 'Pending',
            'confirmed': 'Awaiting Payment',
            'awaiting_payment': 'Awaiting Payment',
            'paid': 'Paid',
            'processing': 'Paid',
            'shipped': 'Paid',
            'delivered': 'Paid',
            'cancelled': 'Cancelled'
        }.get(payment_status, 'Pending')

        payment_info = [
            [Paragraph("<b>Payment Information:</b>", heading_style)],
            [Paragraph(f"Payment Method: {payment_method}", normal_style)],
            [Paragraph(f"Payment Status: {payment_status_display}", normal_style)],
        ]

        if order.get('payment_reference'):
            payment_info.append([Paragraph(f"Reference: {order['payment_reference']}", normal_style)])

        payment_table = Table(payment_info, colWidths=[170*mm])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f3f4f6')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(payment_table)
        elements.append(Spacer(1, 15*mm))

        # Footer
        footer_text = f"""
        <para align=center>
        <b>Thank you for your business!</b><br/>
        For any questions about this invoice, please contact us at info@snowspoiledgifts.co.za<br/>
        <br/>
        <i>{config['SITE_NAME']} - {config['TAGLINE']}</i>
        </para>
        """

        elements.append(Paragraph(footer_text, normal_style))

        # Build PDF
        doc.build(elements)

        return True, output_path

    except Exception as e:
        error_msg = f"Failed to generate invoice PDF: {str(e)}"
        print(error_msg)
        return False, error_msg


def get_invoice_path(invoice_number):
    """Get the file path for an invoice PDF"""
    return os.path.join('static', 'invoices', f"{invoice_number}.pdf")


def invoice_exists(invoice_number):
    """Check if an invoice PDF already exists"""
    return os.path.exists(get_invoice_path(invoice_number))
