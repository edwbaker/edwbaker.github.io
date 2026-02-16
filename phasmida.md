# Phasmida

Phasmida (stick insects and leaf insects) are a fascinating order of insects known for their remarkable camouflage. I have worked on phasmid taxonomy and their status as agricultural pests.

## Publications

{% for pub in site.data.publications %}
{% if pub.topics contains "phasmids" %}
- [{{ pub.title }}]({{ pub.url }}) ({{ pub.year }}){% if pub.journal %} _{{ pub.journal }}_{% endif %}
{% endif %}
{% endfor %}

## External Resources

- [Phasmida Species File](https://phasmida.speciesfile.org/) - Comprehensive taxonomic database for Phasmida
- [Phasmid Study Group](https://phasmid-study-group.org/) - Organisation for the study of stick insects
