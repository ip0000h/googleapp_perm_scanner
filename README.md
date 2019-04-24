### googleapp_perm_scanner

## Описание
Приложение - тестовое задание для AppFlow, для некоммерческих целей(лицензия MIT).
Приложение состоит из 2-ух сервисов:
### crawler
Считывает входные данные из mongodb, производит парсинг данных из google play store и сохранение данных в базу данных.
### client
Клиентская часть для ввода данных и отображения результатов.

## Запуск
Для запуска требуется docker(>=17.06) и docker-compose(>=1.17.1).
Для старта выполните команду: `docker-compose up`.
Приложение будет доступно по адресу: http://localhost:8080/

## Live-Demo
[Ссылка на Live-Demo](http://45.76.84.107:8080/)