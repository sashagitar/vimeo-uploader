<thinking>Для создания качественного `README.md` нужно описать шаги установки, конфигурации, использования программы и работы с переменными окружения для хранения конфиденциальных данных (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN). Описание также должно охватывать основные функции программы, включая загрузку видео на Vimeo и запись результатов в базу данных.</thinking>

<reflection>Программа загружает видео на Vimeo, управляет обработкой пачками и использует SQLite для хранения информации о видео. Конфиденциальные данные нужно хранить в `.env`, и `README.md` должен содержать инструкции для этого. Описание должно быть простым и понятным.</reflection>

<output>

# Видео-обработчик с загрузкой на Vimeo

Эта программа позволяет загружать видео на Vimeo из базы данных SQLite и сохранять ссылки на загруженные видео обратно в базу данных. Она поддерживает обработку видео пачками и обеспечивает продолжение работы с того места, где процесс был завершен ранее.

## Требования

- Python 3.7+
- Установленные библиотеки: `sqlite3`, `vimeo`, `tqdm`, `logging`, `dotenv`

## Установка

1. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/sashagitar/vimeo-uploader.git
   cd vimeo-uploader
   ```

2. Создайте виртуальное окружение (рекомендуется):

   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate  # для Windows
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта и добавьте в него следующие переменные:

   ```bash
   CLIENT_ID=your_vimeo_client_id
   CLIENT_SECRET=your_vimeo_client_secret
   ACCESS_TOKEN=your_vimeo_access_token
   DB_PATH=your_database_path
   ```

5. Убедитесь, что у вас есть база данных SQLite, в которой содержатся таблицы с видео для загрузки. Таблица `videos` должна иметь следующие поля:
   - `file_path`: путь к файлу видео
   - `title`: заголовок видео
   - `description`: описание видео
   - `vimeo_link`: ссылка на Vimeo (обновляется после загрузки)

## Использование

1. Подготовьте базу данных, которая содержит информацию о видео для загрузки.

   ### Пример структуры базы данных

   Таблица `videos`:

   ```sql
   CREATE TABLE IF NOT EXISTS videos (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       file_path TEXT,
       title TEXT,
       description TEXT,
       vimeo_link TEXT
   );
   ```

2. Запустите программу для обработки видео и загрузки на Vimeo:

   ```bash
   python upload_vimeo.py
   ```

   Программа будет загружать видео пачками, начиная с последнего загруженного, и обновлять ссылки на Vimeo в базе данных.

## Конфигурация

- **CLIENT_ID**, **CLIENT_SECRET**, **ACCESS_TOKEN**, **DB_PATH**: эти переменные хранят ваши учетные данные для доступа к API Vimeo. Они должны быть добавлены в файл `.env`.

## Логирование

Логи процесса загрузки сохраняются в файл `video_processing.log`, который содержит информацию об ошибках и скорости загрузки.

## Дополнительные настройки

Вы можете изменить размер пачки для обработки видео, изменив параметр `batch_size` в функции `process_videos_from_database()`.

## Мои контакты

<a href="https://vk.com/hidden_by.the_devil">
<img src="https://sun6-20.userapi.com/s/v1/ig2/xgv1nev3R0LQwj1ixmxgSuVZWK-_r7kh2VQeyFofgymTmF6Mi1YMaKS5Sf3hVqZIstdKGfHzEa3XxTWtay-NTgiD.jpg?size=50x50&amp;quality=95&amp;crop=352,256,1224,1224&amp;ava=1" alt="Александр">
</a>

Email: DAI.20@uni_dubna.ru
