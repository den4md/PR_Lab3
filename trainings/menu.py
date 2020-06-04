import datetime
import os
import time
import traceback
import re
from getpass import getpass
from threading import Lock
from time import sleep
from msvcrt import getwch, kbhit
import cursor
import requests
from colorama import Fore, Style

from thread_pool import ThreadPool


# noinspection PyUnresolvedReferences
def refresh_proxie():
    global proxies
    print('Retrieving proxy')
    response = requests.get('https://sslproxies.org/')
    response_str = response.content.decode('utf-8').replace('\n', '')
    if (proxies is None) or (not (proxies['https'] in response_str)):
        a = re.findall('<table.*?id="proxylisttable".*?>.*?(<tr.*?>.*?<td>anonymous</td>)', response_str)[0]
        proxies = {'https': '', 'http': ''}
        b = re.split(r'<.*?td.*?>', a)
        proxies['https'] = proxies['http'] = b[-10] + ':' + b[-8]
        print('Proxy is refreshed', end='')
    else:
        print('Proxy is already fresh', end='')
    print(f' ({proxies["https"]})')


def clear():
    if is_anchor_changed:
        os.system("cls")
    else:
        for i in range(1, 26):
            print(f'\x1b[{i};1H', end=' ')


def print_menu():
    clear()
    global is_anchor_changed
    if not is_anchor_changed:
        print(f'\x1b[{active[0] + 1 - anchor[0]};1H{Fore.LIGHTGREEN_EX}>{Style.RESET_ALL}', end='',
              flush=True)
    else:
        is_anchor_changed = False
        minim = min(anchor[0] + 25, len(menu_str))
        for i in range(anchor[0], minim):
            if i == active[0]:
                print(f"{Fore.LIGHTGREEN_EX}>{Style.RESET_ALL} ", end='')
            else:
                print("  ", end='')

            if i == minim - 1:
                print(menu_str[i], end='', flush=True)
            else:
                print(menu_str[i])


def up(menu_len):
    global is_anchor_changed
    if active[0] > 0:
        active[0] -= 1
        if (active[0] == anchor[0]) and (active[0] != 0):
            anchor[0] -= 1
            is_anchor_changed = True
    else:
        active[0] = menu_len - 1
        anchor[0] = max(0, menu_len - 25)
        is_anchor_changed = True


def down(menu_len):
    global is_anchor_changed
    if active[0] < menu_len - 1:
        active[0] += 1
        if (active[0] == anchor[0] + 24) and (active[0] != menu_len - 1):
            anchor[0] += 1
            is_anchor_changed = True
    else:
        active[0] = 0
        anchor[0] = 0
        is_anchor_changed = True


def switch_smth(smth: list, num=0, init=None):
    smth[num] = not smth[num]
    if init is not None:
        init()
    return True


def wafflsegates(menu_list: list, menu_enables: list):
    len_ena = len(menu_enables)
    for i, e in enumerate(menu_list):
        if i >= len_ena:
            break
        menu_list[i] = (re.sub(r'(True)|(False)', str(menu_enables[i]), e[0]), e[1])
    global download_enables
    download_enables = menu_enables
    return True


def to_main_menu():
    init_main()
    init_menu()
    return True


def init_menu():
    active[0] = 0
    anchor[0] = 0


def download_concrete_page(href: str, lines: list):
    with download_lock:
        print(f"+ Downloading page ({href})\nTHREAD START")
    response = requests.get(href, proxies=proxies)
    a = response.content.decode('windows-1251')
    results = re.findall(r'(<td class="postslisttopic">(?:(?:.|\s)*?)</td>)', a)
    for result in results:
        lines.append(re.sub(r'[\r\n]', '', ''.join(re.split(r'<.*?>', result))))
    with download_lock:
        print(f"- Page ({href}) downloaded and Regex'ed\nTHREAD END")


def download():
    lines = ["Topics"]
    thread_pool = ThreadPool()
    d = False

    if enable_proxie[0]:
        refresh_proxie()

    filename = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S") + '.txt'
    for i, enable in enumerate(download_enables):
        if enable:
            thread_pool.give_task(download_concrete_page, args=(download_hrefs[i], lines))
            d = True

    thread_pool.join()
    if d:
        file = open(filename, 'w')
        file.write('\n'.join(lines))
        file.close()

        print(f'All chosen topics are saved to {filename}')
        to_main_menu()
    else:
        print("Nothing is chosen")
    input("Press <Enter> to continue")

    return True


download_lock = Lock()
download_hrefs = []
download_enables = []


def get_lambda(menu_enables, n):
    return lambda: switch_smth(smth=menu_enables, num=n, init=lambda: wafflsegates(menu, menu_enables))


def get_req():
    if enable_proxie[0]:
        refresh_proxie()

    print("Retrieving data from page")
    time.sleep(0.5)
    response = requests.get('https://www.sql.ru/forum', proxies=proxies)
    a = response.content.decode('windows-1251')
    print("Regex'ing data")
    time.sleep(0.5)
    result = re.findall(r'<a class="forumLink" href=".*">.*?</a>', a)

    menu.clear()

    # noinspection PyUnusedLocal
    menu_enables = [False for i in range(len(result))]
    global download_enables
    download_enables = menu_enables

    for i, element in enumerate(result):
        menu.append(
            (f'{Fore.LIGHTWHITE_EX}"' + re.split(r'<.*?>', element)[1][:63] + f'"{Style.RESET_ALL} (now = False)',
             get_lambda(menu_enables, i)))
        download_hrefs.append(re.split('"', element)[3])

    menu.append(("Download", download))
    menu.append(("Back", to_main_menu))

    init_menu()
    return True


def post_req():
    global sessionid
    if sessionid == '':
        sessionid = retrieve_sessionid()
        if sessionid == "":
            input("Auth error (maybe wrong credetials), press <Enter> to exit to main menu")
            to_main_menu()
            return True
        else:
            print('Session obtained successfully!')
            file = open('sessionid.txt', 'w+')
            file.write(sessionid)
            file.close()

    comments = input("Write description: ")

    data = {
        'email': "vlada061098@gmail.com",
        'hideemail': 'yes',
        'pass': '',
        'pass2': '',
        'm_url': '',
        'icq': '',
        'sex': 'e',
        'location': "",
        "occupation": '',
        'interests': '',
        "comment": comments,
        'signature': '',
        'm_photo': '',
        "hash": 100426168,
        'submit': ''
    }

    if enable_proxie[0]:
        refresh_proxie()

    response = requests.post(f"https://www.sql.ru/forum/profile.aspx?action=update",
                             cookies={"af_remember": sessionid}, data=data, proxies=proxies)
    response_str = response.content.decode('windows-1251')
    if 'Профиль успешно сохранен' in response_str:
        print('Успещно')
    else:
        print('Denied')
    input('Press <Enter> to exit to main menu')

    to_main_menu()
    return True


def retrieve_sessionid():
    print("Obtaning session")
    if os.path.exists('sessionid.txt'):
        file = open('sessionid.txt', 'r')
        result = file.read()
        file.close()
        return result
    else:
        print("No session found, need to auth")
        return auth()


def auth():
    login = input("login: ")
    password = getpass(prompt='password: ', stream=None)

    if enable_proxie[0]:
        refresh_proxie()

    response = requests.post(f'https://www.sql.ru/forum/login.aspx?login={login}&password={password}&cbremember=yes',
                             proxies=proxies)
    response_str = response.content.decode('windows-1251')
    if "Добро пожаловать в форум" in response_str:
        return response.cookies.get('af_remember')
    else:
        return ''


def head_req():
    if enable_proxie[0]:
        refresh_proxie()

    response = requests.head('https://www.sql.ru/forum', proxies=proxies)
    print("HEADERS")
    for k, v in response.headers.items():
        print(f"\t{k}: {v}")
    input('Press <Enter> to exit to main menu')

    return True


def options_req():
    if enable_proxie[0]:
        refresh_proxie()

    response = requests.options('https://www.sql.ru/forum', proxies=proxies)
    print("ALLOWED METHODS: ")
    print('\t' + str(response.headers['Allow']))
    input('Press <Enter> to exit to main menu')
    return True


def bye():
    print("Bye", end='', flush=True)
    for i in range(3):
        sleep(1)
        print(".", end='', flush=True)
    return False


sessionid = ''
enable_proxie = [False]  # mutable
proxies = None
menu = []
active = [0]  # mutable
anchor = [0]  # mutable
is_anchor_changed = True
menu_actions = []
menu_str = []


def get_str_from_menu(menu_list: list):
    a = []
    for i, w in enumerate(menu_list):
        a.append(w[0])
    return a


def get_action_from_menu(menu_list: list):
    a = []
    for i, w in enumerate(menu_list):
        a.append(w[1])
    return a


def init_main():
    global menu
    if not enable_proxie[0]:
        global proxies
        proxies = None
    menu = [
        (f"Enable proxie (now = {str(enable_proxie[0])})", lambda: switch_smth(smth=enable_proxie, init=init_main)),
        ("Get request", get_req),
        ("Post request", post_req),
        ("Head request", head_req),
        ("Options request", options_req),
        ("Exit", bye)
    ]


def go_loop():
    init_main()
    cursor.hide()
    global active
    global anchor
    global is_anchor_changed
    global menu_actions
    global menu_str
    looping = True

    while looping:
        menu_actions = get_action_from_menu(menu)
        menu_str = get_str_from_menu(menu)
        print_menu()
        while not kbhit():
            pass
        c = getwch().encode('utf8')
        if c in [b'\xc3\xa0', b'\x00']:
            c = getwch().encode('utf8')
            if c == b'H':
                up(len(menu))
            if c == b'P':
                down(len(menu))
        if c == b'\r':
            is_anchor_changed = True
            clear()
            looping = menu_actions[active[0]]()


if __name__ == "__main__":
    try:
        go_loop()

    except:
        traceback.print_exc()
        input()
