# core/pdf_generator.py
import json
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

class SecurityReportPDF(FPDF):
    def header(self):
        # Set font
        self.set_font('Helvetica', 'B', 15)
        # Title
        self.cell(0, 10, 'Smart Contract Security Analysis Report', 0, 1, 'C')
        # Subtitle
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font
        self.set_font('Helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_full_pdf_report(reports_dir: str = "reports", output_filename: str = "Security_Vulnerability_Summary.pdf"):
    """
    Aggregates all JSON reports into a single consolidated PDF report.
    """
    pdf = SecurityReportPDF()
    # Explicitly set margins (15mm left, top, right) to match eff_width of 180mm
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Effective width for multi_cell (A4 is 210mm wide, margin is 15mm each side)
    # Correct calculation: 210 - 15 - 15 = 180
    eff_width = 180 

    report_path = Path(reports_dir)
    if not report_path.exists():
        print(f"[ERROR] Reports directory '{reports_dir}' not found.")
        return

    json_files = list(report_path.glob("*.json"))
    if not json_files:
        print("[ERROR] No JSON reports found to aggregate.")
        return

    # Section 1: Executive Summary
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(eff_width, 10, '1. Executive Summary', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    total_contracts = len(json_files)
    total_issues = 0
    vulnerable_contracts = 0
    
    reports_data = []
    for jf in json_files:
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports_data.append(data)
                total_issues += data.get('total_issues', 0)
                if data.get('total_issues', 0) > 0:
                    vulnerable_contracts += 1
        except:
            continue

    summary_text = (f"This report provides a consolidated view of the static analysis performed on {total_contracts} smart contracts. "
                   f"In total, {total_issues} potential vulnerabilities were identified across {vulnerable_contracts} contracts.")
    pdf.multi_cell(eff_width, 8, summary_text)
    pdf.ln(10)

    # Section 2: Summary Table
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(eff_width, 10, '2. Findings Overview', 0, 1)
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(80, 10, 'Contract Name', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Total Issues', 1, 0, 'C', 1)
    pdf.cell(60, 10, 'Status', 1, 1, 'C', 1)

    # Table Body
    pdf.set_font('Helvetica', '', 10)
    for data in sorted(reports_data, key=lambda x: x.get('contract', '')):
        count = data.get('total_issues', 0)
        status = "VULNERABLE" if count > 0 else "SECURE"
        
        contract_name = data.get('contract', 'Unknown')
        if len(contract_name) > 40:
            contract_name = contract_name[:37] + "..."
            
        pdf.cell(80, 10, contract_name, 1)
        pdf.cell(40, 10, str(count), 1, 0, 'C')
        
        if status == "VULNERABLE":
            pdf.set_text_color(200, 0, 0)
        else:
            pdf.set_text_color(0, 150, 0)
            
        pdf.cell(60, 10, status, 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    pdf.ln(15)

    # Section 3: Detailed Findings
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(eff_width, 10, '3. Detailed Vulnerability Analyses', 0, 1)
    pdf.ln(5)

    vulnerable_reports = [r for r in reports_data if r.get('total_issues', 0) > 0]
    
    if not vulnerable_reports:
        pdf.set_font('Helvetica', 'I', 11)
        pdf.cell(eff_width, 10, 'No vulnerabilities were found in any analyzed contracts.', 0, 1)
    else:
        for data in vulnerable_reports:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_fill_color(255, 240, 240)
            pdf.cell(eff_width, 10, f"Contract: {data.get('contract', 'Unknown')}", 0, 1, 'L', 1)
            pdf.ln(2)
            
            for issue in data.get('issues', []):
                # Clean text to avoid encoding issues with core fonts
                vuln = str(issue.get('vulnerability', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                func = str(issue.get('function', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                expl = str(issue.get('explanation', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                fix = str(issue.get('suggested_fix', 'N/A')).encode('latin-1', 'replace').decode('latin-1')

                # Issue Heading
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(180, 50, 50)
                pdf.cell(eff_width, 8, f"Issue: {vuln} (Severity: {issue.get('severity', 'N/A')})", 0, 1)
                
                # Function Info
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Helvetica', 'I', 10)
                pdf.cell(eff_width, 6, f"Function: {func} | Line: {issue.get('line', 'N/A')}", 0, 1)
                
                # Explanation (Label + Text)
                pdf.set_font('Helvetica', 'B', 10)
                pdf.cell(eff_width, 6, "Explanation:", 0, 1, 'L')
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(eff_width, 6, expl.strip(), align='L')
                
                # Suggested Fix (Label + Text)
                pdf.set_font('Helvetica', 'B', 10)
                pdf.cell(eff_width, 6, "Suggested Fix:", 0, 1, 'L')
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(eff_width, 6, fix.strip(), align='L')
                pdf.ln(5)
            
            pdf.ln(5)

    # Save PDF
    try:
        pdf.output(output_filename)
        print(f"[SUCCESS] Consolidated PDF report generated: {output_filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save PDF: {e}")

if __name__ == "__main__":
    generate_full_pdf_report()
