import xml.etree.ElementTree as ET
from typing import List, Optional

class Manifest:
    def __init__(self,
                 name: str,
                 version: str,
                 creation_date: str,
                 sha256: str,
                 dependencies: List[str],
                 supported_os: List[str],
                 supported_arch: List[str],
                 builder: Optional[str] = None,
                 entry_point: Optional[str] = None):
        self.name = name
        self.version = version
        self.creation_date = creation_date
        self.sha256 = sha256
        self.dependencies = dependencies
        self.supported_os = supported_os
        self.supported_arch = supported_arch
        self.builder = builder
        self.entry_point = entry_point

    @classmethod
    def from_file(cls, filepath: str) -> "Manifest":
        """
        Загружает манифест из XML-файла и возвращает объект Manifest.
        """
        tree = ET.parse(filepath)
        root = tree.getroot()

        name = root.findtext("name")
        version = root.findtext("version")
        creation_date = root.findtext("creationDate")
        sha256 = root.findtext("sha256")

        dependencies = [dep.text for dep in root.findall("dependencies/dependency")]
        supported_os = [os.text for os in root.findall("supportedOS/os")]
        supported_arch = [arch.text for arch in root.findall("supportedArch/arch")]

        builder = root.findtext("builder")
        entry_point = root.findtext("entry_point")

        return cls(
            name=name,
            version=version,
            creation_date=creation_date,
            sha256=sha256,
            dependencies=dependencies,
            supported_os=supported_os,
            supported_arch=supported_arch,
            builder=builder,
            entry_point=entry_point
        )
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            version=data['version'],
            creation_date=data['creation_date'],
            sha256=data['sha256'],
            dependencies=data['dependencies'],
            supported_os=data['supported_os'],
            supported_arch=data['supported_arch'],
            builder=data.get('builder'),
            entry_point=data.get('entry_point')
        )
        
    def to_xml(self, filepath: str):
        """
        Сохраняет манифест в XML-файл.
        """
        root = ET.Element("manifest")
        
        ET.SubElement(root, "name").text = self.name
        ET.SubElement(root, "version").text = self.version
        ET.SubElement(root, "creationDate").text = self.creation_date
        ET.SubElement(root, "sha256").text = self.sha256
        
        dependencies_elem = ET.SubElement(root, "dependencies")
        for dep in self.dependencies:
            ET.SubElement(dependencies_elem, "dependency").text = dep
        
        supported_os_elem = ET.SubElement(root, "supportedOS")
        for os in self.supported_os:
            ET.SubElement(supported_os_elem, "os").text = os
        
        supported_arch_elem = ET.SubElement(root, "supportedArch")
        for arch in self.supported_arch:
            ET.SubElement(supported_arch_elem, "arch").text = arch
        
        if self.builder is not None:
            ET.SubElement(root, "builder").text = self.builder
        
        if self.entry_point is not None:
            ET.SubElement(root, "entry_point").text = self.entry_point
        
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)

    def __repr__(self):
        return (f"Manifest(name={self.name!r}, version={self.version!r}, creation_date={self.creation_date!r}, "
                f"sha256={self.sha256!r}, dependencies={self.dependencies!r}, "
                f"supported_os={self.supported_os!r}, supported_arch={self.supported_arch!r}, "
                f"builder={self.builder!r}, entry_point={self.entry_point!r})")

#ПРИМЕР ИСПОЛЬЗОВАНИЯ:

"""
from manifest import Manifest

manifest = Manifest.from_file("path/to/manifest.xml")
print(manifest)
print("Builder:", manifest.builder)

manifest.to_xml("path/to/manifest.xml")
"""