# GitHub

Профиль `github.com/dpsmpx`, README — репозиторий `dpsmpx/dpsmpx`.
Состояние — аудит, §2.

## Модель

| Поле | Значение |
|---|---|
| Audience | профессиональная, разработчики, соавторы; EN |
| Purpose | визитка инженера; доказательство широты и метода |
| Primary content | PERSON (README профиля), открытые проекты |
| Secondary content | RELEASE/changelog открытых проектов; EDUCATION (гайд о методе — по решению автора) |
| Length | README профиля — экран-два: кто, что строю, как работаю, где следить |
| Visual format | баннер README 1280×640 (2:1); social preview репозиториев 1280×640, PNG/JPG < 1 МБ, лучше без прозрачности |
| CTA | «следите за разработкой: дневник / YouTube» |
| Posting rhythm | README — по вехам; открытые проекты — по ходу |
| Discoverability | поиск GitHub по темам; ссылки с других площадок |
| Retention mechanism | закреплённые репозитории; Follow |
| Cross-platform role | англоязычная точка входа (`CONTENT_STRATEGY.md`, §6) |

## Особенность: главные проекты закрыты

Galdhold и DPlang закрыты (Д17). Профессиональная оценка по GitHub
опирается на видимые следы работы (исследование Marlow & Dabbish, 2013:
`docs/research/developer_branding/DEVELOPER_BRANDING.md`) — у автора их
мало для главных проектов. Поэтому:

- в README профиля — результаты (видео, снимки), метод словами,
  числа с датой из реестра;
- ссылки — только на открытые адреса (не на 404);
- открытые малые проекты закрепить как широту.

## Черновик правок README профиля (ОР-4)

Текст правок — `TODO.md`, пункт «README профиля GitHub». Править
репозиторий `dpsmpx/dpsmpx` — только по согласию автора.

## Публикация и источник фактов

GitHub — прежде всего источник истины о софте: релизы и теги открытых
репозиториев → `data/releases/` (после проверки человеком) → черновик
кампании; публикация — release notes открытых проектов и README профиля
через PR, правку принимает автор (фаза П8; `docs/research/publishing/PLATFORM_APIS.md`, §5).

## Официальные источники

docs.github.com: «Customizing your repository's social media preview»
(≥ 640×320, лучше 1280×640, < 1 МБ), «Managing your profile README».
