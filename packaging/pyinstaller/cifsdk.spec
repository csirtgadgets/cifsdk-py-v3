# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

name = 'cif'

block_cipher = None

submodules = [
    'cifsdk.client',
    'cifsdk.utils',
    'cifsdk._version'
]

hidden_imports = []
for s in submodules:
    hidden_imports.extend(collect_submodules(s))

data = [
    ('../_version', 'cifsdk'),
]

a = Analysis(['cifsdk/client/client.py'],
             binaries=None,
             datas=data,
             hiddenimports=hidden_imports,
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=name,
          debug=False,
          strip=None,
          upx=True,
          console=True )