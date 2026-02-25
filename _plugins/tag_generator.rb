module Jekyll
  class TagPageGenerator < Generator
    safe true

    def generate(site)
      if site.layouts.key? 'tag'
        seen_slugs = {}
        site.tags.each_key do |tag|
          slug = Utils.slugify(tag)
          next if seen_slugs.key?(slug)
          seen_slugs[slug] = true
          site.pages << TagPage.new(site, site.source, tag)
        end
      end
    end
  end

  class TagPage < Page
    def initialize(site, base, tag)
      @site = site
      @base = base
      @dir  = File.join('tags', Utils.slugify(tag))
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'tag.html')
      self.data['tag'] = tag

      # Merge posts from all case variants of this tag
      slug = Utils.slugify(tag)
      all_posts = site.tags.select { |t, _| Utils.slugify(t) == slug }.values.flatten.uniq
      self.data['title'] = "Posts tagged \"#{tag}\""
      self.data['posts'] = all_posts
    end
  end
end
