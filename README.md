# K3 Professional Services website

The source for https://k3professionalservices.com. Netlify builds and publishes
it automatically whenever this repository changes.

## Writing blog posts

Go to **https://k3professionalservices.com/admin**, sign in with GitHub, and
click **New Blog Post**. Fill in the fields, write the post, and click
**Publish → Publish now**. The post is live about a minute later.

- **Drafts:** turn on "Save as draft" to save a post without publishing it.
- **Images:** upload them from the Cover image field or the image button in the
  editor. Landscape images under 500 KB keep pages fast.
- **Featured post:** turn on "Feature at the top of the blog page" for one post.
  If none is featured, the newest post goes first.

## How it's put together

| Folder | What's in it |
| --- | --- |
| `content/blog/` | One file per blog post (written by the editor) |
| `src/pages/` | Every other page: home, about, services, contact, legal |
| `src/templates/` | The blog page's banner and topic-suggestion form |
| `src/build.py` | Adds the shared menu, footer and search details to each page, builds the blog, sitemap and robots.txt |
| `static/` | Files copied as-is: styles, images, the editor at `/admin`, redirects |

`python3 src/build.py` builds the finished site into `site/`. It uses only
Python's standard library, so there is nothing to install.

Forms open the visitor's email app, addressed to general@k3professionalservices.com.

## Hosting notes

This repository is public on purpose: everything in it is already public on the
live site, and Netlify's free plan builds public repositories for any
contributor (it limits private ones to a single verified account).
