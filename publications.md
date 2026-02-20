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

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "name": {{ pub.title | jsonify }},
  "headline": {{ pub.title | jsonify }}
  {%- if pub.url %},
  "url": {% if pub.url contains '://' %}{{ pub.url | jsonify }}{% else %}{{ pub.url | prepend: site.url | jsonify }}{% endif %}
  {%- endif %}
  {%- if pub.authors %},
  "author": [
    {%- assign pub_authors = pub.authors | split: ", " -%}
    {%- assign last_index = pub_authors.size | minus: 1 -%}
    {%- for i in (0..last_index) -%}
      {%- if i | modulo: 2 == 0 -%}
        {%- assign surname = pub_authors[i] -%}
        {%- assign given_idx = i | plus: 1 -%}
        {%- if given_idx <= last_index -%}
          {%- assign given = pub_authors[given_idx] -%}
          {%- if i > 0 %},{% endif %}
    {"@type": "Person", "familyName": {{ surname | jsonify }}, "givenName": {{ given | jsonify }}}
        {%- else -%}
          {%- if i > 0 %},{% endif %}
    {"@type": "Person", "name": {{ surname | jsonify }}}
        {%- endif -%}
      {%- endif -%}
    {%- endfor -%}
  ]
  {%- endif %}
  {%- if pub.year %},
  "datePublished": "{{ pub.year }}"
  {%- endif %}
  {%- if pub.journal %},
  "isPartOf": {"@type": "Periodical", "name": {{ pub.journal | jsonify }}}
  {%- endif %}
  {%- if pub.abstract %},
  "abstract": {{ pub.abstract | jsonify }}
  {%- endif %}
}
</script>

{% endfor %}
