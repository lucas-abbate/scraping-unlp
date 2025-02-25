### Scraper de exámenes del SIU ###

- Debe estar instalado el navegador Firefox.
- Tiene que estar seteado desde la configuración de windows el proxy de la red de la facultad.
    - Puede que intente instalar cosas de internet y que fallen si está activado el proxy. Si es así, descargar el "geckodriver.exe" de https://github.com/mozilla/geckodriver/releases, y ponerlo en la carpeta donde está instalado firefox.
- Debe haber un .txt que tenga el usuario del SIU en la primera linea y la contraseña en la segunda.

## Ejecucion ##
- Abrir una consola en la carpeta donde está "examenes.exe" (Shift + Click Derecho en la carpeta -> Abrir en Terminal/Abrir la ventana de Powershell/Abrir ventana de comandos aquí).
- Se puede ejecutar de distintas formas (los parametros con -- son opcionales):

"""
examenes.exe <ruta_al_txt_con_usuario_y_contraseña> --año=<año> --llamado=<llamado> --output=<carpeta_output> --filename=<nombre_output.xlsx>
"""

- año y llamado son opcionales. Si no se pasan, el programa da a elegir entre los años y llamados disponibles
- output es la carpeta donde se guardará el archivo de excel. Si no se pasa, se guarda en la carpeta donde está el .exe
- filename es el nombre del archivo de excel. Si no se pasa, se guarda con el nombre "output.xlsx"

## Errores ##
- Si al querer empezar, la página que abre es 403 Forbidden, es porque el proxy no está seteado correctamente.
- Si no abre ningún navegador, descargar el geckodriver, y agregarlo al PATH de windows.

