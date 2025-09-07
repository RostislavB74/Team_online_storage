## 2025-09-07 - Product Filtering & Refactoring

### Added
- `ProductFilter`
- `year_collection` field to `TotalProductsSerializer`
- `DEBUG_TOOLBAR_ENABLE` settings variable 

### Moved
- **Filters** - `product/filters.py`
- `Pagination` - `addons/paginations.py`
- **Signals** - from `models.py` to `signals.py`

### Renamed
- `generate_product_new_article`
- `generate_material_article`
- `generate_subproduct_article`
- `generate_product_qr_code`

### Changed
- Removed duplicate `category` field from `Product` model
- Dynamic calculation of `CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT` in `settings.py`

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