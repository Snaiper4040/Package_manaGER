import os
import xml.etree.ElementTree as ET

class PgesManager:
    """
    Класс содержит методы для взаимодействия с файлом pges.xml
    pges.xml - список всех пакетов с их статусами (в кэше, установлен, собран) и версиями
    pges.xml хранится в кэше
    """
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.file_path = os.path.join(cache_dir, "pges.xml")
        if os.path.exists(self.file_path):
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
        else:
            self.root = ET.Element('pges')
            self.tree = ET.ElementTree(self.root)
            self.save()

    def save(self):
        self.tree.write(self.file_path, encoding='utf-8', xml_declaration=True)

    def add_package(self, pge_name: str, version: str = "1.0.0", need_build: bool = False):
        # Проверяем наличие пакета с указанной версией
        if self.get_package(pge_name, version) is not None:
            print(f"Пакет '{pge_name}' версии '{version}' уже записан в pges.xml")
            return False
        pge_elem = ET.SubElement(self.root, 'pge')
        pge_elem.text = pge_name

        # Добавляем версию
        version_elem = ET.SubElement(pge_elem, 'version')
        version_elem.text = version

        # Добавляем состояния
        def add_state(tag, value):
            elem = ET.SubElement(pge_elem, tag)
            elem.text = 'True' if value else 'False'

        add_state('in_cache', False)
        add_state('installed', False)
        if need_build:
            add_state('built', False)
        
        self.save()
        return True

    def get_package(self, pge_name: str, version: str):
        for pge_elem in self.root.findall('pge'):
            # Текст у <pge> — это имя пакета, версия в <version>
            if (pge_elem.text or '').strip() == pge_name:
                version_elem = pge_elem.find('version')
                if version_elem is not None and (version_elem.text or '').strip() == version:
                    info = {
                        'name': pge_elem.text,
                        'version': version_elem.text,
                        'in_cache': False,
                        'installed': False,
                        'built': None
                    }
                    for state in ['in_cache', 'installed', 'built']:
                        elem = pge_elem.find(state)
                        if elem is not None:
                            info[state] = (elem.text == 'True')
                    return info
        print(f"Пакет '{pge_name}' версии '{version}' отсутствует в pges.xml")
        return None
    
    def get_all_packages(self):
        pges_list = list()
        for pge_elem in self.root.findall('pge'):
            info = self.get_package(pge_elem.text, pge_elem.find('version'))
            pges_list.append(info)
        return pges_list

    def update_package(self, pge_name: str, version: str, in_cache: bool = None,
                       installed: bool = None, built: bool = None):
        for pge_elem in self.root.findall('pge'):
            if (pge_elem.text or '').strip() == pge_name:
                version_elem = pge_elem.find('version')
                if version_elem is not None and (version_elem.text or '').strip() == version:
                    # Обновляем только указанные состояния
                    def update_state(tag, value):
                        if value is None:
                            return
                        elem = pge_elem.find(tag)
                        if elem is not None:
                            elem.text = 'True' if value else 'False'

                    update_state('in_cache', in_cache)
                    update_state('installed', installed)
                    update_state('built', built)

                    self.save()
                    return True
        print(f"Пакет '{pge_name}' версии '{version}' отсутствует в pges.xml")
        return False
    
    def remove_package(self, pge_name: str, version: str):
        for pge_elem in self.root.findall('pge'):
            if (pge_elem.text or '').strip() == pge_name:
                version_elem = pge_elem.find('version')
                if version_elem is not None and (version_elem.text or '').strip() == version:
                    self.root.remove(pge_elem)
                    self.save()
                    return True
        print(f"Пакет '{pge_name}' версии '{version}' отсутствует в pges.xml")
        return False
    
    def add_built_field(self, pge_name: str, version: str):
        for pge_elem in self.root.findall('pge'):
            if (pge_elem.text or '').strip() == pge_name:
                version_elem = pge_elem.find('version')
                if version_elem is not None and (version_elem.text or '').strip() == version:
                    built_elem = pge_elem.find('built')
                    if built_elem is None:
                        built_elem = ET.SubElement(pge_elem, 'built')
                        built_elem.text = 'False'
                        self.save()
                        return True
                    return True  # Уже есть
        print(f"Пакет '{pge_name}' версии '{version}' отсутствует в pges.xml")
        return False