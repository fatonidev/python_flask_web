from app import app, mysql, is_logged_in
from flask import render_template, request, redirect, url_for, session, flash, make_response
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from datetime import datetime
from models.datasets import Dataset
from models.rules import Rules
from werkzeug.security import generate_password_hash, check_password_hash
from efficient_apriori import apriori, generate_rules_apriori
from mlxtend.frequent_patterns import association_rules
from var_dump import var_dump
import math

@app.route('/apriory_process')
@is_logged_in()
def index_apriory():    
    # get form data
    start_date = ''
    end_date = ''
    min_support = ''
    min_confidence = ''

    # return apriory with index.html
    return render_template('apriory/index.html', start_date=start_date, end_date=end_date, min_support=min_support, min_confidence=min_confidence)

@app.route('/apriory_process', methods=['POST'])
@is_logged_in()
def apriory_process():
    # delete all
    Rules.delete_all(mysql)

    # get form data
    start_date = request.form['start_date']
    end_date = request.form['end_date']    
    min_support = request.form['min_support']
    min_confidence = request.form['min_confidence']

    # change str to integer
    min_support = float(min_support)/100
    min_confidence = float(min_confidence)/100

    # get dataset by date range
    dataset = Dataset.get_by_date_range(mysql, start_date, end_date)

    #  process apriory
    records = []
    for i in range(0, len(dataset)):
        dataset[i]['items'] = dataset[i]['items'].replace(" ", "")
        records.append(dataset[i]['items'].split(','))

    # get unique items
    transactions = []
    for i in range(0, len(records)):
        # get unique value , if not exist in transactions then append
        for j in range(0, len(records[i])):
            if records[i][j] not in transactions:
                transactions.append(records[i][j])

    data = []                    
    itemsets, rules = apriori(records, min_support=float(min_support), min_confidence=float(min_confidence), verbosity = 1)    
    rules_rhs = filter(lambda rule: len(rule.lhs) == 1 , rules)    

    for rule in sorted(rules_rhs, key=lambda rule: rule.lift):        
        left = ', '.join(rule.lhs)
        right = ', '.join(rule.rhs)

        # insert rules
        Rules.store(mysql, left, right, rule.support, rule.confidence, rule.lift)

        data.append({
            'antecedent': left,
            'consequent': right,
            'support': round(rule.support * 100, 2),
            'confidence': round(rule.confidence * 100, 2),
            'lift': round(rule.lift, 2),            
        })   

    item_data = []
    for item in itemsets:
        item_list = []        
        for i in itemsets[item]:            
            string_rule = ''
            for x in i:
                if string_rule == '':
                    string_rule = x
                else:
                    string_rule = string_rule + '->' + x

            item_list.append({                
                'item': string_rule,                
                'count': itemsets[item][i],
                'support':  round(itemsets[item][i]/len(records) * 100,2),                
            })        

        item_data.append({
            'length': item,
            'items': item_list
        })

    data.sort(key=lambda x: x['confidence'], reverse=True)             

    return render_template('apriory/index.html', datasets=dataset, association_results=data, itemsets=item_data, start_date=start_date, end_date=end_date, min_support=min_support, min_confidence=min_confidence)

@app.route('/apriory_rules')
@is_logged_in()
def apriory_rules():
    # get all rules
    rules = Rules.get_all(mysql)

    rule = []
    for i in rules:
        left = i['left_data']
        right = i['right_data'].replace(" ", "").replace(",", " dan ")
        text = "Jika pembeli membeli " + left + " maka pembeli juga membeli " + right
        rule.append({
            'text': text,
            'support': round(float(i['support']) * 100,2),
            'confidence': round(float(i['confidence']) * 100,2),
            'lift': round(float(i['lift']) * 100,2),
        })

    return render_template('apriory/rules.html', rules=rule)

@app.route('/export_apriori_pdf')
@is_logged_in()
def export_apriori_pdf():
    # get all rules
    rules = Rules.get_all(mysql)

    rule = []
    for i in rules:
        left = i['left_data']
        right = i['right_data'].replace(" ", "").replace(",", " dan ")
        text = "Jika pembeli membeli " + left + " maka pembeli juga membeli " + right
        rule.append({
            'text': text,
            'support': round(float(i['support']) * 100,2),
            'confidence': round(float(i['confidence']) * 100,2),
            'lift': round(float(i['lift']) * 100,2),
        })

    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create PDF document with better margins
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        textColor=colors.HexColor('#696cff'),
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        textColor=colors.black,
        alignment=1  # Center alignment
    )
    
    # Build PDF content
    story = []
    
    # Add company header
    company_title = Paragraph("CV GUNUNG BAJA UTAMA", title_style)
    story.append(company_title)
    
    # Add report title
    report_title = Paragraph("LAPORAN ANALISIS APRIORI", subtitle_style)
    story.append(report_title)
    
    # Add generation date
    current_date = datetime.now().strftime("%d %B %Y")
    date_text = Paragraph(f"Tanggal: {current_date}", subtitle_style)
    story.append(date_text)
    story.append(Spacer(1, 20))
    
    # Prepare table data with better formatting
    data = [['No', 'Aturan Asosiasi', 'Support (%)', 'Confidence (%)', 'Lift']]
    
    for i, item in enumerate(rule, 1):
        # Break long text into multiple lines if needed
        rule_text = item['text']
        if len(rule_text) > 80:
            # Split long text at logical points
            words = rule_text.split(' ')
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 80:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            rule_text = '\n'.join(lines)
        
        data.append([
            str(i), 
            rule_text,
            f"{item['support']:.2f}",
            f"{item['confidence']:.2f}",
            f"{item['lift']:.2f}"
        ])
    
    # Create table with adjusted column widths
    table = Table(data, colWidths=[0.3*inch, 5.0*inch, 0.7*inch, 0.7*inch, 0.7*inch])
    
    # Enhanced table styling with better formatting
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#696cff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align No column
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Left align Aturan column
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),  # Right align numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        
        # Data rows styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        
        # Alternating row colors with softer contrast
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        
        # Add subtle row borders
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.grey),
        
        # Ensure consistent spacing for wrapped text
        ('LEADING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(table)
    
    # Add footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    footer_text = Paragraph("Laporan ini dibuat secara otomatis oleh sistem analisis Apriori", footer_style)
    story.append(footer_text)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=laporan_apriori.pdf'

    return response
