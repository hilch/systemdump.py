import PyInstaller.__main__

PyInstaller.__main__.run([
    '../sources/systemdump.py',
	'--noconfirm',
    '--console',
    '--onefile',
	'--icon',
	'systemdump.ico'
])

