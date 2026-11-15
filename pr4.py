import aiohttp
import asyncio
import json
from datetime import datetime

# Ссылки на API (для марок и для типов кузовов)
URL_MAKES = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
URL_TYPES = "https://vpic.nhtsa.dot.gov/api/vehicles/getvehicletypesformake/audi?format=json"

# Семафор для ограничения одновременных запросов (максимум 3)
sem = asyncio.Semaphore(3)


async def fetch_data(session, url):
    """Делает запрос с таймаутом и обработкой ошибок."""
    async with sem:
        try:
            # Таймаут 5 секунд
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка HTTP {response.status} при запросе {url}")
        except asyncio.TimeoutError:
            print(f"Таймаут при запросе {url}")
        except Exception as e:
            print(f"Ошибка: {e} при запросе {url}")
        return None


async def main():
    async with aiohttp.ClientSession() as session:
        # Запускаем оба запроса параллельно
        results = await asyncio.gather(
            fetch_data(session, URL_MAKES),
            fetch_data(session, URL_TYPES)
        )

        makes_data, types_data = results

        # Формируем итоговый словарь
        final_data = {
            "car_makes": makes_data,
            "car_types": types_data,
            "timestamp": datetime.now().isoformat()
        }

        # Сохраняем в JSON
        if makes_data or types_data:
            with open("cars_data.json", "a", encoding="utf-8") as file:
                file.write(json.dumps(final_data, ensure_ascii=False, indent=4) + "\n")
            print("Данные сохранены в cars_data.json")
        else:
            print("Данные не получены, сохранение пропущено.")


if __name__ == "__main__":
    asyncio.run(main())