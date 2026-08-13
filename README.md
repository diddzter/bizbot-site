# bizbot-site

Rebuild of [bizbot.com](https://www.bizbot.com) off Unicorn Platform onto
WordPress (hosted on Hostinger), with Claude-driven ongoing automation for
blog posts, SEO, new tool listings, and affiliate links.

This repo does **not** contain WordPress itself -- WordPress core, the
database, and plugins live on Hostinger. This repo contains:

- `theme/` -- the BizBot child theme (of GeneratePress)
- `mu-plugins/bizbot-seo-rest-support.php` -- a small always-on plugin that
  makes Yoast's SEO title/description fields reliably writable via the REST
  API (see the comment at the top of that file for why)
- `migration/` -- one-time scripts to import the old site's content
- `automation/` -- ongoing scheduled scripts (blog posts, SEO audits,
  affiliate link sweeps) plus a manual one for adding tools
- `data/` -- the migrated content and configuration (affiliate links, blog
  topic queue) that the automation reads from

## 1. Provision WordPress on Hostinger

Do this on a **staging subdomain first** (e.g. `staging.bizbot.com` or
Hostinger's auto-generated temp domain), not the live `bizbot.com` domain --
keep Unicorn Platform live until everything below is validated.

1. In hPanel, create the WordPress install.
2. Install these plugins:
   - **Yoast SEO** -- SEO titles/descriptions, sitemaps, redirects
   - **Advanced Custom Fields** (free) -- required for the Tool fields the
     theme registers in code (`theme/functions.php`)
   - **ThirstyAffiliates** or **Pretty Links** -- affiliate link cloaking
   - **MailPoet** or **Fluent Forms** -- newsletter signup, tool
     submission, and guest-post contact forms
   - **LiteSpeed Cache** -- Hostinger's native performance plugin
   - **Redirection** (free, by John Godley) -- for importing
     `data/redirects.csv` (Tools -> Redirection -> Import, CSV format)
3. Upload `theme/` as `wp-content/themes/bizbot-site/` and activate it
   (or just push to `main` once `deploy_theme.yml`'s secrets are set --
   see step 4).
4. Upload `mu-plugins/bizbot-seo-rest-support.php` to
   `wp-content/mu-plugins/` (same deal -- `deploy_theme.yml` handles this
   automatically once configured).
5. **Settings -> Permalinks**: set a custom structure of `/blog/%postname%/`
   so blog post URLs match the old site exactly (this preserves SEO --
   see the plan's decision to keep `/blog/` and `/tools/` paths identical).
   Tool and news post types already get `/tools/` and `/news/` prefixes
   from `theme/functions.php`'s CPT registration, no action needed there.
6. **Users -> Profile -> Application Passwords**: create one for the
   automation to use as `WP_APP_USER` / `WP_APP_PASSWORD` (use a dedicated
   user with an Editor or Administrator role, not your personal login).
7. Set up each form plugin's newsletter / tool-submission / guest-post
   forms, then paste their shortcodes into **Appearance -> Customize ->
   BizBot Forms** (three fields there, one per form -- the theme templates
   pull from these automatically).

## 2. Configure GitHub secrets & variables

Repo Settings -> Secrets and variables -> Actions:

**Secrets:**
- `WP_BASE_URL` (e.g. `https://staging.bizbot.com`, no trailing slash)
- `WP_APP_USER`, `WP_APP_PASSWORD`
- `ANTHROPIC_API_KEY`
- `HOSTINGER_SFTP_HOST`, `HOSTINGER_SFTP_USER`, `HOSTINGER_SFTP_PASSWORD`,
  `HOSTINGER_SFTP_PORT` (hPanel -> Files -> FTP Accounts; Hostinger's SFTP
  port is often `65002`, not `22` -- check hPanel)

**Variables:**
- `HOSTINGER_THEME_REMOTE_PATH` (e.g. `public_html/wp-content/themes/bizbot-site`)
- `HOSTINGER_MU_PLUGINS_REMOTE_PATH` (e.g. `public_html/wp-content/mu-plugins`)

## 3. Run the migration

Actions tab -> "Migrate content to WordPress" -> Run workflow.

- Tick "dry run" first to sanity-check the crawl + transform without
  writing anything.
- Full run crawls the ~439 blog posts not already captured in
  `data/blog_posts_seed.json`, merges everything, and pushes it to the
  `WP_BASE_URL` from your secrets. Takes roughly 15-30 minutes (polite
  1s delay between requests to bizbot.com).
- Safe to re-run -- every push is an upsert keyed by slug.
- Check the workflow's run summary and the uploaded `migration-data`
  artifact for anything flagged `needs_manual_review` (a handful of tool
  descriptions and any pages that hit a bot-check wall while crawling).

## 4. Validate on staging

- Homepage tool grid and category filters render.
- Spot-check ~15 blog posts (mix of ones from the manual export and
  freshly-crawled ones).
- All 98 tool pages have a working outbound link (`--check-links` in
  `automation/seo_audit.py` can verify this in bulk once things are live).
- `/sitemap_index.xml` (Yoast's sitemap) has roughly the expected count.
- Newsletter and tool-submission forms actually submit.
- Import `data/redirects.csv` via the Redirection plugin and confirm
  `/home-clone/` → `/`.

## 5. Cut over

Point `bizbot.com`'s DNS (in Hostinger) at the new WordPress install. Keep
the Unicorn Platform site around as a fallback until you're confident
things are stable.

## 6. Ongoing automation

Runs automatically once the secrets above are set:

| Workflow | Schedule | What it does |
|---|---|---|
| `blog_post.yml` | weekly (Tue 09:00 UTC) | Claude writes and **auto-publishes** a new post (topic from `data/blog_topic_queue.json`, or self-proposed), then sweeps it for affiliate-link opportunities |
| `seo_audit.yml` | monthly | Auto-fixes missing/oversized SEO titles & descriptions across posts/pages/tools; reports thin content and broken tool links for manual review |

Manual, run whenever:
- `python3 automation/add_tool.py --name "..." --url "..." --category "..."`
  -- add a new tool listing (auto-writes the description from the tool's
  own homepage if you don't pass `--description`)
- `python3 automation/affiliate_link_sweep.py` -- link any un-linked
  mentions of tools in `data/affiliate_links.json` across all posts
  (also runs automatically after every new blog post)

**To queue blog topics:** edit `data/blog_topic_queue.json` (a plain JSON
array of strings), commit, push. The next scheduled run pops the first one.

**To add an affiliate deal:** edit `data/affiliate_links.json`, commit,
push. It's picked up by both `generate_blog_post.py` (linked when relevant
while writing) and `affiliate_link_sweep.py` (retroactively linked in
existing posts).

**To change the design:** edit `theme/`, push to `main` --
`deploy_theme.yml` ships it to Hostinger automatically.

## Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r migration/requirements.txt -r automation/requirements.txt
cp .env.example .env   # fill in values, then `export $(cat .env | xargs)` or use direnv
```

Migration scripts run in this order: `parse_exports.py` -> `crawl.py` ->
`transform.py` -> `push_to_wp.py`. Automation scripts (`generate_blog_post.py`,
`seo_audit.py`, `add_tool.py`, `affiliate_link_sweep.py`) each run standalone
from inside `automation/` (they import sibling modules `config.py` /
`wp_client.py` directly, so run them from that directory or with it on
`PYTHONPATH`).
