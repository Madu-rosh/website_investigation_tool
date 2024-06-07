import streamlit as st
from streamlit_option_menu import option_menu
import subprocess
import socket
import json
import pandas as pd
from ipwhois import IPWhois
from builtwith import builtwith
import platform
import requests
from urllib.parse import urlparse
from Wappalyzer import Wappalyzer, WebPage
import pydoc
from report_display import display_report, export_to_pdf
from analyze_report import analyze_site  # Ensure this import is correct

def ensure_https(url):
    """Ensure the URL starts with https://"""
    if not urlparse(url).scheme:
        url = "https://" + url
    return url

def traceroute(url):
    """Perform traceroute to the provided URL using an external API"""
    try:
        domain = urlparse(url).netloc
        # Resolve the domain to an IP address to ensure it's valid
        ip = socket.gethostbyname(domain)
    except socket.gaierror as e:
        st.error(f"Error resolving domain: {str(e)}")
        return f"Error resolving domain: {str(e)}"
    
    # Using an external API for traceroute
    try:
        api_key = st.secrets["api"]["ipinfo_key"]
        response = requests.get(f"https://api.ipinfo.io/{ip}/traceroute?token={api_key}")
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Error running traceroute: {response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"Error running traceroute: {str(e)}")
        return None

def dig_command(domain):
    """Run dig command to gather DNS information"""
    try:
        if platform.system().lower() == "windows":
            command = ['nslookup', domain]
        else:
            command = ['dig', domain]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            st.error(f"Error running dig command: {result.stderr}")
            return None
    except FileNotFoundError:
        st.error("dig/nslookup command not found. Please ensure it is installed on your system.")
        return None

def ip_lookup(ip):
    """Perform IP lookup using IPWhois"""
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap()
        return results
    except Exception as e:
        st.error(f"Error looking up IP: {str(e)}")
        return None

def get_ip_from_domain(domain):
    """Resolve domain to IP address"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror as e:
        st.error(f"Error resolving domain: {str(e)}")
        return None

def tech_stack(url):
    """Identify website tech stack using builtwith"""
    try:
        tech_info = builtwith(url)
        return tech_info
    except Exception as e:
        st.error(f"Error identifying tech stack: {str(e)}")
        return None

def check_infrastructure(url):
    """Check website infrastructure details from headers"""
    response = requests.get(url)
    headers = response.headers
    infrastructure = {}

    if 'Server' in headers:
        infrastructure['Server'] = headers['Server']
    if 'X-Cache' in headers:
        infrastructure['Cache'] = headers['X-Cache']
    if 'Via' in headers:
        infrastructure['Via'] = headers['Via']
    if 'cf-ray' in headers or 'CF-Cache-Status' in headers:
        infrastructure['Cloudflare'] = True
    if 'x-amz-cf-id' in headers or 'x-amz-cf-pop' in headers:
        infrastructure['CloudFront'] = True

    return infrastructure

def fetch_site_details(url):
    """Fetch detailed site information using Wappalyzer"""
    try:
        wappalyzer = Wappalyzer.latest()
        webpage = WebPage.new_from_url(url)
        site_details = wappalyzer.analyze_with_versions_and_categories(webpage)
        return site_details
    except Exception as e:
        st.error(f"Error fetching site details: {str(e)}")
        return None

def make_serializable(obj):
    """Convert non-serializable objects to serializable ones"""
    if isinstance(obj, set):
        return list(obj)
    return obj

def generate_report_json(domain, traceroute_data, dig_data, ip_info, tech_info, infra_info, site_details):
    """Generate JSON report from the gathered data"""
    report = {
        "Domain": domain,
        "Traceroute": traceroute_data,
        "Dig": dig_data,
        "IP Lookup": ip_info,
        "Tech Stack": tech_info,
        "Infrastructure": infra_info,
        "Site Details": site_details
    }
    # Convert sets to lists for JSON serialization
    report = {k: make_serializable(v) for k, v in report.items()}
    return report

def generate_markdown_doc():
    """Generate markdown documentation using pydoc"""
    doc = pydoc.render_doc(__name__, renderer=pydoc.plaintext)
    md_doc = f"```\n{doc}\n```"
    return md_doc

st.set_page_config(page_title="Website Investigation Tool", layout="wide")

st.title("Website Investigation Tool")

# Sidebar for navigation
with st.sidebar:
    selected_page = option_menu(
        "Menu",
        ["Home", "Report", "Documentation"],
        icons=["house", "file-earmark-text", "book"],
        menu_icon="cast",
        default_index=0,
    )

# Home Page
if selected_page == "Home":
    st.header("Home")
    st.write("Enter the URL of the website you want to investigate:")
    
    url_input = st.text_input("Website URL", "")
    
    # Use columns to separate main input area from status messages
    col1, col2 = st.columns([1, 2])
    
    if col1.button("Run Investigation"):
        if url_input:
            url = ensure_https(url_input)
            with col2:
                st.write("##### Status")
            with st.spinner('Running traceroute...'):
                traceroute_data = traceroute(url)
                if traceroute_data:
                    col2.success('Traceroute completed')
                else:
                    col2.error('Traceroute failed')

            with st.spinner('Running dig command...'):
                domain = urlparse(url).netloc
                dig_data = dig_command(domain)
                if dig_data:
                    col2.success('Dig command completed')
                else:
                    col2.error('Dig command failed')

            with st.spinner('Looking up IP address...'):
                ip = get_ip_from_domain(domain)
                if ip:
                    col1.write(f"IP Address: {ip}")
                    ip_info = ip_lookup(ip)
                    if ip_info:
                        col2.success('IP lookup completed')
                    else:
                        col2.error('IP lookup failed')
                else:
                    ip_info = None
                    col2.error('Domain resolution failed')

            with st.spinner('Identifying tech stack...'):
                tech_info = tech_stack(url)
                if tech_info:
                    col2.success('Tech stack identification completed')
                else:
                    col2.error('Tech stack identification failed')

            with st.spinner('Checking infrastructure...'):
                infra_info = check_infrastructure(url)
                if infra_info:
                    col2.success('Infrastructure check completed')
                else:
                    col2.error('Infrastructure check failed')

            with st.spinner('Fetching site details...'):
                site_details = fetch_site_details(url)
                if site_details:
                    col2.success('Site details fetched')
                else:
                    col2.error('Failed to fetch site details')

            report = generate_report_json(domain, traceroute_data, dig_data, ip_info, tech_info, infra_info, site_details)

            # Get site description from OpenAI
            with st.spinner('Analyzing site report...'):
                site_description = analyze_site(report)
            
            st.session_state.report = report
            st.session_state.site_description = site_description

            col2.success("Investigation completed! [Visit the Report section to view the report.](#report)")

# Report Page
if selected_page == "Report":
    st.header("Report")
    if "report" in st.session_state:
        report = st.session_state.report
        site_description = st.session_state.site_description
        
        st.subheader("Site Description")
        st.write(site_description)
        
        # Use columns to place export options and buttons
        col1, col2 = st.columns([3, 1])
        
        with col1:
            export_format = st.selectbox("Select export format", ["PDF", "CSV", "JSON"])
        
        with col2:
            if export_format == "CSV":
                report_df = pd.DataFrame([report])
                st.download_button(label="Download as CSV", data=report_df.to_csv(index=False), mime='text/csv', file_name='report.csv')
            elif export_format == "PDF":
                pdf_data = export_to_pdf(report, site_description)
                st.download_button(label="Download as PDF", data=pdf_data, mime='application/pdf', file_name='report.pdf')
            elif export_format == "JSON":
                json_data = json.dumps(report, indent=4)
                st.download_button(label="Download as JSON", data=json_data, mime='application/json', file_name='report.json')

        display_report(report)
    else:
        st.error("No report available. Please run an investigation on the Home page.")

# Documentation Page
if selected_page == "Documentation":
    st.header("Documentation")
    st.write("Documentation generated using `pydoc`.")

    # Generate and display markdown documentation
    md_doc = generate_markdown_doc()
    st.markdown(md_doc)