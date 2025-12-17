import os
import xml.etree.ElementTree as ET

def get(path:str, pge_name):
    """Достает хэш-сумму пакета из full_list.xml"""
    tree = ET.parse(path)
    root = tree.getroot()
    
    for pge in root.findall("package"):
        if pge.get("id") == pge_name:
            return pge.find("sha256").text
    return -1