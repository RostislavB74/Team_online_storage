## 2025-09-11 - BugFix Add product and subproducts
- Added scrips for a backup database model
- Tuned generate articles with found only digits onto string.
- Recovered bug in signal pre_save.

---

## 2025-09-07 - Product Filtering & Refactoring

### Added
- `ProductFilter`
- `year_collection` field to `TotalProductsSerializer`
- `DEBUG_TOOLBAR_ENABLE` settings variable 
- `ProductFilter` added property for filter by coma-separated list and range for values
- `CommaSeparatedIntegerListFilter` custom solution coma-separated list of integer values

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
- Django Admin `ProductAdmin`: added formfield_for_foreignkey() and `_sort_related_fields_byid` for sorf by `pk` {"category", "subcategory", "collection"}
- At `Category`, `Subcategory`, `Collection` models changed string representation with pk index in text

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