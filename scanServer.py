import subprocess
import re

def get_wifi_connected_devices_arp():
    """현재 Wi-Fi 네트워크에 연결된 기기들의 IP 주소를 ARP 테이블에서 가져옵니다."""
    ip_list = set()
    try:
        # Windows
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
        output = result.stdout
        for line in output.splitlines():
            match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if match:
                ip = match.group(1)
                if ip != '255.255.255.255' and not ip.startswith('224.'):
                    ip_list.add(ip)
    except FileNotFoundError:
        # Linux/macOS
        try:
            result = subprocess.run(['arp', '-n'], capture_output=True, text=True, check=True)
            output = result.stdout
            for line in output.splitlines():
                parts = line.split()
                if len(parts) > 1 and re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parts[0]):
                    ip = parts[0]
                    ip_list.add(ip)
        except FileNotFoundError:
            print("arp 명령어를 찾을 수 없습니다.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        return None
    return list(ip_list)

if __name__ == "__main__":
    devices = get_wifi_connected_devices_arp()
    if devices:
        print("현재 Wi-Fi 네트워크에 연결된 기기 (ARP 테이블 기반):")
        for ip in devices:
            print(ip)
    else:
        print("Wi-Fi에 연결된 기기를 찾을 수 없습니다.")