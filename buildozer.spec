name: Build Kivy APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Étape cruciale : installer les dépendances système
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential libltdl-dev libffi-dev libssl-dev python3-dev

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          workdir: .
          buildozer_version: stable

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: ${{ steps.buildozer.outputs.filename }}