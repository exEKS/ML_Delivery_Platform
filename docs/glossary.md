# ML Delivery Platform — Glossary

Короткі визначення термінів, які вже виникли або потрібні на Week 1. Визначення навмисно прості; точні технічні нюанси додаються тоді, коли вони стають потрібними коду.

## Repository

Папка проєкту, історію якої відстежує Git. Прихована директорія `.git` містить commits, branches та службову інформацію.

## Working tree

Поточний стан файлів, які видно у папці repository. Він може відрізнятися від останнього commit.

## Untracked file

Файл, який існує у working tree, але Git ще не почав відстежувати.

## Staging area

Проміжний набір змін, вибраних для наступного commit командою `git add`.

## Commit

Зафіксований знімок вибраних змін із автором, часом і повідомленням. Commit не дорівнює push: спочатку він існує локально.

## Branch

Рухомий покажчик на послідовність commits. `main` — головна branch repository.

## Remote

Посилання локального Git repository на зовнішню копію, наприклад GitHub repository.

## WSL

Windows Subsystem for Linux — Linux-середовище всередині Windows. У цьому проєкті commands і code виконуються в Ubuntu під WSL 2.

## Virtual environment (`.venv`)

Ізольоване Python-середовище проєкту. Воно не дає dependencies одного проєкту змішуватися із системним Python або іншими проєктами.

## Python project

Одиниця, описана `pyproject.toml`: metadata, потрібна версія Python, dependencies і tool configuration.

## Python package

Код, який Python може імпортувати, наприклад `platform_contracts`.

## Distribution package

Назва installable package для package manager. Наприклад, distribution `platform-contracts` надає import package `platform_contracts`.

## Workspace

Кілька Python projects/packages в одному repository зі спільним dependency resolution і `uv.lock`.

## `pyproject.toml`

Стандартний configuration file сучасного Python project. Він описує metadata, Python version, dependencies, build system і налаштування tools.

## Dependency

Зовнішня бібліотека або package, потрібна проєкту.

## Runtime dependency

Dependency, без якої код не може виконувати свою основну функцію. `platform_contracts` потребує Pydantic для validation під час роботи.

## Development dependency

Інструмент розробки, тестування або перевірки, який не обов'язково потрібен production application. Приклади: pytest, Ruff, mypy.

## Version constraint

Дозволений діапазон версій dependency, наприклад `pydantic>=2,<3`.

## Lockfile (`uv.lock`)

Файл із точними resolved versions усіх dependencies. Він допомагає відтворити однакове середовище на іншій машині й у CI.

## Build backend

Tool, який знає, як перетворити source package на installable artifact. У `platform_contracts` цю роль виконує `uv_build`.

## Editable install

Режим, у якому environment посилається на source code repository. Зміна коду одразу доступна імпорту без повторного ручного reinstall.

## Linter

Tool, який статично знаходить підозрілі конструкції та порушення правил коду. У проєкті використовується Ruff.

## Type checker

Tool, який аналізує type hints без запуску програми. У проєкті використовується mypy.

## Unit test

Швидкий тест маленької частини логіки без справжньої мережі, database або cloud infrastructure.

## Contract

Явна домовленість про структуру та semantics даних між частинами системи. Contract каже не лише «які поля є», а й що вони означають.

## `model.yaml`

Versioned зовнішній contract моделі. Він описує training entry point, dataset references, metrics, gates, serving і deployment policy.

## Pydantic model

Python class із typed fields і validation rules. У проєкті Pydantic представлятиме `ModelSpec`.

## YAML

Людинозручний текстовий формат configuration. Відступи в YAML мають структурне значення.

## JSON Schema

Машиночитаний опис дозволеної JSON/YAML structure: required fields, types, ranges, enums і заборонені поля.

## Syntax validation

Перевірка, чи файл взагалі правильно записаний як YAML/JSON.

## Schema validation

Перевірка структури та типів: чи є required fields, чи правильні types, ranges і allowed values.

## Semantic validation

Перевірка змістовних правил, які не завжди виражаються простими types. Наприклад, частки train/validation/test мають у сумі давати `1.0`.

## Artifact

Матеріальний результат pipeline: trained model, metrics JSON, schema, report або container image.

## Model artifact

Серіалізований результат training разом із потрібною metadata. Офіційний production artifact створює trusted platform pipeline, а не випадковий локальний notebook.

## Dataset snapshot

Незмінна versioned копія dataset, на яку можна однозначно послатися і повторити training.

## Manifest

Metadata file про dataset snapshot: source, version, checksums, row count, target і transform version.

## Checksum

Короткий cryptographic fingerprint bytes файла, наприклад SHA-256. Якщо хоча б один byte зміниться, checksum теж зміниться.

## Data schema

Очікувані columns, types, nullable rules, ranges і constraints dataset.

## Data leakage

Ситуація, коли training отримує інформацію, якої не мав би знати під час реального prediction, або коли test data впливає на tuning.

## Train / validation / test split

- **Train:** дані для fit parameters моделі.
- **Validation:** дані для вибору settings і model variant.
- **Test:** фінальна чесна оцінка, яка не використовується для tuning.

## Baseline

Простий відтворюваний початковий результат, з яким порівнюються наступні моделі. На Week 1 це Logistic Regression.

## Candidate

Нова model version, яка проходить evaluation і ще не є основною production model.

## Champion

Поточна схвалена model version, з якою порівнюється candidate.

## Quality gate

Автоматична перевірка policy, яка вирішує, чи може candidate перейти на наступний етап. Сам MLflow не приймає це рішення замість нашого gate code.

## MLflow Tracking

Зберігає experiment runs: parameters, metrics, tags і artifacts.

## Model Registry

Каталог versioned models та їх lifecycle metadata. У проєкті registry є частиною MLflow stack.

## Prometheus

Збирає numeric time-series metrics із працюючих services, наприклад request rate, error rate і latency.

## Grafana

Візуалізує metrics у dashboards і допомагає досліджувати стан системи. Grafana не навчає й не порівнює ML-моделі.

## Control plane

Частина платформи, яка приймає бажаний стан, керує requests, status transitions, policy і audit trail.

## Data plane

Частина системи, через яку проходять prediction requests і model-serving traffic.

## Idempotency

Властивість operation, за якої безпечний повтор того самого request не створює дубльований side effect.

## Source of truth

Авторитетне місце для конкретного виду інформації. Наприклад, repository + Git SHA є source of truth для code version, а versioned object storage manifest — для dataset snapshot.

## ADR

Architecture Decision Record — короткий versioned документ про context, варіанти, decision і consequences важливого рішення.

## Definition of Done

Перевірюваний список умов, після виконання яких задача або milestone справді завершений.

## Failure exercise

Навмисне контрольоване ламання системи, щоб перевірити detection, повідомлення про помилку та recovery path.
