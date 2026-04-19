"""
PDF Health Report Generator
===========================
Generates professional PDF health reports using FPDF2 (Windows-compatible).
No external dependencies like GTK required.
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any


class HealthReportPDF(FPDF):
    """Custom FPDF class for health reports with header and footer"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set consistent margins (15mm all sides)
        self.set_margins(left=15, top=15, right=15)
        font_path = os.path.join(os.path.dirname(__file__), 'fonts')
        self.add_font('DejaVu', '',  os.path.join(font_path, 'DejaVuSans.ttf'))
        self.add_font('DejaVu', 'B', os.path.join(font_path, 'DejaVuSans-Bold.ttf'))
        self.add_font('DejaVu', 'I', os.path.join(font_path, 'DejaVuSans-Oblique.ttf'))

    def header(self):
        """Page header"""
        self.set_font("DejaVu", "B", 22)
        self.set_text_color(0, 102, 204)
        self.cell(0, 14, "HealthCare AI Report",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(4)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        """Page footer"""
        self.set_y(-14)
        self.set_font("DejaVu", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(
            0, 8,
            f"Page {self.page_no()}  |  Medical Disclaimer: This report is for informational "
            "purposes only. Consult a healthcare professional for medical advice.",
            align="C"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _usable_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def _section_title(self, title: str):
        """Blue bold section heading with a horizontal rule underneath."""
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 102, 204)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def _safe_multi_cell(self, w: float, h: float, txt: str, **kwargs):
        """
        Wrapper around multi_cell that resets X to the left margin
        after the call, preventing 'Not enough horizontal space' errors
        on subsequent rows.
        """
        self.multi_cell(w, h, txt, **kwargs)
        self.set_x(self.l_margin)


# ======================================================================
# Public API
# ======================================================================

def generate_health_report_pdf(report_data: Dict[str, Any]) -> BytesIO:
    """
    Generate a PDF health report from report data using FPDF2.

    Args:
        report_data: Dictionary containing user profile, metrics, medications, etc.

    Returns:
        BytesIO object containing the PDF data
    """
    try:
        pdf = HealthReportPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        uw = pdf._usable_width()

        # ============================================================
        # PATIENT PROFILE
        # ============================================================
        pdf._section_title("Patient Profile")

        profile_rows = [
            ("Name:",            str(report_data.get('user_name', 'N/A'))),
            ("Age & Gender:",    f"{report_data.get('age', 'N/A')} yrs, {report_data.get('gender', 'N/A')}"),
            ("Height / Weight:", f"{report_data.get('height_cm', 'N/A')} cm / {report_data.get('weight_kg', 'N/A')} kg"),
            ("BMI:",             f"{report_data.get('bmi', 'N/A')} ({report_data.get('bmi_category', 'N/A')})"),
            ("Fitness Level:",   str(report_data.get('fitness_level', 'N/A'))),
            ("Allergies:",       str(report_data.get('allergies', 'None') or 'None')),
        ]

        label_w = uw * 0.35
        value_w = uw * 0.65

        for label, value in profile_rows:
            pdf.set_font("DejaVu", "B", 9)
            pdf.cell(label_w, 6, label)
            pdf.set_font("DejaVu", "", 9)
            pdf.cell(value_w, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(4)

        # ============================================================
        # HEALTH CONDITIONS
        # ============================================================
        conditions = report_data.get('health_conditions', '') or ''
        if conditions.strip():
            pdf._section_title("Health Conditions")
            pdf.set_font("DejaVu", "", 10)
            pdf._safe_multi_cell(uw, 5, conditions.strip())
            pdf.ln(3)

        # ============================================================
        # HEALTH GOALS
        # ============================================================
        goals_list = report_data.get('health_goals_list', []) or []
        if goals_list:
            pdf._section_title("Health Goals")
            pdf.set_font("DejaVu", "", 10)
            for goal in goals_list:
                pdf._safe_multi_cell(uw, 5, f"  - {goal.strip()}")
            pdf.ln(3)

        # ============================================================
        # CURRENT MEDICATIONS
        # ============================================================
        pdf._section_title("Current Medications")
        medications = report_data.get('medications', []) or []
        if medications:
            for med in medications:
                pdf.set_font("DejaVu", "B", 10)
                pdf.cell(0, 5, f"  {med.get('name', 'Unknown')}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.set_font("DejaVu", "", 9)
                details = (
                    f"  Dosage: {med.get('dosage', 'N/A')}  |  "
                    f"Frequency: {med.get('frequency', 'N/A')}"
                )
                adherence = med.get('adherence_rate')
                if adherence is not None:
                    level = "Excellent" if adherence >= 80 else ("Moderate" if adherence >= 50 else "Low")
                    details += f"  |  Adherence: {adherence}% ({level})"
                pdf._safe_multi_cell(uw, 4, details)
                pdf.ln(1)
        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "  No medications tracked",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)

        pdf.ln(3)

        # ============================================================
        # PAST MEDICATIONS (Discontinued)
        # ============================================================
        past_medications = report_data.get('past_medications', []) or []
        if past_medications:
            pdf._section_title("Past Medications (Discontinued)")
            pdf.set_text_color(120, 120, 120)  # Grey tone for past items
            for med in past_medications:
                pdf.set_font("DejaVu", "B", 9)
                pdf.cell(0, 5, f"  {med.get('name', 'Unknown')}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.set_font("DejaVu", "", 8)
                details = (
                    f"  Dosage: {med.get('dosage', 'N/A')}  |  "
                    f"Frequency: {med.get('frequency', 'N/A')}  |  "
                    f"Status: Discontinued"
                )
                pdf._safe_multi_cell(uw, 4, details)
                pdf.ln(1)
            pdf.set_text_color(0, 0, 0)  # Reset to black
            pdf.ln(3)

        # ============================================================
        # HEALTH METRICS SUMMARY
        # ============================================================
        metrics_summary = report_data.get('metrics_summary', []) or []
        if metrics_summary:
            pdf._section_title("Recent Health Metrics (Last 30 Days)")
            pdf.set_font("DejaVu", "", 9)

            lw = uw * 0.50
            vw = uw * 0.50

            for metric in metrics_summary:
                lbl  = metric.get('label', '')
                val  = metric.get('value', '')
                unit = metric.get('unit', '') or ''
                pdf.cell(lw, 6, f"{lbl}:", border=1)
                pdf.cell(vw, 6, f"{val} {unit}".strip(), border=1,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(4)

        # ============================================================
        # DETAILED HEALTH LOGS TABLE
        # ============================================================
        health_logs = report_data.get('health_logs', []) or []
        if health_logs:
            if pdf.get_y() > 220:
                pdf.add_page()

            pdf._section_title("Detailed Health Logs (Last 15 Entries)")

            # Column widths as fractions of usable width (must sum to 1.0)
            cw = [
                uw * 0.17,  # Date
                uw * 0.22,  # Metric
                uw * 0.14,  # Value
                uw * 0.10,  # Unit
                uw * 0.37,  # Notes
            ]
            headers = ["Date", "Metric", "Value", "Unit", "Notes"]

            # Header row
            pdf.set_font("DejaVu", "B", 8)
            pdf.set_fill_color(0, 102, 204)
            pdf.set_text_color(255, 255, 255)
            for i, hdr in enumerate(headers):
                is_last = (i == len(headers) - 1)
                pdf.cell(
                    cw[i], 6, hdr, border=1, fill=True, align="C",
                    new_x=XPos.LMARGIN if is_last else XPos.RIGHT,
                    new_y=YPos.NEXT    if is_last else YPos.TOP,
                )

            # Data rows
            pdf.set_font("DejaVu", "", 7)
            pdf.set_text_color(0, 0, 0)

            for idx, log in enumerate(health_logs[-15:]):
                fill_color = (240, 246, 255) if idx % 2 == 0 else (255, 255, 255)
                pdf.set_fill_color(*fill_color)

                row = [
                    log.get('date', ''),
                    log.get('metric_type', ''),
                    str(log.get('value', '')),
                    log.get('unit', ''),
                    str(log.get('notes', '') or '')[:35],
                ]
                aligns = ["L", "L", "R", "C", "L"]

                for i, (cell_txt, cell_align) in enumerate(zip(row, aligns)):
                    is_last = (i == len(row) - 1)
                    pdf.cell(
                        cw[i], 5, cell_txt, border=1, fill=True, align=cell_align,
                        new_x=XPos.LMARGIN if is_last else XPos.RIGHT,
                        new_y=YPos.NEXT    if is_last else YPos.TOP,
                    )

        # ============================================================
        # DISCLAIMER
        # ============================================================
        pdf.ln(5)
        pdf.set_font("DejaVu", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf._safe_multi_cell(
            uw, 4,
            "This report is generated by HealthCare AI Assistant for informational purposes only. "
            "Please consult with a healthcare professional for medical advice, diagnosis, or treatment. "
            f"Report ID: {report_data.get('report_id', 'N/A')}"
        )

        pdf_bytes = pdf.output()
        return BytesIO(pdf_bytes)

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


# ======================================================================
# Data Formatter
# ======================================================================

def format_report_data(
    user_profile: Dict,
    health_logs: List[Dict],
    medications: List[Dict],
    adherence_stats: Dict,
    past_medications: List[Dict] = None
) -> Dict[str, Any]:
    """
    Format raw database data for PDF report generation.

    Args:
        user_profile: User profile data from database
        health_logs: List of health log entries
        medications: List of active medication records
        adherence_stats: Medication adherence statistics
        past_medications: List of discontinued medication records

    Returns:
        Formatted dictionary ready for PDF generation
    """
    if past_medications is None:
        past_medications = []

    # ── BMI ──────────────────────────────────────────────────────────
    height_cm = user_profile.get('height_cm') or 0
    weight_kg = user_profile.get('weight_kg') or 0
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1) if height_cm and weight_kg else 0

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal weight"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    # ── Goals ─────────────────────────────────────────────────────────
    health_goals_str = user_profile.get('health_goals', '') or ''
    goals_list = [g.strip() for g in health_goals_str.split(',') if g.strip()]

    # ── Medications ───────────────────────────────────────────────────
    formatted_meds = []
    for med in medications:
        med_adh = adherence_stats.get(med['id'], {})
        rate = med_adh.get('adherence_rate', 0)
        level = 'excellent' if rate >= 80 else ('moderate' if rate >= 50 else 'low')
        formatted_meds.append({
            'id':             med['id'],
            'name':           med.get('name', 'Unknown'),
            'dosage':         med.get('dosage', ''),
            'frequency':      med.get('frequency', ''),
            'adherence_rate': rate,
            'adherence_level': level,
        })

    # ── Past Medications ──────────────────────────────────────────────
    formatted_past_meds = []
    for med in past_medications:
        formatted_past_meds.append({
            'id':        med['id'],
            'name':      med.get('name', 'Unknown'),
            'dosage':    med.get('dosage', ''),
            'frequency': med.get('frequency', ''),
        })

    # ── Health Logs ───────────────────────────────────────────────────
    formatted_logs = []
    for log in health_logs[-30:]:
        formatted_logs.append({
            'date':        (log.get('created_at', '') or '').split('T')[0],
            'metric_type': (log.get('metric_type', '') or '').replace('_', ' ').title(),
            'value':       log.get('value', ''),
            'unit':        log.get('unit', ''),
            'notes':       log.get('notes', '') or '',
        })

    # ── Metrics Summary ───────────────────────────────────────────────
    metrics_by_type: Dict[str, list] = {}
    for log in health_logs[-30:]:
        mt  = log.get('metric_type', '')
        val = log.get('value', '')
        metrics_by_type.setdefault(mt, [])
        try:
            metrics_by_type[mt].append(float(val.split('/')[0] if '/' in val else val))
        except (ValueError, AttributeError):
            pass

    unit_map = {
        'weight': 'kg', 'heart_rate': 'bpm',
        'blood_pressure': 'mmHg', 'blood_sugar': 'mg/dL',
        'sleep': 'hrs', 'exercise': 'min', 'temperature': 'C',
    }
    label_map = {
        'blood_pressure': 'Blood Pressure', 'weight': 'Weight',
        'heart_rate': 'Heart Rate', 'sleep': 'Sleep',
        'exercise': 'Exercise', 'blood_sugar': 'Blood Sugar',
        'temperature': 'Temperature',
    }

    metrics_summary = []
    for mt, vals in metrics_by_type.items():
        if vals:
            metrics_summary.append({
                'label': label_map.get(mt, mt.replace('_', ' ').title()),
                'value': f"{sum(vals) / len(vals):.1f}",
                'unit':  unit_map.get(mt, ''),
            })

    # ── Report ID ─────────────────────────────────────────────────────
    import uuid
    report_id = str(uuid.uuid4())[:8].upper()

    return {
        'user_name':          user_profile.get('name', 'User'),
        'age':                user_profile.get('age', 'N/A'),
        'gender':             user_profile.get('gender', 'N/A'),
        'height_cm':          user_profile.get('height_cm', 'N/A'),
        'weight_kg':          user_profile.get('weight_kg', 'N/A'),
        'bmi':                bmi,
        'bmi_category':       bmi_category,
        'fitness_level':      (user_profile.get('fitness_level', 'N/A') or 'N/A').title(),
        'allergies':          user_profile.get('allergies', 'None') or 'None',
        'health_conditions':  user_profile.get('health_conditions', '') or '',
        'health_goals':       bool(goals_list),
        'health_goals_list':  goals_list,
        'medications':        formatted_meds,
        'past_medications':   formatted_past_meds,
        'adherence_stats':    adherence_stats,
        'health_logs':        formatted_logs,
        'metrics_summary':    metrics_summary,
        'generated_date':     datetime.now().strftime('%B %d, %Y'),
        'generated_datetime': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'report_id':          report_id,
    }