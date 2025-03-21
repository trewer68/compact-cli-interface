import curses
import os
import sys
import time
import subprocess
import ctypes
import sys
import win32gui
import win32process

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
if not is_admin():
    # Перезапуск с правами администратора
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    sys.exit()

def init_colors():
    # Инициализация цветов
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLACK)
    
    curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_GREEN)





def get_folders(directory):
    if os.path.isdir(directory):
        return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    return []

def display_selected(stdscr, selected):
    global var_hdd
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    result_text = f"Вы выбрали следующие папки:"
    stdscr.addstr(1, max(0, w // 2 - len(result_text) // 2), result_text, curses.color_pair(2))

    items_per_row = 3
    for i, folder in enumerate(selected):
        row = i // items_per_row
        col = (i % items_per_row) * (w // items_per_row)

        if row + 3 < h:
            stdscr.addstr(row + 3, col + 2, folder)

    if (var_hdd):
        stdscr.addstr(h - 4, 0, f"Простой", curses.color_pair(3))
    stdscr.addstr(h - 2, 0, "Нажмите 'R' для возврата или Enter для запуска.", curses.color_pair(8))
    stdscr.refresh()
    return stdscr.getch()

def display_logo(stdscr):
    logo = r"""
      mm                                                             .6*"    ,6*"*VA. 
      MM                                                           ,M'      dN     V8 
    mmMMmm  `7Mb,od8  .gP"Ya  `7M'    ,A    `MF' .gP"Ya  `7Mb,od8 ,Mbmmm.   `MN.  ,g9 
      MM      MM' "' ,M'   Yb   VA   ,VAA   ,V  ,M'   Yb   MM' "' 6M'  `Mb.  ,MMMMq.  
      MM      MM     8M ~~~~/    VA ,V  VA ,V   8M ~~~~/   MM     MI     M8 6P   `YMb 
      MM      MM     YM.    ,     VVV    VVV    YM.    ,   MM     WM.   ,M9 8b    `M9 
      `Mbmo .JMML.    `Mbmmd'      W      W      `Mbmmd' .JMML.    WMbmmd9  `MmmmmM9  
                                                                                     
    """
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(0)  # Отключаем курсор
    h, w = stdscr.getmaxyx()
    logo_lines = logo.splitlines()
    for i, line in enumerate(logo_lines):
        stdscr.addstr(h // 2 - len(logo_lines) // 2 + i, (w // 2) - len(line) // 2, line, curses.color_pair(1))
    stdscr.refresh()

    # Ждем 1 секунду
    time.sleep(1)

    stdscr.clear()  # Очищаем экран после логотипа
    curses.curs_set(1)  # Включаем курсор обратно

def menu(stdscr, folders, selected_folders, full_paths, base_path):
    global var_hdd
    global variable
    curses.curs_set(0)
    current_index = 0
    items_per_row = 3

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        c_f = 'True' if variable == "/F" else 'False' #костыль для вывода true/false в сжать принудительно
        
        title_folder = f'[{base_path}]'
        title = f"Выберите папки"
        faq1 = "{Пробел для выбора, Enter для подтверждения}"
        faq2 = "{'A' для выбора/отмены всех, Shift+Q Выход}"
        faq3 = f"['F' Сжать принудительно:{c_f}] ['D' Режим HDD:{var_hdd}]"
        stdscr.addstr(h - 5, 0, faq1, curses.color_pair(8))
        stdscr.addstr(h - 4, 0, faq2, curses.color_pair(8))
        stdscr.addstr(h - 3, 0, faq3, curses.color_pair(8))
        
        stdscr.addstr(1, max(0, w // 2 - len(title) // 2), title_folder, curses.color_pair(4))
        stdscr.addstr(2, max(0, w // 2 - len(title) // 2), title, curses.color_pair(2))

        for idx, folder in enumerate(folders):
            row = idx // items_per_row
            col = (idx % items_per_row) * (w // items_per_row)
            
            if row + 4 >= h - 1:
                break
            
            checkbox = "[x]" if selected_folders[idx] else "[ ]"
            display_folder = os.path.join(base_path, folder) if full_paths else folder
            
            if idx == current_index:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(row + 4, col + 2, checkbox + " " + display_folder)
            if idx == current_index:
                stdscr.attroff(curses.A_REVERSE)
        
        key = stdscr.getch()
        
        if key == curses.KEY_LEFT and current_index % items_per_row > 0:
            current_index -= 1
        elif key == curses.KEY_RIGHT and current_index % items_per_row < items_per_row - 1 and current_index < len(folders) - 1:
            current_index += 1
        elif key == curses.KEY_UP and current_index >= items_per_row:
            current_index -= items_per_row
        elif key == curses.KEY_DOWN and current_index < len(folders) - items_per_row:
            current_index += items_per_row
        elif key in [ord(' '), ord('x'), ord('X'), ord('ч'), ord('Ч')]:  # Space or 'x' to toggle selection
            selected_folders[current_index] = not selected_folders[current_index]
        elif key in [ord('a'), ord('A'), ord('ф'), ord('Ф')]:  # 'A' to select or deselect all
            if any(selected_folders):  # Если хотя бы одна выбрана, отменяем все
                selected_folders = [False] * len(folders)
            else:  # Иначе выбираем все
                selected_folders = [True] * len(folders)
        elif key in [ord('Q'), ord('Й')]:  # 'r' для возврата
            sys.exit()
        elif key in [ord('r'), ord('R'), ord('к'), ord('К')]:  # 'r' для возврата
            return  # Возвращаемся к выбору папок
        elif key in [ord('f'), ord('F'), ord('а'), ord('А')]:  # ПРинудительное сжатие
            if (variable == ""):
                variable = "/F" 
            else:
                variable = ""
        elif key in [ord('d'), ord('D'), ord('в'), ord('В')]:  # ПРинудительное сжатие
            if (var_hdd == False):
                var_hdd = True
            else:
                var_hdd = False
        elif key == 10:  # Enter key
            if any(selected_folders):
                break
            else:
                stdscr.addstr(h - 2, 0, "Ничего не выбрано. Нажмите любую клавишу, чтобы продолжить...", curses.color_pair(1))
                stdscr.refresh()
                stdscr.getch()

    selected = [folder for idx, folder in enumerate(folders) if selected_folders[idx]]

    # Переходим на экран с выбранными папками
    return selected

def print_help():
    help_text = """
    Доступные флаги:
    -p <path>  : Указать путь к директории.
    -a         : Выбрать все папки.
    -z         : Выводить полные пути к папкам.
    -f <value> : Пережать принудительно.
    -l         : Отключить показ логотипа.
    -h, -help  : Вывести это сообщение и завершить скрипт.
    """
    print(help_text)

def main(stdscr):
    global variable
    global var_hdd
    init_colors()
    try:
        os.remove("compact.log.txt")
    except: pass
    # Проверка на наличие флагов помощи
    if '-h' in sys.argv or '-help' in sys.argv:
        print_help()
        sys.exit(0)

    display_logo_enabled = '-l' not in sys.argv  # Флаг для отключения логотипа
    if display_logo_enabled:
        display_logo(stdscr)  # Показ логотипа перед началом

    stdscr.clear()

    # Инициализация переменной f с значением по умолчанию
    variable = ""
    var_hdd = False
    
    # Проверка аргументов командной строки на наличие -f
    var_hdd = True if '-hdd' in sys.argv else False
    variable = "/F" if '-f' in sys.argv else ""
    # if '-f' in sys.argv:
    #     w_index = sys.argv.index('-f') + 1
    #     if w_index < len(sys.argv):
    #         variable = sys.argv[w_index]

    # Проверка аргументов командной строки на наличие -p
    path = ""
    while True:
        if '-p' in sys.argv:
            path_index = sys.argv.index('-p') + 1
            if path_index < len(sys.argv):
                path = sys.argv[path_index]
            else:
                stdscr.clear()
                stdscr.addstr(0, 0, "Путь не указан. Введите путь к директории без \"\": ", curses.color_pair(8))
                stdscr.refresh()
                curses.echo()
                path = stdscr.getstr(1, 0).decode('utf-8').strip()
        else:
            stdscr.clear()
            stdscr.addstr(0, 0, "Путь не указан. Введите путь к директории без \"\": ", curses.color_pair(8))
            stdscr.refresh()
            curses.echo()
            path = stdscr.getstr(1, 0).decode('utf-8').strip()

        folders = get_folders(path)
        
        if folders:
            break  # Если папки найдены, выходим из цикла
        else:
            stdscr.clear()  # Очищаем экран сразу
            # Больше нет сообщения, сразу продолжаем ввод
            stdscr.addstr(0, 0, "Попробуйте еще раз. Введите путь к директории: ", curses.color_pair(1))
            stdscr.refresh()

    ############ Добавляем папку пути в начало списка
    # folders.insert(0, path)

    select_all = '-a' in sys.argv
    full_paths = '-z' in sys.argv  # Флаг для вывода полных путей

    selected_folders = [select_all] * len(folders) if select_all else [False] * len(folders)
    
    while True:
        selected = menu(stdscr, folders, selected_folders, full_paths, path)
        
        
        # display_selected(stdscr, selected).stdscr.addstr(-10, 0, "Путь не указан. Введите путь к директории без \"\": ")
        if selected:
            # После открытия папок остаемся на экране с открытыми папками
            while True:
                size_sum = 0
                h, w = stdscr.getmaxyx()
                result_key = display_selected(stdscr, selected)
                if result_key in [ord('r'), ord('R'), ord('к'), ord('К')]:
                    break  # Возвращаемся к выбору папок
                if result_key == 10:  # Enter key
                    counter = 0
                    for folder in selected:
                        # Определяем полный путь
                        full_path = os.path.join(path, folder) if folder != path else folder
                        size = get_folder_size(full_path) # определяем размер папки ДО процесса компакта
                        #debug
                        #subprocess.Popen(f'cmd /c start \"\" /min cmd /k \" title {full_path} & CHCP 1251 & echo \"{full_path}\" & echo {variable} & timeout -t 9999 & compact /C /S:\"{full_path}\" /A {variable} /I /EXE:LZX & exit \"', creationflags=subprocess.CREATE_NEW_CONSOLE,)  # Открываем проводник Windows с выбранными папками
                        #main
                        subprocess.Popen(f'cmd /c start \"\" /min cmd /k \" title {full_path} & CHCP 1251 & compact /C /S:\"{full_path}\" /A {variable} /I /EXE:LZX & exit\"', creationflags=subprocess.CREATE_NEW_CONSOLE,)  # Открываем проводник Windows с выбранными папками
                        
                        # subprocess.Popen(f'cmd /c start \"\" cmd /k \" title {full_path} & CHCP 1251 & timeout -t 9999\"', creationflags=subprocess.CREATE_NEW_CONSOLE,)  # Открываем проводник Windows с выбранными папками
                        # if (True): #debug
                        
                        if (var_hdd): 
                            size_sum = round(size + size_sum, 3)
                            stdscr.move(h - 4, 0) 
                            stdscr.clrtoeol() #стираем строку
                            stdscr.addstr(h - 4, 0, f"Осталось: {len(selected)-counter} [{full_path}] [{size}|{size_sum}]", curses.color_pair(1))
                            stdscr.refresh()
                            
                            time.sleep(3) #ожидаем пока запустится окно с компактом
                            pids = get_pid_by_partial_window_name(f"{full_path}") #берем его айдишник
                            while pids: #трекаем раз в секунду это окно и если его нет запускаем следующую папку
                                time.sleep(1)
                                pids = get_pid_by_partial_window_name(f"{full_path}")
                            counter=counter+1
                            write_file(full_path)
                
                            # stdscr.getch()  # Ожидаем нажатия клавиши перед возвращением к выбору


def get_folder_size(path='.'):
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return round(total_size / (1024 ** 3), 3)  
    except: return 0

def write_file(text):
    try:
        with open("compact.log.txt", "a") as file:
            file.write(text+"\n")
    except: pass

def get_pid_by_partial_window_name(partial_window_name):
    def callback(hwnd, pids):
        # Получаем заголовок окна
        window_text = win32gui.GetWindowText(hwnd)
        if partial_window_name in window_text:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pids.append(pid)

    pids = []
    win32gui.EnumWindows(callback, pids)
    return pids


curses.wrapper(main)
