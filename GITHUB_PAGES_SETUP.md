# 📝 Настройка GitHub Pages (пошаговая инструкция)

## ✅ Шаг 1: Создайте workflow файл через GitHub

1. Зайдите в ваш репозиторий: https://github.com/raimbekovm/hackathon-urban-tech
2. Нажмите на кнопку **"Add file"** → **"Create new file"**
3. В поле имени файла введите:
   ```
   .github/workflows/deploy-pages.yml
   ```
   (GitHub автоматически создаст папки `.github` и `workflows`)

4. Скопируйте и вставьте следующий код:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
      - master
      - dev
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './frontend'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

5. Нажмите **"Commit new file"** внизу страницы

## ✅ Шаг 2: Включите GitHub Pages

1. В репозитории перейдите в **Settings** → **Pages**
2. В разделе **Source** выберите: **GitHub Actions**
3. Сохраните изменения

## ✅ Шаг 3: Запустите деплой

1. Перейдите во вкладку **Actions** в вашем репозитории
2. Вы увидите workflow "Deploy to GitHub Pages"
3. Если он не запустился автоматически, нажмите на него и выберите **"Run workflow"**
4. Дождитесь завершения (обычно 1-2 минуты)

## ✅ Шаг 4: Получите ссылку на сайт

После успешного деплоя:
1. Зайдите в **Settings** → **Pages**
2. Там будет ссылка на ваш сайт, например:
   ```
   https://raimbekovm.github.io/hackathon-urban-tech/
   ```

## 🔄 Обновление данных

После обновления данных в ML pipeline:

```bash
cp ml/output/*.json frontend/data/
cp ml/output/*.csv frontend/data/
git add frontend/data/
git commit -m "Update data"
git push
```

GitHub Actions автоматически задеплоит обновленную версию!

