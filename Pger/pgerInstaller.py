import os
from pgesManager import PgesManager
import tarfile
import shutil

class PgerInstaller:
    def __init__(self, cache_dir: str, install_dir: str, PM):
        self.cache_dir = cache_dir
        self.install_dir = install_dir
        self.tmp_dir = os.path.join(cache_dir, "tmp\\")
        self.PM = PM
        
    def open_pger(self, pge_name:str, pge_version:str):
        """Распаковывает пакет и сохранеет его в tmp"""
        tmp_path = os.path.join(tmp_dir, f"{pge_name}-{pge_version}")
        try:
            with tarfile.open(pger_path, 'w:gz') as pger_tar:
                pger_tar.extractall(tmp_dir)
            
        except Exception as e:
            print(f"Ошибка при открытии пакета: {e}")
            return False
        return true
        
    
    def install_package(self, pge_name:str, pge_version:str):
        """Устанавоивает пакет"""
        install_path = os.path.join(install_dir, f"{pge_name}-{pge_version}")
        tmp_path = os.path.join(tmp_dir, f"{pge_name}-{pge_version}")
        if self.open_pger(pge_name, pge_version):
            print("Пакет успешно распакован в tmp")
        else:
            shutil.rmtree(tmp_path, ignore_errors=True)
            return False
        try:
            shutil.copytree(tmp_path, install_path)
        except Exception as e:
            print(f"Ошибка при копировании в целевую директорию: {e}")
            shutil.rmtree(tmp_path, ignore_errors=True)
            return False
        PM.update_package(pge_name=pge_name, pge_version=pge_version, installed=True)
        shutil.rmtree(tmp_path, ignore_errors=True)
        print(f"{pge_name} успешно установлен в {install_path}")
        return True
        
    def delete_package(self, pge_name:str, pge_version:str):
        """Удаляет пакет"""
        install_path = os.path.join(install_dir, f"{pge_name}-{pge_version}")
        if os.path.exists(install_path):
            shutil.rmtree(tmp_path, ignore_errors=True)
            print(f"{pge_name} успешно удален.")
            PM.update_package(pge_name=pge_name, pge_version=pge_version, installed=False)
            return True
        print(f"Не удалось удалить  {pge_name}")
        return False