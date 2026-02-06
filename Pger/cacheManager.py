import os
import requests
from pgesManager import PgesManager
import xml.etree.ElementTree as ET

class CacheManager:
    """
    Класс для взаимодействия с кэшем
    Используется для загрузки пакетов в кэш, для очистки кэша
    """
    def __init__(self, cache_dir: str, repository_url: str, PM):
        self.cache_dir = cache_dir
        self.repository_url = repository_url
        self.tmp_dir = os.path.join(cache_dir, "tmp\\")
        self.PM = PM
    
    def get_pge_from_repository(self, pge_name:str, pge_version:str):
        """
        1. Загрузка пакета с удаленного репозитория во временную директорию
        2. Расчет хэш-суммы пакета и сравнение с истинным значением
        3. Регистрация скаченного пакета"(обновление файла pges.xml)
        4. Перемещение пакета в кэша и регистрация перемещения
        5. удаление временного файла
        """
        download_url = f"{self.repository_url}/download/{pge_name}-{pge_version}"
        sha256_url = f"{self.repository_url}/download/sha256/{pge_name}-{pge_version}"
        package_path = os.path.join(self.cache_dir, f"{pge_name}-{pge_version}.pger")
        tmp_path = os.path.join(self.tmp_dir, f"{pge_name}-{pge_version}.pger")
    #___1___#
        response = requests.get(download_url)
        if response.status_code == 200:
            with open(tmp_path, 'wb') as f:
                f.write(response.content) 
        else:
            print(f"Не удалось загрузить файл по ссылке: {download_url}")
            return False
    #___2___#
        response = requests.get(sha256_url)
        if response.status_code == 200:
            if response.text != calculate_sha256(tmp_path):
                print(f"Неверная хэш-сумма пакета {pge_name}-{pge_version}")
                return False
        else:
            print(f"Не удалось получить хэш-сумму пакета {pge_name}-{pge_version}")
            return False
        del response
    #___3___#
        if (not self.PM.add_package(pge_name=pge_name, version=pge_version)):
            os.remove(tmp_path)
            return False
    #___4___#
        if (os.path.exists(package_path)):
            os.remove(package_path)
        os.copy(tmp_path, package_path)
        if (not self.PM.update_package(pge_name=pge_name, version=pge_version, in_cache = True)):
            os.remove(tmp_path)
            return False
    #___5___#
        os.remove(tmp_path)
        print(f"Пакет {pge_name} версии {pge_version} успешно загружен")
        return True
        
    def update_cache(self, mode="latest"): # latest (из list.xml), all (из full_list.xml)
        """
        Обновляет кэш
        mode="latest": скачивает все пакеты из list.xml(находится в репозитории)
        mode="all": скачивает все пакеты со всеми версиями из full_list.xml(находится в репозитории)
        """
        pges_list = list()
        list_url = ""
        tmp_path = ""
        if mode == "latest":
            list_url = f"{self.repository_url}/list"
            tmp_path = os.path.join(self.tmp_dir, "list.xml")
        elif modde == "all":
            list_url = f"{self.repository_url}/full_list"
            tmp_path = os.path.join(self.tmp_dir, "full_list.xml")
        else:
            print("Необходимо указать метод обновления: \"latest\" - для получения последних версий пакетов, \"all\" - для получения всех пакетов")
            return
        response = requests.get(list_url)
        if response.status_code == 200:
            with open(tmp_path, 'wb') as f:
                f.write(response.content) 
        else:
            print(f"Не удалось загрузить список по ссылке: {list_url}")
            return
        del response
        
        tree = ET.parse(tmp_path)
        root = tree.getroot()
        for package_elem in root.findall("package"):
            pge = []
            pge[0] = package_elem.find("name").text
            pge[1] = package_elem.find("version").text
            pges_list.append(pge)
            
        for name, version in pges_list:
            self.get_pge_from_repository(name, version)
    
    def remove_from_cache(self, pge_name:str, pge_version:str):
        """Удаляет пакет из кэша"""
        info = self.PM.get_package(pge_name, pge_version)
        if info is None:
            print(f"Пакет {pge_name}-{pge_version} не существует")
            return
        pge_path = os.path.join(self.cache_dir, f"{pge_name}-{pge_version}.pger")
        if os.remove(pge_path):
            print(f"Пакет {pge_name}-{pge_version} успешно удален из кэша")
            self.PM.update_package(pge_name, pge_version, in_cache = False)
        print(f"Не удалось удалить пакет {pge_name}-{pge_version}")
    
    def clear_cache():
        """Очищает кэш"""
        pges_list = self.PM.get_all_packages()
        for info in pges_list:
            self.remove_from_cache(info.name, info.version)
    
    def calculate_sha256(file_path):
        """Вычисляет SHA256 хеш файла"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()