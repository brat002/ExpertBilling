# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), '../mikrobill/rpc.py'],
             pathex=['/home/al/build_proj/pyinstaller-1.4',
             "/home/al/build_proj/mikrobill/chartprovider/"])
ch_dir = "/home/al/build_proj/mikrobill/chartprovider/" 
collect = COLLECT(
          a.binaries+[("libchartdir.so", ch_dir+"libchartdir.so", "BINARY")])
pyz = PYZ(a.pure)
print a.binaries
exe = EXE( pyz,
          a.scripts,
          a.binaries+[("libchartdir.so", ch_dir+"libchartdir.so", "BINARY")],
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'rpc'),
          debug=True,
          strip=False,
          upx=True,
          console=1
          )
