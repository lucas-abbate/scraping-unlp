import os
import time
from typing import Any, Tuple, Union, List, Optional, Dict

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

from tqdm import tqdm
from IPython.display import clear_output
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import argparse


def fill_textbox(
    browser: webdriver.Firefox,
    selector: str,
    text: str,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Espera a que un textbox sea clickeable, lo limpia y escribe el texto especificado.

    Args:
        browser: Instancia del navegador.
        selector: XPath del elemento textbox.
        text: Texto a ingresar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    for _ in range(3):
        try:
            box = WebDriverWait(browser, timeout).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            time.sleep(residual_timeout)
            box.clear()
            box.send_keys(text)
            return  # Sale si se logra la acción
        except Exception:
            time.sleep(timeout)
            continue


def click_by_xpath(
    browser: webdriver.Firefox,
    selector: str,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Espera a que el elemento especificado por XPath sea clickeable y realiza el clic.

    Args:
        browser: Instancia del navegador.
        selector: XPath del elemento a clickejar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, selector))
    ).click()
    time.sleep(residual_timeout)


def login_siu(browser: webdriver.Firefox, siu_user: str, siu_pass: str) -> None:
    """
    Realiza el login en SIU rellenando los campos de usuario y contraseña.

    Args:
        browser: Instancia del navegador.
        siu_user: Usuario SIU.
        siu_pass: Contraseña SIU.
    """
    fill_textbox(browser, '//*[@id="ef_form_5000221_datosusuario"]', siu_user)
    fill_textbox(browser, '//*[@id="ef_form_5000221_datosclave"]', siu_pass)
    click_by_xpath(browser, '//*[@id="form_5000221_datos_ingresar"]')


def write_in_xpath(
    browser: webdriver.Firefox,
    xpath: str,
    text: str,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Escribe un texto en el elemento identificado por su XPath.

    Args:
        browser: Instancia del navegador.
        xpath: XPath del elemento.
        text: Texto a ingresar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    try:
        element = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        time.sleep(residual_timeout)
        element.clear()
        element.send_keys(text)
    except Exception as e:
        print(f"Error al ingresar texto en el elemento {xpath}: {e}", end="\r")


def select_option_by_value(
    browser: webdriver.Firefox,
    selector: str,
    option_value: str,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Selecciona una opción de un dropdown por el valor de la opción.

    Args:
        browser: Instancia del navegador.
        selector: XPath del dropdown.
        option_value: Valor de la opción a seleccionar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    dropdown = WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, selector))
    )
    select = Select(dropdown)
    try:
        select.select_by_value(option_value)
        time.sleep(residual_timeout)
    except Exception:
        raise ValueError(f"Option with value '{option_value}' not found.")


def select_option_by_text(
    browser: webdriver.Firefox,
    selector: str,
    option_text: str,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Selecciona una opción de un dropdown por el texto visible.

    Args:
        browser: Instancia del navegador.
        selector: XPath del dropdown.
        option_text: Texto visible de la opción a seleccionar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    dropdown = WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, selector))
    )
    select = Select(dropdown)
    try:
        select.select_by_visible_text(option_text)
        time.sleep(residual_timeout)
    except Exception:
        raise ValueError(f"Option with text '{option_text}' not found.")


def get_dropdown_options(
    browser: webdriver.Firefox, selector: str, timeout: int = 10
) -> List[Tuple[str, str]]:
    """
    Retorna una lista de tuplas (valor, texto) de las opciones de un dropdown.

    Args:
        browser: Instancia del navegador.
        selector: XPath del dropdown.
        timeout: Tiempo máximo de espera en segundos.

    Returns:
        Lista de tuplas con (valor, texto) de cada opción.
    """
    dropdown = WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, selector))
    )
    select = Select(dropdown)
    options = [
        (option.get_attribute("value"), option.text) for option in select.options
    ]
    return options


def select_option_by_input(
    browser: webdriver.Firefox,
    selector: str,
    text: bool = False,
    timeout: int = 10,
    residual_timeout: int = 1,
    input_text: Optional[str] = None,
) -> None:
    """
    Permite seleccionar una opción de un dropdown, mostrando las opciones disponibles para elegir
    o utilizando un valor de entrada directo.

    Args:
        browser: Instancia del navegador.
        selector: XPath del dropdown.
        text: Si es True, se selecciona por texto visible; de lo contrario, por valor.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
        input_text: Texto de entrada para seleccionar directamente. Si es None, se muestra la lista de opciones.
    """
    options = get_dropdown_options(browser, selector, timeout)
    if input_text is None:
        if len(options) > 10:
            preview_options = options[:10]
            print("Opciones disponibles (primeras 10):")
            for idx, (_, option_text) in enumerate(preview_options):
                print(f"{idx}: {option_text}")
            print("10: Mostrar todas las opciones")
            valid = False
            while not valid:
                entrada = input(
                    "Ingrese el número de la opción que desea seleccionar: "
                )
                try:
                    indice = int(entrada)
                    if indice == 10:
                        clear_output()
                        print("Opciones disponibles:")
                        for idx, (_, option_text) in enumerate(options):
                            print(f"{idx}: {option_text}")
                        entrada_all = input(
                            "Ingrese el número de la opción que desea seleccionar: "
                        )
                        indice = int(entrada_all)
                        if indice < 0 or indice >= len(options):
                            print("Índice fuera de rango.")
                            continue
                        valid = True
                    elif 0 <= indice < 10:
                        valid = True
                    else:
                        print("Índice fuera de rango.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingrese un número entero.")
        else:
            print("Opciones disponibles:")
            for idx, (_, option_text) in enumerate(options):
                print(f"{idx}: {option_text}")
            valid = False
            while not valid:
                entrada = input(
                    "Ingrese el número de la opción que desea seleccionar: "
                )
                try:
                    indice = int(entrada)
                    if 0 <= indice < len(options):
                        valid = True
                    else:
                        print("Índice fuera de rango.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingrese un número entero.")
        value_to_select = options[indice][0]
    else:
        value_to_select = input_text

    clear_output()
    if text:
        select_option_by_text(
            browser, selector, value_to_select, timeout, residual_timeout
        )
    else:
        select_option_by_value(
            browser, selector, value_to_select, timeout, residual_timeout
        )


def filtrar_año(
    browser: webdriver.Firefox,
    input_text: Optional[str] = None,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Selecciona el año académico en el dropdown correspondiente.

    Args:
        browser: Instancia del navegador.
        input_text: Valor a seleccionar; si es None, se solicita al usuario.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    select_option_by_input(
        browser,
        '//*[@id="ef_ei_38000482_filtroanio_academico"]',
        input_text=input_text,
        timeout=timeout,
        residual_timeout=residual_timeout,
    )


def filtrar_llamado(
    browser: webdriver.Firefox,
    input_text: Optional[str] = None,
    timeout: int = 10,
    residual_timeout: int = 1,
) -> None:
    """
    Selecciona el turno de examen en el dropdown correspondiente.

    Args:
        browser: Instancia del navegador.
        input_text: Valor a seleccionar; si es None, se solicita al usuario.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    text_flag = True if input_text is not None else False
    select_option_by_input(
        browser,
        '//*[@id="ef_ei_38000482_filtroturno_examen"]',
        input_text=input_text,
        text=text_flag,
        timeout=timeout,
        residual_timeout=residual_timeout,
    )


def ejecutar_filtro(
    browser: webdriver.Firefox, timeout: int = 10, residual_timeout: int = 1
) -> None:
    """
    Ejecuta el filtro haciendo clic en el botón correspondiente.

    Args:
        browser: Instancia del navegador.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    click_by_xpath(
        browser, '//*[@id="ei_38000482_filtro_filtrar"]', timeout, residual_timeout
    )


def acta_generator(
    browser: webdriver.Firefox,
    acta_obj: Any,
    timeout: int = 15,
    residual_timeout: int = 1,
) -> Union[Tuple[pd.DataFrame, str], str]:
    """
    Genera un acta a partir de un objeto acta, recopilando la información general y la de los alumnos a lo largo de las páginas.

    Args:
        browser: Instancia del navegador.
        acta_obj: Elemento que representa el acta a procesar.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.

    Returns:
        Una tupla (DataFrame con la información consolidada, actividad) o un string de error.
    """
    acta_obj.click()
    WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ci_38000483_cancelar"]'))
    )
    try:
        soup = BeautifulSoup(browser.page_source, "html.parser")
        info = general_info(soup, timeout, residual_timeout)
        if info["Estado"] == "Anulada":
            back = browser.find_element(By.XPATH, '//*[@id="ci_38000483_cancelar"]')
            back.click()
            time.sleep(residual_timeout)
            try:
                return "Acta anulada", info["Actividad"]
            except:
                return "Acta anulada", "Act. no encontrada"
        tabs = [tab_alumnos(soup, timeout, residual_timeout)]
    except Exception:
        try:
            time.sleep(timeout)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            info = general_info(soup, timeout, residual_timeout)
            tabs = [tab_alumnos(soup, timeout, residual_timeout)]
        except Exception:
            time.sleep(timeout)
            info = general_info(soup, timeout, residual_timeout)

            back = browser.find_element(By.XPATH, '//*[@id="ci_38000483_cancelar"]')
            back.click()
            time.sleep(residual_timeout)
            try:
                return "Error en acta", info["Actividad"]
            except:
                return "Error en acta", "Act. no encontrada"
    try:
        n_pages = int(
            browser.find_element(
                By.XPATH,
                '//*[@id="cuerpo_js_cuadro_38000500_alumnos"]/tbody/tr[4]/td/div/strong[2]',
            ).text
        )
    except exceptions.NoSuchElementException:
        n_pages = 1

    for _ in range(1, n_pages):
        next_page(browser, residual_timeout)
        WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ci_38000483_cancelar"]'))
        )
        soup = BeautifulSoup(browser.page_source, "html.parser")
        tabs.append(tab_alumnos(soup, timeout, residual_timeout))

    tab = pd.concat(tabs, ignore_index=True)
    tab["Nº"] = tab.index + 1
    old_cols = tab.columns.to_list()

    for col, val in info.items():
        tab[col] = val
    old_cols.extend(info.keys())
    tab = tab[old_cols]
    back = browser.find_element(By.XPATH, '//*[@id="ci_38000483_cancelar"]')
    back.click()
    time.sleep(residual_timeout)
    return tab, info["Actividad"]


def general_info(
    soup: BeautifulSoup, timeout: int = 15, residual_timeout: int = 1
) -> Dict[str, Any]:
    """
    Extrae la información general del acta a partir del HTML.

    Args:
        soup: Objeto BeautifulSoup del HTML de la página.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.

    Returns:
        Diccionario con la información general extraída.
    """
    tab = pd.read_html(StringIO(soup.prettify()))[1]
    info: Dict[str, Any] = {}
    tab_info = tab.iloc[1:5]
    for row in tab_info.iterrows():
        info[row[1][0]] = row[1][1]
        info[row[1][2]] = row[1][3]
        info[row[1][4]] = row[1][5]
    for i in range(10):
        try:
            info.pop(str(i))
        except Exception:
            pass
    info.pop("Fecha", None)
    return info


def tab_alumnos(
    soup: BeautifulSoup, timeout: int = 15, residual_timeout: int = 1
) -> pd.DataFrame:
    """
    Extrae la información de los alumnos de una sola página.

    Args:
        soup: Objeto BeautifulSoup del HTML de la página.
        timeout: Tiempo máximo de espera en segundos.
        residual_timeout: Tiempo de espera adicional después de interactuar.

    Returns:
        DataFrame con la información de los alumnos.
    """
    try:
        if "No hay datos cargados" in soup.prettify():
            return pd.DataFrame()
        tab = pd.read_html(StringIO(soup.prettify()))[7]
        tab.columns = tab.iloc[0, :]
        tab = tab.drop(0)
    except Exception:
        time.sleep(timeout)
        try:
            tab = pd.read_html(StringIO(soup.prettify()))[6]
            tab.columns = tab.iloc[0, :]
            tab = tab.drop(0)
        except Exception:
            raise ValueError("No se pudo leer la tabla de alumnos")
    return tab


def next_page(browser: webdriver.Firefox, residual_timeout: int = 1) -> None:
    """
    Navega a la siguiente página del listado.

    Args:
        browser: Instancia del navegador.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    obj = browser.find_element(
        By.XPATH, '//*[@src="/toba_2.6/img/nucleo/paginacion/siguiente.gif?av=3.3.26"]'
    )
    obj.click()
    WebDriverWait(browser, 10).until(
        EC.any_of(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="ei-boton-fila"]')),
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ci_38000483_cancelar"]')),
        )
    )
    time.sleep(residual_timeout)


def prev_page(browser: webdriver.Firefox, residual_timeout: int = 1) -> None:
    """
    Navega a la página anterior del listado.

    Args:
        browser: Instancia del navegador.
        residual_timeout: Tiempo de espera adicional después de interactuar.
    """
    obj = browser.find_element(
        By.XPATH, '//*[@src="/toba_2.6/img/nucleo/paginacion/anterior.gif?av=3.3.26"]'
    )
    obj.click()
    WebDriverWait(browser, 10).until(
        EC.any_of(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="ei-boton-fila"]')),
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ci_38000483_cancelar"]')),
        )
    )
    time.sleep(residual_timeout)
