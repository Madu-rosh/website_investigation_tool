# Website Investigation Tool

This Streamlit app performs an investigation on a provided website URL. The app follows these steps:

1. Perform a traceroute to identify IPs and connections to the website.
2. Run the `dig` (or `nslookup` on Windows) command to gather DNS information.
3. Use IP lookup to gather information about the IPs from the domain name.
4. Identify the website's tech stack using a suitable Python library.
5. Check the website's infrastructure for the use of Cloudflare, CloudFront, and other relevant headers.
6. Fetch detailed site information similar to Wappalyzer using `python-Wappalyzer`.
7. Generate a report with the gathered data.
8. Use OpenAI to analyze the report and generate a detailed site description.

## Installation

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage

To run the Streamlit app, execute the following command:

```sh
streamlit run website_investigation.py
```

## Files

- `website_investigation.py`: The main Streamlit app file.
- `requirements.txt`: List of required Python libraries.
- `README.md`: This file.

## Example

Enter the URL of the website you want to investigate in the Streamlit app and click on "Run Investigation" to get the report.
