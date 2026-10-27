# Phase 2 — Source database and synthetic data generation

## Scope

This phase hardens the existing MySQL schema initialization and the five existing synthetic data generators. No existing project folders were renamed or merged.

## Changes made

- The main generator now calls customers, products, orders, order items, and payments in foreign-key dependency order.
- Customer, product, and order generators fill up to configured target totals instead of inserting the full target on every run.
- Order generation uses customer IDs queried from MySQL rather than assuming IDs are 1 through 5,000.
- Order-item generation selects existing product IDs/prices and only creates items for orders that currently have none.
- Payment generation creates a payment only for orders that do not already have one, calculates amount from order items, and fails clearly if an order has no items.
- Generator functions commit successful batches, roll back on errors, close connections, and return inserted row counts.
- `--reset` explicitly deletes all rows in dependency-safe order and resets AUTO_INCREMENT; it requires typing `RESET` unless `--yes` is supplied.
- Database initialization resolves the SQL schema path relative to the project, so it does not depend on the current working directory.

## Run instructions

From the repository root, after configuring `.env` and confirming local MySQL is running:

```bash
python -m scripts.initialize_database
python -m mysql.generate_data.generate_data_main
```

The default generation command is designed to fill missing rows to the configured targets and to avoid generating duplicate order items/payments on a normal rerun. To intentionally discard all generated rows and rebuild the dataset, use:

```bash
python -m mysql.generate_data.generate_data_main --reset
```

The reset command is destructive. It asks for the exact confirmation `RESET`. For non-interactive use only when intentional:

```bash
python -m mysql.generate_data.generate_data_main --reset --yes
```

## Target counts

Default target totals are 5,000 customers, 500 products, and 20,000 orders. Order-item counts vary because each order receives 1–4 distinct products, and payments are generated for orders that do not yet have a payment. The final order-item count is therefore not fixed.

## Validation status

- Python syntax compilation: passed for the project source files after the Phase 2 changes.
- Live MySQL execution and foreign-key/count validation: not yet run in this environment because no local MySQL service or user credentials are available here.
- AWS integration: out of scope for this phase.

Do not mark this phase fully verified until the run commands succeed against the user's local MySQL instance and the final counts and relationships have been checked.
