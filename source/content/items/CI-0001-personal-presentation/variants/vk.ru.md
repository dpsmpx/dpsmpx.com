---
schema: variant/v1
item: CI-0001
platform: vk
lang: ru
format: post
version: 2
status: ready
trust: validated
media:
- exports/E-ru-vk_post.jpg
generation:
  provider: session
  note: из канона v2; автор — только dpsmpx (Д40)
note: 'Короткая запись VK, RU, с изображением vk_post. Шаблон — templates/vk_post.md. facts: AU-HANDLE,
  AU-METHOD, GH-NAME, GH-GENRE, GH-TECH, GH-ENGINE, GH-ANDROID'
claims:
- AU-HANDLE
- AU-ROLE
- AU-METHOD
- GH-NAME
- GH-GENRE
- GH-TECH
- GH-ENGINE
- CORE-SCALE-2026-10-05
source_version: 2
link: null
approval: null
deps:
  facts:
    AU-ROLE: 0d84826a46110966
    CORE-SCALE-2026-10-05: ddb54a064dc78fd7
    GH-NAME: 18e9e8bc34f1c9f0
    GH-GENRE: 87840cd38160c9f1
    GH-TECH: 885bae9eed2b037d
    GH-ENGINE: 3ae43184e26a50af
    AU-METHOD: 95e9ba70d576890a
    AU-HANDLE: 0535a93f2279e87d
  links:
    L-TG-DEVLOG: e4702bf8299c4509
  releases: {}
  datasets: {}
  canonical:
    version: 2
    sha256: fe64888b48a31219079069bf4113cd66b4cfcf99d2719761072c7d8cbd7d9d86
  media:
    exports/E-ru-vk_post.jpg: ff5618dbbd10154834da6dedcc76a7155654d2d05480633fb993c3af6260ae1d
---
Я — dpsmpx, {{fact:AU-ROLE#2}}: {{fact:CORE-SCALE-2026-10-05#9}}. Игра — {{fact:GH-NAME}}, {{fact:GH-GENRE}}: {{fact:GH-TECH}}, {{fact:GH-ENGINE}}.

{{fact:AU-METHOD}}.

Снимки и подробности — в дневнике разработки: {{link:L-TG-DEVLOG}}
