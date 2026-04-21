# core/pdf_generator.py
import json
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos


class SecurityReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Smart Contract Security Analysis Report', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')


def _cell(pdf, w, h, txt, border=0, align='L', fill=False):
    """Helper: cell that always moves to next line (new_x=LMARGIN, new_y=NEXT)."""
    pdf.cell(w, h, txt, border, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=align, fill=fill)


def _cell_inline(pdf, w, h, txt, border=0, align='L', fill=False):
    """Helper: cell that stays on the same line (new_x=RIGHT, new_y=TOP)."""
    pdf.cell(w, h, txt, border, new_x=XPos.RIGHT, new_y=YPos.TOP, align=align, fill=fill)


def generate_full_pdf_report(reports_dir: str = "reports", output_filename: str = "Security_Vulnerability_Summary.pdf"):
    """
    Aggregates all JSON reports into a single consolidated PDF report.
    Differentiates between Static (Slither) and AI/ML findings.
    """
    pdf = SecurityReportPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # A4 = 210mm wide; margins 15mm each side → 180mm effective width
    eff_width = 180

    report_path = Path(reports_dir)
    if not report_path.exists():
        print(f"[ERROR] Reports directory '{reports_dir}' not found.")
        return

    json_files = list(report_path.glob("*.json"))
    if not json_files:
        print("[ERROR] No JSON reports found to aggregate.")
        return

    # ── Section 1: Executive Summary ──────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    _cell(pdf, eff_width, 10, '1. Executive Summary')
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
        except Exception:
            continue

    summary_text = (
        f"This report provides a consolidated view of the security analysis performed on "
        f"{total_contracts} smart contract(s). In total, {total_issues} potential vulnerabilities "
        f"were identified across {vulnerable_contracts} contract(s)."
    )
    pdf.multi_cell(eff_width, 8, summary_text)
    pdf.ln(10)

    # ── Section 2: Findings Overview Table ────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    _cell(pdf, eff_width, 10, '2. Findings Overview')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    _cell_inline(pdf, 80, 10, 'Contract Name', border=1, align='C', fill=True)
    _cell_inline(pdf, 40, 10, 'Total Issues', border=1, align='C', fill=True)
    _cell(pdf, 60, 10, 'Status', border=1, align='C', fill=True)

    pdf.set_font('Helvetica', '', 10)
    for data in sorted(reports_data, key=lambda x: x.get('contract', '')):
        count = data.get('total_issues', 0)
        status = "VULNERABLE" if count > 0 else "SECURE"

        contract_name = data.get('contract', 'Unknown')
        if len(contract_name) > 40:
            contract_name = contract_name[:37] + "..."

        _cell_inline(pdf, 80, 10, contract_name, border=1)
        _cell_inline(pdf, 40, 10, str(count), border=1, align='C')

        if status == "VULNERABLE":
            pdf.set_text_color(200, 0, 0)
        else:
            pdf.set_text_color(0, 150, 0)

        _cell(pdf, 60, 10, status, border=1, align='C')
        pdf.set_text_color(0, 0, 0)

    pdf.ln(15)

    # ── Section 3: Detailed Findings ──────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    _cell(pdf, eff_width, 10, '3. Detailed Vulnerability Analyses')
    pdf.ln(5)

    vulnerable_reports = [r for r in reports_data if r.get('total_issues', 0) > 0]

    if not vulnerable_reports:
        pdf.set_font('Helvetica', 'I', 11)
        _cell(pdf, eff_width, 10, 'No vulnerabilities were found in any analyzed contracts.')
    else:
        for data in vulnerable_reports:
            # Contract header banner
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_fill_color(220, 230, 255)
            _cell(pdf, eff_width, 10, f"Contract: {data.get('contract', 'Unknown')}", align='L', fill=True)
            pdf.ln(3)

            all_issues = data.get('issues', [])
            static_issues = [i for i in all_issues if not i.get('is_ml_finding')]
            ml_issues     = [i for i in all_issues if i.get('is_ml_finding')]

            # ── 3a. Static Analysis Findings ──────────────────────────────────
            if static_issues:
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_fill_color(240, 240, 240)
                _cell(pdf, eff_width, 8, '  Static Analysis Findings (Slither)', align='L', fill=True)
                pdf.ln(2)

                for issue in static_issues:
                    vuln = str(issue.get('vulnerability', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    func = str(issue.get('function', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    expl = str(issue.get('explanation', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    fix  = str(issue.get('suggested_fix', 'N/A')).encode('latin-1', 'replace').decode('latin-1')

                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.set_fill_color(255, 235, 235)
                    pdf.set_text_color(160, 30, 30)
                    _cell(pdf, eff_width, 7, f"  [{issue.get('severity', 'N/A').upper()}]  {vuln}", align='L', fill=True)

                    pdf.set_text_color(80, 80, 80)
                    pdf.set_font('Helvetica', 'I', 9)
                    _cell(pdf, eff_width, 5, f"  Function: {func}  |  Line: {issue.get('line', 'N/A')}")

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Helvetica', 'B', 9)
                    _cell(pdf, eff_width, 5, '  Explanation:')
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_x(pdf.l_margin + 4)
                    pdf.multi_cell(eff_width - 4, 5, expl.strip(), align='L')

                    pdf.set_font('Helvetica', 'B', 9)
                    _cell(pdf, eff_width, 5, '  Suggested Fix:')
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_x(pdf.l_margin + 4)
                    pdf.multi_cell(eff_width - 4, 5, fix.strip(), align='L')
                    pdf.ln(4)

            # ── 3b. AI-Flagged Semantic Risks ─────────────────────────────────
            if ml_issues:
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_fill_color(230, 240, 255)
                pdf.set_text_color(0, 0, 0)
                _cell(pdf, eff_width, 8, '  AI-Flagged Semantic Risks (ML Model)', align='L', fill=True)
                pdf.ln(2)

                for issue in ml_issues:
                    vuln = str(issue.get('vulnerability', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    func = str(issue.get('function', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    expl = str(issue.get('explanation', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    fix  = str(issue.get('suggested_fix', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
                    confidence = issue.get('confidence', 0.0)

                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.set_fill_color(220, 235, 255)
                    pdf.set_text_color(20, 60, 160)
                    _cell(pdf, eff_width, 7, f"  [AI-{issue.get('severity', 'N/A').upper()}]  {vuln}", align='L', fill=True)

                    pdf.set_text_color(80, 80, 80)
                    pdf.set_font('Helvetica', 'I', 9)
                    _cell(pdf, eff_width, 5,
                          f"  Function: {func}  |  Line: {issue.get('line', 'N/A')}  |  AI Confidence: {confidence:.1%}")

                    # Confidence visual bar
                    bar_x = pdf.l_margin + 4
                    bar_y = pdf.get_y()
                    bar_total_w = eff_width - 8
                    bar_filled_w = bar_total_w * confidence
                    pdf.set_fill_color(200, 220, 255)
                    pdf.rect(bar_x, bar_y, bar_total_w, 3, 'F')
                    pdf.set_fill_color(30, 100, 220)
                    pdf.rect(bar_x, bar_y, bar_filled_w, 3, 'F')
                    pdf.ln(5)

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Helvetica', 'B', 9)
                    _cell(pdf, eff_width, 5, '  AI Reasoning:')
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_x(pdf.l_margin + 4)
                    pdf.multi_cell(eff_width - 4, 5, expl.strip(), align='L')

                    pdf.set_font('Helvetica', 'B', 9)
                    _cell(pdf, eff_width, 5, '  Suggested Fix:')
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_x(pdf.l_margin + 4)
                    pdf.multi_cell(eff_width - 4, 5, fix.strip(), align='L')
                    pdf.ln(4)

            pdf.ln(5)

    # ── Save PDF ───────────────────────────────────────────────────────────────
    try:
        pdf.output(output_filename)
        print(f"[SUCCESS] Consolidated PDF report generated: {output_filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save PDF: {e}")


if __name__ == "__main__":
    generate_full_pdf_report()
