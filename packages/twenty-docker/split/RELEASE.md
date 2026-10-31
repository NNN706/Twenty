# Сборка 2026-11-01

Исходный commit образов: `d8e73154c8d6b03ec63fb10cd771fc23cd5ff684`.

Тег обоих образов: `sha-d8e73154c8d6b03ec63fb10cd771fc23cd5ff684`.

| Образ | Неизменяемый digest |
| --- | --- |
| `ghcr.io/nnn706/twenty-backend` | `sha256:1c00495f516dc004031301dac65af02966d292d353f2eee1441559dd73287dad` |
| `ghcr.io/nnn706/twenty-frontend` | `sha256:dc726ee08b826fe5d1873424e2ff6807e2ccc5a5b15a61829e82cecde0e03575` |

Архитектура: `linux/amd64`. Оба образа собраны и опубликованы через [GitHub Actions](https://github.com/NNN706/Twenty/actions/runs/41252548226); локальная сборка не выполнялась. Dockerfile выбирает отдельные targets `twenty-server` и `twenty-front`.

Исходники и документация: [PR #4](https://github.com/NNN706/Twenty/pull/4), ветка `codex/split-deployment`. Main не изменён и PR не слит. В Settings/Actions отключены 14 upstream-only/duplicate workflows; детали в CI-CD-REVIEW.md.

Проверки: Compose и Nginx proxy smoke прошли в GitHub. Integration job успешно запустил backend с PostgreSQL, Redis и worker, затем два независимых frontend; через оба получены успешные /healthz и JSON /client-config. Все четыре job финального workflow завершились success. Реальное развёртывание на целевых хостах, DNS, firewall, SMTP и OAuth не выполнялось.

Для запуска используйте README.md и соответствующие Compose/env шаблоны. Для private packages потребуется login на GHCR с read:packages. Не используйте первоначальный пробный тег `sha-e61c39bb2624f9126f348231fa6aeced9e3996a3`: финальная версия исправляет APP_VERSION.
