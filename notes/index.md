---
layout: default
title: Notes
description: Notes and resources by Ed Baker
---

# Notes

{% assign notes_by_category = site.data.notes | group_by: "category" %}
{% for category in notes_by_category %}
## {{ category.name }}

{% assign has_subcategories = category.items | where_exp: "item", "item.subcategory" | size %}
{% if has_subcategories > 0 %}
{% assign subcats = category.items | group_by: "subcategory" %}
{% for subcat in subcats %}
{% if subcat.name and subcat.name != "" %}
### {{ subcat.name }}

{% endif %}
{% for note in subcat.items %}
- [{{ note.title }}]({{ note.url }})

{% endfor %}
{% endfor %}
{% else %}
{% for note in category.items %}
- [{{ note.title }}]({{ note.url }})

{% endfor %}
{% endif %}
{% endfor %}
