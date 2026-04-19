import requests
import xml.etree.ElementTree as ET

def fetch_medline_data(query: str):
    url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={query}"
    response = requests.get(url)
    return response.text


def parse_medline(xml_data: str):
    root = ET.fromstring(xml_data)

    results = []
    for doc in root.findall(".//document"):
        title = doc.find("content[@name='title']")
        summary = doc.find("content[@name='FullSummary']")

        if title is not None and summary is not None:
            results.append({
                "title": title.text,
                "summary": summary.text
            })

    return results


def get_medical_info(query: str):
    xml_data = fetch_medline_data(query)
    data = parse_medline(xml_data)

    if not data:
        return None

    return data[0]