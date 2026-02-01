---
layout: default
title: All Publications
description: Complete list of publications by Ed Baker
---

# All Publications

{% for pub in site.data.publications %}
## [{{ pub.title }}]({{ pub.url }})

{% assign authors_highlighted = pub.authors | replace: "Baker, E.", "<u>Baker, E.</u>" %}
{% if pub.authors %}**{{ authors_highlighted }}**{% endif %}{% if pub.year %} ({{ pub.year }}){% endif %}{% if pub.pdf_url %} [[PDF]({{ pub.pdf_url }})]{% endif %}

{% if pub.abstract %}{{ pub.abstract }}{% endif %}

{% endfor %}
