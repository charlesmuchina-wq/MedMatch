"""
PDF Export Service for Audit Reports
Generates professional PDF reports with date filtering (daily, weekly, monthly, quarterly, annual)
"""
import io
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from motor.motor_asyncio import AsyncIOMotorDatabase


class PDFExportService:
    """
    Generates PDF audit reports with customizable date ranges.
    Supports: daily, weekly, monthly, quarterly, annual, and custom date ranges.
    """
    
    # Date range presets
    DATE_PRESETS = {
        "today": {"days": 0, "label": "Today"},
        "yesterday": {"days": 1, "label": "Yesterday"},
        "last_7_days": {"days": 7, "label": "Last 7 Days"},
        "last_30_days": {"days": 30, "label": "Last 30 Days"},
        "this_month": {"type": "month", "label": "This Month"},
        "last_month": {"type": "last_month", "label": "Last Month"},
        "this_quarter": {"type": "quarter", "label": "This Quarter"},
        "last_quarter": {"type": "last_quarter", "label": "Last Quarter"},
        "this_year": {"type": "year", "label": "This Year"},
        "last_year": {"type": "last_year", "label": "Last Year"},
        "custom": {"type": "custom", "label": "Custom Range"}
    }
    
    # Brand colors
    COLORS = {
        "primary": colors.HexColor("#00CED1"),  # Turquoise
        "secondary": colors.HexColor("#1E293B"),  # Slate
        "success": colors.HexColor("#22C55E"),  # Green
        "warning": colors.HexColor("#F59E0B"),  # Amber
        "danger": colors.HexColor("#EF4444"),  # Red
        "muted": colors.HexColor("#64748B"),  # Slate gray
        "light": colors.HexColor("#F8FAFC"),  # Light background
    }

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.styles = self._create_styles()
    
    def _create_styles(self) -> Dict:
        """Create custom paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=self.COLORS["secondary"],
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=30,
            textColor=self.COLORS["muted"],
            alignment=TA_CENTER
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=self.COLORS["primary"],
            borderWidth=1,
            borderColor=self.COLORS["primary"],
            borderPadding=5
        ))
        
        # Subsection style
        styles.add(ParagraphStyle(
            name='Subsection',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=self.COLORS["secondary"]
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # Status styles
        styles.add(ParagraphStyle(
            name='StatusPass',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.COLORS["success"]
        ))
        
        styles.add(ParagraphStyle(
            name='StatusFail',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.COLORS["danger"]
        ))
        
        # Footer style
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=self.COLORS["muted"],
            alignment=TA_CENTER
        ))
        
        return styles
    
    def calculate_date_range(self, preset: str, custom_start: str = None, custom_end: str = None) -> Dict:
        """Calculate start and end dates based on preset or custom range."""
        now = datetime.now(timezone.utc)
        
        if preset == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(hour=23, minute=59, second=59)
        elif preset == "last_7_days":
            start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "last_30_days":
            start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "last_month":
            first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_of_month - timedelta(days=1)
            start = end.replace(day=1)
        elif preset == "this_quarter":
            quarter = (now.month - 1) // 3
            start = now.replace(month=quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "last_quarter":
            quarter = (now.month - 1) // 3
            if quarter == 0:
                start = now.replace(year=now.year - 1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59)
            else:
                start = now.replace(month=(quarter - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_month = quarter * 3
                if end_month in [4, 6, 9, 11]:
                    end_day = 30
                elif end_month == 2:
                    end_day = 28
                else:
                    end_day = 31
                end = now.replace(month=end_month, day=end_day, hour=23, minute=59, second=59)
        elif preset == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif preset == "last_year":
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59)
        elif preset == "custom" and custom_start and custom_end:
            start = datetime.fromisoformat(custom_start.replace('Z', '+00:00'))
            end = datetime.fromisoformat(custom_end.replace('Z', '+00:00'))
        else:
            # Default to last 30 days
            start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "label": self.DATE_PRESETS.get(preset, {}).get("label", "Custom Range"),
            "preset": preset
        }
    
    async def generate_pdf(
        self,
        report_data: Dict,
        date_range: Dict,
        include_sections: List[str] = None
    ) -> bytes:
        """
        Generate a PDF from report data.
        
        Args:
            report_data: The audit report data
            date_range: Date range information
            include_sections: Optional list of sections to include (all if None)
        
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build the document content
        story = []
        
        # Header
        story.extend(self._build_header(report_data, date_range))
        
        # Executive Summary
        story.extend(self._build_executive_summary(report_data))
        
        # Compliance Status
        story.extend(self._build_compliance_status(report_data))
        
        # Sections
        sections = report_data.get("sections", {}) or {}
        if include_sections:
            sections = {k: v for k, v in sections.items() if k in include_sections}
        
        for section_id, section_data in sections.items():
            if section_data is not None:
                story.extend(self._build_section(section_id, section_data))
        
        # Digital Signature
        story.extend(self._build_signature(report_data))
        
        # Footer
        story.extend(self._build_footer(report_data))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_header(self, report_data: Dict, date_range: Dict) -> List:
        """Build the report header."""
        elements = []
        
        # Title
        title = report_data.get("template_name", "Compliance Audit Report")
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        
        # Subtitle with date range
        subtitle = f"Reporting Period: {date_range.get('label', 'Custom Range')}<br/>"
        subtitle += f"{date_range.get('start', '')[:10]} to {date_range.get('end', '')[:10]}"
        elements.append(Paragraph(subtitle, self.styles['ReportSubtitle']))
        
        # Report metadata table
        meta_data = [
            ["Report ID:", report_data.get("report_id", "N/A")],
            ["Region:", report_data.get("region", "N/A")],
            ["Generated:", report_data.get("generated_at", "")[:19].replace("T", " ")],
            ["Organization:", report_data.get("ai_system", {}).get("name", "MedMatch AI Platform")]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS["muted"]),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(meta_table)
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.COLORS["primary"]))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_executive_summary(self, report_data: Dict) -> List:
        """Build the executive summary section."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        compliance = report_data.get("compliance_summary", {})
        
        # Summary stats table
        stats_data = [
            ["Overall Status", "Compliance Score", "Critical Issues", "Warnings"],
            [
                compliance.get("overall_status", "N/A"),
                f"{compliance.get('compliance_score', 0)}%",
                str(compliance.get("critical_issues", 0)),
                str(compliance.get("warnings", 0))
            ]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch]*4)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["light"]),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            # Color the status cell based on value
            ('TEXTCOLOR', (0, 1), (0, 1), 
             self.COLORS["success"] if compliance.get("overall_status") == "COMPLIANT" else self.COLORS["danger"]),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 15))
        
        # AI System info
        ai_system = report_data.get("ai_system", {})
        if ai_system:
            elements.append(Paragraph("AI System Under Review", self.styles['Subsection']))
            system_text = f"""
            <b>System Name:</b> {ai_system.get('name', 'N/A')}<br/>
            <b>Version:</b> {ai_system.get('version', 'N/A')}<br/>
            <b>Type:</b> {ai_system.get('type', 'N/A')}<br/>
            <b>Purpose:</b> {ai_system.get('intended_purpose', 'N/A')}
            """
            elements.append(Paragraph(system_text, self.styles['ReportBody']))
        
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_compliance_status(self, report_data: Dict) -> List:
        """Build the compliance status matrix."""
        elements = []
        
        # Check if there's a compliance_status section
        sections = report_data.get("sections", {})
        compliance_status = sections.get("compliance_status", {})
        
        if compliance_status and compliance_status.get("regulations"):
            elements.append(Paragraph("Compliance Status Matrix", self.styles['SectionHeader']))
            
            # Build table
            table_data = [["Regulation", "Status", "Next Deadline"]]
            
            for reg in compliance_status.get("regulations", []):
                status = reg.get("status", "N/A")
                status_color = self.COLORS["success"] if status == "COMPLIANT" else (
                    self.COLORS["warning"] if status in ["ON_TRACK", "MONITORING"] else self.COLORS["danger"]
                )
                
                table_data.append([
                    reg.get("regulation", "N/A"),
                    status,
                    reg.get("next_deadline", "N/A")
                ])
            
            table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["primary"]),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS["light"]]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_section(self, section_id: str, section_data: Dict) -> List:
        """Build a report section."""
        elements = []
        
        title = section_data.get("title", section_id.replace("_", " ").title())
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Handle different section types
        if "protected_characteristics" in section_data:
            # Bias audit section
            elements.extend(self._build_bias_table(section_data))
        elif "key_findings" in section_data:
            # Executive summary with findings
            elements.extend(self._build_findings_list(section_data))
        elif "mechanisms" in section_data:
            # Human oversight mechanisms
            elements.extend(self._build_mechanisms_table(section_data))
        elif "calculations" in section_data:
            # Impact ratio calculations
            elements.extend(self._build_impact_calculations(section_data))
        elif "metrics" in section_data:
            # Selection rates
            elements.extend(self._build_metrics_tables(section_data))
        elif "certifications" in section_data or "certification" in str(section_data):
            # Certifications
            elements.extend(self._build_certifications(section_data))
        elif section_data.get("content"):
            # Simple content
            elements.append(Paragraph(section_data["content"], self.styles['ReportBody']))
        else:
            # Generic key-value display
            elements.extend(self._build_generic_section(section_data))
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_bias_table(self, section_data: Dict) -> List:
        """Build bias audit results table."""
        elements = []
        
        chars = section_data.get("protected_characteristics", [])
        if not chars:
            return elements
        
        table_data = [["Characteristic", "Impact Ratio", "Threshold", "Status"]]
        
        for char in chars:
            status = char.get("status", "N/A")
            table_data.append([
                char.get("characteristic", "N/A"),
                str(char.get("impact_ratio", "N/A")),
                str(char.get("threshold", 0.80)),
                status
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.25*inch, 1.25*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["secondary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Add conclusion if present
        if section_data.get("conclusion"):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Conclusion:</b> {section_data['conclusion']}", self.styles['ReportBody']))
        
        return elements
    
    def _build_findings_list(self, section_data: Dict) -> List:
        """Build a list of findings."""
        elements = []
        
        if section_data.get("content"):
            elements.append(Paragraph(section_data["content"], self.styles['ReportBody']))
            elements.append(Spacer(1, 10))
        
        findings = section_data.get("key_findings", [])
        if findings:
            elements.append(Paragraph("<b>Key Findings:</b>", self.styles['ReportBody']))
            
            items = []
            for finding in findings:
                status = finding.get("status", "")
                status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "•"
                text = f"{status_icon} {finding.get('finding', str(finding))}"
                items.append(ListItem(Paragraph(text, self.styles['ReportBody'])))
            
            elements.append(ListFlowable(items, bulletType='bullet'))
        
        return elements
    
    def _build_mechanisms_table(self, section_data: Dict) -> List:
        """Build human oversight mechanisms table."""
        elements = []
        
        mechanisms = section_data.get("mechanisms", [])
        if not mechanisms:
            return elements
        
        table_data = [["Mechanism", "Description", "Status"]]
        
        for mech in mechanisms:
            table_data.append([
                mech.get("mechanism", "N/A"),
                mech.get("description", "N/A")[:50] + "..." if len(mech.get("description", "")) > 50 else mech.get("description", "N/A"),
                mech.get("status", "N/A")
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 3*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["secondary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_impact_calculations(self, section_data: Dict) -> List:
        """Build impact ratio calculations table."""
        elements = []
        
        calculations = section_data.get("calculations", [])
        for calc in calculations:
            elements.append(Paragraph(f"<b>{calc.get('category', 'Category')}:</b>", self.styles['Subsection']))
            
            groups = calc.get("groups", [])
            if groups:
                table_data = [["Group", "Applicants", "Selected", "Rate"]]
                for group in groups:
                    table_data.append([
                        group.get("group", "N/A"),
                        str(group.get("applicants", "N/A")),
                        str(group.get("selected", "N/A")),
                        group.get("rate", "N/A")
                    ])
                
                table = Table(table_data, colWidths=[1.5*inch, 1.25*inch, 1.25*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["light"]),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(table)
            
            # Impact ratio result
            impact = calc.get("impact_ratio", "N/A")
            status = calc.get("status", "N/A")
            elements.append(Paragraph(
                f"<b>Impact Ratio:</b> {impact} - <b>Status:</b> {status}",
                self.styles['ReportBody']
            ))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_metrics_tables(self, section_data: Dict) -> List:
        """Build selection/scoring rate metrics tables."""
        elements = []
        
        metrics = section_data.get("metrics", [])
        for metric in metrics:
            elements.append(Paragraph(f"<b>{metric.get('category', 'Category')}:</b>", self.styles['Subsection']))
            
            breakdown = metric.get("breakdown", [])
            if breakdown:
                table_data = [["Value", "Scoring Rate", "Selection Rate"]]
                for item in breakdown:
                    table_data.append([
                        item.get("value", "N/A"),
                        item.get("scoring_rate", "N/A"),
                        item.get("selection_rate", "N/A")
                    ])
                
                table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["light"]),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(table)
            
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_certifications(self, section_data: Dict) -> List:
        """Build certifications list."""
        elements = []
        
        certs = section_data.get("certifications", [])
        if not certs:
            # Single certification
            if section_data.get("auditor"):
                elements.append(Paragraph(
                    f"<b>Auditor:</b> {section_data.get('auditor', 'N/A')}<br/>"
                    f"<b>Certified:</b> {section_data.get('certified', 'N/A')}<br/>"
                    f"<b>Date:</b> {section_data.get('date', 'N/A')[:10] if section_data.get('date') else 'N/A'}",
                    self.styles['ReportBody']
                ))
            return elements
        
        table_data = [["Certification", "Issuer", "Issued", "Expires"]]
        for cert in certs:
            table_data.append([
                cert.get("name", "N/A"),
                cert.get("issuer", "N/A"),
                cert.get("issued", "N/A")[:10] if cert.get("issued") else "N/A",
                cert.get("expires", "N/A")[:10] if cert.get("expires") else "N/A"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["secondary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["muted"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_generic_section(self, section_data: Dict) -> List:
        """Build a generic section from key-value pairs."""
        elements = []
        
        for key, value in section_data.items():
            if key == "title":
                continue
            
            if isinstance(value, dict):
                elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['Subsection']))
                for k, v in value.items():
                    elements.append(Paragraph(f"• {k.replace('_', ' ').title()}: {v}", self.styles['ReportBody']))
            elif isinstance(value, list):
                elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['Subsection']))
                for item in value:
                    if isinstance(item, dict):
                        item_text = ", ".join([f"{k}: {v}" for k, v in item.items()])
                        elements.append(Paragraph(f"• {item_text}", self.styles['ReportBody']))
                    else:
                        elements.append(Paragraph(f"• {item}", self.styles['ReportBody']))
            else:
                elements.append(Paragraph(
                    f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                    self.styles['ReportBody']
                ))
        
        return elements
    
    def _build_signature(self, report_data: Dict) -> List:
        """Build the digital signature section."""
        elements = []
        
        sig = report_data.get("digital_signature", {})
        if sig:
            elements.append(Spacer(1, 20))
            elements.append(HRFlowable(width="100%", thickness=1, color=self.COLORS["muted"]))
            elements.append(Spacer(1, 10))
            
            elements.append(Paragraph("Digital Signature & Integrity", self.styles['Subsection']))
            
            sig_text = f"""
            <b>Algorithm:</b> {sig.get('algorithm', 'SHA-256')}<br/>
            <b>Hash:</b> <font face="Courier" size="8">{sig.get('hash', 'N/A')}</font><br/>
            <b>Signed At:</b> {sig.get('timestamp', 'N/A')[:19].replace('T', ' ') if sig.get('timestamp') else 'N/A'}
            """
            elements.append(Paragraph(sig_text, self.styles['ReportBody']))
        
        return elements
    
    def _build_footer(self, report_data: Dict) -> List:
        """Build the report footer."""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=self.COLORS["muted"]))
        
        retention = report_data.get("retention", {})
        footer_text = f"""
        This report was generated by MedMatch AI Platform.<br/>
        Retention Period: {retention.get('years', 'N/A')} years | 
        Delete After: {retention.get('delete_after', 'N/A')[:10] if retention.get('delete_after') else 'N/A'}<br/>
        © {datetime.now().year} MedMatch. All rights reserved.
        """
        
        elements.append(Paragraph(footer_text, self.styles['Footer']))
        
        return elements


# Singleton
_pdf_service = None

def get_pdf_service(db=None):
    global _pdf_service
    if _pdf_service is None and db is not None:
        _pdf_service = PDFExportService(db)
    return _pdf_service
