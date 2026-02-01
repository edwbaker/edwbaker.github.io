# Orthoptera

Orthoptera (grasshoppers, crickets, and katydids) are one of the most acoustically diverse insect orders. Many species communicate using sound, making them ideal subjects for bioacoustic research.

## Publications

{% for pub in site.data.publications %}
{% if pub.topics contains "orthoptera" %}
- [{{ pub.title }}]({{ pub.url }}) ({{ pub.year }}){% if pub.journal %} _{{ pub.journal }}_{% endif %}
{% endif %}
{% endfor %}

## Related Notes

- [Prophalangopsis](/notes/prophalangopsis)

## External Resources

- [BioAcoustica](https://bio.acousti.ca) - Sound recordings of Orthoptera and other insects
