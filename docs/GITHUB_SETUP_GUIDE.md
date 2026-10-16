# Guia para crear el repo `pension-calculator-col` en GitHub

**Fecha:** 15 oct 2026
**Proposito:** Crear el repo publico en GitHub para pension-calculator

---

## Paso 1: Crear el repo en GitHub

1. **Abre en tu navegador**: https://github.com/new

2. **Completa EXACTAMENTE estos campos** (los importantes):

| Campo | Valor que debes escribir | Notas |
|-------|--------------------------|-------|
| **Owner** | `AndresGM7` (tu usuario) | Debe ser tu cuenta personal |
| **Repository name** | `pension-calculator-col` | **EXACTO** - asi se llamara |
| **Description** | `Calculadora de pensiones en Colombia con datos oficiales del Banrep y SuperFinanciera. Comparador neutral RPM vs RAIS.` | Aparece en tu perfil |
| **Visibility** | `Public` | Para que todos puedan verlo y vos usar GitHub Pages |
| **Add a README file** | **NO marcar** | Ya tenemos un commit local, no duplicar |
| **Add .gitignore** | **NO marcar** | Ya tenemos .gitignore en el repo local |
| **Choose a license** | **NO marcar** | Vamos a agregar MIT despues via archivo |

3. **Click en "Create repository"** (boton verde abajo)

---

## Paso 2: NO hacer nada en la pagina siguiente

Despues de crear el repo, GitHub te muestra una pagina con instrucciones.
**NO ejecutes nada de lo que dice alli** porque ya tenes un repo local con commits.

Lo que veras:

```
Quick setup — if you've done this kind of thing before
```

Cierra esa pagina o andate a otra seccion.

---

## Paso 3: Dame el URL del repo

Decime el URL exacto. Va a ser algo como:

```
https://github.com/AndresGM7/pension-calculator-col
```

Yo voy a:
1. Agregar el remote a tu repo local
2. Hacer el push de los 47 archivos
3. Verificar que todo este commiteado

---

## Paso 4: Configurar el repo post-push

Una vez subido, en GitHub:

### 4a. Agregar descripcion y topics
Click en el engranaje (⚙️) al lado de "About" en la pagina del repo:
- Description: `Calculadora de pensiones en Colombia con datos oficiales del Banrep y SuperFinanciera. Comparador neutral RPM vs RAIS.`
- Website: `https://pension-calc-co.fly.dev`
- Topics: `colombia`, `pensiones`, `pension`, `fastapi`, `python`, `finanzas`

### 4b. Agregar licencia MIT
1. Click "Add file" → "Create new file"
2. Nombre del archivo: `LICENSE`
3. GitHub te ofrece templates → elegi "MIT License"
4. Click "Commit new file"

### 4c. Proteger la rama main
Settings → Branches → Add rule:
- Branch name pattern: `main`
- Marcar: "Require pull request reviews before merging"
- Marcar: "Require status checks to pass before merging" (cuando tengamos CI)

---

## Lo que NO debes hacer

- NO marcar "Add a README file" al crear (ya lo tenes vos)
- NO marcar "Add .gitignore" (ya lo tenes vos)
- NO marcar "Choose a license" (lo agregamos despues)
- NO ejecutar `git init` de nuevo (ya esta inicializado)
- NO ejecutar los comandos de "push an existing repository" de GitHub (rompe tu repo local)

---

## Troubleshooting

### Si te aparece "Repository not found" al hacer push

Es porque el remote no esta bien configurado. Verificar:

```bash
git remote -v
```

Deberia mostrar:
```
origin  https://github.com/AndresGM7/pension-calculator-col.git (fetch)
origin  https://github.com/AndresGM7/pension-calculator-col.git (push)
```

Si esta mal:
```bash
git remote remove origin
git remote add origin https://github.com/AndresGM7/pension-calculator-col.git
```

### Si te pide autenticacion

GitHub ya no acepta passwords. Necesitas un Personal Access Token:

1. Andá a https://github.com/settings/tokens
2. "Generate new token" → "Classic"
3. Scope: `repo` (todo lo de repo)
4. Copia el token
5. Cuando git te pida password, pega el token (no tu password de GitHub)

### Si el push falla con "src refspec main does not match any"

Tu rama local se llama `master`, no `main`. Soluciones:

**A) Push con la rama master:**
```bash
git push -u origin master
```

**B) Renombrar master a main (mas moderno):**
```bash
git branch -M main
git push -u origin main
```

Te recomiendo la B porque GitHub ahora usa `main` como default.

---

## Resumen: que pasa despues

| Paso | Quien lo hace | Tiempo |
|------|---------------|--------|
| 1. Crear repo en github.com/new | Vos | 2 min |
| 2. Darme el URL | Vos | 10 seg |
| 3. Configurar remote + push | Yo | 30 seg |
| 4. Descripcion + topics + license | Vos | 3 min |
| 5. Configurar branch protection | Vos | 2 min |

Total: ~8 minutos para tener el repo 100% listo en GitHub.
