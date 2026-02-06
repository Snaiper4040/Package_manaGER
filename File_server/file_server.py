from flask import Flask, send_file
import os
import get_sha256

app = Flask(__name__)

PACKAGES_DIR = "/repository/packages/"
LIST = "/repository/list.xml"
FULL_LIST = "/repository/full_list.xml"
PORT = 8080

@app.route('/download/<package_name>')
def send_package(package_name):
    """Отправка пакета по имени"""
    package_path = os.path.join(PACKAGES_DIR, package_name)
    
    if not os.path.exists(package_path):
        return "Package not found", 404
    
    return send_file(
        package_path,
        as_attachment=True,
        download_name=package_name
    )

@app.route('/download/sha256/<package_name>')
def send_sha256(package_name):
    """Отправка хэш-суммы пакета"""
    if not os.path.exists(FULL_LIST):
        return "Full list not found", 404
    sha256 = get_sha256.get(FULL_LIST, package_name)
    if (sha256 == -1):
        return "Can not find sha256 for package", 404
    return sha256

@app.route('/list')
def send_list():
    """Отправка списка пакетов"""
    if not os.path.exists(LIST):
        return "List not found", 404
    
    return send_file(
        LIST,
        as_attachment=True,
        download_name="list.xml"
    )
    
@app.route('/full_list')
def send_full_list():
    """Отправка списка всех версий пакетов"""
    if not os.path.exists(FULL_LIST):
        return "Full list not found", 404
    
    return send_file(
        FULL_LIST,
        as_attachment=True,
        download_name="full_list.xml"
    )

if __name__ == '__main__':
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    
    print(f"Starting simple file server on port {PORT}")
    print(f"Packages directory: {PACKAGES_DIR}")
    print("Usage: http://server-ip:8080/download/package-name.pger")
    print("Get list: http://server-ip:8080/list")
    print("Get full list: http://server-ip:8080/full_list")
    
    app.run(host='0.0.0.0', port=PORT)