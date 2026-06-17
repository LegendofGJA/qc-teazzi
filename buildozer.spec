[app]
title = QC Teazzi
package.name = qcteazzi
package.domain = com.lgja.qcteazzi
source.dir = .
source.include_exts = py,kv,png,jpg
version = 1.0.0

requirements = python3,kivy,openpyxl,Pillow,requests,certifi,urllib3,chardet,idna,plyer,android

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.numeric_version = 1
android.accept_sdk_license = True
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1, androidx.core:core:1.12.0

icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

android.app_name = QC Teazzi

[buildozer]
log_level = 2
warn_on_root = 0
