from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageTemplate, SimpleDocTemplate, BaseDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import csv
from Scripts import utils as u

import sys
from reportlab.platypus import Image

def add_page_number(canvas, doc):
    """
    Ajoute un numéro de page en bas de chaque page.
    """
    footer_text = "RAID ESSEC EY 2025 - Classement réalisé par Raid CENTRALESUPELEC"
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.darkgray)
    canvas.drawString(30, 15, footer_text)  # Position (x=30, y=15) en bas à gauche
    page_num = canvas.getPageNumber()
    canvas.drawString(500, 15, f"Page {page_num}")  # Position (x=500, y=15) en bas à droite

def create_pdf(mixite="scratch", ent=0, journee="Weekend"):
    # Create the PDF document
    filename = f'./Resultats finaux/PDF/{journee}/{mixite}/{"Evasion" if ent==1 else "Challenge"}/classement_{mixite}_{"Evasion" if ent==1 else "Challenge"}_{journee}.pdf'
    doc = SimpleDocTemplate(filename, pagesize=letter)

    # doc.addPageTemplates([PageTemplate(onPage=add_page_number)])


    # store if teams are on saturday, sunday or both
    teams = {}
    with open('./Essec_J1/race_results.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter='@')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            data = row[0].split(";")
            teams[data[3]] = [data[3], 'J1']
    
    with open('./Essec_J2/race_results.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter='@')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            data = row[0].split(";")
            if data[3] in teams.keys():
                teams[data[3]][1] = 'Weekend'
            else:
                teams[data[3]] = [data[3], 'J2']

    # print(teams.keys())

    teams['Victoria et Constant'][1] = 'Weekend'
    teams['Pitchou'][1] = 'Weekend'
    teams['Eli & Elvire'][1] = 'Weekend'
    teams['Les Deux Meuh Raids'][1] = 'Weekend'
    teams['Les MarLéaventurières'][1] = 'Weekend'
    teams['Les Troufions'][1] = 'Weekend'
    teams["les Am... d'Orion"][1] = 'Weekend'
    teams["R'édi"][1] = 'Weekend'
    teams['Citron - Sucre'][1] = 'Weekend'
    teams['Sucre - Citron'][1] = 'Weekend'
    teams['La villa'][1] = 'Weekend'
    teams['DSA'][1] = 'Weekend'
    teams['EY1'][1] = 'Weekend'
    

    # Create a list to store the elements
    elements = []

    styles = getSampleStyleSheet()

    # Add logos
    logo1 = Image('./images/Logo noir HD.png', width=100, height=100)
    logo1.hAlign = 'LEFT'
    logo2 = Image('./images/Logo EY.png', width=100, height=100)
    logo2.hAlign = 'RIGHT'
    
    # Create a table to hold the logos side by side
    logo_table = Table([[logo1, logo2]], colWidths=['50%', '50%'])
    logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                  ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elements.append(logo_table)

    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # Add title
    title = Paragraph("Classement Raid ESSEC EY 2025", styles['Title'])
    elements.append(title)
    mixite_text = "Hommes" if mixite == "H" else "Femmes" if mixite == "F" else "Mixte"
    cate_text = "Evasion" if ent == 1 else "Challenge"
    journee_text = "Samedi" if journee == "J1" else "Dimanche" if journee == "J2" else "Weekend"
    if mixite == "scratch":
        subtitle = Paragraph(f"Classement scratch - {journee_text}", styles['Heading2'])
    else:
        subtitle = Paragraph(f"Course {mixite_text} - {cate_text} - {journee_text}", styles['Heading2'])
    subtitle.style.alignment = 1  # 1 is for center alignment
    elements.append(subtitle)
    
    # Sample data for the table
    data = [['Classement', 'Equipe', 'Temps']]

    team_in_list = []
    teams_full_results = {}

    header_teams = []
    
    # Read data from CSV file
    results_path = './Essec_J1/race_results.csv' if journee == "J1" else './Essec_J2/race_results.csv' if journee == "J2" else './fusion_results.csv'
    with open(results_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header_teams = next(csv_reader)[0].split(';')  # Skip header row
        for row in csv_reader:
            row = row[0].split(";")
            teams_full_results[row[3]] = row
            if teams[row[3]][1] == journee:
                if (row[1] == mixite and int(row[2]) == ent) or mixite == "scratch":
                    data.append([0, row[3], u.heure_from_sec(int(row[4]))])
                    team_in_list.append([row[0], row[3]])
        # Sort data based on the time (last column)
        data[1:] = sorted(data[1:], key=lambda x: x[2])

        # Update rankings
        for i in range(1, len(data)):
            data[i][0] = "#" + str(i)  # Add ranking number
    
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
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    # Création des fiches de chaque équipe
    for team in team_in_list:
        team_filename = f'./Resultats finaux/PDF/teams/equipe_{team[0]}.pdf'
        team_doc = SimpleDocTemplate(team_filename, pagesize=letter)
        team_elements = []

        # Add logos
        logo1 = Image('./images/Logo noir HD.png', width=100, height=100)
        logo1.hAlign = 'LEFT'
        logo2 = Image('./images/Logo EY.png', width=100, height=100)
        logo2.hAlign = 'RIGHT'
        
        # Create a table to hold the logos side by side
        logo_table = Table([[logo1, logo2]], colWidths=['50%', '50%'])
        logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        team_elements.append(logo_table)

        team_elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Add title
        team_title = Paragraph(f"Équipe n°{team[0]}", styles['Title'])
        team_elements.append(team_title)
        
        team_name = Paragraph(f"Nom de l'équipe: {team[1]}", styles['Heading2'])
        team_elements.append(team_name)
        
        # Add team data in table format
        team_data = [[header_teams[i], u.heure_from_sec(teams_full_results[team[1]][i])] for i in range(4, len(header_teams))]
        
        team_table = Table(team_data)
        team_table = Table(team_data, colWidths=['40%', '40%'])  # Set column widths to 50% each
        team_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        team_elements.append(team_table)
        
        team_doc.build(team_elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_pdf(mixite=sys.argv[1], ent=int(sys.argv[2]), journee=sys.argv[3])
    else:
        print("Usage: python pdfmaker.py <mixite> <ent>")