from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
includes = ["app"]
packages = ["sqlmodel", "sqlalchemy","textual", "textual._tree_sitter"]
excludes = ["pytest", "cx_Freeze", "textual-dev", "textual-serve", "aiohttp", "click", "msgpack", "colorana", "iniconfig", "packaging", "pluggy", "cx-logging", "dmgbuild","filelock", "lief", "patchelf"]
zip_include_packages: list[str] = []
build_options = {'packages': packages, 'excludes': excludes, 'includes': includes, 'zip_include_packages': zip_include_packages}

base = 'console'

executables = [
    Executable('./main.py', base=base, target_name = 'rivals_viewer')
]

setup(name='rivals_viewer',
      version = '0.3',
      description = 'Application to keep track of Marvel Rivals alts',
      options = {'build_exe': build_options},
      executables = executables)
