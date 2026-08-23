module Jekyll
  class KeywordPageGenerator < Generator
    safe true

    def generate(site)
      keywords = site.data['publications'].flat_map { |publication| publication['topics'] || [] }.uniq
      site.config['publication_keywords'] = keywords.sort
      keywords.each do |keyword|
        site.pages << KeywordPage.new(site, site.source, keyword)
      end
    end
  end

  class KeywordPage < Page
    def initialize(site, base, keyword)
      @site = site
      @base = base
      @dir = File.join('keywords', Utils.slugify(keyword))
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'keyword.html')
      self.data['keyword'] = keyword
      self.data['title'] = keyword.tr('-', ' ').capitalize
      self.data['publications'] = site.data['publications'].select do |publication|
        (publication['topics'] || []).include?(keyword)
      end
    end
  end
end
