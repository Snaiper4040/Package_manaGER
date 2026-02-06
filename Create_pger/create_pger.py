import os
import tarfile
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
from typing import List, Optional
import manifest

def calculate_sha256(file_path):
    """Вычисляет SHA256 хеш файла"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_user_input(info, default=None, required=True):
    """Получает ввод от пользователя с обработкой значений по умолчанию"""
    if default:
        info = f"{info} [{default}]: "
    else:
        info = f"{info}: "
    
    value = None
    while not value:
        value = input(info).strip()
        if not value and default:
            return default
        elif not value and required:
            print("Это поле обязательно для заполнения!")
        else:
            return value

def get_list_input(info, default=None, separator=','):
    """Получает список значений от пользователя"""
    if default:
        info = f"{info} [{default}] (разделитель '{separator}'): "
    else:
        info = f"{info} (разделитель '{separator}'): "
    value = input(info).strip()
    if not value and default:
        return [item.strip() for item in default.split(separator) if item.strip()]
    elif not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]

def create_manifest_interactive(package_name):
    """Интерактивное создание манифеста"""
    print(f"\n=== Создание манифеста для пакета '{package_name}' ===")
    
    version = get_user_input("Версия пакета", "1.0.0")
    dependencies = get_list_input("Зависимости (через запятую)")
    supported_os = get_list_input("Поддерживаемые ОС", default="linux")
    supported_arch = get_list_input("Поддерживаемые архитектуры", default="x86_64")
    builder = get_user_input("Сборщик", required=False)
    
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return manifest.Manifest(
        name=package_name,
        version=version,
        creation_date=creation_date,
        sha256="",  # Будет заполнен после создания архива
        dependencies=dependencies,
        supported_os=supported_os,
        supported_arch=supported_arch,
        builder=builder
    )

def ensure_xml_files_exist():
    """Создает пустые XML файлы, если они не существуют"""
    # list.xml - список последних версий пакетов
    if not os.path.exists("/repository/list.xml"):
        root = ET.Element("packages")
        tree = ET.ElementTree(root)
        tree.write("/repository/list.xml", encoding="utf-8", xml_declaration=True)
        print("Создан пустой list.xml")
    
    # full_list.xml - полный список всех версий пакетов
    if not os.path.exists("/repository/full_list.xml"):
        root = ET.Element("packages")
        tree = ET.ElementTree(root)
        tree.write("/repository/full_list.xml", encoding="utf-8", xml_declaration=True)
        print("Создан пустой full_list.xml")

def update_list_xml(manifest):
    """Обновляет list.xml (только последние версии)"""
    try:
        tree = ET.parse("/repository/list.xml")
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        root = ET.Element("packages")
        tree = ET.ElementTree(root)
    
    # Удаляем старую версию этого пакета, если существует
    for package_elem in root.findall("package"):
        if package_elem.find("name").text == manifest.name:
            root.remove(package_elem)
            break
    
    # Добавляем новую запись
    package_elem = ET.SubElement(root, "package")
    ET.SubElement(package_elem, "name").text = manifest.name
    ET.SubElement(package_elem, "version").text = manifest.version
    ET.SubElement(package_elem, "creation_date").text = manifest.creation_date
    
    # Добавляем зависимости
    deps_elem = ET.SubElement(package_elem, "dependencies")
    for dep in manifest.dependencies:
        ET.SubElement(deps_elem, "dependency").text = dep
    
    tree.write("/repository/list.xml", encoding="utf-8", xml_declaration=True)
    print("Обновлен list.xml")

def update_full_list_xml(manifest):
    """Обновляет full_list.xml (все версии)"""
    try:
        tree = ET.parse("/repository/full_list.xml")
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        root = ET.Element("packages")
        tree = ET.ElementTree(root)
    
    # Проверяем, нет ли уже такой версии
    package_id = f"{manifest.name}-{manifest.version}"
    for package_elem in root.findall("package"):
        if package_elem.get("id") == package_id:
            root.remove(package_elem)
            break
    
    # Добавляем новую запись
    package_elem = ET.SubElement(root, "package")
    package_elem.set("id", package_id)
    ET.SubElement(package_elem, "name").text = manifest.name
    ET.SubElement(package_elem, "version").text = manifest.version
    ET.SubElement(package_elem, "creation_date").text = manifest.creation_date
    ET.SubElement(package_elem, "sha256").text = manifest.sha256
    
    # Добавляем зависимости
    deps_elem = ET.SubElement(package_elem, "dependencies")
    for dep in manifest.dependencies:
        ET.SubElement(deps_elem, "dependency").text = dep
    
    # Добавляем поддерживаемые ОС и архитектуры
    os_elem = ET.SubElement(package_elem, "supported_os")
    for os_name in manifest.supported_os:
        ET.SubElement(os_elem, "os").text = os_name
    
    arch_elem = ET.SubElement(package_elem, "supported_arch")
    for arch_name in manifest.supported_arch:
        ET.SubElement(arch_elem, "arch").text = arch_name
    
    if manifest.builder:
        ET.SubElement(package_elem, "builder").text = manifest.builder
    
    tree.write("/repository/full_list.xml", encoding="utf-8", xml_declaration=True)
    print("Обновлен full_list.xml")

def create_pger_package(folder_path, output_name):
    """Создает пакет в формате .pger с манифестом"""
    # Пути к директориям
    repository_dir = "/repository"
    packages_dir = os.path.join(repository_dir, "packages")
    
    # Создаем директории, если не существуют
    os.makedirs(packages_dir, exist_ok=True)
    os.makedirs(repository_dir, exist_ok=True)
    
    # Проверяем существование XML файлов
    ensure_xml_files_exist()
    
    # Создаем манифест
    manifest = create_manifest_interactive(output_name)
    
    # Полный путь к выходному файлу
    pger_path = os.path.join(packages_dir, f"{output_name}-{manifest.version}.pger")
    
    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не найдена.")
        return False
    
    # Создаем tar.gz архив
    try:
        with tarfile.open(pger_path, 'w:gz') as pger_tar:
            # Добавляем содержимое папки
            pger_tar.add(folder_path, arcname=os.path.basename(folder_path))
            
            # Создаем временный файл манифеста
            manifest_file = os.path.join("/tmp", "manifest.xml")
            manifest.to_xml(manifest_file)
            
            # Добавляем манифест в архив
            pger_tar.add(manifest_file, arcname="manifest.xml")
            
            # Удаляем временный файл
            os.remove(manifest_file)
        
        # Вычисляем SHA256 и обновляем манифест
        manifest.sha256 = calculate_sha256(pger_path)
        
        # Обновляем XML списки
        update_list_xml(manifest)
        update_full_list_xml(manifest)
        
        print(f"Пакет успешно создан: {pger_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании пакета: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python create_pger_2.py <путь_к_папке> <имя_пакета>")
        print("Пример: python create_pger_2.py ./myapp myapp-package")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    output_name = sys.argv[2]
    
    if create_pger_package(folder_path, output_name):
        print("\nПакет успешно создан и добавлен в репозиторий!")
    else:
        print("\nОшибка при создании пакета!")
        sys.exit(1)