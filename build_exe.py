import PyInstaller.__main__

PyInstaller.__main__.run([
    'grocery_management_system.py',
    '--onefile',
    '--windowed',
    '--name=GroceryManagementSystem',
    '--icon=icon.ico',
    '--add-data=requirements.txt;.',
    '--hidden-import=tkcalendar',
    '--hidden-import=mysql.connector',
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.'
])