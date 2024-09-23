import os
import csv
import time
import signal
from tqdm import tqdm
import logging
import sqlite3
import vimeo
from typing import Optional

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def get_video_path(db_path: str, upload_url: str) -> Optional[str]:
    """
    Получает путь к видеофайлу из базы данных по заданному URL для загрузки.

    :param db_path: Путь к базе данных SQLite.
    :param upload_url: URL для загрузки видео.
    :return: Путь к видеофайлу или None, если файл не найден.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем путь к видео из таблицы videos
    cursor.execute("SELECT file_path FROM videos WHERE upload_url = ?", (upload_url,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None

def get_vimeo_client(client_id: str, client_secret: str, access_token: str) -> vimeo.VimeoClient:
    """
    Создает экземпляр Vimeo клиента для работы с API.

    :param client_id: Идентификатор клиента Vimeo.
    :param client_secret: Секрет клиента Vimeo.
    :param access_token: Токен доступа к API Vimeo.
    :return: Экземпляр VimeoClient.
    """
    return vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
    )

def update_video_with_vimeo_link(db_path: str, file_path: str, vimeo_link: Optional[str]) -> None:
    """
    Обновляет запись в базе данных, добавляя ссылку на Vimeo для загруженного видео.

    :param db_path: Путь к базе данных SQLite.
    :param file_path: Путь к видеофайлу.
    :param vimeo_link: Ссылка на видео на Vimeo.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Обновляем запись с добавлением ссылки на Vimeo
    cursor.execute('''
        UPDATE videos
        SET vimeo_link = ?
        WHERE file_path = ?
    ''', (vimeo_link, file_path))

    conn.commit()
    conn.close()

def upload_video(client: vimeo.VimeoClient, video_file_path: str, title: str, description: str) -> Optional[str]:
    """
    Загружает видео на Vimeo и возвращает ссылку на него.

    :param client: Экземпляр VimeoClient.
    :param video_file_path: Путь к видеофайлу.
    :param title: Заголовок видео.
    :param description: Описание видео.
    :return: Ссылка на загруженное видео или None в случае ошибки.
    """
    try:
        # Загрузка видео
        uri = client.upload(video_file_path, data={
            'name': title,
            'description': description
        }, timeout=5)

        # Публикация видео
        client.patch(uri, data={'privacy': {'view': 'anybody'}})

        # Получаем ссылку на загруженное видео
        response = client.get(f'{uri}?fields=link').json()
        return response.get('link')

    except Exception as e:
        print(f"Произошла ошибка при загрузке видео: {e}")
        return None

def get_last_processed_video(db_path: str) -> Optional[int]:
    """
    Получает ID последнего обработанного видео с непустой ссылкой на Vimeo.

    :param db_path: Путь к базе данных SQLite.
    :return: ID последнего обработанного видео или None, если таких видео нет.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем ID последнего обработанного видео
    cursor.execute('''
        SELECT id FROM videos WHERE vimeo_link IS NOT NULL ORDER BY id DESC LIMIT 1
    ''')
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def process_videos_from_database(db_path: str, client: vimeo.VimeoClient, batch_size: int = 10) -> None:
    """
    Обрабатывает и загружает видео из базы данных пачками, начиная с последнего загруженного.

    :param db_path: Путь к базе данных SQLite.
    :param client: Экземпляр VimeoClient для загрузки видео.
    :param batch_size: Количество видео для обработки в одной пачке.
    """
    last_processed_video_id = get_last_processed_video(db_path)

    logging.basicConfig(filename='video_processing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем все записи из таблицы videos, начиная с последнего загруженного видео
    if last_processed_video_id:
        cursor.execute("SELECT id, upload_url, file_path, title, description FROM videos WHERE id > ? AND upload_url IS NOT NULL AND vimeo_link IS NULL ORDER BY id ASC LIMIT ?", 
                       (last_processed_video_id, batch_size))
    else:
        cursor.execute("SELECT id, upload_url, file_path, title, description FROM videos WHERE upload_url IS NOT NULL AND vimeo_link IS NULL ORDER BY id ASC LIMIT ?", 
                       (batch_size,))
    
    rows = cursor.fetchall()
    
    while rows:
        with tqdm(total=len(rows), desc="Загрузка видео", unit="video") as pbar:
            for row in rows:
                video_id, upload_url, video_file_path, title, description = row

                if not os.path.exists(video_file_path):
                    logging.error(f"Файл не найден: {video_file_path}")
                    continue

                start_time = time.time()
                vimeo_link = upload_video(client, video_file_path, title, description)

                if vimeo_link:
                    update_video_with_vimeo_link(db_path, video_file_path, vimeo_link)
                else:
                    logging.error(f"Не удалось загрузить видео: {video_file_path}")

                file_size_mb = os.path.getsize(video_file_path) / (1024 * 1024)
                elapsed_time = time.time() - start_time
                speed_mbps = file_size_mb / elapsed_time

                pbar.set_postfix({"MB/s": f"{speed_mbps:.2f}"})
                pbar.update(1)

        # Получаем следующую пачку видео
        last_processed_video_id = rows[-1][0]
        cursor.execute("SELECT id, upload_url, file_path, title, description FROM videos WHERE id > ? AND upload_url IS NOT NULL AND vimeo_link IS NULL ORDER BY id ASC LIMIT ?", 
                       (last_processed_video_id, batch_size))
        rows = cursor.fetchall()

    conn.close()

if __name__ == "__main__":
    DB_PATH = os.getenv('DB_PATH') 
    client = get_vimeo_client(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)

    # Обрабатываем видео пачками
    process_videos_from_database(DB_PATH, client)
