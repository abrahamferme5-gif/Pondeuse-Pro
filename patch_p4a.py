import os
import re

path = 'python-for-android/pythonforandroid/recipes/libthorvg/__init__.py'
if not os.path.exists(path):
    print(f"Error: {path} not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('"lib/clang/*/lib/linux"', '"lib*/clang/*/lib/linux"')

safe_search = '''matches = glob(pattern) or glob(join(self.ctx.ndk.llvm_prebuilt_dir, "lib64/clang/*/lib/linux", lib_arch))
            clang_lib_dir = matches[0] if matches else join(self.ctx.ndk.llvm_prebuilt_dir, "lib64/clang/14.0.6/lib/linux", lib_arch)'''

code = re.sub(r'clang_lib_dir\s*=\s*glob\(pattern\)\[0\]', safe_search, code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully applied libthorvg patch to python-for-android!")
