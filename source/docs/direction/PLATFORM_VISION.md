# DP Content Platform — постановка автора

**Что это.** Постановка автора от 4 октября 2026 — дословно, без правок
смысла; разбита по разделам только для навигации. Единственная правка —
имя автора заменено на `dpsmpx` (5 октября 2026, Д40: имени нет нигде). Это **вход**, а не
решение: решения по ней — `docs/direction/DECISIONS.md` (Д12 пересмотрен,
Д20–Д33, ОР-11), где что реализовано и какая задача за каким разделом —
`docs/direction/PLATFORM_TRACE.md`, план — `ROADMAP/ROADMAP.md`.

Ответы автора на вопросы сессии 04.10.2026 (сверка с решениями по
`CLAUDE.md`):

| Вопрос | Ответ автора | Где записано |
|---|---|---|
| Публикация системой расходится с Д12 | пересмотреть Д12: публикуется только одобренная автором версия; токены — только у автора; по умолчанию dry-run и тестовый канал; автопубликации нет; первая площадка — Telegram | Д12 |
| Настоящее имя в постановке (ОР-1) | открыть имя; 05.10.2026 — отменено: имени нет нигде | Д20 → Д40 |
| Где рабочий сайт | `dpsmpx.com` | Д21, ОР-11 |
| Язык сайта | русский основной; главная, «обо мне» и проекты — ещё и на английском | Д21 |

---

## Вступление

```text
DP CONTENT PLATFORM — ЕДИНАЯ СИСТЕМА ПУБЛИКАЦИИ, АДАПТАЦИИ И ДИСТРИБУЦИИ КОНТЕНТА
Ты продолжаешь работу над репозиторием системы генерации контента для "dpsmpx".
Проект должен эволюционировать из простого repository для генерации отдельных материалов в единую контентную платформу автора.
Главная стратегическая цель:
«создать собственную единую точку публикации, которая является источником истины для новостей и контента автора, а затем автоматически и контролируемо распространяет адаптированные версии на сайт, Telegram, VK, YouTube, Discord, GitHub и другие поддерживаемые площадки.»
Это не должно быть простым «кросспостинг-ботом».
Нужна полноценная редакционно-техническая система:
Author / Projects
        ↓
Research / Facts
        ↓
Editorial Core
        ↓
Canonical Content
        ↓
Adaptation
        ↓
Validation
        ↓
Approval
        ↓
Website
        ↓
Platform Adapters
        ↓
Social Publication
        ↓
Analytics
        ↓
Feedback
        ↓
Content Strategy
Главный принцип:
«контент создаётся один раз как каноническая сущность, а не отдельно для каждой платформы.»
Социальные сети являются downstream channels.
```

## 1. Важнейший принцип

```text
Система должна работать как:
ONE SOURCE OF TRUTH
        ↓
MANY NATIVE REPRESENTATIONS
а не:
Telegram post
→ copy
→ VK
→ Discord
→ YouTube
Канонический материал должен существовать независимо от конкретной платформы.
Например:
Canonical Story
   ├── website article
   ├── Telegram post
   ├── VK post
   ├── Discord update
   ├── YouTube description
   ├── YouTube short concept
   └── GitHub release note
При этом каждая производная версия может:
- отличаться по длине;
- иметь другой CTA;
- менять порядок информации;
- сокращать техническую часть;
- добавлять платформенный контекст;
- иметь собственный media format.
```

## 2. Сначала провести research

```text
Перед архитектурой изучить актуальное состояние:
Website
Исследовать:
- современные подходы к creator-owned websites;
- headless CMS;
- static publishing;
- hybrid static/dynamic architectures;
- RSS/Atom;
- JSON feeds;
- sitemap;
- SEO;
- Open Graph;
- structured metadata;
- canonical URLs;
- email/newsletter possibilities;
- media storage;
- search;
- archive;
- tags;
- project pages;
- changelog pages.
---
Telegram
Изучить актуальные способы:
- публикации;
- редактирования;
- media upload;
- link generation;
- bot API;
- channel limitations;
- admin permissions;
- message editing;
- threading/comments;
- scheduling.
---
VK
Исследовать актуальный официальный API и возможности:
- создание постов;
- публикация media;
- редактирование;
- scheduled posting;
- albums/photos;
- videos;
- communities;
- authorization;
- permissions;
- rate limits.
Отдельно проверить, что можно делать:
- автоматически;
- полуавтоматически;
- только через UI;
- только владельцем аккаунта.
---
YouTube
Исследовать:
- YouTube Data API;
- upload;
- metadata;
- thumbnails;
- playlists;
- scheduling;
- Shorts;
- analytics APIs;
- OAuth;
- quotas;
- restrictions;
- current API capabilities.
Не предполагать, что любой YouTube workflow можно автоматизировать без ограничений.
---
Discord
Исследовать:
- bot API;
- webhooks;
- posting;
- embeds;
- attachments;
- threads;
- forum channels;
- announcements;
- scheduled events;
- permissions;
- rate limits.
Отдельно разделить:
author account
bot
webhook
server
community features
---
GitHub
Исследовать:
- Releases;
- Discussions;
- Issues;
- README updates;
- API;
- GitHub Apps;
- tokens;
- webhooks;
- release automation.
Но не превращать GitHub в обычную social platform.
GitHub должен оставаться прежде всего:
- source of truth для software;
- release source;
- technical documentation source.
```

## 3. Ключевой вывод research

```text
Не предполагать, что все платформы поддерживают одинаковую автоматизацию.
Создать матрицу:
docs/platforms/PUBLISHING_CAPABILITY_MATRIX.md
с:
Platform| Read| Create| Edit| Delete| Media| Schedule| Analytics| OAuth/API| Automation level
Разделить:
FULLY AUTOMATED
SEMI-AUTOMATED
MANUAL APPROVAL REQUIRED
MANUAL ONLY
UNSUPPORTED
Если официальный API меняется — обновлять matrix, а не ломать архитектуру.
```

## 4. Website должен быть central hub

```text
Создать собственный сайт автора как главную точку присутствия.
Не делать его просто «ещё одной социальной сетью».
Сайт должен быть:
Author
+
Projects
+
News
+
Devlog
+
Articles
+
Media
+
Releases
+
Links
```

## 5. Website information architecture

```text
Предварительно:
/
├── home
├── about
├── projects
│   ├── galdhold
│   ├── dplang
│   └── other
├── news
├── devlog
├── articles
├── releases
├── media
├── downloads
├── contact
├── rss.xml
├── sitemap.xml
└── api/
Измени структуру после исследования.
```

## 6. Home page

```text
Главная страница должна сразу отвечать:
«Кто этот человек?»
«Что он делает?»
«Какие проекты у него главные?»
«Почему за ним интересно следить?»
Порядок приоритетов:
Author
↓
Current main project
↓
Selected other projects
↓
Latest news
↓
Current work
↓
Social links
Не делать домашнюю страницу свалкой всех материалов.
```

## 7. Project pages

```text
Каждый серьёзный проект должен иметь canonical project page.
Например:
/projects/galdhold
/projects/dplang
На странице:
title
short description
status
platforms
technology
screenshots
videos
latest news
roadmap
repository
download
related articles
Все project-specific content objects должны ссылаться на canonical project entity.
```

## 8. News model

```text
Нужна полноценная сущность:
NewsItem
Например:
NewsItem
├── id
├── slug
├── title
├── summary
├── body
├── author
├── date
├── projects
├── tags
├── category
├── media
├── sources
├── claims
├── status
└── publication_targets
```

## 9. Canonical content model

```text
Расширить предыдущий "ContentItem".
CanonicalContent
├── id
├── type
├── title
├── summary
├── body
├── language
├── author
├── source_projects
├── content_pillars
├── audience
├── claims
├── evidence
├── media
├── links
├── CTA
├── publication_policy
├── platform_variants
├── status
├── timestamps
└── provenance
Canonical content не должен содержать platform-specific formatting.
```

## 10. Derived content

```text
Создать отдельный объект:
PlatformVariant
Например:
CanonicalContent
        ↓
TelegramVariant
VKVariant
DiscordVariant
YouTubeVariant
WebsiteVariant
GitHubVariant
Каждая версия хранит:
platform
format
text
media
CTA
status
published_url
publication_id
published_at
version
```

## 11. Content relation graph

```text
Контент должен быть связан:
Project
   ↓
Release
   ↓
News
   ↓
Article
   ↓
Social posts
   ↓
Video
Например:
Galdhold v0.8
  ├── release
  ├── news article
  ├── Telegram announcement
  ├── VK announcement
  ├── Discord update
  ├── YouTube video
  └── GitHub release
Это позволит потом увидеть всю кампанию целиком.
```

## 12. Content campaign

```text
Ввести сущность:
ContentCampaign
Пример:
Campaign: Galdhold v1.0 announcement
Содержит:
objective
launch date
canonical story
assets
platform variants
publication schedule
analytics
results
```

## 13. Publication pipeline

```text
Основной production pipeline:
IDEA
↓
RESEARCH
↓
CANONICAL DRAFT
↓
FACT CHECK
↓
EDITORIAL REVIEW
↓
MEDIA GENERATION
↓
PLATFORM ADAPTATION
↓
PLATFORM VALIDATION
↓
APPROVAL
↓
SCHEDULE
↓
PUBLISH
↓
VERIFY
↓
MEASURE
```

## 14. Publication states

```text
Минимально:
DRAFT
RESEARCHED
READY_FOR_REVIEW
APPROVED
SCHEDULED
PUBLISHING
PUBLISHED
FAILED
RETRY
SUPERSEDED
ARCHIVED
Никогда не смешивать:
content approved
и:
publication successful
```

## 15. Transactional publishing

```text
Публикация должна быть максимально безопасной.
Модель:
prepare
↓
validate
↓
publish
↓
verify
↓
record
Если публикация не удалась:
FAILED
а не:
SUCCESS
```

## 16. Idempotency

```text
Это критически важно.
Если pipeline запустился дважды, он не должен публиковать один и тот же пост два раза.
Каждая публикация должна иметь:
publication_id
content_id
platform
variant_version
idempotency_key
```

## 17. Retry policy

```text
Повторные попытки должны быть:
bounded
exponential backoff
idempotent
auditable
Не делать бесконечные retry.
```

## 18. Failure handling

```text
Платформа может:
- быть недоступна;
- изменить API;
- вернуть auth error;
- изменить rate limit;
- отклонить media;
- отклонить текст;
- вернуть unknown error.
Все они должны превращаться в structured error.
Например:
AUTH_EXPIRED
RATE_LIMITED
MEDIA_REJECTED
INVALID_CONTENT
PERMISSION_DENIED
PLATFORM_UNAVAILABLE
UNKNOWN_PLATFORM_ERROR
```

## 19. Human approval gate

```text
Хотя система должна быть автоматизированной, публикация потенциально репутационно значимого контента не должна происходить без контроля автора, пока не появятся доказанные правила автоматической публикации.
По умолчанию:
generate
→ adapt
→ validate
→ WAIT_FOR_HUMAN_APPROVAL
→ publish
Автоматическая публикация допускается только для классов контента, для которых отдельно принято решение.
```

## 20. Content safety

```text
Создать автоматические проверки:
Factuality
Trademark / branding
Copyright
Privacy
Personal data
Security
Claims
Links
Platform restrictions
```

## 21. Source of truth для фактов

```text
Не позволять AI самостоятельно придумывать:
- project metrics;
- dates;
- releases;
- technology claims;
- downloads;
- user numbers;
- performance numbers.
Для таких данных использовать:
PROJECT_FACTS
RELEASE_DATA
EVIDENCE
```

## 22. Automatic fact injection

```text
Например:
canonical content:
"new release"
template engine:
current version
release date
platform
download link
GitHub release
Данные берутся из structured source, а не переписываются вручную.
```

## 23. Content regeneration

```text
Если:
- release version изменилось;
- link изменился;
- screenshot обновлён;
- project status изменился;
system должна определить затронутый derived content.
Например:
ProjectFact changed
↓
affected canonical content
↓
affected platform variants
↓
mark as stale
Это очень важный механизм.
```

## 24. Stale content detection

```text
Каждый material должен иметь зависимости.
Например:
Post #81
depends on:
  Galdhold v0.8
  screenshot #14
  GitHub release #22
Если release #22 изменён:
Post #81 → STALE
```

## 25. Website as canonical archive

```text
Даже если Telegram пост удалён или VK изменил API, сайт должен хранить собственный:
published content history
Website должен быть permanent archive.
```

## 26. Versioned content

```text
Каждое изменение canonical content:
v1
v2
v3
Производные версии должны знать:
source_version
```

## 27. Content diff

```text
Должна существовать возможность увидеть:
what changed
между двумя версиями.
```

## 28. Cross-platform campaign control

```text
Для каждой новости система должна уметь показать:
Website        ✓ published
Telegram       ✓ published
VK             ✓ published
Discord        ✓ published
YouTube        pending
GitHub         not applicable
То есть campaign dashboard.
```

## 29. Platform adapter interface

```text
Не писать:
if telegram
if vk
if discord
по всей системе.
Использовать:
PlatformAdapter
Например:
publish()
edit()
delete()
uploadMedia()
validate()
getStatus()
Каждый адаптер реализует конкретную платформу.
```

## 30. Authentication architecture

```text
Каждая платформа должна иметь отдельный credential boundary.
Никогда не хранить access tokens в Git.
Использовать:
- environment variables;
- local secret store;
- encrypted credentials;
- platform OAuth where available.
```

## 31. Credential rotation

```text
Сразу продумать:
expired token
refresh
re-authentication
revocation
replacement
Credential loss не должен ломать весь pipeline.
```

## 32. Website technology

```text
Исследуй минимум три архитектуры:
A
Static site + generator
B
Headless CMS + frontend
C
Custom content backend + frontend
Сравнить:
- complexity;
- maintenance;
- cost;
- hosting;
- performance;
- security;
- extensibility;
- automation;
- portability.
Не выбирать custom backend только потому, что это интереснее технически.
```

## 33. Recommended default bias

```text
Предпочтение отдавать:
simple
portable
low-cost
self-hostable
version-controlled
API-first
Сайт не должен требовать сложного backend infrastructure, если статическая архитектура решает задачу.
```

## 34. RSS / Atom

```text
Сайт должен публиковать:
RSS
Atom
JSON Feed
если это оправдано текущей ecosystem.
Это позволит другим системам подписываться на canonical news.
```

## 35. API

```text
Если это оправдано архитектурой, создать versioned API:
/api/v1/
Например:
GET /projects
GET /projects/{id}
GET /news
GET /news/{id}
GET /releases
GET /media
GET /feeds
Но не строить API ради API.
```

## 36. Webhooks

```text
Исследовать event-driven модель:
release created
→ content campaign created
→ canonical article generated
→ social variants generated
Например:
GitHub Release
        ↓
Webhook
        ↓
Content Pipeline
        ↓
Draft campaign
Но автоматическая публикация должна проходить через соответствующие gates.
```

## 37. Project integration

```text
Изучить возможность получать факты автоматически из GitHub:
release
tag
commit
milestone
README
public metrics
Но не публиковать raw GitHub information напрямую.
GitHub data → normalized project facts → editorial content.
```

## 38. Content autogeneration from events

```text
Подготовить архитектуру для:
new release
new milestone
new feature
new video
new article
project state change
major performance result
которые могут создавать draft campaigns.
```

## 39. Media management

```text
Создать media asset model:
MediaAsset
├── id
├── type
├── source
├── dimensions
├── format
├── project
├── license
├── provenance
├── variants
└── usage
```

## 40. Media variants

```text
Хранить:
master
website
telegram
vk
youtube_thumbnail
discord
github
Не генерировать каждый раз заново.
```

## 41. Image quality

```text
Для generated images:
- check dimensions;
- check file format;
- detect accidental artifacts;
- detect unreadable text;
- check subject consistency;
- check brand consistency.
```

## 42. Video pipeline

```text
Подготовить abstraction для:
VideoAsset
но полноценный production video pipeline можно оставить позже.
```

## 43. Content cache

```text
AI generation может быть дорогой.
Нужны:
- prompt hash;
- input hash;
- source context hash;
- model identifier;
- generation parameters;
- result hash.
Если один и тот же material запрошен повторно без изменения inputs — использовать cache.
```

## 44. Model independence

```text
Не связывать content system с одной AI model.
Должна существовать abstraction:
GenerationProvider
Например:
Claude
OpenAI
Grok
local model
image model
video model
Но реальные adapters добавляются только при необходимости.
```

## 45. AI output is untrusted input

```text
Любой AI output считать:
UNVERIFIED
до прохождения проверки.
Это фундаментальный security/quality principle.
```

## 46. Content validator

```text
Создать:
ContentValidator
который проверяет:
- required fields;
- facts;
- references;
- claims;
- prohibited patterns;
- platform constraints;
- links;
- provenance.
```

## 47. Publication audit log

```text
Каждая публикация должна оставлять:
content_id
platform
variant
timestamp
result
remote_id
remote_url
error
author approval
Это позволит восстановить историю.
```

## 48. Website deployment

```text
Deployment должен быть:
commit
→ build
→ validation
→ preview
→ publish
Если preview system возможна — использовать её.
```

## 49. Content preview

```text
Для каждой campaign должно быть возможно посмотреть:
Website preview
Telegram preview
VK preview
Discord preview
YouTube preview
до публикации.
```

## 50. Rendered preview

```text
Особенно для visual content:
не ограничиваться Markdown preview.
Нужно по возможности показывать:
actual final layout
```

## 51. Publication safety

```text
Перед публикацией система должна проверить:
Correct account
Correct destination
Correct language
Correct links
Correct media
Correct timing
Correct content version
```

## 52. Wrong-account protection

```text
Это критически важно.
Если одновременно существуют:
personal Telegram
project Telegram
Discord author
Discord project
YouTube author
YouTube project
pipeline должна иметь явный:
channel_id
account_id
platform_id
и никогда не выводить destination из имени пользователя или свободного текста.
```

## 53. Dry-run mode

```text
У любой публикации должен быть режим:
DRY RUN
Он:
- генерирует;
- адаптирует;
- валидирует;
- показывает destination;
но ничего не публикует.
```

## 54. Safe mode

```text
Также:
SAFE MODE
публикует только на:
- test account;
- private/test channel;
- staging server;
- unlisted website.
Это позволит тестировать pipeline без реального риска.
```

## 55. Sandbox environment

```text
Создать:
development
staging
production
не смешивать credentials.
```

## 56. Idempotent tests

```text
Тестировать:
publish once
publish twice
retry after timeout
token expiration
partial campaign failure
network failure
duplicate webhook
```

## 57. Rate limiting

```text
Каждый adapter должен иметь:
rate limiter
retry policy
backoff policy
Не реализовывать это централизованным способом, если ограничения платформ сильно различаются.
```

## 58. Analytics

```text
Собрать normalized analytics model:
Impression
View
Click
Reaction
Comment
Share
Subscriber
Conversion
Retention
Привязывать к:
campaign
content
variant
platform
publication
```

## 59. Analytics must not define content truth

```text
Метрики отвечают:
«что произошло.»
Они не отвечают автоматически:
«почему это произошло.»
AI может помогать анализировать, но вывод должен быть помечен как interpretation.
```

## 60. Experimentation

```text
Поддержать:
Experiment
например:
title A/B
thumbnail A/B
opening paragraph
CTA
post length
image composition
```

## 61. Content feedback loop

```text
Финальная архитектура:
content
↓
publication
↓
metrics
↓
analysis
↓
strategy adjustment
↓
next content
```

## 62. Self-improvement, but not autonomous drift

```text
Система может рекомендовать:
««технические посты получают больше сохранений»»
но не должна сама менять стратегию навсегда.
Стратегические изменения требуют human approval.
```

## 63. Content governance

```text
Создать:
docs/content/GOVERNANCE.md
описать:
- кто может публиковать;
- какие материалы требуют approval;
- какие можно публиковать автоматически;
- как отменяется публикация;
- кто отвечает за facts;
- кто отвечает за visual quality.
```

## 64. Content retention

```text
Определить:
- сколько хранить rejected variants;
- сколько хранить drafts;
- какие media архивировать;
- что является immutable record;
- что можно удалить.
```

## 65. Backup

```text
Контентная система должна резервироваться отдельно от social platforms.
Минимум:
Git repository
+
local backup
+
offsite backup
Social media не являются backup.
```

## 66. Disaster recovery

```text
Должен существовать документ:
docs/operations/DISASTER_RECOVERY.md
Сценарии:
website lost
repository lost
credential lost
platform API changed
AI provider unavailable
media storage lost
database corrupted
```

## 67. Platform outage

```text
Если Telegram/API/VK/YouTube недоступен:
canonical content remains safe
publication becomes pending
automatic retry later
Система не должна терять основной material.
```

## 68. Offline-first editorial core

```text
По возможности редакционный контент должен быть usable без внешних APIs.
То есть:
content creation
fact storage
drafting
editing
versioning
preview
не должны зависеть от Telegram/VK/YouTube.
```

## 69. Platform adapters must be replaceable

```text
Если VK API изменился:
replace VK adapter
а не переписывать:
- content model;
- campaign system;
- website;
- analytics model.
```

## 70. Monolith vs modules

```text
Исследовать:
single application
modular monolith
microservices
Для текущего масштаба по умолчанию предпочитать modular monolith, если research не докажет необходимость distributed architecture.
Не вводить microservices ради «масштабируемости».
```

## 71. Initial implementation

```text
Не реализовывать сразу все платформы.
Сначала построить вертикальный срез:
Canonical Content
↓
Website
↓
One social adapter
↓
Publication tracking
↓
Analytics placeholder
После этого подключать остальные платформы.
```

## 72. First vertical slice

```text
Первый рабочий путь:
create news
→ validate
→ publish to website
→ generate Telegram variant
→ preview
→ human approval
→ publish to Telegram
→ record result
Только после того, как этот путь надёжен, расширять систему.
```

## 73. Second slice

```text
same canonical news
→ VK adaptation
→ approval
→ publication
→ audit
```

## 74. Third slice

```text
campaign
→ multiple platforms
→ scheduling
→ partial failure
→ retry
→ dashboard
```

## 75. Dashboard

```text
Позже создать web UI:
Drafts
Calendar
Campaigns
Publications
Platforms
Failures
Analytics
Media
Projects
```

## 76. Content calendar

```text
Сделать календарь:
date
campaign
platform
status
asset
approval
Но calendar должен быть derived view над content model, а не отдельной системой данных.
```

## 77. Content search

```text
Добавить search по:
project
tag
date
platform
content type
campaign
status
```

## 78. Localization

```text
Система должна быть готова минимум к:
Russian
English
Но canonical meaning должен быть один.
canonical semantic content
↓
ru variant
en variant
Не делать два независимых source-of-truth текста.
```

## 79. Link management

```text
Canonical URLs должны быть стабильными.
Social variants могут использовать tracking links, но canonical URL должен оставаться независимым.
```

## 80. UTM / tracking

```text
Исследовать:
- UTM;
- campaign IDs;
- platform IDs;
- link shorteners;
- first-party analytics.
Не внедрять tracking, который ухудшает privacy или создаёт ненужную зависимость.
```

## 81. SEO

```text
Исследовать и внедрить только необходимое:
- title;
- meta description;
- Open Graph;
- canonical;
- sitemap;
- structured data;
- robots;
- RSS.
```

## 82. Social discovery

```text
Каждая canonical article/news page должна иметь:
- OG image;
- title;
- description;
- canonical URL.
Чтобы её публикация в социальных сетях выглядела нормально.
```

## 83. Content as API resource

```text
В перспективе:
website
social adapters
mobile app
newsletter
Discord bot
должны читать один content source.
```

## 84. Email / newsletter

```text
Подготовить architecture extension point, но не реализовывать сейчас, если нет реальной необходимости.
```

## 85. Future mobile app

```text
Не строить её сейчас.
Но content API не должен исключать её в будущем.
```

## 86. AI agents

```text
Возможна роль нескольких специализированных агентов:
Research agent
Editorial agent
Fact-check agent
Visual agent
Platform adapter agent
Analytics agent
Но:
агенты не должны иметь unrestricted write access к production publishing layer.
Например:
AI → draft
AI → review
AI → propose
Human/system policy → approve
Publisher → publish
```

## 87. Permission model

```text
Даже внутри собственного приложения предусмотреть роли:
Reader
Editor
Reviewer
Publisher
Admin
AI обычно:
Generator
Reviewer
но не unrestricted Admin.
```

## 88. Audit trail

```text
Каждое изменение:
who
what
when
source
version
должно быть восстановимо.
```

## 89. Content diff + provenance

```text
Для каждого published asset должна существовать цепочка:
source facts
→ canonical content
→ AI generation
→ human edits
→ platform adaptation
→ final publication
```

## 90. Legal safety

```text
Платформенные логотипы, screenshots, фотографии, third-party assets и generated assets должны иметь provenance.
Не использовать API scraping, если официальный API существует.
Не обходить:
- authentication;
- platform restrictions;
- rate limits;
- access controls.
```

## 91. Project branding

```text
Система должна поддерживать несколько брендов:
Author
Galdhold
DPlang
future projects
и не смешивать их автоматически.
Например:
Author post
≠
Galdhold official announcement
```

## 92. Publication policies by brand

```text
Каждый brand должен иметь:
tone
visual style
allowed topics
forbidden topics
CTA
official links
```

## 93. Personal brand vs project brand

```text
Контентная система должна уметь выбирать:
PERSONAL
PROJECT
MIXED
Например:
««Я создал DPlang»»
— personal.
««DPlang v0.1 released»»
— project.
««Почему я решил создать собственный язык»»
— mixed.
```

## 94. Central author website brand

```text
Сайт должен связывать бренды, но не превращаться в безликий корпоративный портал.
Главная entity:
dpsmpx
Проекты являются частью ecosystem.
```

## 95. Repository structure

```text
Адаптируй текущую структуру repository.
Минимально:
/
├── README.md
├── CLAUDE.md
├── TODO.md
├── LICENSE
│
├── apps/
│   ├── web/
│   ├── publisher/
│   └── tools/
│
├── core/
│   ├── content/
│   ├── identity/
│   ├── projects/
│   ├── campaigns/
│   ├── publishing/
│   ├── analytics/
│   └── media/
│
├── adapters/
│   ├── telegram/
│   ├── vk/
│   ├── youtube/
│   ├── discord/
│   └── github/
│
├── website/
│
├── prompts/
│
├── templates/
│
├── tests/
│
├── tools/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── PROCESS.md
    ├── PROVENANCE.md
    │
    ├── direction/
    │   └── DECISIONS.md
    │
    ├── identity/
    │
    ├── content/
    │
    ├── platforms/
    │
    ├── research/
    │
    ├── operations/
    │
    └── audits/
Поменяй структуру после исследования.
```

## 96. Documentation architecture

```text
Обязательно разделить:
DECISIONS
what was decided and why
ARCHITECTURE
how the system works
PROCESS
how work is performed
ROADMAP
what comes next
TODO
unfinished work
RESEARCH
external facts
AUDITS
state at a specific time
IDENTITY
who/what the system represents
PROVENANCE
where assets/data came from
```

## 97. Git / PR workflow

```text
Перенести инженерную дисциплину Galdhold:
task
→ branch
→ implementation
→ targeted checks
→ commit
→ push
→ PR
→ review
→ full verification
→ merge
PR создавать сразу после первого push.
```

## 98. Scope control

```text
Каждая задача должна иметь declared scope.
Посторонние изменения:
- удалить;
- объяснить;
- либо перенести в отдельную задачу.
```

## 99. Check system

```text
Создать систему:
quick checks
affected checks
full checks
release checks
Минимально проверять:
- secrets;
- credentials;
- malformed content;
- invalid links;
- provenance;
- duplicate publication;
- configuration;
- adapters;
- build;
- website;
- tests.
```

## 100. Test strategy

```text
Нужны:
unit
integration
contract
adapter
regression
property
e2e
Особенно важно contract testing для platform adapters.
```

## 101. Platform contract test

```text
Например:
TelegramAdapter
must:
- reject missing credentials
- reject invalid destination
- preserve idempotency
- return remote publication ID
- report structured errors
Такие же contracts для остальных adapters.
```

## 102. Mock platforms

```text
В CI нельзя полагаться только на реальные social APIs.
Создать fake/mock adapters:
MockTelegram
MockVK
MockDiscord
MockYouTube
MockGitHub
и проверять весь publishing pipeline без публикации наружу.
```

## 103. End-to-end test

```text
Тест:
create canonical news
↓
adapt
↓
approve
↓
publish to mock website
↓
publish to mock Telegram
↓
verify
↓
analytics event
```

## 104. Real platform tests

```text
Реальные платформы использовать:
- редко;
- контролируемо;
- только через test destinations/accounts, где это возможно;
- никогда не создавать массовый тестовый мусор в production.
```

## 105. Website staging

```text
Создать:
staging website
production website
Publishing defaults to staging during development.
```

## 106. Observability

```text
Система должна иметь:
- structured logs;
- publication IDs;
- campaign IDs;
- errors;
- latency;
- retries;
- provider response metadata.
Но секреты и чувствительные данные должны быть redacted.
```

## 107. Health check

```text
Добавить:
platform health
credentials health
website health
storage health
AI provider health
```

## 108. Provider failure

```text
AI provider unavailable:
content remains draft
Platform unavailable:
content remains approved/pending publication
Website unavailable:
social publishing may proceed only if canonical source is safely preserved
но решение должно быть policy-based.
```

## 109. No single point of failure

```text
Ни:
- Telegram;
- VK;
- YouTube;
- GitHub;
- website;
- AI provider
не должны быть единственным местом хранения canonical content.
```

## 110. Export

```text
Должна существовать возможность экспортировать всю контентную базу в portable format.
Например:
content export
media export
provenance export
publication history export
```

## 111. Migrations

```text
Own content model version:
content_schema_version
Явные миграции.
Не делать silent destructive migrations.
```

## 112. Backward compatibility

```text
До production public launch format может меняться быстрее.
Но как только сайт и publication history становятся real production data:
explicit migrations
```

## 113. Initial decisions

```text
В "DECISIONS.md" обязательно зафиксировать:
- website is canonical publishing hub;
- canonical content is platform-independent;
- social platforms are downstream;
- platform adapters are replaceable;
- publication is idempotent;
- human approval policy;
- content versioning;
- provenance;
- analytics model;
- identity separation;
- credential isolation;
- website archive;
- backup;
- staging/production;
- AI output is untrusted;
- platform limitations;
- manual fallback policy.
```

## 114. Первые рабочие этапы

```text
Phase 0
Research and architecture.
Phase 1
Canonical content model.
Phase 2
Website MVP.
Phase 3
Publishing engine.
Phase 4
Telegram adapter.
Phase 5
VK adapter.
Phase 6
Discord adapter.
Phase 7
YouTube adapter.
Phase 8
GitHub integration.
Phase 9
Campaigns/scheduling.
Phase 10
Analytics.
Phase 11
Automation.
```

## 115. Что не делать сразу

```text
Не делать:
- массовый autoposting;
- autonomous agent with production access;
- microservices;
- distributed queue;
- Kubernetes;
- custom analytics platform;
- complicated cloud architecture;
- AI-generated strategy without human control;
- universal scraper.
Начать с modular monolith и вертикального среза.
```

## 116. First product after architecture

```text
Первым production content должен оставаться:
«personal presentation image of dpsmpx as an effective AI-assisted systems developer.»
Но теперь она должна пройти через новую систему:
Identity
↓
Canonical Product Brief
↓
Asset Generation
↓
Review
↓
Website publication
↓
Telegram adaptation
↓
VK adaptation
↓
Discord adaptation
↓
YouTube asset/description where applicable
↓
Publication records
```

## 117. Website first-page content

```text
Для первой версии сайта подготовить:
hero
about author
primary projects
latest news
latest project
social links
contact
Не перегружать страницу.
```

## 118. Website must not depend on social media

```text
Socials are distribution channels.
Если Telegram/VK/YouTube исчезнут:
website still exists
content still exists
projects still exist
```

## 119. Content flywheel

```text
Финальная модель:
Projects
↓
Events / milestones
↓
Canonical content
↓
Website
↓
Social adaptations
↓
Audience
↓
Analytics
↓
Knowledge
↓
Better future content
Это должно стать основной архитектурной идеей проекта.
```

## 120. Условие успешной архитектуры

```text
После завершения текущей задачи ты должен иметь возможность сказать:
««Я могу создать одну новость один раз, проверить её один раз, после чего система знает, как показать её на моём сайте и подготовить корректные native-версии для каждой подключённой платформы».»
И при этом:
««Если одна соцсеть исчезнет, изменит API или временно недоступна, мой canonical content и весь архив не теряются».»
```

## 121. Final definition of done

```text
Работа считается законченной только когда:
Research
Исследованы актуальные:
- website architectures;
- Telegram API;
- VK API;
- YouTube API;
- Discord API;
- GitHub API;
- OAuth/credentials;
- rate limits;
- platform restrictions;
- creator website best practices.
Architecture
Определены:
- central hub;
- canonical content;
- project model;
- campaign;
- platform variants;
- adapters;
- publication lifecycle;
- idempotency;
- retry;
- approval;
- provenance;
- analytics;
- identity separation;
- staging/production.
Website
Создан:
- architecture;
- information model;
- initial implementation;
- staging;
- canonical URLs;
- feeds;
- project pages.
Publishing
Работает хотя бы:
canonical content
→ website
→ one social platform
Quality
Есть:
- mock adapters;
- unit tests;
- integration tests;
- contract tests;
- secret scanning;
- provenance;
- publication audit;
- dry-run;
- safe mode;
- failure handling.
Documentation
Есть:
- "CLAUDE.md";
- "README.md";
- "TODO.md";
- "ROADMAP";
- "DECISIONS";
- "ARCHITECTURE";
- "PROCESS";
- research;
- platform matrix;
- content model;
- operations;
- disaster recovery;
- audit.
```

## 122. Ключевой философский принцип

```text
В VoxelRPG архитектура защищает игру от противоречий будущего.
Здесь архитектура должна защищать контент и автора от зависимости от будущего каждой отдельной платформы.
Поэтому:
Author identity
        ↓
Canonical knowledge
        ↓
Canonical content
        ↓
Owned website
        ↓
Replaceable adapters
        ↓
External platforms
Главная собственность автора — не Telegram-пост, не VK-пост и не YouTube-видео.
Главная собственность:
каноническая база знаний + контент + media + provenance + история публикаций.
Социальные сети — только каналы распространения.
```
