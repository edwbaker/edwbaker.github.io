Jekyll::Hooks.register [:pages, :posts], :pre_render do |doc|
  url = doc.url.sub(/\.html\z/, '')
  url = '/' if url.empty?
  doc.data['canonical_url'] = "#{doc.site.config['url']}#{url}"
end
