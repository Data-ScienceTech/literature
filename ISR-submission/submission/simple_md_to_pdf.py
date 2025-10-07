"""
Simple markdown to PDF converter using reportlab
"""

from pathlib import Path
import re

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

def clean_markdown(text):
    """Remove markdown formatting for plain PDF"""
    # Remove image links
    text = re.sub(r'!\[.*?\]\(.*?\)', '[Figure]', text)
    # Remove regular links but keep text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove bold/italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove code blocks
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def convert_with_reportlab():
    """Convert using reportlab - basic but works without external dependencies"""
    
    if not HAS_REPORTLAB:
        raise ImportError("reportlab not available")
    
    md_file = Path("manuscript_ISR_ready.md")
    pdf_file = Path("manuscript_ISR_ready.pdf")
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=11, leading=14))
    styles.add(ParagraphStyle(name='DocTitle', fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='H1', fontSize=14, leading=18, spaceAfter=10, spaceBefore=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='H2', fontSize=12, leading=16, spaceAfter=8, spaceBefore=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='H3', fontSize=11, leading=14, spaceAfter=6, spaceBefore=8, fontName='Helvetica-Bold'))
    
    # Parse content line by line
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            elements.append(Spacer(1, 6))
            i += 1
            continue
        
        # Title (first H1)
        if line.startswith('# ') and len(elements) == 0:
            text = clean_markdown(line[2:])
            elements.append(Paragraph(text, styles['DocTitle']))
            elements.append(Spacer(1, 12))
        
        # H2
        elif line.startswith('## '):
            text = clean_markdown(line[3:])
            elements.append(Paragraph(text, styles['H1']))
        
        # H3
        elif line.startswith('### '):
            text = clean_markdown(line[4:])
            elements.append(Paragraph(text, styles['H2']))
        
        # H4
        elif line.startswith('#### '):
            text = clean_markdown(line[5:])
            elements.append(Paragraph(text, styles['H3']))
        
        # Horizontal rule - page break
        elif line.startswith('---'):
            elements.append(PageBreak())
        
        # Code blocks (skip for now)
        elif line.startswith('```'):
            # Skip until closing ```
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
        
        # Lists
        elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
            text = clean_markdown(line)
            elements.append(Paragraph(text, styles['Normal']))
        
        # Tables (skip header separator)
        elif line.startswith('|') and '---' not in line:
            # Simple table handling - just treat as text
            text = clean_markdown(line)
            elements.append(Paragraph(text, styles['Normal']))
        
        # Regular paragraph
        else:
            text = clean_markdown(line)
            if text:
                elements.append(Paragraph(text, styles['Justify']))
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    print(f"✓ PDF created successfully: {pdf_file}")
    return True

def main():
    print("=" * 60)
    print("Converting manuscript_ISR_ready.md to PDF (Simple Mode)")
    print("=" * 60)
    
    if not HAS_REPORTLAB:
        print("Installing reportlab...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'reportlab'])
        print("Please run this script again.")
        return
    
    try:
        convert_with_reportlab()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
