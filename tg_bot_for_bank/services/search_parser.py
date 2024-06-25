import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_belarusbank(query):
    url = 'https://belarusbank.by/ru/search_site'
    params = {'whotsearch': query}

    logger.info('Отправка запроса к %s с параметрами %s', url, params)
    response = requests.get(url, params=params)

    if response.status_code == 200:
        logger.info('Запрос выполнен успешно, код ответа: %d', response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск секции с результатами
        results_section = soup.find('section', class_='page-section')
        if not results_section:
            logger.warning('Секция с результатами не найдена')
            return 'Ничего не найдено 1'

        results = []
        arr_results = []
        for index, result in enumerate(results_section.find_all('div', class_='search-item flc'), start=1):
            title_element = result.find('h3', class_='search-item__title')
            title = title_element.text.strip() if title_element else 'Без названия'
            link_element = title_element.find('a') if title_element else None
            link = link_element['href'] if link_element else '#'
            description_element = result.find('div', class_='search-item__descr')
            description = description_element.text.strip() if description_element.text else 'Без описания'
            results.append(f'<a href="https://belarusbank.by{link}">{title}</a>\n{description}')

            if index % 20 == 0:
                arr_results.append('\n\n'.join(results))
                results = []

        if results:
            arr_results.append('\n\n'.join(results))
        if arr_results:
            #logger.info('Найдено %d результатов', len(index))
            return arr_results
        else:
            logger.warning('Результаты не найдены')
            return ['Ничего не найдено']
    else:
        logger.error('Ошибка при выполнении запроса, код ответа: %d', response.status_code)
        return 'Ошибка при выполнении запроса'
