# پاک‌کننده و مدیریت فضای دیسک — نسخه ۱
# Super Disk Cleaner & Space Manager — Version 1

**نسخه / Version:** `v1.0.0`  
**توسعه‌دهنده / Author:** `REZA ZOHREVAND`  
**سیستم‌عامل / OS:** Windows  
**زبان / Language:** Python + PyQt5

---

## فارسی

### معرفی

**پاک‌کننده و مدیریت فضای دیسک** یک ابزار دسکتاپ ویندوزی با رابط گرافیکی PyQt5 است که برای پاکسازی فایل‌های موقت و کش‌ها، مشاهده وضعیت پارتیشن‌ها و RAM، پیدا کردن فایل‌های حجیم و اجرای سریع ابزارهای نگهداری ویندوز طراحی شده است.

### امکانات نسخه ۱

- پاکسازی فایل‌های موقت کاربر و Windows Temp
- خالی کردن Recycle Bin
- پاکسازی کش Chrome، Edge، Firefox و Opera
- پاکسازی کش Brave و Vivaldi
- پاکسازی Prefetch و Windows Update Cache
- حذف Memory Dumpها، Minidumpها، برخی Logها و فایل‌های موقت Installer
- Flush کردن DNS Cache
- پاکسازی Recent Documents و Thumbnail Cache
- نمایش پارتیشن‌ها، فضای کل، فضای آزاد و درصد استفاده
- نمودار وضعیت فضای دیسک و دسترسی به Disk Management
- جستجوی فایل‌های بزرگ بر اساس حداقل حجم انتخابی
- نمایش وضعیت RAM
- میانبر Disk Cleanup، Defragment، Task Manager و System Properties
- فعال/غیرفعال کردن Hibernate
- دکمه شناور برای نمایش درصد فضای آزاد درایو C
- اجرای دستی پاکسازی از دکمه شناور
- حالت خودکار برای بررسی فضای آزاد و اجرای پاکسازی انتخاب‌شده
- System Tray برای دسترسی سریع

### پیش‌نیازها

- Windows
- Python 3
- PyQt5
- psutil

### نصب

در Command Prompt یا PowerShell داخل پوشه برنامه اجرا کنید:

```bash
pip install -r requirements.txt
```

### اجرا

```bash
python "باز کننده فضا.py"
```

برای بعضی عملیات‌های سیستمی بهتر است Terminal یا برنامه را با **Run as Administrator** اجرا کنید.

### نحوه استفاده

1. برنامه را اجرا کنید.
2. در تب **پاکسازی پیشرفته** گزینه‌هایی را که می‌خواهید پاک شوند انتخاب کنید.
3. روی **اجرای انتخابی** بزنید.
4. در بخش **مدیریت دیسک** وضعیت پارتیشن‌ها و فضای آزاد را ببینید.
5. در بخش **فایل‌های بزرگ** مسیر و حداقل حجم را انتخاب کنید و اسکن را شروع کنید.
6. در بخش **ابزارهای نگهداری** از ابزارهای ویندوز و وضعیت RAM استفاده کنید.
7. دکمه شناور درصد فضای آزاد درایو `C:` را نشان می‌دهد. کلیک چپ پاکسازی انتخاب‌شده را اجرا می‌کند و کلیک راست منوی حالت خودکار را باز می‌کند.
8. در حالت خودکار، برنامه هر ۳۰ ثانیه فضای آزاد درایو `C:` را بررسی می‌کند و اگر کمتر از آستانه تعیین‌شده باشد، پاکسازی گزینه‌های انتخاب‌شده را اجرا می‌کند.

### هشدار مهم

این برنامه عملیات حذف فایل و اجرای فرمان‌های سیستمی ویندوز را انجام می‌دهد. قبل از استفاده روی سیستم اصلی، گزینه‌های انتخابی را بررسی کنید.

بعضی عملیات‌ها ممکن است به دسترسی Administrator نیاز داشته باشند یا باعث شوند بعضی فایل‌های کش در اجرای بعدی دوباره ساخته شوند.

در نسخه ۱، گزینه **Clear Memory Cache** در کد از یک فراخوانی سطح پایین ویندوز استفاده می‌کند که می‌تواند رفتار غیرمنتظره یا ناپایداری سیستم ایجاد کند. تا زمان بازطراحی این بخش، استفاده از آن توصیه نمی‌شود.

---

## English

### About

**Super Disk Cleaner & Space Manager** is a Windows desktop utility built with PyQt5. It provides disk cleanup tools, disk/RAM monitoring, large-file scanning, and quick access to common Windows maintenance utilities.

### Version 1 Features

- Clean user Temp and Windows Temp files
- Empty Recycle Bin
- Clean Chrome, Edge, Firefox, Opera, Brave, and Vivaldi caches
- Clean Prefetch and Windows Update cache
- Remove Memory Dumps, Minidumps, selected logs, and installer temporary files
- Flush DNS cache
- Clear Recent Documents and thumbnail cache
- Show partitions, total/free space, and usage percentage
- Disk usage chart and Disk Management shortcut
- Scan for large files using a configurable minimum size
- Show RAM usage
- Shortcuts for Disk Cleanup, Defragment, Task Manager, and System Properties
- Toggle Hibernate
- Floating free-space button for drive C
- Manual cleanup from the floating button
- Automatic low-space monitoring and cleanup
- System tray access

### Requirements

- Windows
- Python 3
- PyQt5
- psutil

### Installation

```bash
pip install -r requirements.txt
```

### Run

```bash
python "باز کننده فضا.py"
```

Some system-level cleanup actions may require running the terminal or application **as Administrator**.

### How to Use

1. Launch the application.
2. Select the cleanup tasks you want in the cleanup tab.
3. Run the selected cleanup.
4. Use Disk Management to review partitions and free space.
5. Use the Large Files section to select a path and minimum size, then scan.
6. Use Maintenance Tools for Windows shortcuts and RAM information.
7. The floating button shows the free-space percentage for drive `C:`. Left-click runs the selected cleanup; right-click opens the automatic-mode menu.
8. In automatic mode, the application checks free space on `C:` every 30 seconds. If free space drops below the configured threshold, it runs the currently selected cleanup tasks.

### Important Warning

This program deletes files and executes Windows system commands. Review selected cleanup tasks before running it on an important machine.

In Version 1, the **Clear Memory Cache** action contains a low-level Windows call that may cause unexpected behavior or system instability. Avoid using that action until it is redesigned in a later version.

---

## Project Files

- `باز کننده فضا.py` — main application / فایل اصلی برنامه
- `README.md` — Persian & English documentation / توضیحات فارسی و انگلیسی
- `requirements.txt` — Python dependencies / پیش‌نیازهای پایتون
- `VERSION` — current version / نسخه فعلی
- `Super-Disk-Cleaner-Space-Manager-v1.0.0.zip` — packaged Version 1 / فایل ZIP نسخه ۱

## Version

`v1.0.0`
