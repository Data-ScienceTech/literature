"""
Convert manuscript markdown to PDF using markdown + weasyprint or reportlab
"""

import os
from pathlib import Path

def convert_md_to_pdf():
    """Convert the ISR-ready manuscript to PDF"""
    
    # Try multiple approaches
    approaches = [
        ("markdown + weasyprint", convert_with_weasyprint),
        ("markdown + pdfkit", convert_with_pdfkit),
        ("pypandoc", convert_with_pypandoc),
        ("basic HTML + weasyprint", convert_via_html),
    ]
    
    for name, func in approaches:
        try:
            print(f"Trying: {name}...")
            func()
            print(f"✓ Successfully created PDF using {name}")
            return True
        except ImportError as e:
            print(f"  → {name} not available: {e}")
            continue
        except Exception as e:
            print(f"  → {name} failed: {e}")
            continue
    
    print("\n❌ Could not create PDF with available tools.")
    print("\nPlease install one of the following:")
    print("  pip install weasyprint markdown")
    print("  pip install pdfkit")
    print("  pip install pypandoc")
    print("\nOr install pandoc from: https://pandoc.org/installing.html")
    return False

def convert_with_weasyprint():
    """Convert using markdown + weasyprint"""
    import markdown
    from weasyprint import HTML, CSS
    
    md_file = Path("manuscript_ISR_ready.md")
    pdf_file = Path("manuscript_ISR_ready.pdf")
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )
    
    # Add CSS styling
    css_style = """
    @page {
        size: letter;
        margin: 1in;
    }
    body {
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #000;
    }
    h1 {
        font-size: 18pt;
        font-weight: bold;
        margin-top: 24pt;
        margin-bottom: 12pt;
    }
    h2 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 18pt;
        margin-bottom: 10pt;
    }
    h3 {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 14pt;
        margin-bottom: 8pt;
    }
    p {
        margin-bottom: 10pt;
        text-align: justify;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 12pt 0;
    }
    th, td {
        border: 1px solid #000;
        padding: 6pt;
        text-align: left;
    }
    th {
        background-color: #f0f0f0;
        font-weight: bold;
    }
    code {
        font-family: 'Courier New', monospace;
        background-color: #f5f5f5;
        padding: 2pt 4pt;
    }
    pre {
        background-color: #f5f5f5;
        padding: 10pt;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    """
    
    # Wrap in full HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Mapping the Information Systems Literature</title>
        <style>{css_style}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert to PDF
    HTML(string=full_html).write_pdf(pdf_file)
    print(f"  → Created: {pdf_file}")

def convert_with_pdfkit():
    """Convert using pdfkit (requires wkhtmltopdf)"""
    import markdown
    import pdfkit
    
    md_file = Path("manuscript_ISR_ready.md")
    pdf_file = Path("manuscript_ISR_ready.pdf")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['extra', 'tables'])
    
    # Convert to PDF
    pdfkit.from_string(html_content, str(pdf_file))
    print(f"  → Created: {pdf_file}")

def convert_with_pypandoc():
    """Convert using pypandoc"""
    import pypandoc
    
    md_file = "manuscript_ISR_ready.md"
    pdf_file = "manuscript_ISR_ready.pdf"
    
    pypandoc.convert_file(
        md_file,
        'pdf',
        outputfile=pdf_file,
        extra_args=['--pdf-engine=xelatex']
    )
    print(f"  → Created: {pdf_file}")

def convert_via_html():
    """Simple conversion via HTML intermediate"""
    import markdown
    from weasyprint import HTML
    
    md_file = Path("manuscript_ISR_ready.md")
    pdf_file = Path("manuscript_ISR_ready.pdf")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html = markdown.markdown(md_content)
    HTML(string=html).write_pdf(pdf_file)
    print(f"  → Created: {pdf_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("Converting manuscript_ISR_ready.md to PDF")
    print("=" * 60)
    convert_md_to_pdf()
