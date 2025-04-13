# Building a Local Gutenberg Library  

I like programming. It's fun. It's challenging. It's a great problem-solving exercise. So yeah, I like programming. But I *love* reading. A lot. Like more than you think. And because I love reading, one of my favorite websites--actually, my very favorite website--is [Project Gutenberg](https://gutenberg.org) (PG).

In case you're not familiar with PG, it's a collection of tens of thousands of books that are in the public domain. As you might imagine, the collection abounds with the classics as well as thousands upon thousands of lesser known works. It's a reader's paradise. Most works are available in multiple formats: web, epub, kindle, plain text, and some are even available as audiobooks. And while it appears that most texts are in English, there is a healthy body of non-English literature.  

For a while, I've wanted to curate my own collection of PG texts. Sure, the easiest way would just be to bookmark links to my favorite books. But why do that when I can marry my love of reading with my enjoyment of programming? Enter the Local Gutenberg Library. In a nutshell, I have created a Django app that indexes, organizes, and displays for reading all my favorite PG books. What follows is not a tutorial--the Django is pretty basic and the techniques can be easily learned by any one of the hundreds of excellent tutorials already available. I am, at best, a hobbyist who enjoys programming not because I want to produce widely usable things but because I enjoy the planning and problem-solving that creating a project like this requires of the amateur like myself. Rather, I want to take you through the planning, challenges, and solutions in putting this project together at high level. If you're an experience developer (especially if you're an experienced Django developer), there's probably nothing new in here for you. But if you're just starting out, I hope this will give you a little insight as to how you might go forward with executing what is, in the end, a fairly simple project.

### Requirements  
As I thought about this site, I had a few basic requirements. While I had a list of initial requirements, the list evolved as the site came together. Software/web development is often an iterative process. You do something. You run into challenges or needs you didn't know about until you did that something. Then you have new requirements. Then you repeat. Here's the initial wishlist.
1. I wanted the ability to list my favorite books by title and author.
2. I wanted to be able to create collections of similarly themed books: a philosophy collection, history collection, Sherlock Holmes collection, etc.
3. I wanted search capabilities, allowing me to search by author, title, or collection.
4. I wanted to be able to read each book as a web page, much like they appear on the PG site.
5. I wanted to store as little data as possible locally, preferring to leverage information already available on PG, particularly the text of the books.

### Basic Structure  
The site is built on three very basic models: An author model. A Book model with an Author foreign key. And a Collection model containing a many to many relationship with the Book model. We'll break the models down in more detail later because that's where the magic really happens.

The home page has three links: one to a list of books, one to a list of authors, and one to a list of collections. The items in the book list are linked to the book detail page containing the text of the chosen book. The author list items are linked to a list of books by the chosen author (each of which is linked again to the book detail). And the collection page with links to collections of books (which collections contain links to book details).  

### Where Did I Get the Books?  
Considering I spent the opening couple of paragraphs talking about Project Gutenberg, I don't think it's any surprise that I decided to get the texts from PG, but how? As I said earlier, PG makes texts available in multiple formats. This brings us now to the first decision.

#### How do I retrieve the book texts?  
PG gives you several options. After finding the book you're looking for on PG, you're taken to a landing page for that book giving you the reading/download options. There's a link to read the book simply as a webpage. Those pages are usually formatted simply but pleasantly and often contain pictures. There are several download options in various formats including epub, epub3, and kindle (which I don't believe Amazon recommends anymore). There is also an option to download a zip file containing the html from the webpage version along with an image directory for any images on the page. Finally, there is a plaintext version using utf-8 encoding. So which one to choose?  

The "analog" way to do it would be simply to go to the plaintext version of the book, ctrl-a to copy everything, and then paste it somewhere. The most obvious choice is simply to make the book text one of the Book model fields and paste it there and then use it to populate the book detail template. However, that didn't quite fit into my plan. For one, I didn't want to store book text. No, plaintext doesn't take up a lot of room, but let's face it, if you start adding more than a few Dickens or Tolstoy novels, it starts to add up. Also, the plaintext versions of the books have hard-coded line breaks. If I was to paste the text directly into the template (with a 'linebreaks' filter), the page wouldn't be terribly responsive, leading to funky formatting at certain window sizes. And while generally, the plaintext formatting is such that you can differentiate between paragraphs and chapter, for what I wanted to achieve, I'd have to spend a fair amount of time pressing a lot of buttons. Highlighting, copying, pasting, reformatting much of the text -- not something I was interested in doing. I wanted to let the app do the heavy lifting. Otherwise, I'd just copy and paste into a Word document and move on. 

Another approach could have been to download the zip files containing html and images, store those, and again load them into the detail template. This approach has several advantages over the "analog" approach. I'd have any images that went along with the text. The book would already be formatted using html, making a responsive page much easier to create while I added my own CSS to complement or replace the existing CSS. But this still didn't do it for me. First, I'd still have to put the downloaded content somewhere so I could retrieve it. Remember, I didn't want to store anything and this approach included images which can start to eat up storage space very quickly. And besides, it was all still very manual.  

I toyed around with the idea of putting an iframe in the book detail pages that simply displayed the webpage version of the books directly into the template. It certainly solve the storage problem and I would get the nicely formatted webpage version perfectly recreated in my template. However, iframes have their own set of problems. First, you can't format anything *inside* the iframe. Resizing your app window might resize the iframe with the right styling, but the content inside the iframe wouldn't change. In addition (and we'll get to this later), I didn't necessarily want *everything* on the PG webpage to show up in my app. Second, I didn't want a separate scrollbar inside my app's page. Third, iframes are kind of a pain in the butt to style. No, an iframe would be a simple enough solution, but only if I compromised my vision for the site.  

What if, however, I extracted the html from the webpage version of the books, maybe tweaked a few things in the markup and formatting in memory, and then fed it directly into my template? All of the "tweaking" would be done programmatically and on the fly, so there would no need to store large amounts of text data. This had potential and, in fact, was the approach I took.  

To best see how I did this, let's look at the Book model.  
```python
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, blank=True, null=True)
    url = models.URLField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    collections = models.ManyToManyField('Collection', related_name='books', blank=True)

    @property
    def book_html(self):
        url = self.url
        base_url_end = url.find("pg")
        base_url = url[:base_url_end]
        response = requests.get(url)
        full_html = response.text
        body_close = full_html.find('</body>')
        start = full_html.find("<body>")
        text = full_html[start + 6: body_close]
        soup = BeautifulSoup(text, "html.parser")
        for img in soup.find_all("img"):
            img["src"] = base_url + img["src"]
        for section in soup.find_all("section", class_="pg-boilerplate"):
            section.decompose()
        return str(soup)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
```
The basic structure is very simple. There are five fields: title, author (a Foreign Key to the Author model), url (for the webpage version of the book), slug (for use with url paths), and finally a collections field (a ManyToManyField linked to the Collection model). So at the outset, it's worth noting that these are the only things being stored in our model. An book's entire record would be nothing more than a few k. So far so good. The magic happens in the next part, the `book_html` property. If you're new to Django or have never encountered or used model properties, they are incredibly useful and powerful tools. They allow you to define other model attributes based on the model's fields. For example, I currently have an app in production that, among other things, collects a client's date of birth. I also wanted to be able to see the client's age at any given time. After Django 5, I could have just created a "GeneratedField" which allows you define full-blown model fields using values from other fields. The problem was that the age would be calculated and stored when the instance is saved meaning if I save a client and then pull up their information a year later, the age would be inaccurate because it was calculated at save, not when the record is called up. The logic for a model property, however, executes when it is called, so the age is always up to date. Here, my issue with a GeneratedField was that I'd still be storing the extracted html in my database. Sure, it would make retrieval faster, but this is a personal project that will only ever have one user at a time, so performance wasn't necessarily high on my priority list.