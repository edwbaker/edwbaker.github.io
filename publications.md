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
    {%- assign i = 0 -%}
    {%- while i < pub_authors.size -%}
      {%- assign surname = pub_authors[i] -%}
      {%- assign given_idx = i | plus: 1 -%}
      {%- if given_idx < pub_authors.size -%}
        {%- assign given = pub_authors[given_idx] -%}
        {%- assign next_idx = given_idx | plus: 1 -%}
        {%- if given contains "." -%}
          {%- if i > 0 %},{% endif %}
    {"@type": "Person", "familyName": {{ surname | jsonify }}, "givenName": {{ given | jsonify }}}
          {%- assign i = next_idx -%}
        {%- else -%}
          {%- if i > 0 %},{% endif %}
    {"@type": "Person", "name": {{ surname | jsonify }}}
          {%- assign i = given_idx -%}
        {%- endif -%}
      {%- else -%}
        {%- if i > 0 %},{% endif %}
    {"@type": "Person", "name": {{ surname | jsonify }}}
        {%- assign i = i | plus: 1 -%}
      {%- endif -%}
    {%- endwhile -%}
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
