# Аудит CI/CD форка NNN706/Twenty

База review: commit `a54ddd521d9c869fd1098584bdc9a64da7d895c0`. Проверены все 38 файлов из `.github/workflows`, их секреты, vars, runner labels, registry destinations и вызовы локальных actions. Наличие одноимённого секрета в форке не доказывает доступ к инфраструктуре twentyhq; интеграции с ней исключены из активной папки workflows. Исходники перенесены в `.github/upstream-workflows` для дальнейшего сравнения с upstream; GitHub не исполняет workflow из этой папки.

## Исключённые интеграции

| Workflow | Причина |
| --- | --- |
| `cd-deploy-main.yaml` | Уже был полностью закомментирован; архивирован, ссылается на twentyhq/twenty-infra |
| `cd-deploy-tag.yaml` | `TWENTY_INFRA_TOKEN`, dispatch в twentyhq/twenty-infra |
| `ci-ai-catalog-sync.yaml` | Завершался dispatch через `TWENTY_INFRA_TOKEN` в twentyhq/twenty-infra; автоматический sync не нужен для сборки форка |
| `i18n-pull.yaml`, `i18n-push.yaml` | `CROWDIN_PERSONAL_TOKEN`, официальный Crowdin и `TWENTY_INFRA_TOKEN` |
| `docs-i18n-pull.yaml`, `docs-i18n-push.yaml` | То же: официальный Crowdin и privileged dispatch |
| `post-ci-comments.yaml` | `CI_PRIVILEGED_DISPATCH_TOKEN` и twentyhq/ci-privileged |
| `preview-env-dispatch.yaml`, `visual-regression-dispatch.yaml` | `CI_PRIVILEGED_DISPATCH_TOKEN`, внешний privileged workflow |
| `preview-env-keepalive.yaml` | Upstream preview lifecycle, Docker Hub credentials, долгоживущие временные окружения |
| `claude.yml` | `CLAUDE_CODE_OAUTH_TOKEN` и privileged dispatch; автономные изменения требуют отдельной настройки владельца |
| `docker-image.yml` | Дублирующий publisher, uppercase GHCR reference (`NNN706/Twenty_frontend`), ошибочный `build-args` на уровне jobs |
| `push_frontend_to_ghcr.yaml` | Дублировал публикацию; заменён matrix-сборкой двух совместимых образов в `push_to_ghcr.yaml` |

## Активные workflow

| Workflow | Результат review |
| --- | --- |
| `push_to_ghcr.yaml` | Переписан: targets `twenty-server` / `twenty-front`, GHCR namespace lowercase владельца форка, стандартный GITHUB_TOKEN, `packages: write`, SHA tags, digest summary, linux/amd64. Убрана зависимость от `buildkit:master`; используется setup-buildx default |
| `changed-files.yaml` | Сохранён reusable changed-path filter; contents read, стандартный runner |
| `ci-front.yaml` | Сохранены проверки; `ubuntu-latest-8-cores` заменён стандартным `ubuntu-latest` |
| `ci-merge-queue.yaml` | Сохранён opt-in/merge_group e2e; платный runner заменён стандартным |
| `ci-create-app-e2e-hello-world.yaml`, `ci-create-app-e2e-minimal.yaml`, `ci-create-app-e2e-postcard.yaml` | Сохранены проверки; `ubuntu-latest-4-cores` заменён стандартным |
| `ci-test-docker-compose.yaml` | Сохранены проверки upstream Compose/dev-image; удалены два обязательных login в Docker Hub. Public base images читаются анонимно |
| `ci-breaking-changes.yaml`, `ci-create-app.yaml`, `ci-docs.yaml`, `ci-emails.yaml` | Проверки не требуют секретов twentyhq, сохранены |
| `ci-example-app-hello-world.yaml`, `ci-example-app-postcard.yaml`, `ci-front-component-renderer.yaml` | Проверки не требуют секретов twentyhq, сохранены |
| `ci-sdk.yaml`, `ci-server.yaml`, `ci-shared.yaml`, `ci-ui.yaml` | Проверки не требуют секретов twentyhq, сохранены |
| `ci-utils.yaml`, `ci-website.yaml`, `ci-zapier.yaml` | Проверки сохранены; Danger использует GITHUB_TOKEN этого репозитория |
| `ci-release-create.yaml`, `ci-release-merge.yaml` | Внутрирепозиторные manual/merged-release действия, оставлены. Для create-pull-request требуется настройка репозитория Allow GitHub Actions to create and approve pull requests; это настройка форка, а не доступ к twentyhq |

Локальные actions restore/save cache, yarn-install, changed-path проверки используют runner/cache текущего репозитория. Ссылка `twentyhq/twenty` в default composite action `spawn-twenty-docker-image` — публичный read/build источник, не официальный registry write; в новой публикации этот action не используется. Публичные ссылки на npm/Docker Hub/upstream не удаляются как зависимости чтения.

Перевод custom runner labels в `ubuntu-latest` устраняет зависимость от runner group upstream, но не гарантирует равную скорость/память: тяжёлые тесты могут потребовать tuning. Выполнение всех application tests и внешних интеграций не считается доказанным одним статическим review. Публичные Docker Hub pulls могут ограничиваться anonymous rate limit; при необходимости владелец добавляет собственные credentials, без заимствования аккаунта twentyhq.

## Проверки и эксплуатация

- GitHub Actions должен быть включён в форке. На момент read-only проверки он включён и разрешены public actions.
- Публикация проходит только в namespace владельца через scoped GITHUB_TOKEN. PAT и доступ к registry twentyhq не используются.
- Из ветки можно вызвать существующий `push_to_ghcr.yaml` через workflow_dispatch, не меняя main. До merge новые правила CI хранятся в ветке/PR. Старые scheduled workflows на main могут продолжать запускаться; их отключение в Settings/Actions — отдельное repository-level действие, которое нужно явно отразить в журнале при выполнении.
- Чтобы снова включить исключённую интеграцию, сначала создайте собственный сервис/секреты и проверьте destinations, затем верните файл в `.github/workflows`. Простое добавление upstream secret names не является настройкой интеграции.
