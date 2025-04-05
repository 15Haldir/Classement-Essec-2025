from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import csv
from Scripts import utils as u

import sys
from reportlab.platypus import Image

def create_pdf(mixite="H", ent=0):
    # Create the PDF document
    filename = f'classement_{mixite}_{"Evasion" if ent==1 else "Challenge"}.pdf'
    doc = SimpleDocTemplate(filename, pagesize=letter)

    # store if teams are on saturday, sunday or both
    teams = {}
    with open('./Essec_J1/equipe.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter='@')
        for row in csv_reader:
            data = row[0].split(";")
            teams[data[0]] = [data[1], 'Samedi']
    
    with open('./Essec_J2/equipe.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter='@')
        for row in csv_reader:
            data = row[0].split(";")
            if data[0] in teams.keys()
                teams[data[0]][1] = 'Weekend'
            else:
                teams[data[0]] = [data[1], 'Dimanche']
    

    # Create a list to store the elements
    elements = []

    # Add logo
    logo = Image('./images/Logo noir HD.png', width=100, height=100)
    logo.hAlign = 'LEFT'
    elements.append(logo)
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Classement Samedi Raid ESSEC", styles['Title'])
    elements.append(title)
    mixite_text = "Hommes" if mixite == "H" else "Femmes" if mixite == "F" else "Mixte"
    cate_text = "Evasion" if ent == 1 else "Challenge"
    subtitle = Paragraph(f"Course {mixite_text} - {cate_text}", styles['Heading2'])
    subtitle.style.alignment = 1  # 1 is for center alignment
    elements.append(subtitle)
    
    # Sample data for the table
    data = [['Classement', 'Equipe', 'Temps']]
    
    # Read data from CSV file
    results_path = './Essec_J1/race_results.csv' if sys.argv[3] == "J1" else './Essec_J2/race_results.csv' if sys.argv[3] == "J2" else 'fusion_results.csv'
    with open(results_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            print(row[0].split(";"))
            row = row[0].split(";")
            if row[1] == mixite and int(row[2]) == ent:
                data.append([0, row[3], u.heure_from_sec(int(row[4]))])
        # Sort data based on the time (last column)
        data[1:] = sorted(data[1:], key=lambda x: x[2])
        # Update rankings
        for i in range(1, len(data)):
            data[i][0] = i
    
    # Create the table
    table = Table(data)
    table = Table(data, colWidths=['25%', '45%', '30%'])  # Specify relative widths
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_pdf(mixite=sys.argv[1], ent=int(sys.argv[2]))
    else:
        print("Usage: python pdfmaker.py <mixite> <ent>")