[app]
# (str) Titre de votre application
title = Pondeuse Pro

# (str) Nom du package
package.name = pondeusepro

# (str) Domaine du package
package.domain = com.pondeusepro

# (str) Répertoire source (généralement .)
source.dir = .

# (list) Extensions de fichiers à inclure
source.include_exts = py,png,jpg,kv,atlas

# (list) Dépendances de l'application
requirements = python3,kivy,kivymd==1.1.1,sdl2,pillow,requests,pycryptodomex,jnius

# (str) Version de l'application
version = 1.0

# (str) Orientation (portrait ou all)
orientation = portrait

# (bool) Plein écran
fullscreen = 0

# (list) Permissions Android
android.permissions = INTERNET

# (int) API Android cible
android.api = 33

# (int) API Android minimale
android.minapi = 21

# (str) Version du NDK
android.ndk = 25b

# (bool) Accepter la licence du SDK
android.accept_sdk_license = True

# (list) Architectures cibles
android.archs = arm64-v8a

# (str) Branche de python-for-android
p4a.branch = develop


[buildozer]
# (int) Niveau de log (2 = debug)
log_level = 2

# (str) Répertoire de build
build_dir = .buildozer

# (str) Répertoire de sortie
bin_dir = bin