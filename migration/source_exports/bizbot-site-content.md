# bizbot.com — Site Content & Structure Export

Exported from the Unicorn Platform CMS (project: `biz-dir`, live at bizbot.com / staging at biz-dir.unicornplatform.page) on 2026-08-13. Not exhaustive — fill gaps as needed.

**Update:** a complete, verified list of every published URL on bizbot.com is in the companion file `bizbot-all-urls.csv` (622 URLs total), pulled directly from the live `https://www.bizbot.com/sitemap.xml` and checksum-verified against the site's own data. That supersedes the partial lists below — the CMS builder's page/post sidebar only surfaces a subset at a time (I'd originally found 61 blog posts and 95 tools by scrolling the builder UI; the real numbers are **512 blog posts** and **98 tool pages**). Use the CSV as the authoritative URL inventory for redirects/routing in the rebuild; use this document for the actual page copy and structure.

## Site overview

BizBot is a curated directory of business admin tools (SaaS tool listings organized by category), plus a blog with 60+ SEO/business articles. It's part of a small family of sister directory sites run by the same owner (Didrik Martens): sales-leads-crm.com, content-and-marketing.com, bizbot.no, work-smart-not-hard.tech. These are cross-linked in the footer but are separate projects/domains — out of scope for this export unless you want them too.

## Global navigation (header)

- Logo: "BB" mark + "Business Admin Tools"
- Nav links: **Home**, **About Us**, **Blog**
- CTA button: **Submit your tool!**
- Top announcement bar (site-wide, Unicorn Platform's own promo, not BizBot content): "Unicorn Platform: Try out this website builder for busy makers (20% discount coupon: viafirst20)" — this is a builder-injected ad bar, not real site content, and won't carry over to a rebuild.

## Global footer

- Tagline: "Admin Tools Directory - Streamlining your business operations."
- "Other directories" links: Sales, Leads & CRM tools / Content & Marketing tools / BizBot.no / WorkSmart, NotHard
- Social/follow links

---

## Pages

### 1. Home (`/`)

**Hero**
- H1: "Welcome to BizBot"
- Subhead: "Your comprehensive directory for the best business admin tools for your tech company"
- CTA button: "Explore Now"
- Supporting line: "Find the best tools to streamline your business operations"

**Directory / tool listing section**
- Intro: "One-stop directory for the best admin tools for companies."
- Category filter tags (all present as clickable categories):
  Accounting, Accounting software, Ads Management, Automation & Integration, Bank, Booking, Business planning, Business resources, Business Services, Collaboration, Communication, Communications, Content & Localization, CRM, Customer Service, Customer support, Digital Signatures, Equity management, File Storage, Funding, HR, HR tool, Influencer Marketing, Investor CRM, Legal, Legal Services, Marketing & CRM, Marketing Tools, Payroll, PR & Media, Productivity, Project & Team Tools, Project management, Project Management, Sales & Support Tools, SEO & Analytics, Skill mapping, Time Tracking, Workflow Automation
- Tool cards shown on homepage (each has name + short description; full list is longer, "Show all" button reveals more — likely pulls from a larger backend dataset):
  - **Quadim** — Solving the need for better competence data. Competence is not just about better data - it is about people, collaboration and productivity.
  - **Unicorn Platform** — A no-code website builder that helps startups and small teams create landing pages, blogs, and directories quickly without coding.
  - **SEOBot** — An AI-powered tool that automates SEO content planning and blog article generation. Helps teams maintain consistent publishing while optimizing...
  - **Quicklead** — A sales automation platform that helps teams organize leads, manage outreach campaigns, and track sales pipelines in a streamlined CRM-style interface.
  - **SearchAtlas** — An SEO platform that provides keyword research, competitor analysis, site audits, and performance tracking to help businesses improve search rankings.
  - **ClearCRM** — A customer relationship management platform designed to help teams track deals, manage contacts, and organize sales pipelines through a simple interface.
  - **QuickBooks** — Smart, simple online accounting software for small business. Track expenses, customise invoices, run reports and more, all from one place.
  - **Xero** — Xero online accounting software for your business connects you to your bank, accountant, bookkeeper, and other business apps.
  - *(button: "Show all" — full tool database is larger than what's shown; recommend pulling the complete list from the CMS's directory/database feature rather than page HTML, since it's dynamically rendered)*

**Embedded widgets** — two `tinyadz.com` ad/widget iframes embedded via custom HTML blocks (likely monetization widgets, not core content).

**"Why Choose Our Directory?" section**
- Heading: "Why Choose Our Directory? Find the Best Admin Tools for Your Business"
- Body: "We have carefully curated a comprehensive list of the best admin tools for companies, saving you valuable time and effort in finding the right tools to streamline your business operations and boost productivity."

**About section (also embedded on homepage)**
- Heading: "About Us - The Most Important Things to Know"
- Body: "Welcome to BizBot, your comprehensive directory for the best business admin tools. We are a team of dedicated professionals committed to providing you with the best admin tools for your business. Our platform is designed to streamline your business operations by offering a one-stop directory for all your admin tool needs. Stay updated with the latest tools and trends, and even suggest a tool for review. Ready to streamline your business? Start exploring our directory now!"

**Latest blog posts (homepage teaser, 4 shown)**
- 6 Best AI Presentation Makers for Businesses in 2026 Compared
- Best Email Deliverability Tools for Businesses in 2026
- Best Practices for E-commerce Analytics Integration
- Wireless Threat Detection for Small Businesses

**"Have a tool to suggest?" form section**
- Heading: "Have a tool to suggest?"
- Sub: "Submit your tool for review and get featured in our directory"
- Fields: Email, Website URL, Logo URL, Name of company, Description → Submit button
- Note: "We value your input and strive to provide the most comprehensive directory possible."

**Team section**
- Heading: "Meet Our Team"
- Sub: "We are a team of dedicated professionals committed to providing you with the best admin tools for your business."
- **John Rush** — Tech Maker — "Serial startup founder. Leading 20+ products."
- **Didrik Martens** — Business Maker — "Serial startup founder looking for help from other entrepreneurs from my projects. Read more about me on my blog https://www.eggemartens.com/"

**Newsletter section**
- Heading: "Stay Updated"
- Sub: "Subscribe to our newsletter for the latest updates and trends in admin tools."
- Email field + Subscribe button

---

### 2. Blog (`/blog`)

Blog listing/index page. The CMS builder sidebar only surfaced 61 posts before I found the real count via the live sitemap: **512 published posts**. All 512 URLs are in `bizbot-all-urls.csv`. Titles for the 61 most-recent posts are below (newest first) — full title list for all 512 wasn't pulled (that's a lot of individual page loads), but every URL is captured, so Claude Code can crawl/export full bodies from the live site or CMS as needed. Full body text was only pulled for post #1 as a sample.

1. 6 Best AI Presentation Makers for Businesses in 2026 Compared
2. Best Email Deliverability Tools for Businesses in 2026
3. Parallels Desktop for Developers: Run Windows and Linux on Your Mac Without Buying Another Computer
4. 6 Benefits of Using Cookiebot for Ecommerce Websites in 2026
5. 8 Cookiebot Features That Make Compliance Easier for Businesses in 2026
6. Top 5 Cookie Consent Management Platforms for Websites in 2026: Cookiebot, OneTrust, and More
7. Best Cookie Consent Management Platform for Website Admins in 2026: Cookiebot by Usercentrics
8. Aqua Mail: A Flexible Email Administration Tool for Managing Multiple Accounts Efficiently
9. How HubSpot Breeze AI Automates Tasks and Boosts Team Productivity
10. HubSpot CRM vs Zendesk: Which Customer Support Platform Delivers More Value?
11. HubSpot CRM: Why HubSpot Is the All-in-One Solution for Chat and Email Customer Care
12. MindManager for Students and Educators Review: Features, Benefits, and 65% Discount
13. Tidio Review: AI Chatbot and Help Desk Software for Small and Growing Businesses
14. Why Shutterstock Is a Must-Have Visual Content Tool for Tech Businesses
15. How Genspark AI Workspace Improves Productivity and Efficiency
16. What Most CRM Tools Miss — and How Rewarx Studio Fills the Gap for Growing Businesses
17. How Genspark Improves Conversion Rates Without Manual Optimization
18. Financial Planning for Business Owners: How to Protect and Grow Your Wealth
19. Stop Losing Leads: How HubSpot CRM Helps You Close More Deals Faster
20. 5 Common Trade Compliance Challenges and How the Right Software Solves Them
21. Leadership Skills Every Business Graduate Should Develop
22. Growing Too Fast? 7 Financial Signs You Need Bookkeeping Support Now
23. 5 Signs You Should Consider Virtual Home Staging Services Before Selling Your Property
24. How Does Digital Dentistry Improve Preventive Dental Care? 5 Ways
25. How Do You Market a Board Game on Kickstarter Successfully? 4 Proven Strategies
26. Business Administration for Tour Operators: Systems, Strategy, and Scalable Growth
27. How Small Manufacturers Can Reduce Downtime with the Right Tools
28. How SEO and Paid Ads Work Together to Drive Real Business Growth in 2026
29. 4 Healthcare Compliance Risks Organizations Must Monitor to Avoid Penalties
30. Why Multifamily Properties Struggle With Online Visibility (And How Marketing Can Help)
31. 6 Mistakes Businesses Make When Hiring App Developers
32. 5 Essential Things to Check Before Hiring an Influencer Marketing Agency
33. 6 Key Factors That Set a Reliable Business Supply Center Apart
34. 7 Best Productivity Tools for Remote Teams in 2026
35. Expert tips to help you back up your MacBook with ease
36. 6 Questions to Ask Before Hiring a Marketing Strategist for Your Business
37. Best Team Collaboration Tools for Remote Work
38. What Legal Risks Do Small Businesses Commonly Overlook?
39. How to Build an AI-Powered Admin System for Marketing and Sales
40. 5 Best Admin Tools to Streamline Business Operations in 2026
41. How Do You Choose the Right Home Health Software? 4 Factors to Compare
42. How Small Businesses Are Using AI to Create Scroll-Stopping Visual Content
43. Beyond the Resume: Ranking IT Staffing Companies by Onboarding Speed and Success Rates
44. Top 6 Subscription Management Software for Maximizing Revenue in 2026
45. The Business Skills Logistics Professionals Need to Stay Competitive
46. Operations to Outcomes: Career Growth for Modern Business Professionals
47. How Outsourced Fulfillment & Smart Business Tools Can Drive Growth In Modern Commerce
48. Why Generic SEO Doesn't Work for Competitive Industries
49. Top 9 GRC Software Solutions That Improve
50. Data Integrity in the Aisle: Eliminating Digital Fraud and Human Error with AI-Powered IR Solutions for FMCG
51. How to Build a Career in Business Without Quitting Your Current Job
52. 6 Ways Great Leaders Turn Data Into Decisions That Matter
53. Best Board Portal Providers in 2025
54. Why Purpose-Driven Networking Is the New Growth Engine
55. The Best Digital Marketing Agency Marketing Link in the USA in 2025
56. AI Tools Reshaping Business: How Companies Are Adapting Today
57. 7 Key Financial Management Practices for Startups
58. 15 Game-Changing IT Tools to Transform Your Business Operations
59. How Optimization Techniques Can Transform Business Analytics
60. 7 Essential Financial Management Tips for New Entrepreneurs
61. Aksjonærregsiteroppgaven *(Norwegian title — likely unrelated/test post, worth checking if it should carry over)*

**Sample full post (#1) structure**, for reference on typical article format:
- Title, intro paragraphs
- H2 sections (e.g. "Why Businesses Are Turning to...", "What Makes a Good...")
- Numbered comparison list with per-item subsections: intro blurb, "Key Features" bullet list, "Best For", "Before You Choose"
- "Frequently Asked Questions" section (Q&A pairs)
- "Final Verdict" closing section
- Standard post footer (same as site footer, without the newsletter/team blocks)

Recommend: if Claude Code needs full article bodies, either export via Unicorn Platform's "Export HTML" feature (found under Settings) or have me pull full text post-by-post — 60 posts is a lot to paste manually here.

---

### 3. `/tools`

This is a **dynamic template page**, not static content — it uses placeholder tokens (`{{$title}}`, `{{$text}}`, `{{$category}}`) plus a "WHOA! / Get it" CTA block. This is the template used to render individual tool detail pages from the directory database. It renders **98 individual tool pages** at `/tools/<slug>/` (e.g. `/tools/quickbooks/`, `/tools/hubspot/`, `/tools/slack/` — full list of all 98 slugs is in `bizbot-all-urls.csv`). Structure to preserve in the rebuild:
- Tool title
- Tool description text
- Category tag
- CTA button ("Get it" / outbound link to the tool)

### New: `/news`

Not visible in the CMS builder's page list at all (I only found it via the live sitemap) — a separate news/articles section with its own index and **6 short articles**: AthenaHealth AI patient communication tools, OpenAI Pulse/ChatGPT personalization, Cohere's $6.8B valuation, Stripe's Australia lending expansion, Google's free AI video editing tools, and WhatsApp's AI writing assistant. Worth checking this in the CMS directly since I haven't pulled its content/structure — only confirmed it exists and has these 7 URLs (index + 6 posts).

### 4. `/guest-post-pricing`

**Heading:** "Guest Post Pricing"
**Sub:** "Boost your online presence with high-quality guest posts."
**Quote:** "Backlinks remain one of the most important factors for SEO success, helping websites improve visibility and authority." – Moz

**Pricing tiers:**
| Plan | Articles | Price | Backlinks | Notes |
|---|---|---|---|---|
| Basic | 6 articles | $150/year | 2 do-follow backlinks | Cancel anytime, Premium support |
| Standard | 16 articles | $250/year | 2 do-follow backlinks | Cancel anytime, Premium support |
| Premium | 25 articles | $350/year | 2 do-follow backlinks | Cancel anytime, Premium support |

**Additional terms:** "Link insertions are offered at the same price. Pricing is based on client-provided articles. If we prepare the content, an additional $25 per article applies. After one year of publishing your article, we can add additional links to that article."

**Our Publishing Network** (owned sites where guest posts are published):
- https://www.bizbot.com/
- https://www.sales-leads-crm.com/
- https://www.content-and-marketing.com/
- https://work-smart-not-hard.tech/

**CTA section:** "Ready to Grow Your Online Presence? Select the package that fits your goals or contact us for a custom solution. With Bizbot.com, you'll get more than guest posts — you'll get a partner committed to your SEO success. 📧 Email us at didrik@bizbot.no"

**SEO/body copy sections:** "Why Guest Posting Is Essential for SEO", "Benefits of Choosing Bizbot.com Guest Post Packages" (do-follow backlinks, premium content creation, flexible cancellation, dedicated support), "How Guest Posts Drive Results"

### 5. `/home-clone`

Exact duplicate of the Home page content (word-for-word). Looks like a backup/draft copy left in the CMS — probably safe to ignore/not carry into the rebuild, but flagging in case it was intentional (e.g. an A/B variant).

### 6. `/devtools` and `/nocode`

Both **unpublished**, and both contain identical leftover Unicorn Platform template/demo content ("Best DevTools" / "Best NoCode" headers, generic "Submit Your Startup" GPT-directory template, fake team bios for "Alexander Isora", "Adaline Clay", etc.). This is boilerplate scaffolding from the page template, not real BizBot content — recommend ignoring both unless you intended to build these out.

---

## Notes / things Claude Code should know

- The live/full tool directory is larger than what renders in the homepage HTML (homepage shows 8 of the full 98 tools). Confirmed via sitemap: **98 tool pages** at `/tools/<slug>/`, all listed in `bizbot-all-urls.csv`.
- **Full URL count: 622** (1 home + 1 home-clone + 1 guest-post-pricing + 513 blog section incl. index + 99 tools section incl. index + 7 news section incl. index). Verified by fetching `https://www.bizbot.com/sitemap.xml` directly and checksum-comparing against the reconstructed list — see `bizbot-all-urls.csv` for the definitive, verified list. If rebuilding on a new stack, preserve these exact paths (with trailing slashes, matching the sitemap) for 301 redirects / routing so no inbound links or SEO equity are lost.
- Two embedded `tinyadz.com` widget iframes on the homepage are third-party ad/monetization embeds, not original content.
- Contact email on file: didrik@bizbot.no
- Sister properties cross-linked in footer (separate CMS projects, not part of this export): sales-leads-crm.com, content-and-marketing.com, bizbot.no, work-smart-not-hard.tech
