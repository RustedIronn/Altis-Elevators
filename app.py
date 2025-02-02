from flask import Flask, request, send_file,render_template, send_from_directory, session
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from flask_cors import CORS
from reportlab.lib.pagesizes import A4, letter
import io
import random
import string

app = Flask(__name__)
CORS(app)

# Function to generate a random secret key
def generate_secret_key(length=24):
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

# Set a random secret key each time the app runs
app.secret_key = generate_secret_key()

@app.route('/')
def homepage():
    # Check if form data is in session to pre-fill
    name = session.get('name', '')
    date = session.get('date', '')
    return render_template('index.html', name=name, date=date)  # Adjust HTML to pre-fill fields

def add_image_watermark(pdf, image_path, width, height):
    """
    Adds an image watermark to the PDF, scaling it down and placing it at the center.
    """
    pdf.saveState()
    # Set transparency (alpha)
    pdf.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
    # Scale and position the image (centered and rotated)
    img_width, img_height = 200, 200  # Adjust size of the watermark image
    pdf.drawImage(image_path, width / 2 - img_width / 2, height / 2 - img_height / 2, img_width, img_height, mask='auto')
    pdf.restoreState()

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # Get form data
    name = request.form.get('name')
    date = request.form.get('date')
    customer_id = request.form.get('id')
    reference = request.form.get('reference')
    place = request.form.get('place')
    sub_type = request.form.get('subType')
    lift_type = request.form.get('liftType')
    capacity = request.form.get('capacity')
    price = request.form.get('price')
    price_text = request.form.get('priceText')
    cabin_opening = request.form.get('cabinOpening')
    type_design = request.form.get('typeDesign')
    shaft = request.form.get('shaft')
    car_size = request.form.get('carSize')
    features = request.form.get('features')

    # Validate required fields
    if not name or not date or not customer_id:
        return "Error: Missing required fields (name, date, or customer ID).", 400

    # Create a new PDF
    packet = io.BytesIO()
    pdf = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    image_path = "D:\Employee PDF Generation Backend\logo.png"  # Update this path
    add_image_watermark(pdf, image_path, width, height)

    # Page 1 - Standard content
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, height - 50, "COMPANY")
    pdf.drawString(width - 150, height - 50, "ISO 9001: 2015 CERTIFIED")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 80, f"Ref: AE/QUO/{reference}/2022-23")
    pdf.drawString(50, height - 95, "Besides Lanco Quarters,")
    pdf.drawString(50, height - 110, "Gollapudi,")
    pdf.drawString(50, height - 125, "Vijayawada.")
    pdf.drawString(width - 150, height - 80, f"Date: {date}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(width / 2, height - 160, f"Kind Attention: {name}")

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, height - 200, f"Sub: Quotation for supply of Lift, {place}")

    # Body Text
    body_text = (
        "Dear Sir,\n\n"
        "As discussed with you, we trust our offer will receive your favorable consideration and acceptance. \n"
        "In this connection, we wish to inform you that the lift we have offered is completely of indigenous make.\n\n"
        "We have trained and experienced personnel capable of giving satisfactory after sales service. \n"
        "Further, we keep a reasonable good stock of spare parts, which will be of considerable assistance to us in rendering \n"
        "prompt service to our lifts when required.\n"
        "We are mentioning all these facts as we are sure you will appreciate the importance of prompt after-sales-services, \n"
        "which can cause considerable annoyance to the owner's and users if efficient service is not readily available.\n\n"
        "We trust you will find our offer quite competitive and in case, you require any further clarification, \n"
        "please do communicate with us.\n\n"
        "We assure you of fulfillment of best service."
    )

    pdf.setFont("Helvetica", 10)
    text_object = pdf.beginText(50, height - 240)
    text_object.setLeading(14)
    text_object.textLines(body_text)
    pdf.drawText(text_object)

    # Footer
    footer_start = height - 480
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, footer_start, "Thanking You,")
    pdf.drawString(50, footer_start - 20, "Yours Faithfully,")
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, footer_start - 40, "For ALTIS ELEVATORS")
    pdf.drawString(50, footer_start - 60, "Authorized Signatory")

    # Add a new page for form data
    pdf.showPage()

    add_image_watermark(pdf, image_path, width, height)

    # Page 2 - Form Data Table
    # Draw the text
    pdf.setFont("Helvetica-Bold", 12)
    text_x = width / 2
    text_y = height - 50
    pdf.drawCentredString(text_x, text_y, "NEW ELEVATOR INSTALLATION")

    # Draw the underline
    text_width = pdf.stringWidth("NEW ELEVATOR INSTALLATION", "Helvetica-Bold", 12)
    pdf.line(text_x - text_width / 2, text_y - 2, text_x + text_width / 2, text_y - 2)


    # Define table data
    data = [
        ["Field", "Value"],
        ["Customer ID", customer_id],
        ["Name", name],
        ["Date", date],
        ["Reference", reference],
        ["Place", place],
        ["SUB Type", sub_type],
        ["Lift Type", lift_type],
        ["Capacity", f"{capacity} Kgs"],
        ["Price", price],
        ["Price in Words", price_text],
        ["Cabin Opening", f"{cabin_opening} mm"],
        ["Design", type_design],
        ["Shaft Dimensions", shaft],
        ["Car Size", car_size],
        ["Additional Features", features],
    ]

    # Create a table
    table = Table(data, colWidths=[200, 250])  # Adjust column widths as needed

    # Apply table style
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Body font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [None, None]),  # No background color for rows
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
    ]))



    table_width, table_height = table.wrap(0, 0)
    x_position = (width - table_width) / 2  # Center horizontally
    y_position = height - table_height - 200  # Center vertically with some margin from the top

    table.drawOn(pdf, x_position, y_position)

    # Save PDF
    pdf.save()

    # Move the packet pointer to the beginning
    packet.seek(0)

    # Send the PDF as a response to the client
    return send_file(packet, as_attachment=True, download_name="quotation_with_form_data.pdf", mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)
