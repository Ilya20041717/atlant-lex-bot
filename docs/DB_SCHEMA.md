## Структура базы данных

### organizations
- `id` PK
- `name`
- `created_at`

### users
- `id` PK
- `tg_id` UNIQUE
- `role` (unknown/lead/client/employee/manager/lawyer/owner)
- `org_id` FK -> organizations.id
- `created_at`
- `updated_at`

### lead_profiles
- `id` PK
- `user_id` UNIQUE FK -> users.id
- `debt_amount`
- `creditors_count`
- `overdue_months`
- `income`
- `assets`
- `region`
- `created_at`
- `updated_at`

### stages
- `id` PK
- `code` UNIQUE
- `title`
- `description`
- `client_actions`
- `eta_text`

### clients
- `id` PK
- `user_id` UNIQUE FK -> users.id
- `org_id` FK -> organizations.id
- `contract_number`
- `current_stage_id` FK -> stages.id
- `next_step`
- `total_cost`
- `paid_amount`
- `is_verified`
- `created_at`
- `updated_at`

### client_tasks
- `id` PK
- `client_id` FK -> clients.id
- `title`
- `status` (pending/done)
- `due_date`
- `created_at`

### client_documents
- `id` PK
- `client_id` FK -> clients.id
- `title`
- `status` (not_provided/expected/accepted)
- `updated_at`

### client_payments
- `id` PK
- `client_id` FK -> clients.id
- `amount`
- `due_date`
- `paid_at`
- `status` (planned/paid/overdue)

### notifications
- `id` PK
- `client_id` FK -> clients.id
- `type` (document/action/deadline)
- `text`
- `scheduled_at`
- `sent_at`
- `status` (planned/sent/canceled)
