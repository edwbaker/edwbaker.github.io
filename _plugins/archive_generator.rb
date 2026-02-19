module Jekyll
  class ArchiveGenerator < Generator
    safe true

    MONTH_NAMES = %w[
      January February March April May June
      July August September October November December
    ].freeze

    def generate(site)
      return unless site.layouts.key?('archive_year') && site.layouts.key?('archive_month')

      # Group posts by year and month
      by_year = {}
      site.posts.docs.each do |post|
        year  = post.date.strftime('%Y')
        month = post.date.strftime('%m')

        by_year[year] ||= {}
        by_year[year][month] ||= []
        by_year[year][month] << post
      end

      by_year.each do |year, months|
        # Collect month summary for the year page
        month_summary = months.map do |num, posts|
          { 'num' => num, 'name' => MONTH_NAMES[num.to_i - 1], 'count' => posts.size }
        end.sort_by { |m| m['num'] }.reverse

        all_posts_in_year = months.values.flatten.sort_by { |p| p.date }.reverse

        # Create year page at /:year/
        site.pages << ArchiveYearPage.new(site, site.source, year, all_posts_in_year, month_summary)

        # Create month pages at /:year/:month/
        months.each do |month_num, posts|
          sorted = posts.sort_by { |p| p.date }.reverse
          month_name = MONTH_NAMES[month_num.to_i - 1]
          site.pages << ArchiveMonthPage.new(site, site.source, year, month_num, month_name, sorted)
        end
      end
    end
  end

  class ArchiveYearPage < Page
    def initialize(site, base, year, posts, months)
      @site = site
      @base = base
      @dir  = year
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'archive_year.html')
      self.data['year']   = year
      self.data['posts']  = posts
      self.data['months'] = months
      self.data['title']  = "Posts from #{year}"
    end
  end

  class ArchiveMonthPage < Page
    def initialize(site, base, year, month_num, month_name, posts)
      @site = site
      @base = base
      @dir  = File.join(year, month_num)
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'archive_month.html')
      self.data['year']       = year
      self.data['month']      = month_num
      self.data['month_name'] = month_name
      self.data['posts']      = posts
      self.data['title']      = "Posts from #{month_name} #{year}"
    end
  end
end
