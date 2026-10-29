[app]
title = Pondeuse Pro
package.name = pondeusepro
package.domain = com.pondeusepro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd==1.2.0,pillow,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
p4a.source_dir = ./python-for-android
android.allow_backup = True
android.accept_sdk_license = True
