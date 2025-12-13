# 🚀 Простой деплой на GitHub Pages (без Actions)

Если у вас проблемы с GitHub Actions, используйте этот способ:

## Способ 1: Через настройки GitHub Pages (самый простой)

### Шаг 1: Создайте ветку `gh-pages` и скопируйте туда frontend

```bash
# Создайте ветку gh-pages
git checkout -b gh-pages

# Скопируйте содержимое frontend в корень
cp -r frontend/* .

# Удалите папку frontend (она больше не нужна)
rm -rf frontend

# Закоммитьте
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

### Шаг 2: Настройте GitHub Pages

1. Зайдите в **Settings** → **Pages**
2. В разделе **Source** выберите: **Deploy from a branch**
3. Выберите ветку: **gh-pages**
4. Папка: **/ (root)**
5. Нажмите **Save**

Сайт будет доступен через несколько минут по адресу:
```
https://raimbekovm.github.io/hackathon-urban-tech/
```

---

## Способ 2: Использовать папку `docs` (если хотите остаться на ветке dev)

```bash
# Создайте папку docs в корне
mkdir docs

# Скопируйте содержимое frontend в docs
cp -r frontend/* docs/

# Закоммитьте
git add docs/
git commit -m "Add docs folder for GitHub Pages"
git push
```

Затем в **Settings** → **Pages**:
- Source: **Deploy from a branch**
- Branch: **dev** (или main/master)
- Folder: **/docs**

---

## Способ 3: Создать workflow через веб-интерфейс (если нужен автоматический деплой)

1. Зайдите на https://github.com/raimbekovm/hackathon-urban-tech
2. Нажмите на кнопку **"Add file"** → **"Create new file"**
3. В поле имени файла введите: `.github/workflows/deploy-pages.yml`
4. Скопируйте содержимое из файла `.github/workflows/deploy-pages.yml` (он у вас локально)
5. Нажмите **"Commit new file"**

После этого workflow появится в Actions.

