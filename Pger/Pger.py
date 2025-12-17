import os
import xml.etree.ElementTree as ET
from pgerInstaller import PgerInstaller
from сacheManager import CacheManager
from pgesManager import PgesManager
from contextlib import redirect_stdout
import socket
import io


class Pger():
    def __init__(self):
        tree, root = self.__read_config()
        self.INSTALL_DIR = root.findtext("install_dir")
        self.CACHE_DIR = root.findtext("cache_dir")
        self.REPOSITORY = root.findtext("repository")
        self.PM = PgesManager(cache_dir=self.CACHE_DIR)
        self.CM = CacheManager(cache_dir=self.CACHE_DIR, repository_url=self.REPOSITORY, PM=self.PM)
        self.PI = PgerInstaller(cache_dir=self.CACHE_DIR, install_dir=self.INSTALL_DIR, PM=self.PM)
        self.methods_to_execute = ['install', 'delete', 'clear_cache', 'update_cache', 'list']
        self.running = True
        
        self.socket_path = '/tmp/pger.sock'
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(1)

    def __read_config(self):
            config_path = "/etc/pger/config.xml"
            tree = ET.parse(config_path)
            root = tree.getroot()
            return tree, root
            
    def install(self, pge_name:str, pge_version:str):
        if not self.CM.get_pge_from_repository(pge_name, pge_version): return
        self.PI.install_package(pge_name, pge_version)
        return
    
    def delete(self, pge_name:str, pge_version:str, rm_from_cache = False):
        if not self.PI.delete_package(pge_name, pge_version):return
        if rm_from_cache:
            self.CM.remove_from_cache(pge_name, pge_version)
        return

    def clear_cache(self):
        self.CM.clear_cache()
        return
    
    def update_cache(self, mode = None):
        self.CM.update_cache(mode)
        return
        
    def list(self):
        print(self.PM.get_all_packages())
        return
        
    def run(self):
        while self.running:
            try:
                conn = self.sock.accept()[0]
                data = conn.recv(1024).decode('utf-8').strip()
                
                if data == 'stop':
                    self.running = False
                    response = "pger остановлен"
                    conn.send(response.encode('utf-8'))
                    conn.close()
                    break
                elif data.startswith('call_method:'):
                    parts = data[len('call_method:'):].split()
                    method_name = parts[0]
                    args = parts[1:]
                    
                    stdout_capture = io.StringIO()
                    try:
                        if method_name in self.methods_to_execute:
                            method = getattr(self, method_name)
                            method(*args)
                        response = stdout_capture.getvalue()
                    except AttributeError:
                        response = f"Ошибка: метод {method_name} не найден!"
                    except Exception as e:
                        response = f"Ошибка: {e}"
                    conn.send(response.encode('utf-8'))
                else:
                    response = "Неизвестная команда!"
                    conn.send(response.encode('utf-8'))
                
                conn.close()
            except Exception as e:
                if 'conn' in locals():
                    conn.close()
        self.sock.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)            