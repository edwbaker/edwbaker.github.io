---
layout: default
title: All Publications
description: Complete list of publications by Ed Baker
---

# All Publications

{% for pub in site.data.publications %}
## [{{ pub.title }}]({{ pub.url }})

{% if pub.authors %}**{{ pub.authors }}**{% endif %}{% if pub.year %} ({{ pub.year }}){% endif %}{% if pub.pdf_url %} [[PDF]({{ pub.pdf_url }})]{% endif %}

{% if pub.abstract %}{{ pub.abstract }}{% endif %}

{% endfor %}

## External profiles

- [Google Scholar](https://scholar.google.com/citations?user=44XAtwYAAAAJ)
- [ORCID](https://orcid.org/0000-0002-5887-9543)
- [Co-authorship Cloud](/pubs/wikidata-author-cloud)
