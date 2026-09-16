import sys
import os
import shutil
import tempfile
import subprocess
import ctypes
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QGroupBox, QCheckBox, QPushButton, QTextEdit, QLabel,
    QProgressBar, QSpinBox, QMessageBox, QToolTip, QFileDialog, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QComboBox, QSplitter, QFrame,
    QMenu, QAction, QSystemTrayIcon
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPoint
)
from PyQt5.QtGui import (
    QFont, QColor, QLinearGradient, QBrush, QCursor, QPainter, QPen
)
import psutil


# ========== توابع کمکی ==========
def format_bytes(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def delete_folder_contents(folder):
    freed = 0
    if not os.path.exists(folder):
        return 0
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            try:
                path = os.path.join(root, name)
                freed += os.path.getsize(path)
                os.remove(path)
            except:
                pass
        for name in dirs:
            try:
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
            except:
                pass
    return freed


# ========== Thread پاکسازی ==========
class CleanupWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks

    def run(self):
        try:
            selected = [k for k, v in self.tasks.items() if v]
            if not selected:
                self.log_signal.emit("⚠️ هیچ وظیفه‌ای انتخاب نشده.")
                self.finished_signal.emit(False, "هیچ عملی انجام نشد.")
                return

            total = len(selected)
            done = 0
            total_freed = 0

            if self.tasks.get('temp', False):
                self.log_signal.emit("🗑️ حذف فایل‌های موقت...")
                freed = self._clean_temp()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('recycle', False):
                self.log_signal.emit("♻️ خالی کردن سطل زباله...")
                self._empty_recycle_bin()
                self.log_signal.emit("   ✅ انجام شد.")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('chrome', False):
                self.log_signal.emit("🌐 پاک کردن کش Chrome...")
                freed = self._clean_browser_cache('Chrome')
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('edge', False):
                self.log_signal.emit("🌐 پاک کردن کش Edge...")
                freed = self._clean_browser_cache('Edge')
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('firefox', False):
                self.log_signal.emit("🦊 پاک کردن کش Firefox...")
                freed = self._clean_browser_cache('Firefox')
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('opera', False):
                self.log_signal.emit("🎭 پاک کردن کش Opera...")
                freed = self._clean_browser_cache('Opera')
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('prefetch', False):
                self.log_signal.emit("⚙️ حذف فایل‌های Prefetch...")
                freed = self._clean_prefetch()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('windows_update', False):
                self.log_signal.emit("🔄 حذف کش آپدیت ویندوز...")
                freed = self._clean_windows_update()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('memory_dump', False):
                self.log_signal.emit("💀 حذف فایل‌های Memory Dump...")
                freed = self._clean_memory_dumps()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('logs', False):
                self.log_signal.emit("📜 حذف فایل‌های Log سیستمی...")
                freed = self._clean_logs()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('installer_temp', False):
                self.log_signal.emit("📦 حذف فایل‌های موقت نصب...")
                freed = self._clean_installer_temp()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('dns_cache', False):
                self.log_signal.emit("🌍 پاک کردن کش DNS...")
                self._flush_dns()
                self.log_signal.emit("   ✅ انجام شد.")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('chromium_extra', False):
                self.log_signal.emit("🧩 پاک کردن کش مرورگرهای Chromium...")
                freed = self._clean_extra_chromium()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('recent_docs', False):
                self.log_signal.emit("📁 پاک کردن لیست اسناد اخیر...")
                self._clear_recent_docs()
                self.log_signal.emit("   ✅ انجام شد.")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            if self.tasks.get('thumbnails', False):
                self.log_signal.emit("🖼️ حذف Thumbnails...")
                freed = self._clean_thumbnails()
                total_freed += freed
                self.log_signal.emit(f"   ✅ آزاد شد: {format_bytes(freed)}")
                done += 1
                self.progress_signal.emit(int(done / total * 100))

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, f"✅ پاکسازی کامل شد. مجموع فضای آزاد شده: {format_bytes(total_freed)}")
        except Exception as e:
            self.log_signal.emit(f"❌ خطای کلی: {str(e)}")
            self.finished_signal.emit(False, f"خطا: {str(e)}")

    # ---- عملیات حذف ----
    def _clean_temp(self):
        freed = delete_folder_contents(tempfile.gettempdir())
        sys_temp = os.environ.get('SystemRoot', 'C:\\Windows') + '\\Temp'
        if os.path.exists(sys_temp):
            freed += delete_folder_contents(sys_temp)
        return freed

    def _empty_recycle_bin(self):
        try:
            subprocess.run(["powershell.exe", "-Command", "Clear-RecycleBin -Force"], capture_output=True, timeout=30)
        except:
            for part in psutil.disk_partitions():
                if 'fixed' in part.opts.lower():
                    rec = os.path.join(part.mountpoint, '$Recycle.Bin')
                    if os.path.exists(rec):
                        shutil.rmtree(rec, ignore_errors=True)

    def _clean_browser_cache(self, browser):
        freed = 0
        local = os.environ.get('LOCALAPPDATA', '')
        roaming = os.environ.get('APPDATA', '')
        paths = []
        if browser == 'Chrome':
            paths = [
                os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache')
            ]
        elif browser == 'Edge':
            paths = [
                os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache')
            ]
        elif browser == 'Firefox':
            profiles = os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(profiles):
                for profile in os.listdir(profiles):
                    cache_path = os.path.join(profiles, profile, 'cache2')
                    if os.path.exists(cache_path):
                        freed += delete_folder_contents(cache_path)
                    startup = os.path.join(profiles, profile, 'startupCache')
                    if os.path.exists(startup):
                        freed += delete_folder_contents(startup)
            return freed
        elif browser == 'Opera':
            paths = [
                os.path.join(roaming, 'Opera Software', 'Opera Stable', 'Cache'),
                os.path.join(roaming, 'Opera Software', 'Opera Stable', 'Code Cache')
            ]
        for p in paths:
            if os.path.exists(p):
                freed += delete_folder_contents(p)
        return freed

    def _clean_prefetch(self):
        pf = os.environ.get('SystemRoot', 'C:\\Windows') + '\\Prefetch'
        freed = 0
        if os.path.exists(pf):
            for f in os.listdir(pf):
                if f.lower().endswith('.pf'):
                    try:
                        p = os.path.join(pf, f)
                        freed += os.path.getsize(p)
                        os.remove(p)
                    except:
                        pass
        return freed

    def _clean_windows_update(self):
        dist = os.environ.get('SystemRoot', 'C:\\Windows') + '\\SoftwareDistribution\\Download'
        return delete_folder_contents(dist)

    def _clean_memory_dumps(self):
        freed = 0
        sys_root = os.environ.get('SystemRoot', 'C:\\Windows')
        mem_dump = os.path.join(sys_root, 'MEMORY.DMP')
        if os.path.isfile(mem_dump):
            try:
                freed += os.path.getsize(mem_dump)
                os.remove(mem_dump)
            except:
                pass
        minidump = os.path.join(sys_root, 'Minidump')
        if os.path.isdir(minidump):
            freed += delete_folder_contents(minidump)
        return freed

    def _clean_logs(self):
        freed = 0
        log_dirs = [
            os.environ.get('SystemRoot', 'C:\\Windows') + '\\Logs',
            os.environ.get('SystemRoot', 'C:\\Windows') + '\\Debug'
        ]
        for d in log_dirs:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for file in files:
                        if file.endswith(('.log', '.etl', '.old', '.tmp')):
                            try:
                                path = os.path.join(root, file)
                                freed += os.path.getsize(path)
                                os.remove(path)
                            except:
                                pass
        return freed

    def _clean_installer_temp(self):
        installer = os.environ.get('SystemRoot', 'C:\\Windows') + '\\Installer'
        freed = 0
        if os.path.exists(installer):
            for f in os.listdir(installer):
                if f.lower().endswith('.tmp'):
                    try:
                        p = os.path.join(installer, f)
                        freed += os.path.getsize(p)
                        os.remove(p)
                    except:
                        pass
        return freed

    def _flush_dns(self):
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=10)
        except:
            pass

    def _clean_extra_chromium(self):
        local = os.environ.get('LOCALAPPDATA', '')
        freed = 0
        for br in ['BraveSoftware', 'Vivaldi']:
            base = os.path.join(local, br)
            if os.path.exists(base):
                for root, _, _ in os.walk(base):
                    if 'Cache' in root or 'Code Cache' in root:
                        freed += delete_folder_contents(root)
        return freed

    def _clear_recent_docs(self):
        recent = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Recent')
        if os.path.exists(recent):
            delete_folder_contents(recent)

    def _clean_thumbnails(self):
        thumb_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Explorer')
        freed = 0
        if os.path.exists(thumb_path):
            for f in os.listdir(thumb_path):
                if 'thumbcache' in f.lower():
                    try:
                        p = os.path.join(thumb_path, f)
                        freed += os.path.getsize(p)
                        os.remove(p)
                    except:
                        pass
        return freed


# ========== ویجت نمودار دایره‌ای ==========
class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.used = 0
        self.free = 0
        self.setMinimumSize(150, 150)

    def set_data(self, used, free):
        self.used = used
        self.free = free
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(5, 5, -5, -5)
        total = self.used + self.free
        if total == 0:
            return
        used_angle = int(360 * (self.used / total))
        painter.setBrush(QBrush(QColor(239, 68, 68)))  # red used
        painter.drawPie(rect, 0, used_angle * 16)
        painter.setBrush(QBrush(QColor(34, 197, 94)))  # green free
        painter.drawPie(rect, used_angle * 16, (360 - used_angle) * 16)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        percent = (self.used / total) * 100
        painter.drawText(rect, Qt.AlignCenter, f"{percent:.1f}%")


# ========== دکمه شناور ==========
class AdvancedFloatingButton(QWidget):
    auto_toggled = pyqtSignal(bool)
    manual_clean = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(120, 120)

        self.auto_mode = False
        self.drag_pos = None

        self.btn = QPushButton(self)
        self.btn.setGeometry(5, 5, 110, 110)
        self.btn.setObjectName("floatBtn")
        self.btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn.setToolTip("کلیک چپ: پاکسازی دستی\nکلیک راست: منوی تنظیمات")
        self.btn.clicked.connect(self.on_left_click)
        self.btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn.customContextMenuRequested.connect(self.show_menu)

        self.btn.setStyleSheet("""
            QPushButton#floatBtn {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #3b82f6, stop:1 #1e3a8a);
                color: white;
                border-radius: 55px;
                font: bold 24px 'Segoe UI';
                border: 3px solid #facc15;
            }
            QPushButton#floatBtn:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #2563eb, stop:1 #1e40af);
                border: 3px solid #fbbf24;
            }
        """)
        self.update_percent_text()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_percent_text)
        self.timer.start(3000)

    def update_percent_text(self):
        try:
            usage = psutil.disk_usage('C:\\')
            percent = int((usage.free / usage.total) * 100)
            self.btn.setText(f"{percent}%")
            tooltip = f"فضای آزاد: {format_bytes(usage.free)}\nحالت خودکار: {'فعال' if self.auto_mode else 'غیرفعال'}"
            self.btn.setToolTip(tooltip)
        except:
            self.btn.setText("?%")

    def on_left_click(self):
        self.manual_clean.emit()

    def show_menu(self, pos):
        menu = QMenu()
        act_auto = QAction(f"🔁 حالت خودکار: {'فعال' if self.auto_mode else 'غیرفعال'}", self)
        act_auto.triggered.connect(self.toggle_auto)
        menu.addAction(act_auto)
        act_hide = QAction("👁️ مخفی کردن دکمه شناور", self)
        act_hide.triggered.connect(self.hide)
        menu.addAction(act_hide)
        menu.exec_(self.btn.mapToGlobal(pos))

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        self.auto_toggled.emit(self.auto_mode)
        self.update_percent_text()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


# ========== تب مدیریت دیسک ==========
class DiskManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        drives_group = QGroupBox("💽 اطلاعات پارتیشن‌ها")
        drives_layout = QVBoxLayout()
        self.drives_tree = QTreeWidget()
        self.drives_tree.setHeaderLabels(["درایو", "برچسب", "فایل سیستم", "فضای کل", "فضای آزاد", "درصد استفاده", "وضعیت"])
        self.drives_tree.setAlternatingRowColors(True)
        drives_layout.addWidget(self.drives_tree)
        drives_group.setLayout(drives_layout)
        layout.addWidget(drives_group)

        details_group = QGroupBox("📊 جزئیات درایو انتخاب شده")
        details_layout = QHBoxLayout()
        self.pie_chart = PieChartWidget()
        self.pie_chart.setFixedSize(180, 180)
        self.drive_info_label = QLabel("روی یک درایو کلیک کنید")
        self.drive_info_label.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(self.pie_chart)
        details_layout.addWidget(self.drive_info_label, 1)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        tools_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 به‌روزرسانی")
        btn_refresh.clicked.connect(self.refresh_drives)
        btn_disk_mgmt = QPushButton("💿 باز کردن Disk Management")
        btn_disk_mgmt.clicked.connect(self.open_disk_mgmt)
        tools_layout.addWidget(btn_refresh)
        tools_layout.addWidget(btn_disk_mgmt)
        layout.addLayout(tools_layout)

        self.refresh_drives()
        self.drives_tree.itemClicked.connect(self.on_drive_clicked)

    def refresh_drives(self):
        self.drives_tree.clear()
        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or part.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total = format_bytes(usage.total)
                free = format_bytes(usage.free)
                used_percent = usage.percent
                status = "✅ سالم" if used_percent < 90 else "⚠️ تقریبا پر"
                item = QTreeWidgetItem([
                    part.mountpoint, part.device, part.fstype,
                    total, free, f"{used_percent}%", status
                ])
                self.drives_tree.addTopLevelItem(item)
            except:
                continue
        for i in range(self.drives_tree.columnCount()):
            self.drives_tree.resizeColumnToContents(i)

    def on_drive_clicked(self, item, col):
        drive = item.text(0)
        try:
            usage = psutil.disk_usage(drive)
            self.pie_chart.set_data(usage.used, usage.free)
            text = f"<b>درایو {drive}</b><br>فضای کل: {format_bytes(usage.total)}<br>استفاده شده: {format_bytes(usage.used)}<br>آزاد: {format_bytes(usage.free)}<br>"
            if usage.free < 5 * 1024**3:
                text += "<span style='color:#f97316;'>⚠️ فضای آزاد کم است!</span>"
            self.drive_info_label.setText(text)
        except:
            self.drive_info_label.setText("خطا در خواندن اطلاعات")

    def open_disk_mgmt(self):
        subprocess.run("diskmgmt.msc", shell=True)


# ========== تحلیلگر فایل‌های بزرگ ==========
class ScanWorker(QThread):
    file_found = pyqtSignal(str, int, str, str)

    def __init__(self, root_path, min_size):
        super().__init__()
        self.root_path = root_path
        self.min_size = min_size

    def run(self):
        for dirpath, dirnames, filenames in os.walk(self.root_path, followlinks=False):
            for fn in filenames:
                try:
                    full = os.path.join(dirpath, fn)
                    size = os.path.getsize(full)
                    if size >= self.min_size:
                        mtime = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M:%S")
                        self.file_found.emit(fn, size, full, mtime)
                except:
                    continue
            self.msleep(1)


class DiskAnalyzerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.addItems(['C:\\', 'D:\\', 'E:\\', os.path.expanduser('~')])
        btn_browse = QPushButton("📂 انتخاب پوشه")
        btn_browse.clicked.connect(self.browse_folder)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 10240)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        btn_scan = QPushButton("🔍 جستجوی فایل‌های بزرگ")
        btn_scan.clicked.connect(self.scan_large_files)
        top_layout.addWidget(QLabel("مسیر:"))
        top_layout.addWidget(self.path_combo)
        top_layout.addWidget(btn_browse)
        top_layout.addWidget(QLabel("حداقل حجم:"))
        top_layout.addWidget(self.size_spin)
        top_layout.addWidget(btn_scan)
        layout.addLayout(top_layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["نام فایل", "اندازه", "مسیر کامل", "تاریخ تغییر"])
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

        self.status_label = QLabel("آماده")
        layout.addWidget(self.status_label)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
        if folder:
            self.path_combo.setCurrentText(folder)

    def scan_large_files(self):
        path = self.path_combo.currentText()
        if not os.path.exists(path):
            QMessageBox.warning(self, "خطا", "مسیر وجود ندارد.")
            return
        min_size = self.size_spin.value() * 1024 * 1024
        self.tree.clear()
        self.status_label.setText("در حال جستجو... لطفاً صبر کنید")
        QApplication.processEvents()
        self.thread = ScanWorker(path, min_size)
        self.thread.file_found.connect(self.add_file_to_tree)
        self.thread.finished.connect(lambda: self.status_label.setText("جستجو کامل شد."))
        self.thread.start()

    def add_file_to_tree(self, name, size, fullpath, mod_time):
        item = QTreeWidgetItem([name, format_bytes(size), fullpath, mod_time])
        self.tree.addTopLevelItem(item)


# ========== تب ابزارهای نگهداری ==========
class MaintenanceTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        tools_group = QGroupBox("🛠️ ابزارهای سیستمی")
        tools_layout = QGridLayout()
        btns = [
            ("🧹 Disk Cleanup (cleanmgr)", self.run_disk_cleanup),
            ("🔧 Defragment (dfrgui)", self.run_defrag),
            ("📊 Task Manager", self.run_taskmgr),
            ("💾 System Properties", self.run_sysdm),
            ("⚡ Hibernate: Off/On Toggle", self.toggle_hibernate),
            ("🗑️ Clear Memory Cache", self.clear_memory_cache),
        ]
        for i, (text, func) in enumerate(btns):
            btn = QPushButton(text)
            btn.clicked.connect(func)
            tools_layout.addWidget(btn, i//2, i%2)
        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)

        ram_group = QGroupBox("🧠 وضعیت حافظه RAM")
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel()
        self.ram_progress = QProgressBar()
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_progress)
        ram_group.setLayout(ram_layout)
        layout.addWidget(ram_group)
        self.update_ram_info()
        self.ram_timer = QTimer(self)
        self.ram_timer.timeout.connect(self.update_ram_info)
        self.ram_timer.start(5000)

    def update_ram_info(self):
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        percent = int(mem.percent)   # ← تبدیل به int برای setValue
        self.ram_label.setText(f"کل: {total_gb:.2f} GB | استفاده شده: {used_gb:.2f} GB | آزاد: {mem.available/(1024**3):.2f} GB")
        self.ram_progress.setValue(percent)
        self.ram_progress.setFormat(f"{percent}% استفاده")

    def run_disk_cleanup(self):
        subprocess.Popen("cleanmgr.exe")
    def run_defrag(self):
        subprocess.Popen("dfrgui.exe")
    def run_taskmgr(self):
        subprocess.Popen("taskmgr.exe")
    def run_sysdm(self):
        subprocess.Popen("sysdm.cpl")
    def toggle_hibernate(self):
        result = subprocess.run(["powercfg", "/a"], capture_output=True, text=True)
        if "Hibernation" in result.stdout and "Not Available" not in result.stdout:
            subprocess.run(["powercfg", "/h", "off"], capture_output=True)
            QMessageBox.information(self, "Hibernate", "Hibernate غیرفعال شد (فضای هارد آزاد شد).")
        else:
            subprocess.run(["powercfg", "/h", "on"], capture_output=True)
            QMessageBox.information(self, "Hibernate", "Hibernate فعال شد.")
    def clear_memory_cache(self):
        try:
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
            ctypes.windll.ntdll.NtRaiseHardError(0xdeadbeef, 0, 0, 0, 0, ctypes.byref(ctypes.c_uint()))
        except:
            subprocess.run(["powershell.exe", "-Command", "Clear-RecycleBin -Force"], capture_output=True)
            QMessageBox.information(self, "حافظه", "سطل زباله خالی شد.")


# ========== پنجره اصلی ==========
class SuperCleanerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Disk Cleaner Pro 2026")
        self.setGeometry(100, 50, 1100, 750)
        self.setMinimumSize(900, 600)

        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QTabWidget::pane { border: 1px solid #334155; border-radius: 10px; background-color: #1e293b; }
            QTabBar::tab { background-color: #0f172a; color: #cbd5e1; padding: 8px 18px; font: bold 12px; }
            QTabBar::tab:selected { background-color: #3b82f6; color: white; }
            QGroupBox { font: bold 13px; color: #f1f5f9; border: 2px solid #3b82f6; border-radius: 12px; margin-top: 12px; background-color: #1e293b; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px; color: #60a5fa; }
            QCheckBox { color: #e2e8f0; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background-color: #334155; }
            QCheckBox::indicator:checked { background-color: #10b981; }
            QPushButton { background-color: #3b82f6; color: white; border-radius: 8px; padding: 8px 16px; border: none; }
            QPushButton:hover { background-color: #2563eb; }
            QTextEdit { background-color: #0f172a; color: #cbd5e6; font-family: monospace; border-radius: 8px; border: 1px solid #334155; }
            QProgressBar { border-radius: 6px; text-align: center; background-color: #334155; color: white; height: 20px; }
            QProgressBar::chunk { background-color: #10b981; }
            QTreeWidget { background-color: #0f172a; color: #cbd5e1; alternate-background-color: #1e293b; }
            QMenu { background-color: #1e293b; color: white; border-radius: 8px; }
            QMenu::item:selected { background-color: #3b82f6; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        self.clean_tab = QWidget()
        self.setup_clean_tab()
        self.tabs.addTab(self.clean_tab, "🧹 پاکسازی پیشرفته")
        self.tabs.addTab(DiskManagerTab(), "💽 مدیریت دیسک")
        self.tabs.addTab(DiskAnalyzerTab(), "📂 فایل‌های بزرگ")
        self.tabs.addTab(MaintenanceTab(), "🛠️ ابزارهای نگهداری")

        main_layout.addWidget(self.tabs)

        self.floating_btn = AdvancedFloatingButton()
        self.floating_btn.manual_clean.connect(self.run_selected_cleanup)
        self.floating_btn.auto_toggled.connect(self.on_auto_mode)
        self.floating_btn.show()

        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.auto_check_space)
        self.auto_mode_enabled = False
        self.auto_threshold_mb = 2048

        self.tray = QSystemTrayIcon(self)
        tray_menu = QMenu()
        show_action = QAction("نمایش دکمه شناور", self)
        show_action.triggered.connect(self.show_floating)
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        self.tray.setContextMenu(tray_menu)
        self.tray.setToolTip("Super Disk Cleaner")
        self.tray.show()

    def setup_clean_tab(self):
        layout = QVBoxLayout(self.clean_tab)
        tasks_group = QGroupBox("✅ وظایف پاکسازی (گزینه‌های دلخواه را تیک بزنید)")
        grid_layout = QGridLayout()
        self.tasks = {}
        task_list = [
            ('temp', '🗑️ فایل‌های موقت (Temp)'),
            ('recycle', '♻️ خالی کردن سطل زباله'),
            ('chrome', '🌐 کش مرورگر Chrome'),
            ('edge', '🌐 کش مرورگر Edge'),
            ('firefox', '🦊 کش مرورگر Firefox'),
            ('opera', '🎭 کش مرورگر Opera'),
            ('prefetch', '⚙️ فایل‌های Prefetch'),
            ('windows_update', '🔄 کش آپدیت ویندوز'),
            ('memory_dump', '💀 فایل‌های Memory Dump'),
            ('logs', '📜 فایل‌های Log سیستمی'),
            ('installer_temp', '📦 فایل‌های موقت نصب'),
            ('dns_cache', '🌍 پاک کردن کش DNS'),
            ('chromium_extra', '🧩 مرورگرهای Chromium (Brave, Vivaldi)'),
            ('recent_docs', '📁 پاک کردن اسناد اخیر'),
            ('thumbnails', '🖼️ حذف Thumbnails'),
        ]
        row, col = 0, 0
        for key, text in task_list:
            cb = QCheckBox(text)
            self.tasks[key] = cb
            grid_layout.addWidget(cb, row, col)
            row += 1
            if row > 7:
                row = 0
                col += 1
        tasks_group.setLayout(grid_layout)
        layout.addWidget(tasks_group)

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("🚀 اجرای انتخابی")
        self.run_btn.clicked.connect(self.run_selected_cleanup)
        self.auto_thresh_spin = QSpinBox()
        self.auto_thresh_spin.setRange(500, 10000)
        self.auto_thresh_spin.setValue(2048)
        self.auto_thresh_spin.setSuffix(" MB")
        self.auto_thresh_spin.valueChanged.connect(self.set_auto_threshold)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(QLabel("آستانه خودکار (MB):"))
        btn_layout.addWidget(self.auto_thresh_spin)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("📋 گزارش عملیات:"))
        layout.addWidget(self.log_text)

    def run_selected_cleanup(self):
        selected = {k: cb.isChecked() for k, cb in self.tasks.items()}
        if not any(selected.values()):
            QMessageBox.information(self, "توجه", "حداقل یک گزینه را انتخاب کنید.")
            return
        self.run_btn.setEnabled(False)
        self.log_text.clear()
        self.worker = CleanupWorker(selected)
        self.worker.log_signal.connect(self.log_text.append)
        self.worker.finished_signal.connect(self.on_cleanup_finished)
        self.worker.start()

    def on_cleanup_finished(self, success, message):
        self.run_btn.setEnabled(True)
        self.log_text.append(message)
        if success:
            QMessageBox.information(self, "پایان", message)

    def on_auto_mode(self, enabled):
        self.auto_mode_enabled = enabled
        if enabled:
            self.auto_timer.start(30000)
            self.log_text.append("🔁 حالت خودکار فعال شد (چک هر ۳۰ ثانیه).")
        else:
            self.auto_timer.stop()
            self.log_text.append("⏹️ حالت خودکار غیرفعال شد.")

    def set_auto_threshold(self, val):
        self.auto_threshold_mb = val

    def auto_check_space(self):
        if not self.auto_mode_enabled:
            return
        try:
            free_mb = psutil.disk_usage('C:\\').free / (1024*1024)
            if free_mb < self.auto_threshold_mb:
                self.log_text.append(f"⚠️ فضای آزاد کمتر از {self.auto_threshold_mb} MB است. اجرای خودکار پاکسازی...")
                self.run_selected_cleanup()
        except:
            pass

    def show_floating(self):
        self.floating_btn.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    window = SuperCleanerWindow()
    window.show()
    sys.exit(app.exec_())
