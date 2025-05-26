if __name__ == '__main__':
    import os
    import sys
    import subprocess

    install_module_list = [
        'websockets',
        'numpy',
        'opencv-python',
        'opencv-contrib-python',
        'asyncio',
        'flask',
        'matplotlib',

        'wheel -U',
        'socket'
        'setuptools -U',
        'websocket-client',
        'pyaudio',
        'noisereduce',
    ]
    print('설치 될 module list')
    for i in install_module_list: print(f'\t- {i}')
    a = input('module 설치하시겠습니까? y/N:\t')

    if a.lower()=='y':
        print('설치 시작')
        process = subprocess.Popen(
            f"{sys.executable} -m pip install {' '.join(install_module_list)}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            if process.poll() is not None and not output:
                break
        for line in process.stderr:
            print(line.strip())
        print('설치 완료')
    else: print('설치 취소')
    input('Enter 를 눌러 종료')    
    sys.exit()