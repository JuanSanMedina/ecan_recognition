import socket
hostname = socket.gethostname()
if hostname == 'CUSP-raspberrypi':
    import upload_functions as uf


if __name__ == '__main__':
    uf.get_preview(url = 'http://128.122.72.105:8000')
