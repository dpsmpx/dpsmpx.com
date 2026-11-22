# Статус книги

<!-- book-gate:begin -->
book_writing: forbidden
steam_release_fact: none
permission_decision: none
<!-- book-gate:end -->

Книга не пишется (D-01). Работа над текстом разрешается, только когда
выполнены оба условия D-02:

1. есть активный факт с меткой `steam-release` о выпуске VoxelRPG в
   Steam (источник — страница игры в магазине Steam);
2. принято отдельное решение с меткой `book-permission`, которое
   ссылается на этот факт.

Тогда в блоке выше, в одном коммите с решением: `book_writing: allowed`,
`steam_release_fact: F-NNNN`, `permission_decision: D-NN`.
`tools/verify/check_book_gate.py` сверяет все три поля между собой, с
фактом, с решением и с этапом 5 (`docs/direction/ROADMAP/stage-5.md`).

До этого в `docs/book/` лежат только этот файл, `OUTLINE.md` (структура
без прозы) и `NON_GOALS.md`; других файлов и черновиков глав нет нигде в
репозитории.

Факта с меткой `steam-release` нет. Наблюдения о Steam на дату создания
репозитория — F-0032, F-0033, F-0034.
