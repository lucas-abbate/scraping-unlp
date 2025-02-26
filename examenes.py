import os
import time
import argparse
from typing import Optional
import pandas as pd
from tqdm import tqdm
from IPython.display import clear_output
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


from bs4 import BeautifulSoup

import funcs as fx  # Módulo que contiene funciones auxiliares para el scraping


def main(
    siu_credentials: str,
    año: Optional[int] = None,
    llamado: Optional[str] = None,
    residual_timeout: int = 1,
) -> pd.DataFrame:
    """
    Función principal para la extracción de actas de examen desde el sitio de SIU.

    Realiza lo siguiente:
        - Lee las credenciales de SIU desde un archivo.
        - Inicia el navegador y accede a la URL indicada.
        - Realiza el login y la navegación a la sección de "Imprimir acta".
        - Filtra las actas según el año y el llamado.
        - Recorre las páginas y actas disponibles, extrayendo la información correspondiente.
        - Retorna un DataFrame consolidado con la información extraída.

    Args:
        siu_credentials: Ruta al archivo con las credenciales de SIU.
        año: Año a filtrar (opcional).
        llamado: Llamado a filtrar (opcional).
        residual_timeout: Tiempo de espera residual entre interacciones.

    Returns:
        DataFrame con la información consolidada de las actas.
    """
    # Leer credenciales de SIU
    with open(siu_credentials, "r") as f:
        lines = f.readlines()
    siu_user = lines[0].strip()
    siu_pass = lines[1].strip() if len(lines) > 1 else ""

    url = "https://guarani3-gerencial.guarani.cespi.unlp.edu.ar/guarani/3.11/aplicacion.php"

    print("Se va a abrir un navegador. Ingresar las credenciales del proxy")
    print("", end="\r")
    clear_output()

    try:
        browser = webdriver.Firefox()
    except:
        browser = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install())
        )

    browser.get(url)

    # Realizar login
    fx.login_siu(browser, siu_user, siu_pass)
    browser.switch_to.window(browser.window_handles[1])
    fx.click_by_xpath(browser, '//*[@id="menu_img"]')
    fx.write_in_xpath(browser, '//*[@id="buscar_text"]', "Imprimir acta")
    fx.click_by_xpath(browser, '//*[@id="elemento_buscar_menu_38000085"]')

    # Filtrar por año y llamado
    fx.filtrar_año(browser, str(año) if año is not None else None)
    fx.filtrar_llamado(browser, llamado)
    fx.ejecutar_filtro(browser)

    dfs = []
    try:
        pags = int(
            browser.find_element(
                By.XPATH,
                '//*[@id="cuerpo_js_cuadro_38000496_cuadro_actas"]/tbody/tr[4]/td/div/strong[2]',
            ).text
        )
    except exceptions.NoSuchElementException:
        pags = 1

    # Iterar sobre las páginas de actas
    for i in tqdm(range(pags), desc="Páginas", position=0, leave=True):
        if i != 0:
            fx.next_page(browser, residual_timeout)

        actas = browser.find_elements(By.XPATH, '//*[@class="ei-boton-fila"]')
        if i != 0:
            fx.prev_page(browser, residual_timeout)

        # Iterar sobre las actas de la página actual
        pbar = tqdm(range(len(actas)), desc="Actas", leave=False, position=1)
        for j in pbar:
            try:
                curr_pag = browser.find_element(
                    By.XPATH, '//*[@id="cuadro_38000496_cuadro_actas__pagina_actual"]'
                ).get_property("value")
            except exceptions.NoSuchElementException:
                time.sleep(5 * residual_timeout)
                try:
                    back = browser.find_element(
                        By.XPATH, '//*[@id="ci_38000483_cancelar"]'
                    )
                    back.click()
                    time.sleep(5 * residual_timeout)
                except exceptions.NoSuchElementException:
                    curr_pag = "1"
            # Asegurarse que estamos en la página correcta
            while curr_pag != str(i + 1):
                fx.next_page(browser, 2)
                curr_pag = browser.find_element(
                    By.XPATH, '//*[@id="cuadro_38000496_cuadro_actas__pagina_actual"]'
                ).get_property("value")

            try:
                actas = browser.find_elements(By.XPATH, '//*[@class="ei-boton-fila"]')
                df, act = fx.acta_generator(browser, actas[j])
                pbar.set_postfix_str(f"{act}")
                if isinstance(df, str):
                    tqdm.write(f"{df} {act}")
                    continue
                elif df.empty:
                    tqdm.write(f"Acta {act} vacía")
                    continue
            except Exception:
                try:
                    time.sleep(5 * residual_timeout)
                    # actas = browser.find_elements(
                    #     By.XPATH, '//*[@class="ei-boton-fila"]'
                    # )
                    df, act = fx.acta_generator(browser, actas[j])
                    pbar.set_postfix_str(f"{act}")
                    if isinstance(df, str):
                        tqdm.write(f"{df} {act}")
                        continue
                    elif df.empty:
                        tqdm.write(f"Acta {act} vacía")
                        continue
                except Exception:
                    tqdm.write(f"Error en acta {act}")
                    continue

            dfs.append(df)
    browser.quit()
    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script para scraping de actas de examen."
    )
    parser.add_argument(
        "siu_credentials", help="Ruta al archivo con las credenciales de SIU."
    )
    parser.add_argument("--año", type=int, help="Año a filtrar.", default=None)
    parser.add_argument("--llamado", type=str, help="Llamado a filtrar.", default=None)
    parser.add_argument(
        "--residual_timeout", type=int, help="Tiempo de espera residual.", default=1
    )
    parser.add_argument(
        "--output", type=str, help="Ruta al directorio de salida.", default=""
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="Nombre del archivo de salida.",
        default="output.xlsx",
    )

    args = parser.parse_args()
    result = main(args.siu_credentials, args.año, args.llamado, args.residual_timeout)

    if args.output == "":
        args.output = os.getcwd()

    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)

    output_filename = (
        args.filename if args.filename.endswith(".xlsx") else f"{args.filename}.xlsx"
    )
    result.to_excel(os.path.join(args.output, output_filename), index=False)
