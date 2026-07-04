# Library Management

A Frappe app for running a library: cataloging books, managing memberships, issuing/returning
books, tracking fines, and queueing reservations. Includes a public web portal for browsing the
catalog, self-registering as a member, and a "My Books" page for members to see what they've
borrowed, what they owe, and their reservation status.

## How it fits together

- **Article** — a catalog entry (one row per physical copy). Status is one of
  `Available` / `Issued` / `Reserved`.
- **Library Member** — a person. Created automatically when a Website User signs up, or via the
  public `/register` page. A `User` account is created alongside it (with no roles) so the member
  can log in to the portal.
- **Library Membership** — a submittable, paid membership period (`Monthly` / `Quarterly` /
  `Yearly`). Submitting it sets the member's `membership_expiry` and grants the `Library Member`
  role (which is what unlocks issuing/returning books and reserving articles); cancelling it
  reverts both.
- **Library Transaction** — an `Issue` or `Return` record. Issuing requires an active membership
  and an available Article; returning late calculates a fine from `Library Settings`.
- **Books Reservation** — a queue entry for an Article that's currently checked out. When it's
  returned, the next pending reservation in the queue is notified by email.

## Roles

- **System Manager** — full administrative access.
- **Librarian** — day-to-day operations: manage Articles, Library Members, Memberships,
  Transactions, and Reservations.
- **Library Member** — granted automatically on a paid, submitted Library Membership. Lets a
  member view their own data through the portal.

## Configuration

**Library Settings** (single doctype, Librarian/System Manager only):
- `fine_per_day` — currency charged per day a Return is late (must be ≥ 0).
- `loan_period_days` — default loan length in days used to compute an Issue's due date (must be
  > 0).

## Scheduled jobs

Run daily (`hooks.py` → `scheduler_events`):
- `check_expired_memberships` — expires memberships past their `to_date` and removes the
  `Library Member` role.
- `cancel_expired_reservations` — cancels reservations that went unclaimed for 2+ days after
  notification, and notifies the next member in the queue if one exists.

## Installation

```bash
bench get-app library_management <repo-url>
bench --site <site-name> install-app library_management
```

Then, as a System Manager, open **Library Settings** and set `fine_per_day` and
`loan_period_days` for your library before going live.

## Development vs. production

This app is normally developed with `developer_mode: 1` set in `site_config.json`, which allows
live DocType/report/dashboard edits. Before deploying for real members:
- Set `developer_mode: 0` (or simply remove the key) in the site's `site_config.json`.
- Run `bench setup production <user>` to put supervisor + nginx in front of the site instead of
  the `bench start` dev server.
- Do not leave `ignore_csrf` or `allow_guests_to_upload_files` enabled in production site config.

## Tests

```bash
bench --site <site-name> run-tests --app library_management
```
