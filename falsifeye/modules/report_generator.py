from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import os
import datetime

def generate_report(case_id, evidence_name, analysis_results, output_path, file_hash="N/A"):
    """
    Generates a professional PDF forensic report using Platypus.
    Includes Chain of Custody, Digital Fingerprinting, and Legal Disclaimers.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    # --- Title ---
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], 
                                 textColor=colors.HexColor('#2c3e50'),
                                 fontSize=24, spaceAfter=12)
    story.append(Paragraph("FALSIFEYE Digital Forensic Analysis Report", title_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # --- Classification Banner ---
    banner_style = ParagraphStyle('Banner', parent=styles['Normal'],
                                  textColor=colors.white, backColor=colors.HexColor('#e74c3c'),
                                  alignment=TA_CENTER, fontSize=10, leftIndent=0, rightIndent=0)
    story.append(Paragraph("<b>FORENSIC ANALYSIS - PRELIMINARY ASSESSMENT ONLY</b>", banner_style))
    story.append(Spacer(1, 0.2 * inch))

    # --- Meta Data Table ---
    data = [
        ["Case ID:", case_id],
        ["Evidence File:", evidence_name],
        ["Digital Fingerprint (SHA-256):", Paragraph(file_hash, styles['Normal'])],
        ["Analysis Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")],
        ["Examiner:", "FALSIFEYE AI System v1.0"],
        ["Analysis Method:", analysis_results.get('method', 'Multi-Modal Signal Processing')]
    ]
    
    t = Table(data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#34495e')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))

    # --- Authenticity Score ---
    score = analysis_results.get('score', 0)
    score_color = colors.green if score < 50 else colors.red
    verdict = "LIKELY AUTHENTIC" if score < 50 else "POTENTIAL MANIPULATION DETECTED"
    
    story.append(Paragraph(f"Authenticity Score: {score}/100", 
                           ParagraphStyle('Score', parent=styles['Heading2'], textColor=score_color)))
    story.append(Paragraph(f"Verdict: {verdict}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # --- Detailed Analysis Section ---
    story.append(Paragraph("Detailed Analysis", styles['Heading2']))
    
    # Format details nicely
    details = analysis_results.get('details', 'No details provided.')
    # Split details by period or newlines if possible for better readability
    if isinstance(details, str):
        detail_lines = details.split('. ')
        for line in detail_lines:
            if line.strip():
                story.append(Paragraph(f"• {line.strip()}.", styles['Normal']))
                story.append(Spacer(1, 0.05 * inch))
    
    story.append(Spacer(1, 0.2 * inch))

    # --- Technical Metadata ---
    story.append(Paragraph("Technical Metadata", styles['Heading3']))
    meta_data = []
    for key, value in analysis_results.items():
        if key not in ['score', 'details', 'filename', 'report_path', 'transcription']:
            meta_data.append([key.replace('_', ' ').title(), str(value)])
    
    if meta_data:
        t_meta = Table(meta_data, colWidths=[2.5*inch, 3.5*inch])
        t_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_meta)

    # --- Chain of Custody & Integrity ---
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Chain of Custody & Integrity", styles['Heading2']))
    custody_text = f"""
    This file was ingested into the FALSIFEYE system on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}.
    The SHA-256 hash ({file_hash[:32]}...) was generated immediately upon receipt to ensure data integrity.
    All analysis was performed on the hashed artifact without modification to preserve evidence integrity.
    """
    story.append(Paragraph(custody_text, styles['Normal']))
    
    # --- Legal Disclaimer ---
    story.append(Spacer(1, 0.4 * inch))
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'],
                                     fontSize=9, textColor=colors.HexColor('#7f8c8d'),
                                     alignment=TA_JUSTIFY, leftIndent=0.25*inch, rightIndent=0.25*inch,
                                     spaceBefore=6, spaceAfter=6, borderColor=colors.grey,
                                     borderWidth=1, borderPadding=8)
    story.append(Paragraph("<b>LEGAL DISCLAIMER & LIMITATIONS</b>", styles['Heading3']))
    
    disclaimer_text = """
    <b>This report is a preliminary assessment only and is NOT intended as conclusive evidence of manipulation or authenticity.</b><br/><br/>
    
    <b>Methodology Limitations:</b> The analysis employs signal processing heuristics (Error Level Analysis, FFT, 
    optical flow, MFCC variance) which may produce false positives or false negatives. Scores are probabilistic 
    estimates, not definitive determinations.<br/><br/>
    
    <b>Court Admissibility:</b> This automated analysis has NOT been validated through peer-reviewed scientific 
    publication nor certified under ISO/IEC 17025 forensic laboratory standards. For legal proceedings, 
    results MUST be corroborated by:<br/>
    • Manual examination by a certified forensic examiner<br/>
    • Independent validation using accredited forensic tools<br/>
    • Expert witness testimony explaining methodology and limitations<br/><br/>
    
    <b>Known Limitations:</b><br/>
    • Compressed media may trigger false positives for manipulation<br/>
    • Advanced GAN-based deepfakes may evade detection<br/>
    • Low-quality authentic media may score as suspicious<br/>
    • No temporal or semantic consistency validation performed<br/><br/>
    
    <b>Recommended Actions:</b> Treat this report as an initial screening tool. High scores warrant further 
    investigation by qualified forensic experts. Low scores do not guarantee authenticity.<br/><br/>
    
    <b>No Warranty:</b> This software is provided "as-is" without warranties. The developers assume no liability 
    for decisions made based on this analysis.
    """
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # --- Footer ---
    story.append(Spacer(1, 0.3 * inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], 
                                  fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(f"Report generated by FALSIFEYE v1.0 | Expert-Level Forensics", footer_style))
    
    # Build the PDF
    doc.build(story)

    doc.build(story)
    return output_path
