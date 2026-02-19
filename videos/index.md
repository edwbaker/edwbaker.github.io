# Videos

{% for p in site.pages %}
{%- if p.url contains '/videos/' and p.url != '/videos/' -%}
- [{{ p.title | default: p.url | split: '/' | last | replace: '.html', '' }}]({{ p.url }})
{% endif %}
{%- endfor -%}
