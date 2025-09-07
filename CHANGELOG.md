## 2025-09-07  Product filtering

- Added ProductFilter
- Refactoring **filters** to `product/filters.py`.
- Refactoring `Pagination` to `addons/paginations.py`
- Refactoring dedupe `category` field from the `Product` model
- Refactoring move signals from `model.py` to `signals.py`
- Refactoring by rename to `generate_product_new_article` ,` generate_material_article`, `generate_subproduct_article`
- Refactoring `TotalProductsSerializer` added `year_collection` field
- Refactoring moved generate_qr_code, generate_product_new_article, generate_sku, generate_subproduct_new_article to utils.py


---
## 2025-09-04 — pre-commit

- Added package `pre-commit`.
- Configured `pre-commit` to apply actions on **committed files only**:
  - Check Python lint with `ruff` (files in `src/*.py`).
  - Format code with `black` (files in `src/*.py`).
  - Auto-generate `openapi.yaml` and add it to git **only if dependent routing files changed**.
- Added helper script `scripts/generate_openapi.py` for **cross-platform automatic generation** of `openapi.yaml`.

*Note*: for activate pre-commit functionality please run `pre-commit install` after upgrade or install packages from **dev** group

---