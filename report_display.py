import streamlit as st
import pandas as pd
from fpdf import FPDF
import json

def display_report(report):
    """Display the investigation report in the UI"""
    st.header("Investigation Report")

    # Basic Info
    st.subheader("Basic Info")
    basic_info_df = pd.DataFrame({
        "Domain": [report["Domain"]],
        "Server": [report.get("Infrastructure", {}).get("Server", "N/A")],
        "Address": [report.get("IP Lookup", {}).get("asn_cidr", "N/A")],
        "Name": [report.get("IP Lookup", {}).get("asn_description", "N/A")],
        "Addresses": [", ".join(report.get("IP Lookup", {}).get("network", {}).get("cidr", []))],
        "Aliases": [report["Domain"]],
    }).T
    st.table(basic_info_df)

    # Traceroute
    st.subheader("Traceroute")
    st.text(report["Traceroute"])

    # Dig Command
    st.subheader("DNS Information")
    st.text(report["Dig"])

    # IP Lookup
    st.subheader("IP Lookup")
    ip_lookup_data = report["IP Lookup"]
    for key, value in ip_lookup_data.items():
        st.markdown(f"**{key}**")
        if isinstance(value, list):
            st.json(value)
        else:
            st.text(value)

    # Tech Stack
    st.subheader("Tech Stack")
    st.json(report["Tech Stack"])

    # Infrastructure
    st.subheader("Infrastructure")
    st.json(report["Infrastructure"])

    # Site Details
    st.subheader("Site Details")
    st.json(report["Site Details"])

def export_to_pdf(report, site_description):
    """Export report to PDF"""
    pdf = PDF()
    pdf.add_page()

    # Site Description
    pdf.chapter_title("Site Description")
    pdf.chapter_body(site_description)
    
    # Basic Info
    pdf.chapter_title("Basic Info")
    basic_info = [
        ["Domain", report["Domain"]],
        ["Server", report.get("Infrastructure", {}).get("Server", "N/A")],
        ["Address", report.get("IP Lookup", {}).get("asn_cidr", "N/A")],
        ["Name", report.get("IP Lookup", {}).get("asn_description", "N/A")],
        ["Addresses", ", ".join(report.get("IP Lookup", {}).get("network", {}).get("cidr", []))],
        ["Aliases", report["Domain"]],
    ]
    for row in basic_info:
        pdf.chapter_body(f"{row[0]}: {row[1]}")
    
    # Traceroute
    pdf.chapter_title("Traceroute")
    pdf.chapter_body(report["Traceroute"])
    
    # Dig Command
    pdf.chapter_title("DNS Information")
    pdf.chapter_body(report["Dig"])

    # IP Lookup
    pdf.chapter_title("IP Lookup")
    pdf.chapter_body(json.dumps(report["IP Lookup"], indent=4))

    # Tech Stack
    pdf.chapter_title("Tech Stack")
    pdf.chapter_body(json.dumps(report["Tech Stack"], indent=4))

    # Infrastructure
    pdf.chapter_title("Infrastructure")
    pdf.chapter_body(json.dumps(report["Infrastructure"], indent=4))

    # Site Details
    pdf.chapter_title("Site Details")
    pdf.chapter_body(json.dumps(report["Site Details"], indent=4))

    return pdf.output(dest='S').encode('latin1')

class PDF(FPDF):
    """Custom PDF class for structured reports"""
    
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Website Investigation Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        if not isinstance(body, str):
            body = json.dumps(body, indent=4)
        self.multi_cell(0, 10, body)
        self.ln()