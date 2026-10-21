[app]
title = Pondeuse Pro
package.name = pondeusepro
package.domain = com.pondeusepro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd==1.1.1,sdl2,pillow,requests,sqlite3,supabase,pyjwt,cryptography
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
