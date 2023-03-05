import re
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Haga falso si desea ver la automatización en vivo.
head = True



def agenteUsuario():
    """
    agenteUsuario Funcion para generar aleatoriamente un navegador en la nueva consulta a realizar

    Returns:
        string: User Agent
    """
    with open('comparer/user-agents.txt') as f:
    # with open('user-agents.txt') as f:
        agente = f.read().split("\n")
        return random.choice(agente)


class TryExcept:
    """
     Creamos un try general para cuando no existe un texto o atributo que estemos buscando con los XPATH
    """
    def text(self, element):
        try:
            return element.inner_text().strip()
        except AttributeError:
            return "-"

    def attributes(self, element, attr):
        try:
            return element.get_attribute(attr)
        except AttributeError:
            return " Valor No disponible"


def scraping(prompt, head=True):
    """
    scraping Función principal del código, se ingresa el producto y realiza las búsquedas y extracción de información
    """
    # main Data
    data = []
    # Instanciamos la clase
    catchClause = TryExcept()

    ml_product1 = prompt.replace(" ", "-")
    ml_product2 = prompt.replace(" ", "%20")

    # Definir la URL del sitio web que se desea consultar
    url = f"https://listado.mercadolibre.com.mx/{ml_product1}#D[A:{ml_product2}]"

    # Inicializar Playwright y abrir un navegador
    with sync_playwright() as play:
        # browser = play.chromium.launch(headless=head, slow_mo=3*1000)
        browser = play.chromium.launch(headless=head)
        page = browser.new_page(user_agent=agenteUsuario())

        # Acceder a la página web
        page.goto(url)

        # Obtenemos todos los resultados de la pagina
        totalResults = "//li[contains(@class,'ui-search-layout__item')]"

        # Creamos los XPATH para cada elemento que vamos a obtener
        name = "//h2[contains(@class,'ui-search-item__title')]"
        id = "//input[@name='itemId']"
        price = "//div[@class='ui-search-price ui-search-price--size-medium shops__price']//div[@class='ui-search-price__second-line shops__price-second-line']//span[@class='price-tag-amount']//span"
        original_price = "//s[@class='price-tag ui-search-price__part ui-search-price__original-value shops__price-part price-tag__disabled']//span[@class='price-tag-amount']//span"
        flash_sale = "//label[@class='ui-search-styled-label ui-search-item__highlight-label__text' and contains(text(), 'OFERTA')]"
        rating = "//span[@class='ui-search-reviews__ratings']//*[contains(@class, 'star-full')]"
        rating_half = "//span[@class='ui-search-reviews__ratings']//*[contains(@class, 'star-half')]"
        rating_number = "//span[@class='ui-search-reviews__amount']"
        link = "//div[@class='ui-search-result__image shops__picturesStyles']//a"
        img = "//div[@class='ui-search-result__image shops__picturesStyles']//img"
        label = "//label[@class='ui-search-styled-label ui-search-item__highlight-label__text']"
        free_shipping = "//p[@class='ui-search-item__shipping ui-search-item__shipping--free shops__item-shipping-free']"
        is_full = "//*[@href='#full']"

        # Esperamos la carga total de la pagina, de lo contrario controlamos el error y mostramos un error
        try:
            page.wait_for_selector(totalResults, timeout=10*1000)
        except PlaywrightTimeoutError:
            print(f"Error al cargar contenido. Vuelva a intentarlo en unos minutos.. URL: {url}")

        # Comenzamos con la extraccion de datos
        for content in page.query_selector_all(totalResults):
            # Inicializamos las variables que requieren tratamiento especial
            real_price = ""
            real_original_price = ""
            real_rating = 0.0
            real_rating_number = 0
            real_flash_sale = False
            real_link = "-"
            real_img = "-"
            real_free_shipping = False
            real_is_full = False

            # Seccion de tratamiento especial de datos
            for single_element in content.query_selector_all(price):
                real_price += single_element.inner_text().strip()

            for single_element in content.query_selector_all(original_price):
                real_original_price += single_element.inner_text().strip()

            real_rating += len(content.query_selector_all(rating))

            if len(content.query_selector_all(rating_half)):
                real_rating += .5

            if "-" not in catchClause.text(content.query_selector(rating_number)):
                real_rating_number = int(catchClause.text(content.query_selector(rating_number)))

            if "#" in catchClause.attributes(content.query_selector(link), 'href'):
                real_link = catchClause.attributes(content.query_selector(link), 'href').split("#")[0]

            if len(content.query_selector_all(flash_sale)):
                real_flash_sale = True

            if "webp" in catchClause.attributes(content.query_selector(img), 'src'):
                real_img = catchClause.attributes(content.query_selector(img), 'src').replace("webp", "jpg")

            if len(content.query_selector_all(free_shipping)):
                real_free_shipping = True

            if len(content.query_selector_all(is_full)):
                real_is_full = True

            single_data = {
                "source": "mercado_libre",
                "name": catchClause.text(content.query_selector(name)),
                "id": catchClause.attributes(content.query_selector(id), 'value'),
                "price": real_price,
                "price_float": float(real_price.replace("$", "").replace(",", "")),
                "original_price": real_original_price,
                "flash_sale": real_flash_sale,
                "rating": real_rating,
                "rating_number": real_rating_number,
                "link": real_link,
                "img": real_img,
                "label": catchClause.text(content.query_selector(label)).lower().capitalize(),
                "free_shipping": real_free_shipping,
                "is_full_or_prime": real_is_full,
            }

            # Agregando información recolectada
            data.append(single_data)

        # Cerrar el navegador
        # browser.close()

    ####################################################################################################

    amnz_product = prompt.replace(" ", "=")

    # Definir la URL del sitio web que se desea consultar
    url = f"https://www.amazon.com.mx/s?k={amnz_product}"

    # Inicializar Playwright y abrir un navegador
    with sync_playwright() as play:
        # browser = play.chromium.launch(headless=head, slow_mo=3*1000)
        browser = play.chromium.launch(headless=head)
        page = browser.new_page(user_agent=agenteUsuario())

        # Acceder a la página web
        page.goto(url)

        # Obtenemos todos los resultados de la pagina
        totalResults = "//div[@data-component-type='s-search-result']"

        # Creamos los XPATH para cada elemento que vamos a obtener
        name = "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']"
        id = "data-asin"
        price = "//span[@data-a-color='base']/span[@class='a-offscreen']"
        original_price = "//span[@data-a-color='secondary']/span[@class='a-offscreen']"
        flash_sale = "//span[@data-a-badge-color='sx-lightning-deal-red']//span[@class='a-badge-text'][@data-a-badge-color='sx-cloud']"
        rating = "//span[@class='a-declarative']/a/i/span[@class='a-icon-alt']"
        # rating_half = "//span[@class='ui-search-reviews__ratings']//*[contains(@class, 'star-half')]"
        rating_number = "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style']/span[@class='a-size-base s-underline-text']"
        link = "//div[@class='ui-search-result__image shops__picturesStyles']//a"
        img = "//img[@class='s-image']"
        label = "//label[@class='ui-search-styled-label ui-search-item__highlight-label__text']"
        free_shipping = "//span[contains(@aria-label, 'GRATIS')]"
        is_prime = "//span[contains(@class, 's-prime')]"

        # Esperamos la carga total de la pagina, de lo contrario controlamos el error y mostramos un error
        try:
            page.wait_for_selector(totalResults, timeout=10*1000)
        except PlaywrightTimeoutError:
            print(f"Error al cargar contenido. Vuelva a intentarlo en unos minutos. URL: {url}")

        # Comenzamos con la extraccion de datos
        for content in page.query_selector_all(totalResults):
            real_price = catchClause.text(content.query_selector(price))
            real_price_float = 0.0
            real_flash_sale = False
            real_rating = 0.0
            real_rating_number = 0
            real_label = "-"
            real_link = "-"
            real_free_shipping = False
            real_is_prime = False

            if "-" not in real_price:
                real_price_float = float(catchClause.text(content.query_selector(price)).replace("$", "").replace(",", ""))

            if len(content.query_selector_all(flash_sale)):
                real_flash_sale = True

            if "-" not in catchClause.text(content.query_selector(rating)):
                real_rating = float(catchClause.text(content.query_selector(rating)).split(" ")[0])

            if "-" not in catchClause.text(content.query_selector(rating_number)):
                real_rating_number = int(re.sub(r"[()]", "", catchClause.text(content.query_selector(rating_number))).replace(",", ""))

            for single_label in content.query_selector_all(label):
                real_label += " " + single_label.strip()

            # if "-" not in catchClause.attributes(content.query_selector(name), 'href'):
            real_link = f"""http://www.amazon.com.mx{catchClause.attributes(content.query_selector(name), 'href')}"""
            real_link = '/'.join(real_link.split('/')[:6])

            if len(content.query_selector_all(free_shipping)):
                real_free_shipping = True

            if len(content.query_selector_all(is_prime)):
                real_is_prime = True

            single_data = {
                "source": "amazon",
                "name": catchClause.text(content.query_selector(name)),
                "id": catchClause.attributes(content, id),
                "price": real_price,
                "price_float": real_price_float,
                "original_price": catchClause.text(content.query_selector(original_price)),
                "flash_sale": real_flash_sale,
                "rating": real_rating,
                "rating_number": real_rating_number,
                "link": real_link,
                "img": f"""{catchClause.attributes(content.query_selector(img), 'src')}""",
                "label": real_label,
                "free_shipping": real_free_shipping,
                "is_full_or_prime": real_is_prime,
            }

            # Agregando información recolectada
            data.append(single_data)

        # Cerrar el navegador
        browser.close()
    return sorted(data, key=lambda x: x["price_float"], reverse=True)

# print(scraping("triangulo pikler", False))
